
from django.db import models
from productside.models import ProductVariant
from django.db.models.signals import post_save
from django.dispatch import receiver

    
    
class Slider(models.Model):
    DISCOUNT_DEALS = (
        ('HOT DEALS', 'HOT DEALS'),
        ('NEW ARRIVALS', 'NEW ARRIVALS'),
        ('SPECIAL OFFERS', 'SPECIAL OFFERS'),
    )
    Image=models.ImageField(upload_to='slider_images')
    Discount_deals=models.CharField(choices=DISCOUNT_DEALS,max_length=100,null=True)
    Product=models.ForeignKey(ProductVariant,on_delete=models.CASCADE,null=True)    
    
    
    def __str__(self):
        return self.Product.product.name



from django.contrib.auth.models import User
from django.db import models
import random
import string


class ReferralOffers(models.Model):
    referrer_amount=models.IntegerField()
    referral_discount=models.IntegerField()
    referral_description=models.CharField(max_length=100)
    
    def __str__(self):
        return self.referral_description
    
    
class ReferralCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    referral_code = models.CharField(max_length=20, unique=True)
    referrer = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='referrals')

    def __str__(self):
        return self.referral_code

    @staticmethod
    def generate_referral_code(user):
        # Get the user's initials
        user_name_initial = user.username[:1].upper()
        

        # Generate a random string of characters (you can modify the length as needed)
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

        # Combine the user's initials and the random string to create the referral code
        referral_code = f"{user_name_initial}-{random_string}"

        return referral_code
    
    
    from django.db.models.signals import post_save
    from django.dispatch import receiver
    
    @receiver(post_save, sender=User)
    def create_referral_code(sender, instance, created, **kwargs):
        if created:
            # Generate the referral code for the new user
            referral_code = ReferralCode.generate_referral_code(instance)

            # Create a new ReferralCode instance and associate it with the user
            ReferralCode.objects.create(user=instance, referral_code=referral_code)
            

class PersonalDetails(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    contact = models.CharField(max_length=15, null=True, blank=True)
    country = models.CharField(max_length=15, null=True, blank=True)
    state = models.CharField(max_length=15, null=True, blank=True)
    
    def __str__(self):
        return self.user.username
    
    @receiver(post_save, sender=User)
    def create_user_wishlist(sender, instance, created, **kwargs):
        if created:
            PersonalDetails.objects.create(user=instance)