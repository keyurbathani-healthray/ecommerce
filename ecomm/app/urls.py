
from django.urls import path
from . import views

urlpatterns = [
   path('', views.home, name='home'),
   path('aboutus/', views.aboutus, name='aboutus'),
   path('contactus/', views.contactus, name='contactus'),
   path('category/<slug:val>/', views.CategoryView.as_view(), name='category'),
   path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_details'),
   path('category-title/<val>/', views.CategoryTitleView.as_view(), name='category-title'),


   # Authentication URLs
   path('register/', views.customer_registration, name='customer-registration'),
   path('login/', views.customer_login, name='customer-login'),
   path('logout/', views.customer_logout, name='customer-logout'),
   ]  
