from django.db import models
from django.contrib.auth.models import User
from productside.models import *
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    contact=models.CharField(max_length=15)
    def __str__(self):
        return f'{self.fullname}, {self.address}, {self.city}, {self.pincode}'


from django.db import models
from django.utils import timezone
from datetime import timedelta


class Order(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ORDERED', 'ordered'),
        ('SHIPPED', 'Shipped'),
        ('CANCELLED', 'Cancelled'),
        ('DELIVERED', 'Delivered'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('PREPAID', 'Prepaid'),
        ('COD', 'Cash on Delivery'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address=models.ForeignKey(Address, on_delete=models.CASCADE)
    order_date = models.DateTimeField(default=timezone.now)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='ordered')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_id = models.CharField(max_length=50, null=True,blank=True)
    delivery_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.id}  {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.order_date:
            self.order_date = timezone.now()  # Set the order date to the current time if it's not set
        if not self.delivery_date:
            self.delivery_date = self.order_date + timedelta(hours=24)
        super().save(*args, **kwargs)
        
        
class Orderlist(models.Model):
    order_id=models.ForeignKey(Order, on_delete=models.CASCADE)
    product= models.ForeignKey(ProductVariant, on_delete= models.CASCADE)
    quantity= models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.order_id}{self.product.product.name}'