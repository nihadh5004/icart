from django.urls import path,include
from . import views
urlpatterns = [
   path('', views.home , name='home'),
   path('signin', views.signin  ,name='signin' ),
   path('signup', views.signup ,name='signup'),
   path('activate/<uidb64>/<token>', views.activate ,name='activate'),
   path('verify_otp/<user_for_otp>',views.verify_otp,name='verify_otp'),
   path('signout', views.signout ,name='signout'),
   path('send_otp', views.send_otp , name='send_otp')
]
