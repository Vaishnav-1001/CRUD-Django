import random
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.mail import send_mail
from .models import todo, OTPRecord

# Create your views here.

@login_required
def home(request):
    if request.method == "POST":
        task = request.POST.get('task')
        # Store task only if task is not empty and not just spaces 
        if task and task.strip():
            new_todo = todo(username=request.user, item_name=task)
            new_todo.save()
        return redirect('home-page')
        
    todos = todo.objects.filter(username=request.user)
    return render(request, 'todoapp/todo.html', {'todos': todos})


def register(request):
    if request.user.is_authenticated:
        return redirect('home-page')
        
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confirmpassword')
        email = request.POST.get('email')
         
        # Password checks
        if len(password) < 8:
            messages.error(request, 'Password should be at least 8 characters')
            return redirect('register-page')
        elif password != confirmpassword:
            messages.error(request, 'Passwords do not match')
            return redirect('register-page')
            
        # Unique username check
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists...')
            return redirect('register-page')
        
        # 1. Generate 6-digit code
        otp_code = str(random.randint(100000, 999999))
        
        # 2. Save to database
        OTPRecord.objects.update_or_create(
            email=email,
            defaults={'otp': otp_code, 'created_at': timezone.now()}
        )
         
        # 3. Send Email
        send_mail(
            'Your Registration Code',
            f'Your OTP is: {otp_code}. It expires in 5 minutes.',
            'noreply@yourdomain.com',
            [email],
            fail_silently=False,
        )
        
        # 4. Save registration details to session for the verification view
        request.session['reg_email'] = email
        request.session['reg_username'] = username
        request.session['reg_password'] = password

        return redirect('verify_otp')

    return render(request, 'todoapp/register.html', {})


def verify_otp(request):
    # Retrieve data from the registration session pipeline
    email = request.session.get('reg_email')
    username = request.session.get('reg_username')
    password = request.session.get('reg_password')
    
    # Send user back if registration data is absent
    if not email or not username or not password:
        messages.error(request, "Please start the registration process first.")
        return redirect('register-page')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        
        try:
            record = OTPRecord.objects.get(email=email)
            
            if record.is_expired():
                messages.error(request, "OTP has expired. Please register again.")
                return redirect('register-page')
                
            if record.otp == entered_otp:
                # SUCCESS! Write user account to the database
                new_user = User.objects.create_user(username=username, password=password, email=email)
                new_user.save()
                
                # Cleanup: Wipe OTP record and staging sessions
                record.delete() 
                del request.session['reg_email']
                del request.session['reg_username']
                del request.session['reg_password']
                
                messages.success(request, "Registration successful! You can now log in.")
                return redirect('login-page') 
            else:
                messages.error(request, "Invalid OTP. Please try again.")
                
        except OTPRecord.DoesNotExist:
            messages.error(request, "No OTP found for this email.")
            return redirect('register-page')

    return render(request, 'todoapp/verify_otp.html', {'email': email})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home-page')
        
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Validate profile credentials
        validate_user = authenticate(request, username=username, password=password)
        
        if validate_user is not None:
            login(request, validate_user)
            return redirect('home-page')
        else:
            messages.error(request, 'Wrong user details or User does not exist')
            return redirect('login-page')
        
    return render(request, 'todoapp/login.html', {})


def logout_view(request):
    logout(request)
    return redirect('login-page')


def delete(request, item_name):
    get_todo = todo.objects.filter(username=request.user, item_name=item_name)
    get_todo.delete()
    return redirect('home-page')


def update(request, item_name):
    # Update task completion status
    todo.objects.filter(username=request.user, item_name=item_name).update(status=True)
    return redirect('home-page')
