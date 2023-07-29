from django.urls import path
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
   path('_reset_password', views.reset_password , name='reset_password'),
   path('res_pass/<uidb64>/<token>', views.res_pass ,name='res_pass'),
   path('update_password/<int:user_id>', views.update_password, name='update_password'),
   path('email_send', views.email_send , name='email_send')
]
