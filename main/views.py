from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView

from goods.models import Categories


class IndexView(TemplateView):
    template_name = "main/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "HomeMade"
        context["content"] = " Furniture store HomeMade"
        return context


class DeliveryAndPaymentView(TemplateView):
    template_name = "main/delivery_and_payment.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site_name"] = "HomeMade"
        return context


class ContactInformationsView(TemplateView):
    template_name = "main/contact_informations.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site_name"] = "HomeMade"
        return context


class AboutView(TemplateView):
    template_name = "main/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site_name"] = "HomeMade"
        return context


class PrivacyPolicyView(TemplateView):
    template_name = "main/privacy_policy.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site_name"] = "HomeMade"
        return context


class TermsAndConditionsView(TemplateView):
    template_name = "main/terms_and_conditions.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site_name"] = "HomeMade"
        return context
