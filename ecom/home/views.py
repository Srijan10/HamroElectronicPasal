import random
import string
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView ,TemplateView, View, ListView, CreateView

from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from .forms import CheckoutForm, CouponForm, RefundForm, PaymentForm, ComputerMaintainanceForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.
from home.models import Item,Slider,Brand, OrderItem , Order,Category, Address,Coupon,Payment,Refund, Comment,Setting,Maintaince,ShopCart
from .forms import UserUpdateForm, ProfileUpdateForm, UserRegisterForm, CommentForm, RiviewForm,ComputerMaintainanceForm

class EcomMixin(object):
    def dispatch(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            if request.user.is_authenticated and request.user.customer:
                cart_obj.customer = request.user.customer
                cart_obj.save() 
        return super().dispatch(request, *args, **kwargs)

class BaseNavView(View):
    template_context = {}



class HomeBaseView(ListView):
    model = Item
    template_name= 'index.html'

    def get_context_data(self,**kwargs):
        context = super(HomeBaseView, self).get_context_data(**kwargs)
        # context['posts'] = Post.objects.all()
        context['items'] = Item.objects.all()[:10]
        context['sliders']=Slider.objects.all()
        context['indexsale'] = Item.objects.all().order_by('id')[:3]
        context['indexrecent'] = Item.objects.all().order_by('?')[:]
        context['indexnew'] = Item.objects.all().order_by('-id')[:3]
        context['indexdefault'] = Item.objects.filter(status = 'default')[:3]
        context['brands'] = Brand.objects.all()
        context['categorys']= Category.objects.all()[:5]
        # for sc in ShopCart:
        #     total += sc.item.price*sc.quantity

        # context['total':total]
        # And so on for more models
        return context


class CategoryView(ListView):
    model = Item
    template_name = "category.html"

    def get_context_data(self, **kwargs):
        context = super(CategoryView, self).get_context_data(**kwargs)
        # context['posts'] = Post.objects.all()
        context['items'] = Item.objects.all()
        context['categorys'] = Category.objects.all()
        context['indexsale'] = Item.objects.filter(status = 'sale')[:3]
        context['indexrecent'] = Item.objects.filter(status = 'recent')[:3]
        context['indexnew'] = Item.objects.filter(status = 'new')[:3]
        context['indexdefault'] = Item.objects.filter(status = 'default')[:3]
        # And so on for more models
        return context




class CategoryListView(ListView):
    model = Item
    template_name = 'category_item.html'
    def get_context_data(self,**kwargs):
        context = super(CategoryListView,self).get_context_data(**kwargs)
        
        def query(self):
            category = self.kwargs.get('category')
            return category
        
        def get_queryset(self):
            category = self.kwargs.get('category')
            return Item.objects.filter(category__title=category)
        
        context['items'] = Item.objects.all()
        context['categorys'] = Category.objects.all()
        context['object_list'] = get_queryset(self)
        context['category_list'] = query(self)
        # And so on for more models
        return context
   

def search(request):
    try:
        search = request.GET.get('search')
    except:
        search = None
    if search:
        items = Item.objects.filter(title__contains = search)
        context = {'items': items, 'query': search}
        template = 'search.html'
    else:
        template= 'index.html'
        context= {}
    
    return render(request, template, context)



class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            categorys = Category.objects.all()[:5]
            form = CheckoutForm()
            context = {
                'categorys': categorys,
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})

            billing_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='B',
                default=True
            )
            if billing_address_qs.exists():
                context.update(
                    {'default_billing_address': billing_address_qs[0]})
            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("home:checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():

                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    print("Using the defualt shipping address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default shipping address available")
                        return redirect('home:checkout')
                else:
                    print("User is entering a new shipping address")
                    shipping_address1 = form.cleaned_data.get(
                        'shipping_address')
                    shipping_address2 = form.cleaned_data.get(
                        'shipping_address2')
                    shipping_phone = form.cleaned_data.get('shipping_phone')

                    if is_valid_form([shipping_address1, shipping_phone]):
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                           
                            phone=shipping_phone,
                            address_type='S'
                        )
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required shipping address fields")

                use_default_billing = form.cleaned_data.get(
                    'use_default_billing')
                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')

                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()

                elif use_default_billing:
                    print("Using the defualt billing address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='B',
                        default=True
                    )
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default billing address available")
                        return redirect('home:checkout')
                else:
                    print("User is entering a new billing address")
                    billing_address1 = form.cleaned_data.get(
                        'billing_address')
                    billing_address2 = form.cleaned_data.get(
                        'billing_address2')
                    billing_phone = form.cleaned_data.get('billing_phone')

                    if is_valid_form([billing_address1, billing_phone]):
                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            phone=billing_phone,
                            address_type='B'
                        )
                        billing_address.save()

                        order.billing_address = billing_address
                        order.save()

                        set_default_billing = form.cleaned_data.get(
                            'set_default_billing')
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required billing address fields")

                payment_option = form.cleaned_data.get('payment_option')

                if payment_option == 'S':
                    return HttpResponse("ESEWA SERVICE IS NOT AVAILABLE RIGHT NOW.")
                elif payment_option == 'P':
                    return redirect('home:payment', payment_option='PaymentOneDelivery')
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('home:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("home:order-summary")


class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False,
            }
            userprofile = self.request.user.userprofile
            return redirect("home:payment",context)
        else:
            messages.warning(
                self.request, "You have not added a billing address")
            return redirect("home:checkout")



class ProductBaseView(BaseNavView):
    model = Item
    template_name = "shop.html"

    def get(self,request):
        self.template_context['items']=Item.objects.all()
        self.template_context['categorys']=Category.objects.all()[:5]
        return render(self.request,'shop.html',self.template_context)


class CartBaseView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order,
                'categorys' : Category.objects.all()[:5],
                'recentitems' : Item.objects.all().order_by('-id')[:3],
                'randomitems' : Item.objects.all().order_by('?')[:3],
            }
            return render(self.request, 'cart.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")



class ItemDetailView(DetailView):
    model = Item
    template_name = 'single-product.html'
    def get_context_data(self,**kwargs):
        context = super(ItemDetailView, self).get_context_data(**kwargs)
        context['items'] = Item.objects.all()
        context['categorys'] = Category.objects.all()[:5]
        context['indexsale'] = Item.objects.filter(status = 'sale')
        context['indexrecent'] = Item.objects.filter(status = 'recent')
        context['indexnew'] = Item.objects.filter(status = 'new')
        context['indexdefault'] = Item.objects.filter(status = 'default')
        context['comments']= Comment.objects.filter(status="New")
        context['cform'] = CommentForm
        context['rform'] = RiviewForm
        return context

def addcomment(request, id):
    url = request.META.get('HTTP_REFERER')
    
    if request.method == 'POST':  # check post
        form = CommentForm(request.POST)
        if form.is_valid():
            data = Comment()
            data.comment = form.cleaned_data['comment']
            data.ip = request.META.get('REMOTE_ADDR')
            data.item_id=id
            current_user= request.user
            data.user_id=current_user.id
            data.save()
            messages.success(request, "Your comment has been sent. Thank you for your interest.")
            return HttpResponseRedirect(url)

    return HttpResponseRedirect(url)

def addRiview(request):
    url = request.META.get('HTTP_REFERER')  # get last url
#    return HttpResponse(url)
    if request.method == 'POST':
      form = RiviewForm(request.POST)
      if form.is_valid():
         data = Riview()  # create relation with model
         data.rate = form.cleaned_data['rate']
         current_user= request.user
         data.user_id=current_user.id
         data.save()  # save data to table
         messages.success(request, "Your review has ben sent. Thank you for your interest.")
         return HttpResponseRedirect(url)

    return HttpResponseRedirect(url)

def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid

def register(request):
    categorys = Category.objects.all()[:5]
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You are now able to log in')
            return redirect('login',{'categorys':categorys})
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form, 'categorys':categorys})


def shopcart(request):
    setting = Setting.objects.get(pk=1)
    category = Category.objects.all()
    current_user = request.user
    shopcart = ShopCart.objects.filter(user_id=current_user.id)
    total = 0
    for sc in shopcart:
        total += sc.item.price * sc.quantity
    context = {'setting':setting,'shopcart':shopcart, 'category':category, 'total':total}
    return render(request, 'cart.html', context)


@login_required
def add_to_cart(request, slug):
    
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    shop_cart, created = ShopCart.objects.get_or_create(item=item, user=request.user,ordered=False)
    if shop_cart:
        control = 1 # The product is in the cart
    else:
        control = 0 # The product is not in the cart"""

    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if item.quantity >= 1:
            if order.items.filter(item__slug=item.slug).exists():
                order_item.quantity += 1
                shop_cart.quantity += 1
                item.quantity = item.quantity - 1
                item.save()
                order_item.save()
                shop_cart.save()
                
                messages.info(request, "This item quantity was updated.")
                return redirect("home:cart")
            else:
                order.items.add(order_item)
                item.quantity = item.quantity -1
                item.save()
                messages.info(request, "This item was added to your cart.")
                return redirect("home:cart")
        else:
            messages.info(request,"Out of Stock")
            return HttpResponse("Out of stock")

    else:
        if item.quantity >= 1:
            
            item.quantity = item.quantity - 1
            item.save()
            ordered_date = timezone.now()
            order = Order.objects.create(
                user=request.user, ordered_date=ordered_date)
            order.items.add(order_item)
        
            messages.info(request, "This item was added to your cart.")
            return redirect("home:cart")
        else:
            messages.info(request,"Out of Stock")
            return HttpResponse("Out of stock")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            shop_cart = ShopCart.objects.filter(
                 user=request.user,
                 ordered=False
                )[0]
            item.quantity = item.quantity + order_item.quantity
            item.save()
            order.items.remove(order_item)
            order.items.remove(shop_cart)
            order_item.delete()
            shop_cart.delete()
            messages.info(request, "This item was removed from your cart.")
            return redirect("home:cart")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("home:shop", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("home:shop", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            shop_cart = ShopCart.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
                shop_cart.quantity -=1
                shop_cart.save()
                item.quantity= item.quantity + 1
                item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("home:cart")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("home:shop", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("home:shop", slug=slug)

@login_required
def profile(request):
    categorys = Category.objects.all()[:5]
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST,instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                    request.FILES,
                                    instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request,f'Your account has been updated!')
            return redirect('home:profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form' : u_form,
        'p_form' : p_form,
        'categorys' : categorys

    }

    return render(request, 'profile.html', context)


def aboutus(request):
    setting = Setting.objects.get(pk=1)
    categorys = Category.objects.all()[:5]
    context = {'setting':setting, 'categorys':categorys}
    return render(request, 'aboutus.html', context)

@login_required
def Maintain(request):
    instance = request.user
    print(instance)
    if request.method == 'POST':
        mform = ComputerMaintainanceForm(request.POST,instance)
        if mform.is_valid():
            data = Maintaince()
            email = request.POST['email']
            data.email = email
            phone = request.POST['phone']
            data.phone = phone
            problem = request.POST['problem']          
            data.problem = problem 
            current_user= request.user
            data.user= current_user
            data.save()
            return redirect('home:maintain')
    else:
        mform = ComputerMaintainanceForm(instance=request.user)
    template_name = 'maintance.html'
    context = {'mform' : mform}
    return render(request, template_name, context)


class OrderSummaryView(LoginRequiredMixin,View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            categorys = Category.objects.all()[:5]
            context = {
                'object': order,
                'categorys': categorys
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")