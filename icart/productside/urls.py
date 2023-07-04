from django.urls import path,include
from . import views
urlpatterns = [
   path('shop/', views.shop , name='shop'),
   # path('shop_category/<category_id>' , views.shop_category , name="shop_category"),
   path('product_detail/<slug:slug>', views.product_detail , name='product_detail'),
   path('index', views.index ,name='index'),
]