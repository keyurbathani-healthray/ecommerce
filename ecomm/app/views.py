from django.shortcuts import render, redirect
from .models import Product
from django.views import View
from .forms import CustomerRegistrationForm, CustomerLoginForm, CustomPasswordChangeForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            # Update the session to prevent logging out the user
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomPasswordChangeForm(user=request.user)
    return render(request, 'app/changepassword.html', {'form': form})

def home(request):
    return render(request, 'app/home.html')

def aboutus(request):
    return render(request, 'app/aboutus.html')

def contactus(request):
    return render(request, 'app/contactus.html')



class CategoryView(View): 
    def get(self, request, val):
        product = Product.objects.filter(category=val)
        title = Product.objects.filter(category=val).values('title')
        return render(request, 'app/category.html', locals())
    

class CategoryTitleView(View):
    def get(self, request, val):
        product = Product.objects.filter(title=val)
        title = Product.objects.filter(category=product[0].category).values('title')
        return render(request, 'app/category.html', locals())


class ProductDetailView(View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        return render(request, 'app/product_details.html', locals())
    

# ✅ Registration View
def customer_registration(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '🎉 Registration successful! You can now log in.')
            # Redirect to the named login URL after successful registration
            return redirect('customer-login')
        else:
            messages.error(request, '⚠️ Please correct the errors below and try again.')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'app/customerregistration.html', {'form': form})


# ✅ Login View
def customer_login(request):
    if request.method == 'POST':
        form = CustomerLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'👋 Welcome back, {user.first_name or user.username}!')
                # Redirect to the named home URL after successful login
                return redirect('home')
            else:
                messages.error(request, '❌ Invalid credentials, please try again.')
        else:
            messages.error(request, '⚠️ Please correct the errors below.')
    else:
        form = CustomerLoginForm()
    return render(request, 'app/customerlogin.html', {'form': form})


# ✅ Logout View
def customer_logout(request):
    logout(request)
    # messages.success(request, '👋 You have been logged out successfully.')
    # Redirect to the named home URL after logout
    return redirect('home')  # Redirect to home after logout
