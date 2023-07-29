#for authentication
from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login ,logout
from django.core.mail import send_mail , EmailMessage
from .models import *
# for sending mails importing host from settings
from icart import settings
#for encoding and decoding the primary key of user and rendering it to the verification mail page
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode 
from django.utils.encoding import force_bytes , force_str
# importing the token geneater which creates a unique hash value for user
from .token import generate_token
#for storing current time and user creation time
from datetime import timedelta
from django.utils import timezone
#for creating random values fo otp
import random
from .models import Slider
from productside.models import *
from django.views.decorators.cache import cache_control
from django.http import HttpResponseRedirect
from cartside.models import *
# Create your views here.
from django.db.models import F

def home(request):
  
   
    sliders = Slider.objects.all()
    # Retrieve the 10 latest products based on the ID
    latest_products = Product.objects.filter(is_active=True).order_by('-id')[:10] 
    print(sliders)
    context = {
        
        'sliders': sliders,
        'latest_products': latest_products,
    }
    
    return render(request, 'home.html', context)

def signin(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method=='POST':
        username=request.POST['username']
        pass1=request.POST['pass1']
        
        user=authenticate(username=username, password=pass1)
        
        if user is not None:
            generated_otp=random.randint(100000,999999)
            request.session['otp']=str(generated_otp)
            
            # sending OTP through mail
            subject = 'iCart Confirmation OTP'
            message = f'Hello {user.username},\nWe are happy to serve you\n \nPlease Verify your account by OTP: {generated_otp}'
            from_email=settings.EMAIL_HOST_USER
            to_list=[user.email]
            
            send_mail(subject,message,from_email,to_list,fail_silently=True)
        
            
            # login(request, user)
            # return redirect('home')
            messages.success(request, 'OTP has been succesfully sent to your mail')
            #rendering to the page where we can enter otp , also sending the primary key 
            return render (request,'authentication/otp_verification.html',{'user_for_otp':user.pk})
        else: 
            messages.error(request, 'invalid credentials')
            return redirect('signin')
        
        
    return render(request, 'authentication/signin.html')

def verify_otp(request,user_for_otp):
    if request.user.is_authenticated:
        return redirect ('home')
    if request.method=='POST':
        otp=request.POST['otp']
        generated_otp=request.session.get('otp')
        #checking the otp enterd is same as send to the email
        if otp==generated_otp:
            myuser=User.objects.get(pk=user_for_otp)
            login(request,myuser)
            del request.session['otp']
            return redirect('home')
        else:
            messages.error(request,'invalid otp')
            return redirect('signin')

def signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method=='POST':
        username=request.POST['username']
        email=request.POST['email']
        pass1=request.POST['pass1']    
        pass2=request.POST['pass2']    
        referral=request.POST['referral']  
        # if User.objects.filter(email=email).exists():
        #     messages.error(request, 'Email already exists. Please use a different email.')
        #     return render(request, 'authentication/signup.html')  
        if referral:
            try:
                referral_code_obj = ReferralCode.objects.get(referral_code=referral)
                referrer = referral_code_obj.user
            except ReferralCode.DoesNotExist:
                messages.error(request, 'Invalid referral code')
                return redirect('signup')

        myuser=User.objects.create_user(username,email,pass1)
        myuser.is_active=False
        myuser.save()
        if referral:
            referral_user=ReferralCode.objects.get(user=myuser)
            referral_user.referrer=referrer
            referral_user.save()
        messages.success(request,'We have sent a link to your mail,Please Verify Account from Your Email')
        
        #email
        # subject='Welcome to icart'
        # message='Hello' + myuser.username +'!!'
        # from_email=settings.EMAIL_HOST_USER
        # to_list=[myuser.email]
        # send_mail(subject,message,from_email,to_list,fail_silently=True)
        
        #email confirmation for the user
        current_site = get_current_site(request)
        email_subject = 'confirm Your email @ iCart'
        message2 = render_to_string('authentication/emailconfirmation.html',{
            'name': myuser.username ,
            'domain': current_site.domain ,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser),
        })
        email = EmailMessage(
            email_subject,message2,
            settings.EMAIL_HOST_USER,
            [myuser.email] 
        )
        email.fail_silently = True
        email.send()
       
        return redirect('email_send')
    
    return render(request,'authentication/signup.html')

def email_send(request):
    return render(request, 'authentication/email_send.html')
    

def activate(request,uidb64,token):
    try:
        uid=force_str(urlsafe_base64_decode(uidb64))
        myuser=User.objects.get(pk=uid)
    except(TypeError,ValueError,OverflowError, User.DoesNotExist):
        myuser=None
    # checking the user and token doesnt has a conflict  
    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active=True
        myuser.save()
        login(request,myuser)
        return redirect('home')
    else:
        # Delete the user if activation fails and the activation link is expired
        user_creation_time = myuser.date_joined
        # Define the expiration time (24 hours after user creation)
        expiration_time = user_creation_time + timedelta(hours=24)  

        if myuser is not None and myuser.is_active == False and timezone.now() > expiration_time:
            myuser.delete()

        return render(request, 'authentication/verification_failed.html')


def signout(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('home')
    
    
from twilio.rest import Client
from django.conf import settings
from django.http import HttpResponse
def send_otp(phone_number):
    # Generate the OTP
    otp = '645736'  # Implement your OTP generation logic here

    # Create a Twilio client
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    # Send the SMS with the OTP
    message = client.messages.create(
        body=f"Your OTP is: {otp}",
        from_=settings.TWILIO_PHONE_NUMBER,
        to='+919539782052'
    )
    return HttpResponse('OTP sent succesfully')






def reset_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        
        try:
            user = User.objects.get(email=email)
            # User with the entered email exists
            # Proceed with sending the email confirmation

            current_site = get_current_site(request)
            r_subject = 'Reset Password @ iCart'
            message3 = render_to_string('authentication/r_content.html', {
                'name': user.username,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': generate_token.make_token(user),
            })
            email = EmailMessage(
                r_subject, message3,
                settings.EMAIL_HOST_USER,
                [user.email]
            )
            email.fail_silently = True
            email.send()

            messages.success(request, 'The link to reset password has sent to your mail')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        except User.DoesNotExist:
            # User with the entered email does not exist
            messages.error(request, 'User does not exist')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'authentication/reset_password.html')

def res_pass(request,uidb64,token):
    try:
        uid=force_str(urlsafe_base64_decode(uidb64))
        myuser=User.objects.get(pk=uid)
    except(TypeError,ValueError,OverflowError, User.DoesNotExist):
        myuser=None
    # checking the user and token doesnt has a conflict  
    if myuser is not None and generate_token.check_token(myuser,token):
        return render(request,'authentication/new_password.html' ,{'user': myuser})
   
def update_password(request, user_id):
    if request.method =='POST':
        pass1=request.POST['pass1']
        pass2=request.POST['pass2']
        if pass1 == pass2 :
            user=User.objects.get(id=user_id)
            user.set_password(pass1)
            user.save()
        
            messages.success(request, 'Password Updated Succesfully')
            return redirect('signin')
        else:
            messages.error(request,'Passwords didnt match, Please enter both passwords Correctly')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
  
  
def guest_signin(request):
    
    if request.method=='POST':
        username=request.POST['username']
        pass1=request.POST['pass1']
        
        user=authenticate(username=username, password=pass1)
        
        if user is not None:
            generated_otp=random.randint(100000,999999)
            request.session['otp']=str(generated_otp)
            
            # sending OTP through mail
            subject = 'iCart Confirmation OTP'
            message = f'Hello {user.username},\nWe are happy to serve you\n \nPlease Verify your account by OTP: {generated_otp}'
            from_email=settings.EMAIL_HOST_USER
            to_list=[user.email]
            
            send_mail(subject,message,from_email,to_list,fail_silently=True)
        
            
            # login(request, user)
            # return redirect('home')
            messages.success(request, 'OTP has been succesfully sent to your mail')
            #rendering to the page where we can enter otp , also sending the primary key 
            return render (request,'authentication/guest_otp_verification.html',{'user_for_otp':user.pk})
        else: 
            messages.error(request, 'invalid credentials')
            return redirect('guest_signin')
        
        
    return render(request, 'authentication/signin.html')


def guest_verify_otp(request,user_for_otp):
    
    if request.method=='POST':
        otp=request.POST['otp']
        generated_otp=request.session.get('otp')
        cart=request.session.get('cart_id')
        guest_cart_id=UserCart.objects.get(id=cart)
        wishlist=request.session.get('wishlist_id')
        try:
            guest_wishlist_id=UserWishlist.objects.get(id=wishlist)
        except:
            guest_wishlist_id=None
        #checking the otp entered is same as send to the email
        if otp==generated_otp:
            myuser=User.objects.get(pk=user_for_otp)
            login(request,myuser)
            user_cart=UserCart.objects.get(user=myuser)
            cart_items=Cart.objects.filter(cart_id=guest_cart_id)
            for product in cart_items:
                cart_item = Cart.objects.filter(cart_id=user_cart, product=product.product).first()
                if cart_item:
                    # Product already exists in the cart, increase the quantity
                    cart_item.quantity += product.quantity
                    cart_item.price += product.price
                    cart_item.save()
                else:
                    Cart.objects.create(
                        cart_id=user_cart,
                        product=product.product,
                        quantity=product.quantity,
                        price=product.price
                    )
            del request.session['otp']
            guest_cart_id.delete()
            del request.session['cart_id']
            if guest_wishlist_id != None:
                guest_wishlist_id.delete()
                del request.session['wishlist_id']
            return redirect('cart')
        else:
            messages.error(request,'invalid otp')
            return redirect('signin')
         