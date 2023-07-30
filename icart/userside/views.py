from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
from cartside.models import *
from django.db.models import Sum
from django.http import HttpResponseRedirect
from authentication.models import *
from django.core.paginator import Paginator

# Create your views here.

#checkout page 
def checkout(request):
    if request.user.is_authenticated:
        user=request.user
        
        addresses=Address.objects.filter(user=user)
        cart=UserCart.objects.get(user=user)
        products=Cart.objects.filter(cart_id=cart)
        productstotal = Cart.objects.filter(cart_id=cart).aggregate(total_price=Sum('price'))
        total_price = productstotal['total_price']
        #Rechecking the user doesnt deleted and reduced the cart amount less than coupon min. amount
        if cart.coupon:
            if cart.coupon.minimum_amount > total_price:
                return redirect('cart')
                
        if not products:
            return redirect('shop')
        for product in products:
            if product.quantity > product.product.stock:
                # The item has insufficient stock, redirect to cart page
                messages.error(request, f"Sorry!!.Insufficient stock for '{product.product.product.name}'. Please update your cart.")
                return redirect('cart')
        context={
            'addresses': addresses,
        }
        return render (request, 'checkout.html', context)
    else:
        messages.error(request, 'You want signin to make an order')
        return render(request,'authentication/signin.html')

#adding new address
def add_address(request):
    if request.user.is_authenticated:

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
    else:
        return redirect('signin')

#editing the existing address in the checkout page
def edit_address(request, address_id):
    if request.user.is_authenticated:
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
    else:
        return redirect('signin')


def payment_page(request, address_id):
    if request.user.is_authenticated:
       
        user=request.user
        cart_id=UserCart.objects.get(user=user)
        products=Cart.objects.filter(cart_id=cart_id)
        if not products:
                messages.error(request, "Please add something to cart")
                return redirect('home')
        address = Address.objects.get(id=address_id)
        
        refer_table=ReferralOffers.objects.all()
        wallet=Wallet.objects.get(user=user)
        productstotal = Cart.objects.filter(cart_id=cart_id).aggregate(total_price=Sum('price'))
        total_price = productstotal['total_price']
        discount_amount=0
        #If the user applied any coupon
        if cart_id.coupon:    
            discount_price= total_price - cart_id.coupon.discount_price
        else:
            discount_price = total_price
            
        referral_code_obj = ReferralCode.objects.get(user=user)
        old_orders=Order.objects.filter(user=user)
        if refer_table:
            if referral_code_obj.referrer and not old_orders:
                refer_discount=refer_table[0].referral_discount
                discount_amount = min(total_price * Decimal(refer_discount) / Decimal('100'), Decimal('100'))
                discount_price -= discount_amount
            
        
        context={
            'address': address ,
            'total_price' : total_price ,
            'discount_price' : discount_price ,
            'cart_id' : cart_id ,
            'wallet': wallet ,
            'discount_amount' : discount_amount
        }
        
        return render (request,'payment.html', context)
    else:
        return redirect('signin')

from django.http import JsonResponse
from django.template.loader import render_to_string


def place_order(request, address_id):
    if request.user.is_authenticated:

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
            refer_table=ReferralOffers.objects.all()
            referral_code_obj = ReferralCode.objects.get(user=user)
            old_orders=Order.objects.filter(user=user)
            if refer_table:
                if referral_code_obj.referrer and not old_orders:    
                    referrer = referral_code_obj.referrer  # Assuming 'referrer' is the field containing the referrer user
                    referrer_wallet = Wallet.objects.get(user=referrer)
                    referrer_money=refer_table[0].referrer_amount
                    if referrer_wallet.money==None:
                        referrer_wallet.money = referrer_money
                    else:
                        referrer_wallet.money += referrer_money
                    referrer_wallet.save()
    
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
        else:
            return redirect('signin')



from decimal import Decimal 
import razorpay
from django.conf import settings
# Create an instance of the Razorpay client using your API credentials

client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))


import razorpay
# import hashlib

def initiate_payment(request):
    if request.user.is_authenticated:

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
    else:
        return redirect('signin')

    
#order conftirmation page
def order_confirmation(request, order_id):
    if request.user.is_authenticated:

        order=Order.objects.get(id=order_id)
        context={
                'order' : order
            }
        return render (request,'order_confirmation.html' , context)
    else:
        return redirect('signin')
 
#list of the orders user has done
def my_orders(request):
    if request.user.is_authenticated:
        user=request.user
        orders=Order.objects.filter(user=user).order_by('-id')
        
        
        paginator = Paginator(orders, 8) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context={
        'orders': page_obj 
        }

        return render (request, 'my_orders.html' , context )
    else:
        return redirect('signin')

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
    if request.user.is_authenticated:
        order=Order.objects.get(id=order_id)
        
        context={
        'order': order 
        }
        return render(request, 'order_detail.html', context)
    else:
        return redirect('signin')
   
    
def address(request):
    if request.user.is_authenticated:

        user=request.user
        addresses=Address.objects.filter(user=user)
        context={
            'addresses' : addresses
        }
        return render (request, 'address.html', context)
    else:
        return redirect('signin')

from authentication.models import ReferralCode
#details of the user
def profile_details(request):
    if request.user.is_authenticated:
        user = request.user
        personal=PersonalDetails.objects.get(user=user)
        referral_code=ReferralCode.objects.get(user=user)
        if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
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
                return JsonResponse({'status': 'error', 'message': 'user not found'}, status=404)
            if not email   :
                messages.error(request , "Email Cant be blank")
                return JsonResponse({'status': 'error', 'message': 'Order not found'}, status=404)
            
            personal.contact=phone
            print(personal.contact)
            personal.country=country
            personal.state=state
            personal.save()
            
            
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            # user.phone = phone
            user.email = email
            user.save()
            success=True
            # Update additional profile fields if applicable
            # ...

            messages.success(request, 'Profile updated successfully.')
            return JsonResponse({'success' : success})  # Redirect to the profile page or a success page
    else:
        messages.error(request, "please login !!")
        return redirect('signin')

    context={
        'user' : user,
        'personal' : personal,
        'referral_code': referral_code
    }
    
    return render (request, 'profile.html', context)  

def profile_add_address(request):
    if request.user.is_authenticated:
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
    else:
        return redirect('signin')


from django.contrib.auth import authenticate, login

def change_password(request, user_id):
    if request.user.is_authenticated:
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
    else:
        return redirect('signin')



import razorpay

def initiate_refund(request):
    client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
    order_id = request.POST.get('order_id')
    print(order_id)
    order = Order.objects.get(id=order_id)
    payment_id = order.payment_id
    print(payment_id)
    amount = order.total_price
    amount = 100
    try:
        refund = client.payment.refund(payment_id, {
            'amount': amount * 100,
        })

        if refund.get('id'):
            # Refund successful
            refund_id = refund['id']
            success = True
            # Perform any additional actions or update your database as required
            data = {'refund_id': refund_id, 'success': success}
            return JsonResponse(data)
        else:
            # Refund failed
            error_message = refund.get('error_description', 'Refund failed.')
            return JsonResponse({'error': error_message}, status=400)

    except Exception as e:
            print(payment_id)
            # Handle any exceptions that occur during the refund process
            error_message = 'There is an issue with the server. Please try again later.'
            return JsonResponse({'error': str(e), 'error_message': error_message}, status=500)
    
def initiate_return(request):
    if request.user.is_authenticated:
        order_id = request.POST.get('order_id')
        order = Order.objects.get(id=order_id)
        order.payment_status = 'PENDING'
        order.save() 
        data={
            "payment_status" : order.payment_status
        }
        return JsonResponse(data)   
    else:
        return redirect('signin')

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
    if request.user.is_authenticated:
        user=request.user
        wallet=Wallet.objects.get(user=user)
        
        context={
            "wallet" : wallet 
        }
        
        return render(request, 'wallet.html' , context)
    else:
        return redirect('signin')

import random
from django.core.mail import send_mail , EmailMessage



def mail_to_emailchange(request):
            generated_otp=random.randint(100000,999999)
            user=request.user
            request.session['otp']=str(generated_otp)
            
            # sending OTP through mail
            subject = 'iCart Confirmation OTP'
            message = f'Hello {user.username},\nWe are happy to serve you\n \nPlease Verify your account by OTP: {generated_otp}'
            from_email=settings.EMAIL_HOST_USER
            to_list=[user.email]
            
            send_mail(subject,message,from_email,to_list,fail_silently=True)
            success = True
            return JsonResponse({'success': success})
 
def verify_otp_for_mail(request):
    if request.method=='POST':
        otp=request.POST['otp']
        generated_otp=request.session.get('otp')
        #checking the otp enterd is same as send to the email
        if otp==generated_otp:
          
            del request.session['otp']
            success=True
            
            return JsonResponse({'success': success})
  
  
def walletpay(request):
    if request.user.is_authenticated:
        total_price_str = request.POST['total_price']
        total_price = Decimal(total_price_str)
        print(total_price)
        user=request.user
        wallet=Wallet.objects.get(user=user)
        print(wallet.money)
        wallet.money -= total_price
        wallet.save()
        success=True
        data={
            "success" : success
        }
        return JsonResponse(data) 
    else:
        return redirect('signin')    

def wallet_refund(request):
    if request.user.is_authenticated:
        user=request.user
        order_id = request.POST.get('order_id')
        print(order_id)
        order = Order.objects.get(id=order_id)
        total_price=order.total_price            
        wallet=Wallet.objects.get(user=user)
        print(wallet.money)
        if wallet.money is None:
            wallet.money = total_price
        else:
            wallet.money += total_price
                
        wallet.save()
        success=True
        data={
            "success" : success
        }
        return JsonResponse(data)     
    else:
        return redirect('signin')



from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa

def download_invoice(request, order_id):
    order = Order.objects.get(id=order_id)
    items=Orderlist.objects.filter(order_id=order)
    # Get the HTML template for the invoice
    template = get_template('invoice_template.html')
    
    # Define the context for the template
    context = {
        'order': order,
        "items" : items,
        # Add any other context variables you need for the invoice template
    }
    
    # Render the template with the context
    rendered_template = template.render(context)
    
    # Create a PDF response
    pdf_response = HttpResponse(content_type='application/pdf')
    pdf_response['Content-Disposition'] = 'attachment; filename="Invoice.pdf"'

    # Generate the PDF from the HTML content
    pisa_status = pisa.CreatePDF(
        src=rendered_template,
        dest=pdf_response,
    )

    # Check if PDF generation was successful
    if pisa_status.err:
        return HttpResponse('PDF generation failed', status=500)

    return pdf_response
