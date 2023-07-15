from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.http import HttpResponseRedirect
from decimal import Decimal
from django.db.models import Sum
from django.contrib import messages

# Create your views here.
def addcart(request, slug):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity'))
        productvariant = get_object_or_404(ProductVariant, slug=slug)
        user = request.user
        price = Decimal(productvariant.price)
        totalprice = price * Decimal(quantity)
        if productvariant.discount_price:
            totalprice = productvariant.discount_price * Decimal(quantity)
        
        cart = UserCart.objects.get(user=user)
        
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
    user=request.user
    cart_id=UserCart.objects.get(user=user)
    products=Cart.objects.filter(cart_id=cart_id)
    productstotal = Cart.objects.filter(cart_id=cart_id).aggregate(total_price=Sum('price'))
    total_price = productstotal['total_price']
    if not products:
        cart_id.coupon =None
        cart_id.save()
        messages.error(request, 'The cart is empty, Please add something to the cart')
        return redirect('shop')
    
    
    if request.method=='POST':
        coupon=request.POST['coupon']
        coupon_obj=Coupon.objects.filter(coupon_code=coupon)
        if not coupon_obj:
            messages.error(request, 'Invalid Coupon')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        if cart_id.coupon:
            messages.error(request , 'Coupon already exists')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        if total_price < coupon_obj[0].minimum_amount :
            messages.error(request, f'Amount should be greater than  {coupon_obj[0].minimum_amount}.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        
        cart_id.coupon=coupon_obj[0]
        cart_id.save()
        messages.success(request, 'Coupon applied succesfully')

    if cart_id.coupon:
        if cart_id.coupon.minimum_amount > total_price:
            messages.error(request, f'Amount should be greater than  {cart_id.coupon.minimum_amount}.')
            cart_id.coupon=None
            cart_id.save()
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


def delete_coupon(request, cart_id):    
    cart=UserCart.objects.get(id=cart_id)
    cart.coupon = None
    cart.save()
    messages.error(request , 'Coupon removed')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



import json
from django.http import JsonResponse
def update_quantity(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
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
            
            # Prepare the success response data
            response_data = {
                'success': True,
                'message': 'Quantity updated successfully!',
                'price': product.price,
                'quantity': product.quantity,
            }

        return JsonResponse(response_data)

    response_data = {
        'success': False,
        'message': 'Invalid request',
    }

    return JsonResponse(response_data, status=400)

def removecart(request,product_id):
    product=Cart.objects.get(id=product_id)
    product.delete()
    
    return redirect('cart')