
from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from . import views

urlpatterns = [
   path('', views.home, name='home'),
   path('aboutus/', views.aboutus, name='aboutus'),
   path('contactus/', views.contactus, name='contactus'),
   path('category/<slug:val>/', views.CategoryView.as_view(), name='category'),
   path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_details'),
   path('category-title/<val>/', views.CategoryTitleView.as_view(), name='category-title'),
   path('profile/', views.customer_profile.as_view(), name='customer-profile'),
   path('address/', views.customer_address, name='customer-address'),
   path('updateaddress/<int:pk>/', views.update_address.as_view(), name='update-address'),
   path('delete-address/<int:pk>/', views.delete_address, name='delete-address'),
   path('add-to-cart/<int:pk>/', views.add_to_cart, name='add-to-cart'),
   path('buy-now/<int:pk>/', views.buy_now, name='buy-now'),
   path('cart/', views.show_cart, name='show-cart'),
   path('checkout/', views.checkout, name='checkout'),
   path('paymentdone/', views.payment_done, name='paymentdone'),
   path('orders/', views.orders, name='orders'),


   path('pluscart/', views.plus_cart, name='pluscart'),
   path('minuscart/', views.minus_cart, name='minuscart'),
   path('removecart/', views.remove_cart, name='removecart'),

   # Wishlist URLs
   path('wishlist/', views.show_wishlist, name='show-wishlist'),
   path('add-to-wishlist/<int:pk>/', views.add_to_wishlist, name='add-to-wishlist'),
   path('remove-from-wishlist/<int:pk>/', views.remove_from_wishlist, name='remove-from-wishlist'),
   path('pluswishlist/', views.plus_wishlist, name='pluswishlist'),
   path('minuswishlist/', views.minus_wishlist, name='minuswishlist'),


   # Authentication URLs
   path('register/', views.customer_registration, name='customer-registration'),
   path('login/', views.customer_login, name='customer-login'),
   path('logout/', views.customer_logout, name='customer-logout'),
   path('change-password/', views.change_password, name='change-password'),
   
   # Password Reset URLs
   path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='app/password_reset.html'), name='password_reset'),
   path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='app/password_reset_done.html'), name='password_reset_done'),
   path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='app/password_reset_confirm.html'), name='password_reset_confirm'),
   path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='app/password_reset_complete.html'), name='password_reset_complete'),


   ]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


admin.site.site_header = "Neel Dairy Admin"
admin.site.site_title = "Neel Dairy"
admin.site.index_title = "Welcome to Neel Dairy"
