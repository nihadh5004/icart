from django.shortcuts import render
from django.core.paginator import Paginator
from .models import *
from django.shortcuts import get_object_or_404
from cartside.models import *

# Create your views here.
def shop(request):
   
        
    category_id = request.GET.get('category')  # Get the selected category ID from the query parameters
    max_price = request.GET.get('max_price')

    products = Product.objects.filter(is_active=True)
    if category_id:
        products = products.filter(category_id=category_id)  # Filter products by the selected category ID
    for product in products:
        if max_price:
            selected_variant = product.productvariant_set.filter(price__lte=max_price).first()
        else:
            selected_variant = product.productvariant_set.all().order_by('?').first()
        product.selected_variant = selected_variant


    categories = Categories.objects.all()
    
    # Pagination
    # Show 4 products per page
    paginator = Paginator(products, 4) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    

    context = {
        'products': products,
        'categories': categories,
        'category_id' : category_id,
        'products': page_obj,
        'max_price': max_price,
    }
    
    return render(request, 'shop.html', context)


def product_detail(request, slug):
    product = Product.objects.get(slug=slug)
    color = request.GET.get('color')  # Get the color value from the URL query parameters
    color_id=Color.objects.get(color=color)
    storage = request.GET.get('storage')  # Get the storage value from the URL query parameters
    storage_id=Storage.objects.get(storage=storage)
    productvariant = get_object_or_404(ProductVariant, product=product, color=color_id.id, storage=storage_id.id)
    
    
    storages=ProductVariant.objects.filter(product=product).values_list('storage__storage',flat=True).distinct()
    colors=ProductVariant.objects.filter(product=product).values_list('color__color',flat=True).distinct()
    related_products = Product.objects.filter(category=product.category).exclude(slug=product.slug)[:3]
    
     # Check if the product is in the wishlist
    if request.user.is_authenticated:
        wishlist_items = UserWishlist.objects.get(user=request.user)  # Assuming you have a related name 'wishlist_items' for the wishlist relationship in the UserProfile model
        is_in_wishlist = Wishlist.objects.filter(wishlist_id=wishlist_items, product=productvariant).exists()
    else:
        is_in_wishlist=None
    context={
        'product': product, 
        'related_products': related_products ,
        # 'producttable': producttable ,
        'storages': storages ,
        'colors':colors ,
        'productvariant' : productvariant ,
        'is_in_wishlist' : is_in_wishlist ,
        }
    return render(request, 'product-details.html', context )

def index(request):
    return render (request, 'index.html')