# from django import forms
# from .models import Product, ProductVariant, ProductImage
# from django import forms
# from multiupload.fields import MultiFileField

# class ProductImageForm(forms.ModelForm):
#     images = MultiFileField(min_num=0, max_num=10, max_file_size=1024*1024*5)

#     class Meta:
#         model = ProductImage
#         fields = ['images']

        
# class ProductVariantForm(forms.ModelForm):
#     class Meta:
#         model = ProductVariant
#         fields = ('color', 'storage', 'price', 'stock', 'displayimage')
#         widgets = {
#             'displayimage': forms.ClearableFileInput(),
#         }

# class ProductForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = ['name', 'description', 'category']
