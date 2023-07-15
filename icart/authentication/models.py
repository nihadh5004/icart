
from django.db import models
from productside.models import ProductVariant


    
    
class Slider(models.Model):
    DISCOUNT_DEALS = (
        ('HOT DEALS', 'HOT DEALS'),
        ('NEW ARRIVALS', 'NEW ARRIVALS'),
        ('SPECIAL OFFERS', 'SPECIAL OFFERS'),
    )
    Image=models.ImageField(upload_to='media/slider_imgs')
    Discount_deals=models.CharField(choices=DISCOUNT_DEALS,max_length=100,null=True)
    Product=models.ForeignKey(ProductVariant,on_delete=models.CASCADE,null=True)    
    
    
    def __str__(self):
        return self.Product.product.name

