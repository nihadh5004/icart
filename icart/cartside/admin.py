from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(UserCart)
admin.site.register(Cart)
admin.site.register(Wallet)
admin.site.register(UserWishlist)
admin.site.register(Wishlist)