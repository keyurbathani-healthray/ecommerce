
from django.urls import path
from . import views

urlpatterns = [
   path('', views.home, name='home'),
   path('category/<slug:val>/', views.CategoryView.as_view(), name='category'),
   path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_details'),

   ]  
