
from django.db import models



    
    
class Slider(models.Model):
    DISCOUNT_DEALS = (
        ('HOT DEALS', 'HOT DEALS'),
        ('NEW ARRIVALS', 'NEW ARRIVALS'),
    )
    Image=models.ImageField(upload_to='media/slider_imgs')
    Discount_deals=models.CharField(choices=DISCOUNT_DEALS,max_length=100)
    Sale=models.IntegerField()
    Product_name=models.CharField(max_length=200)
    Discount=models.IntegerField()
    Links=models.CharField(max_length=200)
    
    
    def __str__(self):
        return self.Product_name
