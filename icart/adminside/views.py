from django.shortcuts import render, redirect,get_object_or_404
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

# from productside.forms import ProductForm

# Create your views here.



#  dashboard function of the admin 
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
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

            
            # The total count of the pending orders to be shipped
            total_pending=ordered_orders.aggregate(total_pending=Sum('order_count'))['total_pending']



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

            return render(request, 'admin/dashboard.html', context)
        else:
            return redirect('_admin_signin')
    else:
        return redirect('_admin_signin')

# signin function for the admin 
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
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


# Signout function for the admin
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_signout(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('_admin_signin')


# Function for listing the total users in admin side
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def userlist(request):
    
    #Retreiving all users from the user table according to the date they has joined.
    users=User.objects.all().order_by('date_joined')
    context={
        'users': users
    }
    return render (request, 'admin/userlist.html', context)


#Function to block the user which leads to reject the access from the website.
def block_user(request, user_id):
    
    #Retreiving the user detail according to the argument that has passed to the function 
    user = get_object_or_404(User, id=user_id)
    user.is_active = False
    user.save()
    return redirect('userlist')  


# Function unblock the user who has been blocked.
def unblock_user(request, user_id):
    
    #Retreiving the user detail according to the argument that has passed to the function 
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    return redirect('userlist') 



# Function to list the categories in the website.
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def categorylist(request):
    
    #Retreiving the category name and the number of the products present in that category.
    product_counts = Categories.objects.annotate(product_count=Count('product')).order_by('id')
    context={
        'product_counts': product_counts
    }
    return render (request, 'admin/categorylist.html', context)


# Function to create new categories from the admin side.
def create_category(request):
    if request.method == 'POST':
        # Retrieve the category name from the form data
        category_name = request.POST['category_name']
        
        # Create a new category object
        category = Categories(category_name=category_name)
        
        # Save the category to the database
        category.save()
        
        
        return redirect('categorylist')  
        
    return render(request, 'admin/create_category.html')


# Function to list the products in the admin side
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def productlist(request):
    
    #Retreiving the total products from the products table based on descending order they has created.
    products=Product.objects.all().order_by('-id')
    context={
        'products': products
    }
    return render(request,'admin/productlist.html', context)




# def create_product(request):
#     if request.method == 'POST':
#         form = ProductForm(request.POST, request.FILES)
#         if form.is_valid():
#             product = form.save(commit=False)
#             product.save()

#             images = request.FILES.getlist('images')
#             for image in images:
#                 ProductImage.objects.create(product=product, image=image)

#             # Redirect to a view showing the list of products
#             return redirect('product_list')  
#     else:
#         form = ProductForm()

#     return render(request, 'create_product.html', {'form': form})


# def save_product(request,product_id):
#     if request.method == 'POST':
        
#         product = get_object_or_404(Product, id=product_id)
#         form = ProductForm(request.POST, request.FILES, instance=product)

#         if form.is_valid():
#             product = form.save()
#             product.save()
            
#             images = request.FILES.getlist('images')
#             for image in images:
#                 ProductImage.objects.create(product=product, image=image)
#             # Redirect to the product list or another relevant view
#             return redirect('productlist')
#     else:
#         form = ProductForm(instance=product)

#     # If the form submission is invalid or the request method is not POST,
#     # render the edit form again with the errors or empty form
#     return render(request, 'edit_product.html', {'form': form})

# def edit_product(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     form = ProductForm(instance=product)
#     images=ProductImage.objects.filter(product=product_id)
#     context = {'form': form,
#                'product': product_id ,
#                'images': images
#                }
#     return render(request, 'edit_product.html', context)



    
    
# Deleting the product from the website, still it will be in the database  
def softdelete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.is_active = False
    product.save()
    return redirect('productlist') 


# Undoing the deletion of the product.
def undo_softdelete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.is_active = True
    product.save()
    return redirect('productlist') 


# Listing the total orders in th admin side.
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def orderlist(request):
    orders=Order.objects.all().order_by('-id')
    
    context={
        'orders' : orders
    }
    
    return render (request, 'admin/orderlist.html' , context)

#Details of the selected order and the products that has ordered in that order.
def order_details(request, order_id):
    order=Order.objects.get(id=order_id)
    context={
        'order' : order
    }
    
    return render (request, 'admin/order_details.html', context)
 
# Function to ship the orders  from adminside 
def update_order(request):
    order_id = request.POST['order_id']
    payment_status = request.POST['payment_status']
    order = get_object_or_404(Order, id=order_id)

    # Update the payment status to "Shipped"
    order.payment_status = payment_status
    order.save()

    response_data = {'message': 'Order Status  Updated successfully'}

    return JsonResponse(response_data)
#Function to cancel order from adminside.
def reject_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Update the payment status to "Rejected"
    order.payment_status = "CANCELLED"
    order.save()

    return redirect('orderlist')


#Listing the variants of a product and the details and images
def productvariantlist(request, product_id):
    product=Product.objects.get(id=product_id)
    
    variants=ProductVariant.objects.filter(product=product)
    context={
        'variants' : variants,
        'product' : product
    }
   
    return render (request , 'admin/productvariantlist.html' , context)





from django.utils.text import slugify


#Function to add a new product
def add_product(request):
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
    
# Function to add a new variant to existing product   
def add_variant(request, product_id):
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
        if price is not None and discount is not None:
                discount_price = float(price) - float(price) * (float(discount) / float(100))
        else:
            discount_price = None
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


#Function to edit the variant details and images.
def edit_variant(request, variant_id):
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

#function to delete the existing images of variants.
def delete_product_image(request,product_image_id):
    product_image = get_object_or_404(ProductImage, id=product_image_id)
    product=product_image.product.product.id
    product_image.delete()
    
    return redirect('productvariantlist' ,product_id=product)



    