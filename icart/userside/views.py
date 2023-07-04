from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
from django.http import HttpResponse
from cartside.models import *
from django.db.models import Sum

# Create your views here.
def checkout(request):
    user=request.user
    addresses=Address.objects.filter(user=user)
    cart=UserCart.objects.get(user=user)
    products=Cart.objects.filter(cart_id=cart)
    if not products:
        return redirect('shop')
    context={
        'addresses': addresses,
    }
    return render (request, 'checkout.html', context)


def add_address(request):
    if request.method == "POST":
        fullname=request.POST['fullname']
        address=request.POST['address']
        street=request.POST['street']
        city=request.POST['city']
        state=request.POST['state']
        pincode=request.POST['pincode']
        phone=request.POST['phone']
        
        user=request.user
        Address.objects.create(user=user, fullname=fullname, address=address, street=street, city=city , state=state, pincode=pincode, contact=phone)
        messages.success(request, 'Address adding succesfully')
        return redirect ('checkout')
    return render(request,'add_address.html')

def edit_address(request, address_id):
    address = Address.objects.get(id=address_id)

    if request.method == "POST":
        fullname = request.POST['fullname']
        address_text = request.POST['address']
        street = request.POST['street']
        city = request.POST['city']
        state = request.POST['state']
        pincode = request.POST['pincode']
        phone = request.POST['phone']
        
        address.fullname = fullname
        address.address = address_text
        address.street = street
        address.city = city
        address.state = state
        address.pincode = pincode
        address.contact = phone
        address.save()
        
        messages.success(request, 'Address edited successfully')
        return redirect('checkout')
    
    
    context={
        'address' : address,
    }
    return render(request, 'edit_address.html' , context )


def payment_page(request, address_id):
    address = Address.objects.get(id=address_id)
    user=request.user
    cart_id=UserCart.objects.get(user=user)
    
    products=Cart.objects.filter(cart_id=cart_id)
    productstotal = Cart.objects.filter(cart_id=cart_id).aggregate(total_price=Sum('price'))
    total_price = productstotal['total_price']
    
    context={
        'address': address ,
        'total_price' : total_price
    }
    
    return render (request,'payment.html', context)


def place_order(request, address_id):
    address=Address.objects.get(id=address_id)
    user=request.user
    cart_id=UserCart.objects.get(user=user)
    productstotal = Cart.objects.filter(cart_id=cart_id).aggregate(total_price=Sum('price'))
    total_price = productstotal['total_price']
    
    order=Order.objects.create(user=user ,address=address, total_price=total_price, payment_status= 'ORDERED' ,payment_method = 'Cash on Delivery' )
    
    cart_items=Cart.objects.filter(cart_id=cart_id)
    
    for product in cart_items:
        Orderlist.objects.create(order_id=order, 
                                 product=product.product, 
                                 quantity=product.quantity,
                                 price=product.price)
        product.delete()
        
    context={
        'order' : order
    }
    
    return render (request , 'order_confirmation.html', context)


def my_orders(request):
    user=request.user
    orders=Order.objects.filter(user=user).order_by('-id')
    
    context={
       'orders': orders 
    }

    return render (request, 'my_orders.html' , context )

        
def cancel_order(request, order_id):
    order=Order.objects.get(id=order_id)
    order.delete()
    
    return redirect('my_orders')
    
def address(request):
    user=request.user
    addresses=Address.objects.filter(user=user)
    context={
        'addresses' : addresses
    }
    return render (request, 'address.html', context)

def profile_details(request):
    user = request.user
    if request.method == 'POST':
        # Retrieve form data
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phone = request.POST['phone']
        email = request.POST['email']
        country = request.POST['country']
        state = request.POST['state']

        # Update user profile
        
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        # user.phone = phone
        user.email = email
        user.save()

        # Update additional profile fields if applicable
        # ...

        messages.success(request, 'Profile updated successfully.')
        return redirect('profile_details')  # Redirect to the profile page or a success page

    context={
        'user' : user
    }
    
    return render (request, 'profile.html', context)  

def profile_add_address(request):
    if request.method == "POST":
        fullname=request.POST['fullname']
        address=request.POST['address']
        street=request.POST['street']
        city=request.POST['city']
        state=request.POST['state']
        pincode=request.POST['pincode']
        phone=request.POST['phone']
        
        user=request.user
        Address.objects.create(user=user, fullname=fullname, address=address, street=street, city=city , state=state, pincode=pincode, contact=phone)
        messages.success(request, 'Address added succesfully')
        return redirect ('address')
    return render(request,'profile_add_address.html')