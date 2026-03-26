from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views import View
from carts.mixins import CartMixin
from django.shortcuts import get_object_or_404
from django.db.models import Sum, F

from carts.models import Cart
from carts.utils import get_user_carts
from goods.models import Products

from .models import Cart, Products
import logging


logger = logging.getLogger(__name__)


class CartAddView(CartMixin, View):
    def post(self, request):
        product_id = request.POST.get("product_id")
        product = get_object_or_404(Products, id=product_id)

        cart = self.get_cart(request, product=product)

        if cart:
            cart.quantity += 1
            cart.save()
        else:

            Cart.objects.create(
                user=request.user if request.user.is_authenticated else None,
                session_key=(
                    request.session.session_key
                    if not request.user.is_authenticated
                    else None
                ),
                product=product,
                quantity=1,
            )

        return JsonResponse(
            {
                "success": True,
                "message": f"{product.name} added to cart!",
                "total_quantity": self.get_total_quantity(request),
                "cart_items_html": self.render_cart(request),
            }
        )


logger = logging.getLogger(__name__)


class CartChangeView(CartMixin, View):
    def post(self, request):
        cart_id = request.POST.get("cart_id")
        quantity = request.POST.get("quantity")

        cart = self.get_cart(request, cart_id=cart_id)

        if cart:
            cart.quantity = max(1, int(quantity))
            cart.save()

            user_cart = get_user_carts(request)

            return JsonResponse(
                {
                    "message": "The quantity has been changed",
                    "cart_items_html": self.render_cart(request),
                    "total_quantity": user_cart.total_quantity(),
                    "total_price": user_cart.total_price(),
                }
            )

        return JsonResponse({"message": "Error: Cart not found"}, status=404)


logger = logging.getLogger(__name__)


class CartRemoveView(CartMixin, View):
    def post(self, request):
        cart_id = request.POST.get("cart_id")

        cart_item = self.get_cart(request, cart_id=cart_id)

        if cart_item:
            cart_item.delete()

            cart_items_html = self.render_cart(request)

            return JsonResponse(
                {
                    "message": "The product has been removed",
                    "cart_items_html": cart_items_html,
                    "total_quantity": self.get_total_quantity(request),
                }
            )

        return JsonResponse(
            {"message": "The product has already been deleted or not found."},
            status=404,
        )
