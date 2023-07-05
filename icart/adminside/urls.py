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
    path('ship_order/<int:order_id>' , views.ship_order , name='ship_order'),
    path('reject_order/<int:order_id>' , views.reject_order , name='reject_order'),
    path('add_product', views.add_product , name='add_product'),
    path('productvariantlist/<int:product_id>' , views.productvariantlist , name='productvariantlist'),
    path('add_variant/<int:product_id>' , views.add_variant , name='add_variant'),
    path('edit_variant/<int:variant_id>' , views.edit_variant , name='edit_variant'),
]