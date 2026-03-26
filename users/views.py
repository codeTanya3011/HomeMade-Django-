from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import auth, messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.db.models import Prefetch
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView
from carts.models import Cart
from common.mixins import CacheMixin
from orders.models import Order, OrderItem

from users.forms import ProfileForm, UserLoginForm, UserRegistrationForm


class UserLoginView(LoginView):
    template_name = 'users/login.html'
    form_class = UserLoginForm

    def form_valid(self, form):
        # 1. Запоминаем анонимный ключ СЕЙЧАС, пока он не протух
        session_key = self.request.session.session_key
        
        # 2. Логиним пользователя (стандартный метод Django)
        auth.login(self.request, form.get_user())
        
        # 3. Теперь, когда юзер уже в системе (self.request.user обновлен)
        user = self.request.user
        
        if session_key:
            # Чистим старое, привязываем новое
            Cart.objects.filter(user=user).delete()
            Cart.objects.filter(session_key=session_key).update(user=user)
        
        messages.success(self.request, f"{user.username}, You are logged in!")

        # 4. ВАЖНО: Возвращаем редирект вручную, не ломая логику super()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        redirect_page = self.request.POST.get('next', None)
        if redirect_page and redirect_page != reverse('user:logout'):
            return redirect_page
        return reverse_lazy('main:index')
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Authorization'
        return context


class UserRegistrationView(CreateView):
    template_name = 'users/registration.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('users:profile')

    def form_valid(self, form):
        # 1. Сначала сохраняем анонимную сессию
        session_key = self.request.session.session_key
        
        # 2. Сохраняем пользователя и логиним его
        user = form.save()
        auth.login(self.request, user)

        # 3. Переносим корзину
        if session_key:
            Cart.objects.filter(session_key=session_key).update(user=user)

        messages.success(self.request, f"{user.username}, You have successfully registered!")
        
        # 4. Всегда возвращаем редирект
        return HttpResponseRedirect(self.success_url)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registration'
        return context


class UserProfileView(LoginRequiredMixin, CacheMixin , UpdateView):
    template_name = 'users/profile.html'
    form_class = ProfileForm
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "An error has occurred")
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Cabinet'

        orders = Order.objects.filter(user=self.request.user).prefetch_related(
                Prefetch(
                    "orderitem_set",
                    queryset=OrderItem.objects.select_related("product"),
                )
            ).order_by("-id")

        context['orders'] = self.set_get_cache(orders, f"user_{self.request.user.id}_orders", 60)
        return context


class UserCartView(TemplateView):
    template_name = 'users/users_cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Cart'
        return context

@login_required
def logout(request):
    messages.success(request, f"{request.user.username}, You have logged out of your account.")
    auth.logout(request)
    return redirect(reverse('main:index'))





# def login(request):
#     if request.method == 'POST':
#         form = UserLoginForm(data=request.POST)
#         if form.is_valid():
#             username = request.POST['username']
#             password = request.POST['password']
#             user = auth.authenticate(username=username, password=password)

#             session_key = request.session.session_key

#             if user:
#                 auth.login(request, user)
#                 messages.success(request, f"{username},")

#                 if session_key:
#                     # delete old authorized user carts
#                     forgot_carts = Cart.objects.filter(user=user)
#                     if forgot_carts.exists():
#                         forgot_carts.delete()
#                     # add new authorized user carts from anonimous session
#                     Cart.objects.filter(session_key=session_key).update(user=user)

#                 redirect_page = request.POST.get('next', None)
#                 if redirect_page and redirect_page != reverse('user:logout'):
#                     return HttpResponseRedirect(request.POST.get('next'))

#                 return HttpResponseRedirect(reverse('main:index'))
#     else:
#         form = UserLoginForm()
#     context = {
#         'title': "",
#         'form': form
#     }
#     return render(request, 'users/login.html', context)

# def registration(request):
#     if request.method == 'POST':
#         form = UserRegistrationForm(data=request.POST)
#         if form.is_valid():
#             form.save()

#             session_key = request.session.session_key

#             user = form.instance
#             auth.login(request, user)

#             if session_key:
#                     Cart.objects.filter(session_key=session_key).update(user=user)
#             messages.success(request, f"{user.username},")
#             return HttpResponseRedirect(reverse('main:index'))
#     else:
#         form = UserRegistrationForm()
#     context = {
#         'title': "",
#         'form' : form
#     }
#     return render(request, 'users/registration.html', context)

# @login_required
# def profile(request):
#     if request.method == 'POST':
#         form = ProfileForm(data=request.POST, instance=request.user, files=request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "")
#             return HttpResponseRedirect(reverse('user:profile'))
#     else:
#         form = ProfileForm(instance=request.user)  

#     orders = Order.objects.filter(user=request.user).prefetch_related(
#                 Prefetch(
#                     "orderitem_set",
#                     queryset=OrderItem.objects.select_related("product"),
#                 )
#             ).order_by("-id")

#     context = {
#         'title': "",
#         'form': form,
#         'orders': orders,
#     }
#     return render(request, 'users/profile.html', context)

# def users_cart(request):
#     return render(request, 'users/users_cart.html')
    



