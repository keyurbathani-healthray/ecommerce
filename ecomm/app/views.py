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
    # STEP 1: Check if user is authenticated before proceeding to checkout
    if not request.user.is_authenticated:
        messages.warning(request, 'Please log in to proceed with checkout.')
        return redirect('customer-login')
    
    # STEP 2: Get user and fetch their saved addresses
    user = request.user
    add = Customer.objects.filter(user=user)  # Get all addresses saved by this user
    
    # STEP 3: Calculate total cart amount
    cart_items = cart.objects.filter(user=user)  # Get all items in user's cart
    amount = 0
    shipping_amount = 40  # Fixed shipping charge
    for p in cart_items:
        amount += p.total_cost  # Calculate total cost of all products
    totalamount = amount + shipping_amount  # Add shipping to get final amount
    
    # STEP 4: Convert amount to paise (Razorpay requires amount in smallest currency unit)
    razoramount = int(totalamount * 100)  # ₹256 = 25600 paise
    
    # STEP 5: Initialize Razorpay client with API credentials
    client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
    
    # STEP 6: Prepare order data for Razorpay
    data = {
        "amount": razoramount,      # Amount in paise
        "currency": "INR",          # Indian Rupees
        "receipt": "order_rcptid_12"  # Internal order reference (can be dynamic)
    }
    
    # STEP 7: Create order on Razorpay server - This generates a unique order_id
    # This must be done BEFORE showing payment modal to user
    payment_response = client.order.create(data=data)
    print(payment_response)
    #  Sample response from Razorpay:
    # {'amount': 25600, 'amount_due': 25600, 'amount_paid': 0, 'attempts': 0, 
    #  'created_at': 1762246256, 'currency': 'INR', 'entity': 'order', 
    #  'id': 'order_RbbSoOOag4InGB', 'notes': [], 'offer_id': None, 
    #  'receipt': 'order_rcptid_12', 'status': 'created'}
    
    # STEP 8: Extract order_id and status from Razorpay response
    order_id = payment_response['id']  # Unique order ID from Razorpay (e.g., 'order_RbbSoOOag4InGB')
    order_status = payment_response['status']  # Should be 'created'
    
    # STEP 9: Save Payment record in OUR database for tracking
    # This links the Razorpay order_id with our user and amount
    if order_status == 'created':
        payment = Payment(
            user=user,                          # User who is making payment
            amount=totalamount,                 # Total amount (₹256)
            razorpay_order_id=order_id,        # Store Razorpay's order_id for later matching
            razorpay_payment_status=order_status  # Status: 'created' (will be updated to 'paid' later)
        )
        payment.save()  # Save to database
    
    # STEP 10: Render checkout page with all variables
    # The order_id and razoramount will be used in JavaScript to open Razorpay modal
    return render(request, 'app/checkout.html', locals())

def payment_done(request):
    # STEP 11: Extract payment details from URL parameters sent by Razorpay
    # After successful payment, Razorpay redirects here with these parameters
    cust_id = request.GET.get('cust_id')      # Customer address ID selected by user
    order_id = request.GET.get('order_id')    # Razorpay order_id (e.g., 'order_RbbSoOOag4InGB')
    payment_id = request.GET.get('payment_id')  # Razorpay payment_id (e.g., 'pay_RbcZ8PhVlUEuka')
    
    # STEP 12: Validate that all required parameters are present
    if not cust_id or not order_id or not payment_id:
        messages.error(request, 'Invalid payment information.')
        return redirect('checkout')
    
    try:
        # STEP 13: Find the Payment record we created earlier using order_id
        # This matches the Razorpay order_id with our database record
        payment = Payment.objects.get(razorpay_order_id=order_id)
        
        # STEP 14: Get the user from Payment record (not from request)
        # This ensures we're processing payment for the correct user
        # Important: request.user might be AnonymousUser if session expired
        user = payment.user  # Get the actual user who created this payment
        
        # STEP 15: Validate that the customer address belongs to this user
        # Security check to prevent unauthorized address access
        customer = Customer.objects.get(id=cust_id, user=user)
        
        # STEP 16: Update payment status to PAID in our database
        payment.razorpay_payment_id = payment_id  # Store Razorpay's payment_id
        payment.razorpay_payment_status = 'paid'  # Update status from 'created' to 'paid'
        payment.paid = True  # Mark payment as completed
        payment.save()  # Save changes to database
        
        # STEP 17: Process cart items and create OrderPlaced records
        cart_items = cart.objects.filter(user=user)  # Get all items in user's cart
        
        # STEP 18: Create individual OrderPlaced record for each cart item
        for c in cart_items:
            OrderPlaced(
                user=user,              # User who placed the order
                customer=customer,      # Delivery address
                product=c.product,      # Product ordered
                quantity=c.quantity,    # Quantity ordered
                payment=payment         # Link to Payment record
            ).save()  # Save order to database
            
            # STEP 19: Delete item from cart after order is placed
            c.delete()  # Remove from cart
        
        # STEP 20: Show success message and redirect to orders page
        messages.success(request, 'Payment successful! Your order has been placed.')
        return redirect('orders')  # Redirect to view all orders
        
    # STEP 21: Handle errors gracefully
    except Payment.DoesNotExist:
        messages.error(request, 'Payment record not found.')
        return redirect('checkout')
    except Customer.DoesNotExist:
        messages.error(request, 'Invalid customer address.')
        return redirect('checkout')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('checkout')

def orders(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Please log in to view your orders.')
        return redirect('customer-login')
    op = OrderPlaced.objects.filter(user=request.user)
    return render(request, 'app/orders.html', locals())

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
        if c.quantity > 1:
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