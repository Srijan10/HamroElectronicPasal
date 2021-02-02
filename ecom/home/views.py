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
from home.models import Item,Slider,Brand, OrderItem , Order,Category, Address,Coupon,Payment,Refund, Comment,Setting,Maintaince
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
        context['indexsale'] = Item.objects.filter(status = 'sale')[:3]
        context['indexrecent'] = Item.objects.filter(status = 'recent')[:3]
        context['indexnew'] = Item.objects.filter(status = 'new')[:3]
        context['indexdefault'] = Item.objects.filter(status = 'default')[:3]
        context['brands'] = Brand.objects.all()
        context['categorys']= Category.objects.all()[:5]
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



class CheckoutView(EcomMixin, CreateView):
    template_name = "checkout.html"
    form_class = CheckoutForm
    success_url = reverse_lazy("home:index")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.customer:
            pass
        else:
            return redirect('login')
        
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
        else:
            cart_obj = None
        context['cart'] = cart_obj
        context['object_list'] = Item.objects.all()
        return context

    def form_valid(self, form):
        cart_id = self.request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            form.instance.cart = cart_obj
            form.instance.subtotal = cart_obj.total
            form.instance.discout = 0
            form.instance.total = cart_obj.total
            form.instance.order_status = "Order Received"
            del self.request.session['cart_id']

        else:
            return redirect("home:index")


        return super().form_valid(form)



class ProductBaseView(BaseNavView):
    model = Item
    template_name = "shop.html"

    def get(self,request):
        self.template_context['items']=Item.objects.all()
        self.template_context['categorys']=Category.objects.all()[:5]
        return render(self.request,'shop.html',self.template_context)


class CartBaseView(LoginRequiredMixin, View):
    categorys = Category.objects.all()[:5]
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)

            context = {
                'object': order,
                'categorys' : categorys
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

@login_required
def add_to_cart(request, slug):
    
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if item.quantity >= 1:
            if order.items.filter(item__slug=item.slug).exists():

                order_item.quantity += 1
                item.quantity = item.quantity - 1
                item.save()
                order_item.save()
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
            item.quantity = item.quantity + order_item.quantity
            item.save()
            order.items.remove(order_item)
            order_item.delete()
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
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("home:shop")
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

def ComputerMaintainance(request):
    if request.method == 'POST':
        if form.is_valid():
            return HttpResponse('/The Maintaince Form was sent./')
    else:
        form = ComputerMaintainanceForm()

    return render(request, 'maintance.html',{'form':form})


def aboutus(request):
    setting = Setting.objects.get(pk=1)
    categorys = Category.objects.all()[:5]
    context = {'setting':setting, 'categorys':categorys}
    return render(request, 'aboutus.html', context)

@login_required
def Maintain(request):
    mform = ComputerMaintainanceForm()
    if request.method == 'POST':
        mform = ComputerMaintainanceForm(request.POST)
        if mform.is_valid():
            mform.save()

    template_name = 'maintance.html'
    context = {'mform' : mform}
    return render(request, template_name, context)