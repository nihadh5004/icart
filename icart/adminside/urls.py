from django.urls import path
from . import views
urlpatterns = [
    path('_admin_dashboard', views._admin_dashboard , name='_admin_dashboard'),
    path('_admin', views._admin_signin ,name='_admin_signin'),
    path('_admin_signout', views.admin_signout ,name='admin_signout'),
    path('userlist', views.userlist ,name='userlist'),
    path('user/<int:user_id>/block/', views.block_user, name='block_user'),
    path('user/<int:user_id>/unblock/', views.unblock_user, name='unblock_user'),
    path('productlist', views.productlist  ,name='productlist'),
    path('pending_orders', views.pending_orders  ,name='pending_orders'),
    path('categorylist', views.categorylist , name='categorylist'),
    path('create_category', views.create_category , name='create_category'),
    
    # path('create_product', views.create_product , name='create_product'),
    # path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete_product_image/<int:product_image_id>' , views.delete_product_image , name='delete_product_image'),
    # path('save_product/<int:product_id>/', views.save_product, name='save_product'),
    path('softdelete/<int:product_id>/', views.softdelete_product, name='softdelete_product'),
    path('undo_softdelete/<int:product_id>/', views.undo_softdelete_product, name='undo_softdelete_product'),
    path('orderlist' , views.orderlist , name='orderlist'),
    path('order_details/<int:order_id>' , views.order_details , name='order_details'),
    path('update_order' , views.update_order , name='update_order'),
    path('reject_order/<int:order_id>' , views.reject_order , name='reject_order'),
    path('add_product', views.add_product , name='add_product'),
    path('productvariantlist/<int:product_id>' , views.productvariantlist , name='productvariantlist'),
    path('add_variant/<int:product_id>' , views.add_variant , name='add_variant'),
    path('edit_variant/<int:variant_id>' , views.edit_variant , name='edit_variant'),
   
    path('download_template/', views.download_template, name='download_template'),
    path('couponlist', views.couponlist, name='couponlist'),
    path('create_coupon', views.create_coupon , name='create_coupon'),
    path('disable_coupon/<int:coupon_id>' , views.disable_coupon , name='disable_coupon'),
    path('enable_coupon/<int:coupon_id>' , views.enable_coupon , name='enable_coupon'),
    path('edit_coupon/<int:coupon_id>' , views.edit_coupon , name='edit_coupon'),
    path('referral', views.referral , name='referral'),
    path('add_referral', views.add_referral , name='add_referral'),
    path('edit_referral', views.edit_referral , name='edit_referral'),
    path('delete_referral', views.delete_referral , name='delete_referral'),
    
    path('create_banner', views.create_banner , name='create_banner'),
    path('banners', views.banners , name='banners'),
    path('delete_banner/<int:banner_id>' , views.delete_banner , name='delete_banner'),


]