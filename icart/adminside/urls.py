from django.urls import path,include
from . import views

urlpatterns = [
  path('admin_signin', views.admin_signin, name='admin_signin'),
]