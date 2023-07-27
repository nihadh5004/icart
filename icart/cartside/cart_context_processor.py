from cartside.models import *
from django.contrib.auth.models import User


def cart_item_count_context(request):
    if request.user.is_authenticated:
        user=request.user
        # Your code to get the cart items and calculate the cart_item_count
        cart=UserCart.objects.get(user=user)
        cart_items = Cart.objects.filter(cart_id=cart)
        cart_item_count = len(cart_items)  # Calculate the number of items in the cart

        # Return a dictionary with the variable you want to add to the context
        return {'cart_item_count': cart_item_count}
    else:
        cart_item_count = 0 
        
        return {'cart_item_count': cart_item_count}


def wishlist_item_count_context(request):
    if request.user.is_authenticated:
        user=request.user
        # Your code to get the cart items and calculate the cart_item_count
        wish=UserWishlist.objects.get(user=user)
        wishlist_items = Wishlist.objects.filter(wishlist_id=wish)
        wishlist_item_count = len(wishlist_items)  # Calculate the number of items in the cart

        # Return a dictionary with the variable you want to add to the context
        return {'wishlist_item_count': wishlist_item_count}
    else:
        wishlist_item_count = 0 
        
        return {'wishlist_item_count': wishlist_item_count}