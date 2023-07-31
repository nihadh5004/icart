from cartside.models import *
from django.contrib.auth.models import User

def cart_item_count_context(request):
    if request.user.is_authenticated:
        # Code for authenticated user
        user = request.user
        cart = UserCart.objects.get(user=user)
        cart_items = Cart.objects.filter(cart_id=cart)
        cart_item_count = len(cart_items)
    else:
        # Code for guest user
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart_items = Cart.objects.filter(cart_id=cart_id)
            cart_item_count = len(cart_items)
        else:
            cart_item_count = 0

    return {'cart_item_count': cart_item_count}


def wishlist_item_count_context(request):
    if request.user.is_authenticated:
        # Code for authenticated user
        user = request.user
        wish = UserWishlist.objects.get(user=user)
        wishlist_items = Wishlist.objects.filter(wishlist_id=wish)
        wishlist_item_count = len(wishlist_items)
    else:
        # Code for guest user
        wishlist_id = request.session.get('wishlist_id')
        if wishlist_id:
            wishlist_items = Wishlist.objects.filter(wishlist_id=wishlist_id)
            wishlist_item_count = len(wishlist_items)
        else:
            wishlist_item_count = 0

    return {'wishlist_item_count': wishlist_item_count}
