from django.urls import path,include
from . import views

urlpatterns = [
  path('addcart/<slug:slug>', views.addcart, name='addcart'),
  path('wishlist', views.wishlist, name='wishlist'),
  path('addwishlist', views.addwishlist, name='addwishlist'),
  path('removewishlist', views.removewishlist, name='removewishlist'),
  path('cart', views.cart, name='cart'),
  path('update_quantity',views.update_quantity,name='update_quantity'),
  path('removecart/<int:product_id>', views.removecart, name='removecart'),
  path('delete_coupon/<int:cart_id>' , views.delete_coupon , name='delete_coupon'),
  path('getcart', views.getcart , name='getcart'),
  # path('add_to_guestcart', views.add_to_guestcart , name='add_to_guestcart'),
]
