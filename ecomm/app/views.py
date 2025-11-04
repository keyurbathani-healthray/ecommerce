from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import OrderPlaced, Payment, Product, Customer, cart , get_object_or_404
from django.views import View
from .forms import CustomerProfileForm, CustomerRegistrationForm, CustomerLoginForm, CustomPasswordChangeForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
# from django.views.decorators.csrf import csrf_protect
# from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import razorpay
from django.conf import settings


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
            messages.error(request, 'Please correct the errors above.')
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



class customer_profile(View):
    def get(self, request):
        form = CustomerProfileForm()
        return render(request, 'app/customerprofile.html', locals())
    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
           customer = form.save(commit=False)
           customer.user = request.user
           customer.save()
           messages.success(request, '🎉 Profile updated successfully!')
           return redirect('customer-profile')
        else :
            messages.warning(request, '⚠️ Please correct the errors above.')
        return render(request, 'app/customerprofile.html', locals())

def customer_address(request):
    add = Customer.objects.filter(user=request.user)
    return render(request, 'app/customeraddress.html', locals())


class update_address(View):
    def get(self, request, pk):
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)
        return render(request, 'app/updateaddress.html', locals())
    def post(self, request, pk):
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(request.POST,instance=add)
        if form.is_valid():
            form.save()
            messages.success(request, '🎉 Address updated successfully!')
            return redirect('customer-address')
        else :
            messages.warning(request, '⚠️ Please correct the errors above.')
        return render(request, 'app/updateaddress.html', locals())
    


def delete_address(request, pk):
      if request.method == 'POST':
        address_to_delete = Customer.objects.get(pk=pk)
        address_to_delete.delete()
        # Redirect back to the address list page
        return redirect('customer-address')
    
    # If it's a GET request, just redirect back.
    # This prevents users from visiting the delete URL directly.
    #   return redirect('customer-address')



# ✅ Logout View
def customer_logout(request):
    logout(request)
    # messages.success(request, '👋 You have been logged out successfully.')
    # Redirect to the named home URL after logout
    return redirect('home')  # Redirect to home after logout



def add_to_cart(request, pk):
    user = request.user
    product = get_object_or_404(Product, pk=pk)

    # Check if the item is already in the cart
    # This is the most important change
    cart_item, created = cart.objects.get_or_create(user=user, product=product)

    if not created:
        # If it's not created, it already exists, so just increase quantity
        cart_item.quantity += 1
        cart_item.save()
         # If it was 'created', the quantity defaults to 1 (from the model)
         # So, we don't need to do anything else.
    return redirect("/cart")

def show_cart(request):
    user = request.user
    cart_items = cart.objects.filter(user=user)
    amount = 0
    shipping_amount = 40
    for p in cart_items:
        # value = p.quantity * p.product.discounted_price
        amount = amount + p.total_cost
    totalamount = amount + shipping_amount
    return render(request, 'app/addtocart.html', locals())


def checkout(request):
    user = request.user
    add = Customer.objects.filter(user=user)
    cart_items = cart.objects.filter(user=user)
    amount = 0
    shipping_amount = 40
    totalamount = 0
    order_id = None
    razoramount = 0
    
    for p in cart_items:
        amount += p.total_cost
    totalamount = amount + shipping_amount
    razoramount = int(totalamount * 100)  # Razorpay amount should be in paise
    
    # Only create Razorpay order when form is submitted (POST request)
    if request.method == 'POST':
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        data = {
            "amount": razoramount,
            "currency": "INR",
            "receipt": "order_rcptid_12"
        }
        payment_response = client.order.create(data=data)
        print(payment_response)
        order_id = payment_response['id']
        order_status = payment_response['status']
        if order_status == 'created':
            payment = Payment(
                user=user,
                amount=totalamount,
                razorpay_order_id=order_id,
                razorpay_payment_status=order_status
            )
            payment.save()
        # Return the order details as JSON for AJAX request
        return JsonResponse({
            'order_id': order_id,
            'razorpay_key': settings.RAZOR_KEY_ID,
            'amount': razoramount,
            'user_name': user.get_full_name() or user.username,
            'user_email': user.email,
        })
    
    return render(request, 'app/checkout.html', locals())

def payment_done(request):
    user = request.user
    cust_id = request.GET.get('cust_id')
    order_id = request.GET.get('order_id')
    payment_id = request.GET.get('payment_id')
    
    # Validate inputs
    if not cust_id or not order_id or not payment_id:
        messages.error(request, 'Invalid payment data received.')
        return redirect('checkout')
    
    try:
        customer = Customer.objects.get(id=cust_id)
    except Customer.DoesNotExist:
        messages.error(request, 'Customer address not found.')
        return redirect('checkout')
    
    try:
        payment = Payment.objects.get(razorpay_order_id=order_id)
    except Payment.DoesNotExist:
        messages.error(request, f'Payment record not found for order: {order_id}')
        return redirect('checkout')
    
    payment.razorpay_payment_id = payment_id
    payment.razorpay_payment_status = 'paid'
    payment.paid = True
    payment.save()
    
    cart_items = cart.objects.filter(user=user)
    for c in cart_items:
        OrderPlaced(
            user=user,
            customer=customer,
            product=c.product,
            quantity=c.quantity,
            payment=payment
        ).save()
        c.delete()
    
    messages.success(request, 'Payment successful! Your order has been placed.')
    return redirect('orders')

def orders(request):
    # op = OrderPlaced.objects.filter(user=request.user)
    return render(request, 'app/orders.html')

def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']    
        c = cart.objects.get(Q(id=prod_id) & Q(user=request.user))
        c.quantity += 1
        c.save()
        amount = 0
        shipping_amount = 40
        cart_items = cart.objects.filter(user=request.user)
        for p in cart_items:
            amount += p.total_cost
        totalamount = amount + shipping_amount
        data = {
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': totalamount
        }
        return JsonResponse(data)
    
def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = cart.objects.get(Q(id=prod_id) & Q(user=request.user))
        c.quantity -= 1
        c.save()
        amount = 0
        shipping_amount = 40
        cart_items = cart.objects.filter(user=request.user)
        for p in cart_items:
            amount += p.total_cost
        totalamount = amount + shipping_amount
        data = {
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': totalamount
        }
        return JsonResponse(data)
    
def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = cart.objects.get(Q(id=prod_id) & Q(user=request.user))
        c.delete()
        amount = 0
        shipping_amount = 40
        cart_items = cart.objects.filter(user=request.user)
        for p in cart_items:
            amount += p.total_cost
        totalamount = amount + shipping_amount
        data = {
            'amount': amount,
            'totalamount': totalamount
        }
        return JsonResponse(data)