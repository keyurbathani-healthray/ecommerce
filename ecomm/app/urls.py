
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
   path('', views.home, name='home'),
   path('aboutus/', views.aboutus, name='aboutus'),
   path('contactus/', views.contactus, name='contactus'),
   path('category/<slug:val>/', views.CategoryView.as_view(), name='category'),
   path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_details'),
   path('category-title/<val>/', views.CategoryTitleView.as_view(), name='category-title'),
   path('profile/', views.customer_profile.as_view(), name='customer-profile'),
#    path('address/', views.customer_address.as_view(), name='customer-address'),



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
   ]  
