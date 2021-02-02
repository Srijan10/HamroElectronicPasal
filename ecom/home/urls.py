from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import (
    register,
    HomeBaseView,
    ProductBaseView,
    CartBaseView,
    CheckoutView,
    ItemDetailView,
    CategoryListView,
    CategoryView,
    search,
    add_to_cart,
    remove_from_cart,
    remove_single_item_from_cart,
    profile,
    addcomment,
    addRiview,
    aboutus,
    Maintain,
    )
app_name = 'home'

urlpatterns = [
    
    path('',HomeBaseView.as_view(),name='home'),
    path('register/',register,name= 'register'),
    path('products/',ProductBaseView.as_view(),name = 'products'),
    path('single-product/<slug>/',ItemDetailView.as_view(),name = 'single-product'),
    path('category/',CategoryView.as_view(),name='category'),
    path('category/<category>/',CategoryListView.as_view(),name='category-list'),
    path('cart/',CartBaseView.as_view(), name = 'cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('add-to-cart/<slug>/',add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('search',search, name='search'),
    path('profile/',profile,name="profile"),
    path('login/', auth_views.LoginView.as_view(template_name='home/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='home/logout.html'), name='logout'),
    path('password-reset/',auth_views.PasswordResetView.as_view(
             template_name='home/password_reset.html'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='home/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='home/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='home/password_reset_complete.html'
         ),
         name='password_reset_complete'),
    path('addcomment/<int:id>', addcomment,name='addcomment'),
    
    path('addRiview/', addRiview,name='addRiview'),
    path('aboutus/',aboutus, name='aboutus'),
    path('maintain/',Maintain,name='maintain'),
   
]