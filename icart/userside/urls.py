from django.urls import path,include
from . import views

urlpatterns = [
  path('checkout>', views.checkout, name='checkout'),
  path('add_address', views.add_address, name='add_address'),
  path('edit_address/<int:address_id>', views.edit_address, name='edit_address'),
  path('payment_page/<int:address_id>', views.payment_page , name='payment_page'),
  path('place_order/<int:address_id>', views.place_order , name='place_order'),
  path('my_orders', views.my_orders , name='my_orders'),
  path('cancel_order/<int:order_id>', views.cancel_order , name='cancel_order'),
  path('profile_details', views.profile_details , name='profile_details'),
  path('address', views.address, name='address'),
  path('profile_add_address', views.profile_add_address, name='profile_add_address'),

]
