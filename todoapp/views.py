from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from .models import todo
from django.contrib.auth.decorators import login_required
# Create your views here.


@login_required
def home(request):
    if request.method == "POST":
        task = request.POST.get('task')
        new_todo = todo(username = request.user, item_name = task)
        new_todo.save()
        return redirect('home-page')
    todos = todo.objects.filter(username = request.user)
    return render(request, 'todoapp/todo.html', {'todos':todos})

def register(request):
    if request.user.is_authenticated:
        return redirect('home-page')
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confirmpassword')
         
        #check for password length
        if len(password) < 8:
            messages.error(request, 'Password should atleast 8 characters')
            return redirect('register-page')
        elif password!= confirmpassword:
            messages.error(request, 'Password donot match')
            return redirect('register-page')
        get_all_users = User.objects.filter(username=username)
        print(get_all_users)
        # User already exist...
    
        if get_all_users:
            messages.error(request, 'Username already exist...')
            return redirect('register-page')
        
        messages.success(request,"Registration successful! Redirecting to login...")
        new_user = User.objects.create_user(username= username, password =password)
        new_user.save()

        return render(request, 'todoapp/register.html',{'reg_success':True})
        


    return render(request, 'todoapp/register.html', {})

def logout_view(request):
    logout(request)
    return redirect('login-page')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home-page')
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        #check whether the user exist or not
        #if User exist return User object alse None
        validate_user = authenticate(request,username=username,password=password)
        # user exist
        if validate_user is not None:
            #if user exist redirect to home page..
            login(request,validate_user)
            return redirect('home-page')
        else:
            messages.error(request,'Wrong user details or User does not exist')
            return redirect('login-page')
        
    return render(request,'todoapp/login.html', {})


def delete(request,item_name):
    get_todo = todo.objects.filter(username=request.user, item_name=item_name)
    get_todo.delete()
    return redirect('home-page')

def update(request,item_name):
    #Update the existing task status..
    todo.objects.filter(username=request.user, item_name=item_name).update(status=True)
    return redirect('home-page')