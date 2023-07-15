from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
from cartside.models import *
from django.db.models import Sum
from django.http import HttpResponseRedirect
# Create your views here.

#checkout page 
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

#adding new address
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


#editing the existing address in the checkout page
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

#payment page
def payment_page(request, address_id):
    address = Address.objects.get(id=address_id)
    user=request.user
    cart_id=UserCart.objects.get(user=user)
    
    products=Cart.objects.filter(cart_id=cart_id)
    productstotal = Cart.objects.filter(cart_id=cart_id).aggregate(total_price=Sum('price'))
    total_price = productstotal['total_price']
    
    #If the user applied any coupon
    if cart_id.coupon:    
        discount_price= total_price - cart_id.coupon.discount_price
    else:
        discount_price = total_price
    context={
        'address': address ,
        'total_price' : total_price ,
        'discount_price' : discount_price ,
        'cart_id' : cart_id ,
    }
    
    return render (request,'payment.html', context)

from django.http import JsonResponse
from django.template.loader import render_to_string


def place_order(request, address_id):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':

        address=Address.objects.get(id=address_id)
        paymentMethod=request.POST.get('paymentMethod')
        payment_id = request.POST.get('payment_id')
        total_price=request.POST.get('total_price')
        user=request.user
        cart_id=UserCart.objects.get(user=user)
        # productstotal = Cart.objects.filter(cart_id=cart_id).aggregate(total_price=Sum('price')) 
        # total_price = productstotal['total_price']
        # if cart_id.coupon:
        #     total_price = productstotal['total_price'] - cart_id.coupon.discount_price
            
        
        order=Order.objects.create(user=user ,address=address, total_price=total_price, payment_status= 'ORDERED' ,payment_method = paymentMethod ,payment_id= payment_id  )
        
        cart_items=Cart.objects.filter(cart_id=cart_id)
        
        for product in cart_items:
            Orderlist.objects.create(order_id=order, 
                                    product=product.product, 
                                    quantity=product.quantity,
                                    price=product.price)
            product_variant = product.product
            product_variant.stock -= product.quantity
            product_variant.save()
            product.delete()
        
        
        cart_id.coupon =None
        cart_id.save()
        
        context={
            'order' : order
        }
        
        
        rendered_html = render_to_string('order_confirmation.html', context)
        
        # Return a JSON response with the order details and the rendered HTML string
        return JsonResponse({'order_id': order.id, 'order_total': order.total_price, 'rendered_html': rendered_html})
        # return render (request , 'order_confirmation.html', context)
    



from decimal import Decimal 
import razorpay
from django.conf import settings
# Create an instance of the Razorpay client using your API credentials

client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))


import razorpay
# import hashlib

def initiate_payment(request):
    # ... Your code to handle the payment initiation ...
    amount = request.POST.get('total_price')
    amount = int(float(amount))

    # Create a new Razorpay order
    order_amount = amount * 100  # Amount in paise (e.g., 50000 paise = ₹500)
    order_currency = 'INR'
    order_receipt = 'order_receipt'  # Unique order receipt identifier
    notes = {'shipping_address': '123, Shipping Street'}

    client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

    razorpay_order = client.order.create(
        {'amount': order_amount, 'currency': order_currency, 'receipt': order_receipt, 'notes': notes}
    )
    
    # Retrieve the Razorpay order ID from the response
    razorpay_order_id = razorpay_order['id']
   
   
#    # Manually generate the Razorpay signature for the order
#     signature = f"{razorpay_order_id}"  # Concatenation of order ID and payment ID
#     secret_key = settings.RAZORPAY_API_SECRET 
#     generated_signature = hashlib.sha256(f"{signature}".encode()).hexdigest()
#     # Prepare the response with the Razorpay order ID and signature
   
    response_data = {
        'razorpay_order_id': razorpay_order_id,
        'amount' : order_amount ,
        'currency' : order_currency ,
        
        # 'razorpay_signature': generated_signature
    }

    # Return the response as JSON
    return JsonResponse(response_data)

    
#order conftirmation page
def order_confirmation(request, order_id):
    order=Order.objects.get(id=order_id)
    context={
            'order' : order
        }
    return render (request,'order_confirmation.html' , context)
 
#list of the orders user has done
def my_orders(request):
    user=request.user
    orders=Order.objects.filter(user=user).order_by('-id')
    
    context={
       'orders': orders 
    }

    return render (request, 'my_orders.html' , context )

#cancelling the order        

def cancel_order(request):
    try:
        order_id = request.POST.get('order_id')
        order = Order.objects.get(id=order_id)
        order.payment_status = 'CANCELLED'
        order.save()

        ordered_items = Orderlist.objects.filter(order_id=order)
        for product in ordered_items:
            product_variant = product.product
            product_variant.stock += product.quantity
            product_variant.save()

        return JsonResponse({'status': 'success'})
    except Order.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Order not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

#deatils of the order and list of items in the order
def user_order_detail(request, order_id):
    order=Order.objects.get(id=order_id)
    
    context={
       'order': order 
    }
    return render(request, 'order_detail.html', context)
   
    
def address(request):
    user=request.user
    addresses=Address.objects.filter(user=user)
    context={
        'addresses' : addresses
    }
    return render (request, 'address.html', context)


#details of the user
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
        if not username   :
            messages.error(request , "Username Cant be blank")
            return redirect('profile_details')
        if not email   :
            messages.error(request , "Email Cant be blank")
            return redirect('profile_details')
        if email !=user.email:
            messages.success(request,'OTP Send to your mail')
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


from django.contrib.auth import authenticate, login

def change_password(request, user_id):
    user = User.objects.get(id=user_id)
    
    if request.method == 'POST':
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        
        if pass1 == pass2:
            user.set_password(pass1)
            user.save()
            
            # Reauthenticate the user with updated credentials
            updated_user = authenticate(request, username=user.username, password=pass1)
            if updated_user is not None:
                login(request, updated_user)
            
            return redirect('profile_details')
        else:
            messages.error(request, 'Passwords do not match')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    return render(request, 'change_password.html', {'user': user})



import razorpay

def initiate_refund(request):
    client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
    order_id = request.POST.get('order_id')
    order=Order.objects.get(id=order_id)
    payment_id = order.payment_id
    amount = order.total_price
    amount = int(float(amount))
    try:
        refund = client.payment.refund(payment_id, {
            'amount': amount * 100,  
            "speed": "optimum",
        })

        if refund.get('id'):
            # Refund successful
            refund_id = refund['id']
            # Perform any additional actions or update your database as required
            return JsonResponse({'refund_id': refund_id})
        else:
            # Refund failed
            error_message = refund.get('error_description', 'Refund failed.')
            return JsonResponse({'error': error_message}, status=400)

    except Exception as e:
        # Handle any exceptions that occur during the refund process
        return JsonResponse({'error': str(e)}, status=500)
    
    
def return_order(request):
    try:
        order_id = request.POST.get('order_id')
        order = Order.objects.get(id=order_id)
        order.payment_status = 'RETURNED'
        order.save()

        ordered_items = Orderlist.objects.filter(order_id=order)
        for product in ordered_items:
            product_variant = product.product
            product_variant.stock += product.quantity
            product_variant.save()
            
        user=order.user
        user=User.objects.get(id=user.id)
        print(user.username)
        wallet=Wallet.objects.get(user=user)
        print(wallet.user.username)
        print(wallet.money)
        if wallet.money==None:
            wallet.money= order.total_price
        else:
            wallet.money = wallet.money + order.total_price
        print(wallet.money)

        wallet.save()
        
        return JsonResponse({'status': 'success'})
    except Order.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Order not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    
    
def wallet(request):
    user=request.user
    wallet=Wallet.objects.get(user=user)
    
    context={
        "wallet" : wallet 
    }
    
    return render(request, 'wallet.html' , context)