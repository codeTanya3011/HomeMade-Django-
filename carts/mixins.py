from django.template.loader import render_to_string
from django.urls import reverse
from carts.models import Cart
from carts.utils import get_user_carts
from django.db.models import Sum
import logging

# Configure the logger
logger = logging.getLogger(__name__)


class CartMixin:
    def get_cart(self, request, product=None, cart_id=None):
        query_kwargs = {}

        if request.user.is_authenticated:
            query_kwargs["user"] = request.user
        else:
            if not request.session.session_key:
                request.session.create()
            query_kwargs["session_key"] = request.session.session_key

        logger.info(
            f"Getting cart for session_key: {request.session.session_key}, user: {request.user}"
        )

        if product:
            query_kwargs["product"] = product
        if cart_id:
            query_kwargs["id"] = cart_id

        try:
            cart = Cart.objects.filter(**query_kwargs).first()
            logger.info(f"Cart retrieved: {cart}")
            return cart
        except Cart.DoesNotExist:
            logger.warning("Cart not found")
            return None

    def get_total_quantity(self, request):

        query_kwargs = {}

        if request.user.is_authenticated:
            query_kwargs["user"] = request.user
        else:
            query_kwargs["session_key"] = request.session.session_key

        total = Cart.objects.filter(**query_kwargs).aggregate(total=Sum("quantity"))[
            "total"
        ]
        total_quantity = total or 0
        logger.info(f"Total quantity in cart: {total_quantity}")
        return total_quantity

    def render_cart(self, request):
        user_cart = get_user_carts(request)

        total_price = user_cart.total_price()

        context = {
            "carts": user_cart,
            "total_quantity": self.get_total_quantity(request),
            "total_price": total_price,
        }

        referer = request.META.get("HTTP_REFERER", "")
        if reverse("orders:create_order") in referer:
            context["order"] = True

        return render_to_string(
            "carts/includes/included_cart.html", context, request=request
        )
