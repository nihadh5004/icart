from django.db import models
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse

# Create your models here.
class Categories(models.Model):
    category_name=models.CharField(max_length=100)
    
    def __str__(self):
        return self.category_name
    
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category=models.ForeignKey(Categories, on_delete=models.CASCADE)
    slug = models.SlugField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})
    
    

    
    
class Storage(models.Model):
    storage = models.IntegerField()
    
    def __str__(self):
        return str(self.storage)

class Color(models.Model):
    color = models.CharField(max_length=10)
    
    def __str__(self):
        return self.color
    
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True,blank=True)
    discount = models.IntegerField( null=True,blank=True)
    stock = models.PositiveIntegerField(default=0)
    displayimage= models.ImageField(upload_to='product_images')
    slug = models.SlugField(blank=True, unique=True)
     
    def save(self, *args, **kwargs):
        if not self.slug:
            slug_str = f"{self.product.name} {self.color} {self.storage}"
            self.slug = slugify(slug_str)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.product.name} - {self.color} - {self.storage}'
    
class ProductImage(models.Model):
    product=models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    image=models.ImageField(upload_to="product_images/images")
    
    def __str__(self):
        return self.product.product.name
    

class Coupon(models.Model):
    coupon_code=models.CharField(max_length=10)
    is_expired=models.BooleanField(default=False)
    discount_price=models.IntegerField(default=50)
    minimum_amount=models.IntegerField(default=500)
    
    def __str__(self):
        return self.coupon_code