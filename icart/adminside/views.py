from django.shortcuts import render, redirect,get_object_or_404 , HttpResponse
from django.contrib.auth import authenticate, login ,logout
from django.contrib import messages
from django.contrib.auth.models import User
from userside.models import *
from django.db.models import Count
from django.views.decorators.cache import cache_control
from datetime import date
from django.db.models import Sum, Count
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator


# Create your views here.

from django.template.loader import get_template
from xhtml2pdf import pisa
import io
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
import os
import json
from django.template import RequestContext
from xhtml2pdf import pisa
from authentication.models import *

import json
from django.core.serializers import serialize
from django.db.models.query import QuerySet
from django.http import JsonResponse
import decimal


#function to download sales report
def download_template(request):
    if request.user.is_authenticated and request.user.is_superuser: 
        # Replace 'download_template.html' with the path to your HTML template file
        template_name = 'admin/download_template.html'

        # Get the JSON data from the request parameters
        json_data = request.GET.get('json_data', '{}')
        context_data = json.loads(json_data)

        # Render the HTML template with the parsed context data
        rendered_template = render_to_string(template_name, {'context_data': context_data})

        # Create a PDF response
        pdf_response = HttpResponse(content_type='application/pdf')
        pdf_response['Content-Disposition'] = 'attachment; filename="ICART_SALES_REPORT.pdf"'

        # Generate the PDF from the HTML content
        pisa_status = pisa.CreatePDF(
            src=rendered_template,
            dest=pdf_response,
        )

        # Check if PDF generation was successful
        if pisa_status.err:
            return HttpResponse('PDF generation failed', status=500)

        return pdf_response
    else:
        return redirect('_admin_signin')



# Encoding the context of dashboard to json file and dumbing it to print salesreport.pdf
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, QuerySet):
            return serialize('json', obj)
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj, Categories):  # Replace 'Categories' with the actual model name
            return obj.category_name  # Replace 'category_name' with the actual attribute name in your model
        else:
            return super().default(obj)



#  dashboard function of the admin 
def _admin_dashboard(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            start_date = request.GET.get('start_date')  # Get the start date from the query parameters
            end_date = request.GET.get('end_date')  # Get the end date from the query parameters

            if not start_date and not end_date:
                # Set both start_date and end_date to the current date
                start_date = (date.today() - timedelta(days=3)).isoformat()
                end_date = date.today().isoformat()
            elif not start_date:
                # Set start_date to end_date
                start_date = end_date
            elif not end_date:
                # Set end_date to start_date
                end_date = start_date

            # Filter orders based on the provided dates
            order_counts = Order.objects.filter(order_date__date__range=[start_date, end_date]).exclude(payment_status__in=['CANCELLED', 'RETURNED'])\
                .values('order_date__date') \
                .annotate(order_count=Count('id'), total_price_sum=Sum('total_price')) \
                .order_by('order_date__date')
            
            
            # Filter orders which is delivered based on the provided dates   
            delivered_orders = Order.objects.filter(
                    order_date__date__range=[start_date, end_date],
                    payment_status='DELIVERED'
                ).values('order_date__date').annotate(
                    order_count=Count('id'),
                    total_price_sum=Sum('total_price')
                ).order_by('order_date__date')

            
            #taking the total deliverd order counts based on the provided dates 
            total_deliveries=delivered_orders.aggregate(total_deliveries=Sum('order_count'))['total_deliveries']
            
            # Filter orders which has been ordered  by users  based on the provided dates
            ordered_orders = Order.objects.filter(
                    order_date__date__range=[start_date, end_date],
                    payment_status='ORDERED'
                ).values('order_date__date').annotate(
                    order_count=Count('id'),
                    total_price_sum=Sum('total_price')
                ).order_by('order_date__date')

            
            returned_orders = Order.objects.filter(
                    order_date__date__range=[start_date, end_date],
                    payment_status='PENDING'
                ).values('order_date__date').annotate(
                    order_count=Count('id'),
                    total_price_sum=Sum('total_price')
                ).order_by('order_date__date')

            
            # The total count of the pending orders to be shipped
            total_pending=returned_orders.aggregate(total_pending=Sum('order_count'))['total_pending']



            #The top products which has highest sales on the provided dates
            top_products = Orderlist.objects.filter(order_id__order_date__date__range=[start_date, end_date]) \
                .values('product__product__name') \
                .annotate(total_sales=Sum('quantity')) \
                .order_by('-total_sales')[:5]
            
            #Calculate the total revenue of the provided dates    
            total_price_sum = order_counts.aggregate(total_price_sum=Sum('total_price'))['total_price_sum']
            
            # Calculate the total number of the orders based on the provided dates
            total_orders = order_counts.aggregate(total_orders=Sum('order_count'))['total_orders']

            
            # List the recent 5 orders in the dashboard for ease of access
            recent_orders=Order.objects.all().order_by('-id')[:5]
            
            #categories and the product count of the categories
            categories = Categories.objects.annotate(product_count=Count('product'))

            context = {
                'order_counts': order_counts,
                'total_price_sum': total_price_sum,
                'total_orders': total_orders,
                'top_products' : top_products,
                'total_deliveries' : total_deliveries ,
                'total_pending' : total_pending ,
                'recent_orders' : recent_orders ,
                'categories' : categories ,
                'start_date' : start_date ,
                'end_date' : end_date ,
            }
            context_data = {
                'order_counts': list(order_counts),
                'total_price_sum': total_price_sum,
                'total_orders': total_orders,
                'top_products': list(top_products),
                'total_deliveries': total_deliveries,
                'total_pending': total_pending,
                'start_date' : start_date ,
                'end_date' : end_date ,
                'categories': list(categories),
                
                  # Keep end_date as is, since it's already a string
            }
            
              # Convert the context_data to a JSON string
            json_data = json.dumps(context_data, cls=CustomJSONEncoder)
            # Pass the JSON data to the download_template view
            download_link = f"/download_template/?json_data={json_data}"

            # Include the download_link in the context to use it in the dashboard.html template
            context['download_link'] = download_link
            return render(request, 'admin/dashboard.html', context)
        else:
            return redirect('_admin_signin')
    else:
        return redirect('_admin_signin')



def _admin_signin(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect ('_admin_dashboard')
    if request.method=='POST':
        username=request.POST['username']
        pass1=request.POST['pass1']
        
        user=authenticate(username=username, password=pass1)
        
        if user is not None and user.is_superuser:
            login(request,user)
            return redirect('_admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('_admin_signin')
    return render (request, 'admin/admin_signin.html')



def admin_signout(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('_admin_signin')


def userlist(request):
    if request.user.is_authenticated and request.user.is_superuser:  
        #Retreiving all users from the user table according to the date they has joined.
        users=User.objects.all().order_by('date_joined')
        # Show  orders per page
        paginator = Paginator(users, 10) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context={
            'users': page_obj
        }
        return render (request, 'admin/userlist.html', context)
    else:
        return redirect('_admin_signin')



def block_user(request, user_id):
    if request.user.is_authenticated and request.user.is_superuser: 
        #Retreiving the user detail according to the argument that has passed to the function 
        user = get_object_or_404(User, id=user_id)
        user.is_active = False
        user.save()
        return redirect('userlist')  
    else:
        return redirect('_admin_signin')




def unblock_user(request, user_id):
    if request.user.is_authenticated and request.user.is_superuser: 
        #Retreiving the user detail according to the argument that has passed to the function 
        user = get_object_or_404(User, id=user_id)
        user.is_active = True
        user.save()
        return redirect('userlist') 
    else:
        return redirect('_admin_signin')



def categorylist(request):
   if request.user.is_authenticated and request.user.is_superuser: 
        #Retreiving the category name and the number of the products present in that category.
        product_counts = Categories.objects.annotate(product_count=Count('product')).order_by('id')
        context={
            'product_counts': product_counts
        }
        return render (request, 'admin/categorylist.html', context)
   else:
       return redirect('_admin_signin')



def create_category(request):
    if request.user.is_authenticated and request.user.is_superuser: 
        if request.method == 'POST':
            # Retrieve the category name from the form data
            category_name = request.POST['category_name']
            
            # Create a new category object
            category = Categories(category_name=category_name)
            
            # Save the category to the database
            category.save()
            
            
            return redirect('categorylist')  
        return render(request, 'admin/create_category.html')
    else:
        return redirect('_admin_signin')



def productlist(request):
    if request.user.is_authenticated and request.user.is_superuser: 
        #Retreiving the total products from the products table based on descending order they has created.
        products=Product.objects.all().order_by('-id')
        # Show  orders per page
        paginator = Paginator(products, 10) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context={
            'products': page_obj
        }
        return render(request,'admin/productlist.html', context)
    else:
        return redirect('_admin_signin')
 
    

def softdelete_product(request, product_id):
    if request.user.is_authenticated and request.user.is_superuser: 
        product = get_object_or_404(Product, id=product_id)
        product.is_active = False
        product.save()
        return redirect('productlist') 
    else:
        return redirect('_admin_signin')




def undo_softdelete_product(request, product_id):
    if request.user.is_authenticated and request.user.is_superuser: 
        product = get_object_or_404(Product, id=product_id)
        product.is_active = True
        product.save()
        return redirect('productlist') 
    else:
        return redirect ('_admin_signin')


def pending_orders(request):
    if request.user.is_authenticated and request.user.is_superuser: 
        orders=Order.objects.filter(payment_status="PENDING").order_by('-id')

        context={
            'orders' : orders
        }
        
        return render (request, 'admin/pendinglist.html' , context)
    else:
        return redirect('_admin_signin')



def orderlist(request):
    if request.user.is_authenticated and request.user.is_superuser: 
        orders=Order.objects.all().order_by('-id')
        # Show  orders per page
        paginator = Paginator(orders, 10) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context={
            'orders' : page_obj,
            
        }
        
        return render (request, 'admin/orderlist.html' , context)
    else:
        return redirect('_admin_signin')


#Details of each orders
def order_details(request, order_id):
    if request.user.is_authenticated and request.user.is_superuser: 
        order=Order.objects.get(id=order_id)
        context={
            'order' : order
        }
        
        return render (request, 'admin/order_details.html', context)
    
    else:
        return redirect('_admin_signin')

# Function to update the order status from adminside 
def update_order(request):
    if request.user.is_authenticated and request.user.is_superuser: 
        order_id = request.POST['order_id']
        payment_status = request.POST['payment_status']
        order = get_object_or_404(Order, id=order_id)

        # Update the payment status to "Shipped"
        order.payment_status = payment_status
        order.save()

        response_data = {'message': 'Order Status  Updated successfully'}

        return JsonResponse(response_data)
    return redirect ('_admin_signin')


#Function to cancel order from adminside.
def reject_order(request, order_id):
    if request.user.is_authenticated and request.user.is_superuser: 
        order = get_object_or_404(Order, id=order_id)

        # Update the payment status to "Rejected"
        order.payment_status = "CANCELLED"
        order.save()

        return redirect('orderlist')
    else:
        return redirect('_admin_signin')


def productvariantlist(request, product_id):
    if request.user.is_authenticated and request.user.is_superuser: 
        product=Product.objects.get(id=product_id)
        
        variants=ProductVariant.objects.filter(product=product)
        context={
            'variants' : variants,
            'product' : product
        }
    
        return render (request , 'admin/productvariantlist.html' , context)
    else:
        return redirect('_admin_signin')

from django.utils.text import slugify


def add_product(request):
    if request.user.is_authenticated and request.user.is_superuser: 
        if request.method == 'POST':
            product_name = request.POST.get('product_name')
            category_id = request.POST.get('category')
            description = request.POST.get('description')
            stock = request.POST.get('stock')
            price = request.POST.get('price')
            storage = request.POST.get('storage')
            color = request.POST.get('color')
            display_image = request.FILES.get('display_image')
            images = request.FILES.getlist('images')

            # Create the product
            category = Categories.objects.get(id=category_id)
            product = Product.objects.create(name=product_name, description=description, category=category)
            
            # Create the product variant
            storage_obj = Storage.objects.get(storage=storage)
            color_obj = Color.objects.get(color=color)
            variant = ProductVariant.objects.create(
                product=product,
                color=color_obj,
                storage=storage_obj,
                price=price,
                stock=stock,
                displayimage=display_image
            )

            # Create product images
            for image in images:
                ProductImage.objects.create(product=variant, image=image)

            return redirect('productlist')
        else:
            categories = Categories.objects.all()
            storage_options = Storage.objects.all()
            colours = Color.objects.all()
            context = {
                'categories': categories,
                'storage_options': storage_options,
                'colours': colours
            }
            return render(request, 'admin/add_product.html', context)
    else:
        return redirect('_admin_signin')
    
def add_variant(request, product_id):
    if request.user.is_authenticated and request.user.is_superuser: 
        product=Product.objects.get(id=product_id)

        if request.method == 'POST':
            stock = request.POST.get('stock')
            price = request.POST.get('price')
            discount = request.POST.get('discount')
            storage = request.POST.get('storage')
            color = request.POST.get('color')
            display_image = request.FILES.get('display_image')
            images = request.FILES.getlist('images')
            
            storage_obj = Storage.objects.get(storage=storage)
            color_obj = Color.objects.get(color=color)
            if price  and  discount  :
                # Validate discount value
                try:
                    discount = int(discount)
                    if discount < 0 or discount > 100:
                        raise ValueError("Discount must be a value between 0 and 100.")
                except ValueError:
                    messages.error(request, 'Invalid discount value. Discount must be a value between 0 and 100.')
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                
                discount_price = float(price) - float(price) * (float(discount) / float(100))
            else:
                discount_price = None
                discount=None
            variant = ProductVariant.objects.create(
                product=product,
                color=color_obj,
                storage=storage_obj,
                price=price,
                discount=discount,
                discount_price=discount_price,
                stock=stock,
                displayimage=display_image
            )
        
            for image in images:
                ProductImage.objects.create(product=variant, image=image)

            return redirect('productvariantlist' ,product_id=product.id )
        
        storage_options = Storage.objects.all()
        colours = Color.objects.all()
        context = {
                'product' : product ,
                'storage_options': storage_options,
                'colours': colours
            }
        return render(request, 'admin/add_variant.html' ,context)
    else:
        return redirect ('_admin_signin')


def edit_variant(request, variant_id):
    if request.user.is_authenticated and request.user.is_superuser: 
        variant = get_object_or_404(ProductVariant, id=variant_id)

        if request.method == 'POST':
            stock = request.POST.get('stock')
            price = request.POST.get('price')
            discount = request.POST.get('discount')
            display_image = request.FILES.get('display_image')
            images = request.FILES.getlist('images')

            
            
            # Update stock and price if provided
            if stock:
                variant.stock = stock
            if price:
                variant.price = price
            if  discount :
                # Validate discount value
                try:
                    discount=int(discount)
                    if discount < 0 or discount > 100:
                        raise ValueError("Discount must be a value between 0 and 100.")
                except ValueError:
                    messages.error(request, 'Invalid discount value. Discount must be a value between 0 and 100.')
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

                discount_price = float(variant.price) - float(variant.price) * (float(discount) / float(100))
                variant.discount=discount
                variant.discount_price=discount_price
            # Update display image if provided
            if display_image:
                variant.displayimage = display_image

            # Add additional images if provided
            for image in images:
                variant.productimage_set.create(image=image)

            # Save the changes
            variant.save()

            return redirect('productvariantlist', variant.product.id)

        context = {'variant': variant}
        return render(request, 'admin/update_stock.html', context)
    else:
        return redirect('_admin_signin')

def delete_product_image(request,product_image_id):
    if request.user.is_authenticated and request.user.is_superuser: 
        product_image = get_object_or_404(ProductImage, id=product_image_id)
        product=product_image.product.product.id
        product_image.delete()
        
        return redirect('productvariantlist' ,product_id=product)
    else:
        return redirect('_admin_signin')


def couponlist(request):
    if request.user.is_authenticated and request.user.is_superuser: 
        coupons=Coupon.objects.all()
        context={
            "coupons" : coupons
        }
        return render (request, 'admin/couponlist.html', context)
    else:
        return redirect('_admin_signin')

def create_coupon(request):
    if request.user.is_authenticated and request.user.is_superuser: 
        if request.method == 'POST':
            # Retrieve the category name from the form data
            coupon_name = request.POST['coupon_name']
            discount_price = request.POST['discount_price']
            minimum_amount = request.POST['minimum_amount']
            
        # Check if a coupon with the same name already exists
            if Coupon.objects.filter(coupon_code=coupon_name).exists():
                messages.error(request, 'Coupon with this name already exists.')
                return redirect('couponlist')
            else:
                # Create the coupon if it doesn't already exist
                Coupon.objects.create(coupon_code=coupon_name, discount_price=discount_price, minimum_amount=minimum_amount)
                messages.success(request, 'Coupon created successfully.')
                return redirect('couponlist')
            
        return render(request, 'admin/create_coupon.html')
    else:
        return redirect('_admin_signin')

def disable_coupon(request, coupon_id):
    if request.user.is_authenticated and request.user.is_superuser: 
        coupon=Coupon.objects.get(id=coupon_id)
        coupon.is_expired = True
        coupon.save()
        return redirect('couponlist')
    else:
        return redirect('_admin_signin')

def enable_coupon(request, coupon_id):
    if request.user.is_authenticated and request.user.is_superuser: 
        coupon=Coupon.objects.get(id=coupon_id)
        coupon.is_expired = False
        coupon.save()
        return redirect('couponlist')
    else:
        return redirect ('_admin_signin')

def edit_coupon(request,coupon_id):
    if request.user.is_authenticated and request.user.is_superuser: 
        coupon=Coupon.objects.get(id=coupon_id)
        if request.method == 'POST':
            # Retrieve the category name from the form data
            coupon_name = request.POST['coupon_name']
            discount_price = request.POST['discount_price']
            minimum_amount = request.POST['minimum_amount']
            
            coupon.coupon_code=coupon_name
            coupon.discount_price=discount_price
            coupon.minimum_amount=minimum_amount
            coupon.save()
            
            return redirect('couponlist')  
        context={
            'coupon': coupon
        }    
        return render(request, 'admin/edit_coupon.html', context)
    else:
        return redirect('_admin_signin')


def referral(request):
    if request.user.is_authenticated and request.user.is_superuser: 
        refer=ReferralOffers.objects.all().order_by('-id')
        if refer:
            referrer_amount=refer[0].referrer_amount
            referral_discount=refer[0].referral_discount
            referral_description=refer[0].referral_description    
            
            context={
                "referrer_amount" : referrer_amount ,
                "referral_discount" : referral_discount ,
                "referral_description" : referral_description ,
                'refer' : refer
            }
            
            return render(request, 'admin/referral.html' , context)
        return render(request, 'admin/referral.html' )
    else:
        return redirect('_admin_signin')

def add_referral(request):
    if request.user.is_authenticated and request.user.is_superuser: 
        if request.method=='POST':
            referrer_amount=request.POST['referrer_amount']
            referral_discount=request.POST['referral_discount']
            referral_description=request.POST['referral_description']
            
            ReferralOffers.objects.create(referrer_amount=referrer_amount,referral_discount=referral_discount, referral_description=referral_description  )
            return redirect('referral')
        
        return render (request, 'admin/add_referral.html')
    else:
        return redirect('_admin_signin')

def edit_referral(request):
    if request.user.is_authenticated and request.user.is_superuser: 
        refer=ReferralOffers.objects.all().order_by('-id')
        if refer:
            referrer_amount=refer[0].referrer_amount
            referral_discount=refer[0].referral_discount
            referral_description=refer[0].referral_description    
            
        
        if request.method=='POST':
            referrer_amount=request.POST['referrer_amount']
            referral_discount=request.POST['referral_discount']
            referral_description=request.POST['referral_description']
            
            if refer:
                refer[0].referrer_amount=referrer_amount
                refer[0].referral_discount =referral_discount
                refer[0].referral_description =  referral_description 
                
                refer[0].save()
                return redirect('referral')
        context={
                "referrer_amount" : referrer_amount ,
                "referral_discount" : referral_discount ,
                "referral_description" : referral_description ,
                'refer' : refer
            }
        return render(request, 'admin/edit_referral.html', context)
    else:
        return redirect ('_admin_signin')

def delete_referral(request):
    if request.user.is_authenticated and request.user.is_superuser: 
        refer=ReferralOffers.objects.all().order_by('-id')
        refer[0].delete()
        return redirect('referral')
    else:
        return redirect ('_admin_signin')


def banners(request):
    if request.user.is_authenticated and request.user.is_superuser: 
        banners=Slider.objects.all()
        
        context={
            'banners' : banners
        }
        return render (request, 'admin/bannerlist.html' , context)
    else:
        return redirect ('_admin_signin')

def create_banner(request):
    if request.user.is_authenticated and request.user.is_superuser: 
        if request.method =="POST":
            Image = request.FILES.get('Image')
            Discount_deals = request.POST.get('Discount_deals')
            Product = request.POST.get('Product')

            product=ProductVariant.objects.get(id=Product)
            banner=Slider.objects.create(Image=Image, Discount_deals=Discount_deals, Product=product)
            return redirect('banners')
        products = ProductVariant.objects.all()
        deals_choices = [choice[1] for choice in Slider.DISCOUNT_DEALS]
        context={
            'products' : products,
            'deals_choices': deals_choices,
        }
        return render (request, 'admin/create_banner.html' , context)
    else:
        return redirect ('_admin_signin')


def delete_banner(request,banner_id):
    if request.user.is_authenticated and request.user.is_superuser: 
        banner=Slider.objects.get(id=banner_id)
        banner.delete()
        
        return redirect('banners')
    else:
        return redirect ('_admin_signin')

