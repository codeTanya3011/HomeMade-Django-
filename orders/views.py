from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.forms import ValidationError
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import FormView
import re

from carts.models import Cart
from orders.forms import CreateOrderForm
from orders.models import Order, OrderItem


class CreateOrderView(LoginRequiredMixin, FormView):
    template_name = "orders/create_order.html"
    form_class = CreateOrderForm
    success_url = reverse_lazy("users:profile")

    def get_initial(self):
        initial = super().get_initial()

        initial["first_name"] = self.request.user.first_name
        initial["last_name"] = self.request.user.last_name

        initial["phone_number"] = self.request.user.phone_number
        return initial

    def form_valid(self, form):
        user = self.request.user
        cart_items = Cart.objects.filter(user=user)

        if not cart_items.exists():
            messages.error(
                self.request,
                "Your cart is empty. Please add items before placing an order.",
            )
            return self.render_to_response(self.get_context_data(form=form))

        phone_raw = form.cleaned_data.get("phone_number", "")
        phone_clean = re.sub(r"\D", "", str(phone_raw or ""))

        if len(phone_clean) < 7:
            messages.error(self.request, "Phone number must contain at least 7 digits.")
            return self.render_to_response(self.get_context_data(form=form))

        try:
            with transaction.atomic():

                order = Order.objects.create(
                    user=user,
                    phone_number=phone_clean,
                    requires_delivery=form.cleaned_data.get("requires_delivery", False),
                    delivery_address=form.cleaned_data.get("delivery_address", ""),
                    payment_on_get=form.cleaned_data.get("payment_on_get", False),
                )

                if not user.phone_number:
                    user.phone_number = phone_clean
                    user.save()

                for cart_item in cart_items:
                    product = cart_item.product
                    if product.quantity < cart_item.quantity:

                        raise ValidationError(
                            f'Insufficient quantity of "{product.name}" in stock.'
                        )

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        name=product.name,
                        price=product.sell_price(),
                        quantity=cart_item.quantity,
                    )

                    product.quantity -= cart_item.quantity
                    product.save()

                cart_items.delete()

            messages.success(self.request, "The order has been placed successfully!")
            return redirect(self.get_success_url())

        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.render_to_response(self.get_context_data(form=form))
        except Exception as e:
            messages.error(self.request, f"Something went wrong: {str(e)}")
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Placing an order"
        context["order"] = True
        return context
