from django.http import Http404
from django.views.generic import DetailView, ListView

from goods.models import Products
from goods.utils import q_search
from django.contrib import messages


class CatalogView(ListView):
    model = Products
    template_name = "goods/catalog.html"
    context_object_name = "goods"
    paginate_by = 12
    allow_empty = True
    slug_url_kwarg = "category_slug"

    def get_queryset(self):
        category_slug = self.kwargs.get(self.slug_url_kwarg)
        on_sale = self.request.GET.get("on_sale")
        order_by = self.request.GET.get("order_by")
        query = self.request.GET.get("q")

        goods = super().get_queryset()

        if query is not None:
            query = query.strip()

            if not query:
                messages.warning(self.request, "Enter your search term!")
                goods = Products.objects.all()
            else:

                goods = q_search(query)
                if not goods.exists():
                    messages.info(self.request, f"On request '{query}' nothing found")

        elif category_slug == "all":
            goods = goods
        else:
            goods = goods.filter(category__slug=category_slug)

        if on_sale:
            goods = goods.filter(discount__gt=0)
        if order_by and order_by != "default":
            goods = goods.order_by(order_by)

        return goods

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Catalog"
        context["slug_url"] = self.kwargs.get(self.slug_url_kwarg)
        return context


class ProductView(DetailView):
    template_name = "goods/product.html"
    slug_url_kwarg = "product_slug"
    context_object_name = "product"

    def get_object(self, queryset=None):
        slug = self.kwargs.get(self.slug_url_kwarg)
        if not slug:
            raise Http404("Page not found")

        try:
            product = Products.objects.get(slug=slug)
            return product
        except Products.DoesNotExist:
            raise Http404("Product not found")