from django.urls import path
from . import views


urlpatterns = [
    path('', views.login_view , name = "login-page"),
    path('home/', views.home , name = "home-page"),
    path('register/', views.register , name = "register-page"),
    path('delete-task/<str:item_name>/', views.delete , name = "delete"),
    path('update-task/<str:item_name>/', views.update , name = "update"),
     path('logout/', views.logout_view , name = "logout"),
     path('verify_otp/',views.verify_otp, name='verify_otp')
]