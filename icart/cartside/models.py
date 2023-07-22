from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from productside.models import *

class UserCart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True)
    coupon=models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return f'{self.id}'

@receiver(post_save, sender=User)
def create_user_cart(sender, instance, created, **kwargs):
    if created:
        UserCart.objects.create(user=instance)


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    money=models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    
    def __str__(self):
        return f'{self.id} - {self.user.username}'

@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)





class UserWishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    def __str__(self):
        return f'{self.id} - {self.user.username}'

@receiver(post_save, sender=User)
def create_user_wishlist(sender, instance, created, **kwargs):
    if created:
        UserWishlist.objects.create(user=instance)
        

class Wishlist(models.Model):
    wishlist_id = models.ForeignKey(UserWishlist, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)      

    def __str__(self):
        return f'{self.id} - {self.wishlist_id} - {self.product}'
       
class Cart(models.Model):
    cart_id = models.ForeignKey(UserCart, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.id} - {self.cart_id} - {self.product}'

    def total_price(self):
        return self.quantity * self.price