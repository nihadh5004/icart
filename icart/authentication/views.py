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

# Create your views here.
from django.db.models import F

def home(request):
    
    sliders = Slider.objects.all()
    user = request.user
    name = user.username
    # Retrieve the 10 latest products based on the ID
    latest_products = Product.objects.filter(is_active=True).order_by('-id')[:10] 
    
    context = {
        'name': name,
        'sliders': sliders,
        'latest_products': latest_products,
    }
    
    return render(request, 'home.html', context)


def signin(request):
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
            
            #rendering to the page where we can enter otp , also sending the primary key 
            return render (request,'authentication/otp_verification.html',{'user_for_otp':user.pk})
        else: 
            messages.error(request, 'invalid credentials')
            return redirect('signin')
        
        
    return render(request, 'authentication/signin.html')

def verify_otp(request,user_for_otp):
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
    if request.method=='POST':
        username=request.POST['username']
        email=request.POST['email']
        pass1=request.POST['pass1']    
        pass2=request.POST['pass2']    
        
        myuser=User.objects.create_user(username,email,pass1)
        myuser.is_active=False
        myuser.save()
        
        messages.success(request,'Please Verify Account from Your Email')
        
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
       
        return redirect('signin')
    
    return render(request,'authentication/signup.html')
    
    
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
        messages.success(request,"Succesfully logged out")
        return redirect('signin')