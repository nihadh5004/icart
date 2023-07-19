from django.urls import path,include
from . import views

from django.contrib.auth import views as auth_views

urlpatterns = [
   path('', views.home , name='home'),
   path('signin', views.signin  ,name='signin' ),
   path('guest_signin', views.guest_signin  ,name='guest_signin' ),
   path('signup', views.signup ,name='signup'),
   path('activate/<uidb64>/<token>', views.activate ,name='activate'),
   path('verify_otp/<user_for_otp>',views.verify_otp,name='verify_otp'),
   path('guest_verify_otp/<user_for_otp>',views.guest_verify_otp,name='guest_verify_otp'),
   path('signout', views.signout ,name='signout'),
   path('send_otp', views.send_otp , name='send_otp'),
   
   
   # path('reset_password/', auth_views.PasswordResetView.as_view(template_name='authentication/reset_password.html'), name='reset_password'),
   # path('reset_password_done/', auth_views.PasswordResetDoneView.as_view(template_name='authentication/reset_password_done.html'), name='password_reset_done'),
   # path('reset_password_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='authentication/reset_password_confirm.html'), name='password_reset_confirm'),
   # path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='authentication/reset_password_complete.html'), name='password_reset_complete'),


   path('_reset_password', views.reset_password , name='reset_password'),
   path('res_pass/<uidb64>/<token>', views.res_pass ,name='res_pass'),
   path('update_password/<int:user_id>', views.update_password, name='update_password'),
]
