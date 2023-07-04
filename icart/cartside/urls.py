from django.urls import path,include
from . import views

urlpatterns = [
  path('addcart/<slug:slug>', views.addcart, name='addcart'),
  path('cart', views.cart, name='cart'),
  path('update_quantity',views.update_quantity,name='update_quantity'),
  path('removecart/<int:product_id>', views.removecart, name='removecart'),

]
