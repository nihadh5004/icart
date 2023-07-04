from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Product)
admin.site.register(Categories)
admin.site.register(Color)
admin.site.register(Storage)
admin.site.register(ProductVariant)
admin.site.register(ProductImage)