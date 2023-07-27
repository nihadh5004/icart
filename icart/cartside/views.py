
from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.http import HttpResponseRedirect
from decimal import Decimal
from django.db.models import Sum
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder  # Import DjangoJSONEncoder
from django.views.decorators.cache import cache_control
from django.core.paginator import Paginator

# Create your views here.
def addcart_wishlist(request,slug):
    if request.user.is_authenticated:
            user=request.user
            cart = UserCart.objects.get(user=user)
            quantity = 1
            productvariant = get_object_or_404(ProductVariant, slug=slug)
            user = request.user
            price = Decimal(productvariant.price)
            totalprice = price * Decimal(quantity)
            #if the product has discount price then applying it
            if productvariant.discount_price:
                totalprice = productvariant.discount_price * Decimal(quantity)
            
            
            if quantity > productvariant.stock:
                # Display an error message if the quantity is greater than the stock
                messages.error(request, 'Requested quantity is greater than available stock.')
            else:
                # Check if the product is already in the cart
                cart_item = Cart.objects.filter(cart_id=cart, product=productvariant).first()
                if cart_item:
                    # Product already exists in the cart, increase the quantity
                    cart_item.quantity += quantity
                    cart_item.price += totalprice
                    cart_item.save()
                else:
                    # Product does not exist in the cart, create a new cart item
                    Cart.objects.create(cart_id=cart, product=productvariant, quantity=quantity, price=totalprice)
                messages.success(request, 'Item Added to Cart')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('signin')

            
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def addcart(request, slug):
    #if user is logged in 
        if request.user.is_authenticated:
            user=request.user
            cart = UserCart.objects.get(user=user)
            # if user is not logged in 
        else:
            cart_id=request.session.get('cart_id')
            if not cart_id:
                cart=UserCart.objects.create()
                request.session['cart_id']=cart.id
            else :
                cart=UserCart.objects.get(id=cart_id)
        #Taking the quantity as value and passing it to database   
        if request.method == 'POST':
            quantity = int(request.POST.get('quantity'))
            productvariant = get_object_or_404(ProductVariant, slug=slug)
            user = request.user
            price = Decimal(productvariant.price)
            totalprice = price * Decimal(quantity)
            #if the product has discount price then applying it
            if productvariant.discount_price:
                totalprice = productvariant.discount_price * Decimal(quantity)
            
            
            if quantity > productvariant.stock:
                # Display an error message if the quantity is greater than the stock
                messages.error(request, 'Requested quantity is greater than available stock.')
            else:
                # Check if the product is already in the cart
                cart_item = Cart.objects.filter(cart_id=cart, product=productvariant).first()
                if cart_item:
                    # Product already exists in the cart, increase the quantity
                    cart_item.quantity += quantity
                    cart_item.price += totalprice
                    cart_item.save()
                else:
                    # Product does not exist in the cart, create a new cart item
                    Cart.objects.create(cart_id=cart, product=productvariant, quantity=quantity, price=totalprice)
                messages.success(request, 'Item Added to Cart')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    
def cart(request):  
    #Checking if the user is logged in 
        if request.user.is_authenticated:
            user=request.user
            cart_id=UserCart.objects.get(user=user)
    #if user is not logged in 
        else:
            cart=request.session.get('cart_id')
            if not cart:
                cart=UserCart.objects.create()
                cart=cart.id
                print(cart)
                request.session['cart_id']=cart
            cart_id=UserCart.objects.get(id=cart)
            
        products=Cart.objects.filter(cart_id=cart_id).order_by('-id')
        productstotal = Cart.objects.filter(cart_id=cart_id).aggregate(total_price=Sum('price'))
        total_price = productstotal['total_price']
        #if cart doesnt have any product then redirect to shop
        if not products:
            cart_id.coupon =None
            cart_id.save()
            messages.error(request, 'The cart is empty, Please add something to the cart')
            return redirect('shop')
        
        #The coupon functionality
        if request.method=='POST':
            coupon=request.POST['coupon']
            coupon_obj=Coupon.objects.filter(coupon_code=coupon)
            #if the coupon is invalid
            if not coupon_obj or coupon_obj[0].is_expired:
                messages.error(request, 'Invalid Coupon')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            # if user already entered a coupon 
            if cart_id.coupon:
                messages.error(request , 'Coupon already exists')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            #If the cart amount is less than coupon min. amount
            if total_price < coupon_obj[0].minimum_amount :
                messages.error(request, f'Amount should be greater than  {coupon_obj[0].minimum_amount}.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            
            
            cart_id.coupon=coupon_obj[0]
            cart_id.save()
            messages.success(request, 'Coupon applied succesfully')
        #Rechecking the user doesnt deleted and reduced the cart amount less than coupon min. amount
        if cart_id.coupon:
            if cart_id.coupon.minimum_amount > total_price:
                messages.error(request, f'Amount should be greater than  {cart_id.coupon.minimum_amount}.Coupon has been removed')
                cart_id.coupon=None
                cart_id.save()
        #if cart has a coupon then changing the price according to coupon 
        if cart_id.coupon:    
            discount_price= total_price - cart_id.coupon.discount_price
        else:
            discount_price = total_price
        context={
            'cart_id' : cart_id ,
            'products': products,
            'total_price': total_price ,
            'discount_price' : discount_price
            
        }
        
        return render (request, 'cart.html', context)
    
from django.utils.crypto import get_random_string

def getcart(request):
    if request.user.is_authenticated:
        # User is logged in, redirect to the cart view
        return redirect('cart')

#using to remove coupon
def delete_coupon(request, cart_id):  
      
    cart=UserCart.objects.get(id=cart_id)
    cart.coupon = None
    cart.save()
    messages.error(request , 'Coupon removed')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



import json
from django.http import JsonResponse
# Function to update quantity from cart when pressing add or minus
def update_quantity(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.user.is_authenticated:
            user=request.user
            cart_id=UserCart.objects.get(user=user)
        else:
            id=request.session.get('cart_id')
            cart_id=UserCart.objects.get(id=id)
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity'))  # Convert the quantity to an integer
        product = Cart.objects.get(id=product_id)

        if quantity > product.product.stock:
            # Display an error message if the quantity is greater than the stock
            response_data = {
                'success': False,
                'message': 'Requested quantity is greater than available stock.',
            }
        else:
            product.quantity = quantity
            product.price = product.product.price * Decimal(product.quantity)
            if product.product.discount_price:
                product.price = product.product.discount_price * Decimal(product.quantity)
            product.save()
            
            productstotal = Cart.objects.filter(cart_id=cart_id).aggregate(total_price=Sum('price'))
            total_price = productstotal['total_price']
            if cart_id.coupon:    
                discount_price= total_price - cart_id.coupon.discount_price
            else:
                discount_price = total_price
            # Prepare the success response data
            response_data = {
                'success': True,
                'message': 'Quantity updated successfully!',
                'price':f"${product.price}",
                'quantity': product.quantity,
                'total_price' : f"${total_price}" ,
                'discount_price' : f"${discount_price}",
            }

        return JsonResponse(response_data)

    response_data = {
        'success': False,
        'message': 'Invalid request',
    }

    return JsonResponse(response_data, status=400)


#function to remove item from the cart
def removecart(request,product_id):
    product=Cart.objects.get(id=product_id)
    product.delete()
    
    return redirect('cart')


from django.http import JsonResponse

#function to add item to wishlist
def addwishlist(request):
    user=request.user
    slug=request.POST['slug']
    product=ProductVariant.objects.get(slug=slug)
    
    wishlist=UserWishlist.objects.get(user=user)
    
    if not Wishlist.objects.filter(wishlist_id=wishlist, product=product).exists():
    
        Wishlist.objects.create(wishlist_id=wishlist, product=product)
    success = True    
    
    return JsonResponse({success : 'success'})


#function to remove item from wishlist
def removewishlist(request):
    user=request.user
    slug=request.POST['slug']
    product=ProductVariant.objects.get(slug=slug)
    
    wishlist=UserWishlist.objects.get(user=user)
    
    if  Wishlist.objects.filter(wishlist_id=wishlist, product=product).exists():
        item=Wishlist.objects.get(wishlist_id=wishlist, product=product)
        item.delete()
    success = True    
    
    return JsonResponse({success : 'success'})
    
#function to render wishlist page   
def wishlist(request):
    user =request.user
    wishlist=UserWishlist.objects.get(user=user)
    items=Wishlist.objects.filter(wishlist_id=wishlist)
    
    paginator = Paginator(items, 4) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context={
        'items': page_obj
    }
    
    return render (request, 'wishlist.html', context)