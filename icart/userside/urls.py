from django.urls import path,include
from . import views

urlpatterns = [
  path('checkout>', views.checkout, name='checkout'),
  path('add_address', views.add_address, name='add_address'),
  path('edit_address/<int:address_id>', views.edit_address, name='edit_address'),
  path('payment_page/<int:address_id>', views.payment_page , name='payment_page'),
  path('place_order/<int:address_id>', views.place_order , name='place_order'),
  path('my_orders', views.my_orders , name='my_orders'),
  path('_cancel_order', views.cancel_order , name='cancel_order'),
  path('return_order', views.return_order , name='return_order'),
  path('profile_details', views.profile_details , name='profile_details'),
  path('address', views.address, name='address'),
  path('profile_add_address', views.profile_add_address, name='profile_add_address'),
  path('user_order_detail/<int:order_id>', views.user_order_detail , name='user_order_detail'),
  path('order_confirmation/<int:order_id>' , views.order_confirmation , name='order_confirmation'),
  path('initiate_payment', views.initiate_payment, name='initiate_payment'),
  path('initiate_refund', views.initiate_refund, name='initiate_refund'),
  path('change_password/<int:user_id>', views.change_password , name='change_password'),
  path('wallet' ,views.wallet, name='wallet'),
  path('mail_to_emailchange' , views.mail_to_emailchange , name='mail_to_emailchange'),
  path('verify_otp_for_mail' , views.verify_otp_for_mail , name='verify_otp_for_mail'),
]
