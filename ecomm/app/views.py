from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from .models import OrderPlaced, Payment, Product, Customer, cart, whishlist, Invoice, get_object_or_404
from django.views import View
from .forms import CustomerProfileForm, CustomerRegistrationForm, CustomerLoginForm, CustomPasswordChangeForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
# from django.views.decorators.csrf import csrf_protect
# from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
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
        # Check if product is in user's wishlist
        in_wishlist = False
        if request.user.is_authenticated:
            in_wishlist = whishlist.objects.filter(user=request.user, product=product).exists()
        return render(request, 'app/product_details.html', {'product': product, 'in_wishlist': in_wishlist})
    

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

def buy_now(request, pk):
    # Check if user is authenticated
    if not request.user.is_authenticated:
        messages.warning(request, 'Please log in to continue.')
        return redirect('customer-login')
    
    # Store product ID and quantity in session for buy now checkout
    request.session['buy_now_product_id'] = pk
    request.session['buy_now_quantity'] = 1  # Default quantity is 1
    
    # Redirect to checkout
    return redirect('checkout')

def show_cart(request):
    user = request.user
    cart_items = cart.objects.filter(user=user)
    amount = 0
    
    for p in cart_items:
        amount = amount + p.total_cost
    
    # Calculate GST (5% SGST + 5% CGST = 10% total GST)
    sgst = amount * 0.05  # 5% SGST
    cgst = amount * 0.05  # 5% CGST
    total_gst = sgst + cgst
    
    # Apply shipping charge logic: Free shipping for orders ≥ ₹500
    if amount >= 500:
        shipping_amount = 0
    else:
        shipping_amount = 40
    
    totalamount = amount + total_gst + shipping_amount
    return render(request, 'app/addtocart.html', locals())



def checkout(request):
    # STEP 1: Check if user is authenticated before proceeding to checkout
    if not request.user.is_authenticated:
        messages.warning(request, 'Please log in to proceed with checkout.')
        return redirect('customer-login')
    
    # STEP 2: Get user and fetch their saved addresses
    user = request.user
    add = Customer.objects.filter(user=user)  # Get all addresses saved by this user
    
    # STEP 3: Check if user explicitly came from cart (has ?from=cart parameter)
    from_cart = request.GET.get('from') == 'cart'
    
    # STEP 4: If coming from cart, clear any buy_now session data
    if from_cart:
        if 'buy_now_product_id' in request.session:
            del request.session['buy_now_product_id']
        if 'buy_now_quantity' in request.session:
            del request.session['buy_now_quantity']
    
    # STEP 5: Check if this is a "Buy Now" checkout or regular cart checkout
    buy_now_product_id = request.session.get('buy_now_product_id')
    buy_now_quantity = request.session.get('buy_now_quantity', 1)
    
    # STEP 6: Calculate total amount based on checkout type
    amount = 0
    
    if buy_now_product_id:
        # Buy Now checkout - single product
        try:
            product = Product.objects.get(pk=buy_now_product_id)
            amount = product.discounted_price * buy_now_quantity
            # Create a temporary cart_items list for template rendering
            class BuyNowItem:
                def __init__(self, product, quantity):
                    self.product = product
                    self.quantity = quantity
                    self.total_cost = product.discounted_price * quantity
            
            cart_items = [BuyNowItem(product, buy_now_quantity)]
            is_buy_now = True
        except Product.DoesNotExist:
            messages.error(request, 'Product not found.')
            # Clear invalid session data
            if 'buy_now_product_id' in request.session:
                del request.session['buy_now_product_id']
            if 'buy_now_quantity' in request.session:
                del request.session['buy_now_quantity']
            return redirect('home')
    else:
        # Regular cart checkout
        cart_items = cart.objects.filter(user=user)
        if not cart_items:
            messages.warning(request, 'Your cart is empty.')
            return redirect('show-cart')
        for p in cart_items:
            amount += p.total_cost  # Calculate total cost of all products
        is_buy_now = False
    
    # Calculate GST (5% SGST + 5% CGST = 10% total GST)
    sgst = amount * 0.05  # 5% SGST
    cgst = amount * 0.05  # 5% CGST
    total_gst = sgst + cgst
    
    # Apply shipping charge logic: Free shipping for orders ≥ ₹500
    if amount >= 500:
        shipping_amount = 0
    else:
        shipping_amount = 40
    
    totalamount = amount + total_gst + shipping_amount  # Add GST and shipping to get final amount
    
    # STEP 7: Convert amount to paise (Razorpay requires amount in smallest currency unit)
    razoramount = int(totalamount * 100)  # ₹256 = 25600 paise
    
    # STEP 8: Initialize Razorpay client with API credentials
    client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
    
    # STEP 9: Prepare order data for Razorpay
    data = {
        "amount": razoramount,      # Amount in paise
        "currency": "INR",          # Indian Rupees
        "receipt": "order_rcptid_12"  # Internal order reference (can be dynamic)
    }
    
    # STEP 8: Create order on Razorpay server - This generates a unique order_id
    # This must be done BEFORE showing payment modal to user
    payment_response = client.order.create(data=data)
    print(payment_response)
    #  Sample response from Razorpay:
    # {'amount': 25600, 'amount_due': 25600, 'amount_paid': 0, 'attempts': 0, 
    #  'created_at': 1762246256, 'currency': 'INR', 'entity': 'order', 
    #  'id': 'order_RbbSoOOag4InGB', 'notes': [], 'offer_id': None, 
    #  'receipt': 'order_rcptid_12', 'status': 'created'}
    
    # STEP 9: Extract order_id and status from Razorpay response
    order_id = payment_response['id']  # Unique order ID from Razorpay (e.g., 'order_RbbSoOOag4InGB')
    order_status = payment_response['status']  # Should be 'created'
    
    # STEP 10: Save Payment record in OUR database for tracking
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
        
        # STEP 17: Check if this is a Buy Now order or regular cart order
        buy_now_product_id = request.session.get('buy_now_product_id')
        buy_now_quantity = request.session.get('buy_now_quantity', 1)
        
        if buy_now_product_id:
            # Buy Now order - create single OrderPlaced record
            try:
                product = Product.objects.get(pk=buy_now_product_id)
                OrderPlaced(
                    user=user,              # User who placed the order
                    customer=customer,      # Delivery address
                    product=product,        # Product ordered
                    quantity=buy_now_quantity,  # Quantity ordered
                    payment=payment         # Link to Payment record
                ).save()  # Save order to database
                
                # Clear buy now session data
                del request.session['buy_now_product_id']
                if 'buy_now_quantity' in request.session:
                    del request.session['buy_now_quantity']
                
                messages.success(request, 'Payment successful! Your order has been placed.')
                return redirect('orders')
                
            except Product.DoesNotExist:
                messages.error(request, 'Product not found.')
                return redirect('home')
        else:
            # Regular cart checkout - process cart items and create OrderPlaced records
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
        cart_items = cart.objects.filter(user=request.user)
        for p in cart_items:
            amount += p.total_cost
        
        # Calculate GST (5% SGST + 5% CGST = 10% total GST)
        sgst = amount * 0.05  # 5% SGST
        cgst = amount * 0.05  # 5% CGST
        total_gst = sgst + cgst
        
        # Apply shipping charge logic: Free shipping for orders ≥ ₹500
        if amount >= 500:
            shipping_amount = 0
        else:
            shipping_amount = 40
        
        totalamount = amount + total_gst + shipping_amount
        cart_count = cart_items.count()
        data = {
            'quantity': c.quantity,
            'amount': amount,
            'sgst': sgst,
            'cgst': cgst,
            'totalamount': totalamount,
            'shipping_amount': shipping_amount,
            'cart_count': cart_count
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
        cart_items = cart.objects.filter(user=request.user)
        for p in cart_items:
            amount += p.total_cost
        
        # Calculate GST (5% SGST + 5% CGST = 10% total GST)
        sgst = amount * 0.05  # 5% SGST
        cgst = amount * 0.05  # 5% CGST
        total_gst = sgst + cgst
        
        # Apply shipping charge logic: Free shipping for orders ≥ ₹500
        if amount >= 500:
            shipping_amount = 0
        else:
            shipping_amount = 40
        
        totalamount = amount + total_gst + shipping_amount
        cart_count = cart_items.count()
        data = {
            'quantity': c.quantity,
            'amount': amount,
            'sgst': sgst,
            'cgst': cgst,
            'totalamount': totalamount,
            'shipping_amount': shipping_amount,
            'cart_count': cart_count
        }
        return JsonResponse(data)
    
def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = cart.objects.get(Q(id=prod_id) & Q(user=request.user))
        c.delete()
        amount = 0
        cart_items = cart.objects.filter(user=request.user)
        for p in cart_items:
            amount += p.total_cost
        
        # Calculate GST (5% SGST + 5% CGST = 10% total GST)
        sgst = amount * 0.05  # 5% SGST
        cgst = amount * 0.05  # 5% CGST
        total_gst = sgst + cgst
        
        # Apply shipping charge logic: Free shipping for orders ≥ ₹500
        if amount >= 500:
            shipping_amount = 0
        else:
            shipping_amount = 40
        
        totalamount = amount + total_gst + shipping_amount
        cart_count = cart_items.count()
        data = {
            'amount': amount,
            'sgst': sgst,
            'cgst': cgst,
            'totalamount': totalamount,
            'shipping_amount': shipping_amount,
            'cart_count': cart_count
        }
        return JsonResponse(data)

# Wishlist Views
def add_to_wishlist(request, pk):
    if not request.user.is_authenticated:
        messages.warning(request, 'Please log in to add items to wishlist.')
        return redirect('customer-login')
    
    user = request.user
    product = get_object_or_404(Product, pk=pk)
    
    # Check if item already exists in wishlist
    wishlist_item, created = whishlist.objects.get_or_create(user=user, product=product)
    
    if created:
        messages.success(request, f'{product.title} added to your wishlist!')
    else:
        messages.info(request, f'{product.title} is already in your wishlist.')
    
    return redirect('product_details', pk=pk)

def show_wishlist(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Please log in to view your wishlist.')
        return redirect('customer-login')
    
    user = request.user
    wishlist_items = whishlist.objects.filter(user=user)
    return render(request, 'app/wishlist.html', {'wishlist_items': wishlist_items})

def remove_from_wishlist(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Please log in'})
    
    try:
        wishlist_item = whishlist.objects.get(Q(id=pk) & Q(user=request.user))
        wishlist_item.delete()
        wishlist_count = whishlist.objects.filter(user=request.user).count()
        return JsonResponse({
            'success': True,
            'message': 'Item removed from wishlist',
            'wishlist_count': wishlist_count
        })
    except whishlist.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Item not found'})

def plus_wishlist(request):
    if request.method == 'GET':
        prod_id = request.GET.get('prod_id')
        user = request.user
        product = get_object_or_404(Product, id=prod_id)
        
        # Add to wishlist
        wishlist_item, created = whishlist.objects.get_or_create(user=user, product=product)
        wishlist_count = whishlist.objects.filter(user=user).count()
        
        return JsonResponse({
            'message': 'Added to wishlist' if created else 'Already in wishlist',
            'wishlist_count': wishlist_count
        })

def minus_wishlist(request):
    if request.method == 'GET':
        prod_id = request.GET.get('prod_id')
        try:
            wishlist_item = whishlist.objects.get(Q(product__id=prod_id) & Q(user=request.user))
            wishlist_item.delete()
            wishlist_count = whishlist.objects.filter(user=request.user).count()
            return JsonResponse({
                'message': 'Removed from wishlist',
                'wishlist_count': wishlist_count
            })
        except whishlist.DoesNotExist:
            wishlist_count = whishlist.objects.filter(user=request.user).count()
            return JsonResponse({
                'message': 'Item not in wishlist',
                'wishlist_count': wishlist_count
            })


# Search Results Page View
def search_results(request):
    """
    Display search results page.
    Searches products by title and category only.
    Redirects to home if no query provided.
    """
    query = request.GET.get('q', '').strip()
    
    # Redirect to home page if search query is empty
    if not query:
        return redirect('home')
    
    # Search only in title and category (not description)
    products = Product.objects.filter(
        Q(title__icontains=query) |
        Q(category__icontains=query)
    )
    
    return render(request, 'app/search_results.html', {
        'products': products,
        'query': query
    })


@login_required
def generate_invoice(request, order_id):
    """
    Generate or retrieve invoice for a delivered order.
    Creates invoice in database if doesn't exist.
    """
    try:
        # Get the order
        order = OrderPlaced.objects.get(id=order_id, user=request.user)
        
        # Check if order is delivered
        if order.status != 'Delivered':
            messages.warning(request, 'Invoice can only be generated for delivered orders.')
            return redirect('orders')
        
        # Check if invoice already exists
        invoice = Invoice.objects.filter(order=order).first()
        
        if not invoice:
            # Calculate amounts
            subtotal = order.quantity * order.product.discounted_price
            sgst = round(subtotal * 0.05, 2)
            cgst = round(subtotal * 0.05, 2)
            
            # Determine shipping charge (free if subtotal >= 500)
            shipping_charge = 0 if subtotal >= 500 else 40
            
            total_amount = subtotal + sgst + cgst + shipping_charge
            
            # Create new invoice
            invoice = Invoice.objects.create(
                order=order,
                user=request.user,
                customer=order.customer,
                payment=order.payment,
                
                # Product details
                product_title=order.product.title,
                product_quantity=order.quantity,
                product_price=order.product.discounted_price,
                
                # Payment summary
                subtotal=subtotal,
                sgst=sgst,
                cgst=cgst,
                shipping_charge=shipping_charge,
                total_amount=total_amount,
                
                # Delivery address
                delivery_name=order.customer.name,
                delivery_mobile=order.customer.mobile,
                delivery_locality=order.customer.locality,
                delivery_city=order.customer.city,
                delivery_state=order.customer.state,
                delivery_zipcode=order.customer.zipcode,
                
                # Payment details
                payment_method='Online Payment (Razorpay)',
                razorpay_payment_id=order.payment.razorpay_payment_id,
            )
            
            messages.success(request, f'Invoice {invoice.invoice_number} generated successfully!')
        
        # Redirect to view invoice
        return redirect('view-invoice', invoice_id=invoice.id)
        
    except OrderPlaced.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('orders')
    except Exception as e:
        messages.error(request, f'Error generating invoice: {str(e)}')
        return redirect('orders')


@login_required
def view_invoice(request, invoice_id):
    """
    View invoice in browser (HTML format).
    """
    try:
        invoice = Invoice.objects.get(id=invoice_id, user=request.user)
        return render(request, 'app/invoice.html', {'invoice': invoice})
    except Invoice.DoesNotExist:
        messages.error(request, 'Invoice not found.')
        return redirect('orders')


@login_required
def download_invoice(request, invoice_id):
    """
    Download invoice as PDF file using ReportLab.
    """
    try:
        invoice = Invoice.objects.get(id=invoice_id, user=request.user)
        
        # Create a file-like buffer to receive PDF data
        buffer = BytesIO()
        
        # Create the PDF object using the buffer
        pdf = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=72)
        
        # Container for PDF elements
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#198754'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#198754'),
            spaceAfter=12,
        )
        
        normal_style = styles['Normal']
        
        # Company Header
        elements.append(Paragraph("DAIRY PRODUCTS", title_style))
        elements.append(Paragraph("TAX INVOICE", ParagraphStyle(
            'Subtitle', parent=styles['Normal'], fontSize=12, alignment=TA_CENTER, textColor=colors.grey
        )))
        elements.append(Spacer(1, 20))
        
        # Company and Invoice Info Table
        header_data = [
            ['Phone: +91 1234567890', f'Invoice No: {invoice.invoice_number}'],
            ['Email: support@dairy.com', f'Invoice Date: {invoice.invoice_date.strftime("%d %b, %Y")}'],
            ['Website: www.dairy.com', f'Order Date: {invoice.order.ordered_date.strftime("%d %b, %Y")}'],
        ]
        
        header_table = Table(header_data, colWidths=[3*inch, 3*inch])
        header_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 20))
        
        # Bill To Section
        elements.append(Paragraph("BILL TO:", heading_style))
        bill_to_text = f"""
        <b>{invoice.delivery_name}</b><br/>
        {invoice.delivery_locality}<br/>
        {invoice.delivery_city}, {invoice.delivery_state}<br/>
        PIN: {invoice.delivery_zipcode}<br/>
        Mobile: {invoice.delivery_mobile}<br/>
        Email: {invoice.user.email}
        """
        elements.append(Paragraph(bill_to_text, normal_style))
        elements.append(Spacer(1, 20))
        
        # Items Table
        elements.append(Paragraph("ORDER DETAILS:", heading_style))
        items_data = [
            ['Item Description', 'Quantity', 'Unit Price', 'Total'],
            [invoice.product_title, str(invoice.product_quantity), 
             f'₹{invoice.product_price}', f'₹{invoice.subtotal}']
        ]
        
        items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#198754')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(items_table)
        elements.append(Spacer(1, 20))
        
        # Totals Table
        shipping_text = "FREE" if invoice.shipping_charge == 0 else f'₹{invoice.shipping_charge}'
        totals_data = [
            ['Subtotal:', f'₹{invoice.subtotal}'],
            ['SGST (5%):', f'₹{invoice.sgst}'],
            ['CGST (5%):', f'₹{invoice.cgst}'],
            ['Shipping:', shipping_text],
            ['<b>TOTAL AMOUNT:</b>', f'<b>₹{invoice.total_amount}</b>'],
        ]
        
        totals_table = Table(totals_data, colWidths=[4.5*inch, 2*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#198754')),
            ('FONTSIZE', (0, -1), (-1, -1), 14),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#198754')),
        ]))
        elements.append(totals_table)
        elements.append(Spacer(1, 30))
        
        # Payment Information
        elements.append(Paragraph("PAYMENT INFORMATION:", heading_style))
        payment_text = f"""
        Payment Method: {invoice.payment_method}<br/>
        Payment Status: <font color='green'><b>PAID</b></font><br/>
        """
        if invoice.razorpay_payment_id:
            payment_text += f"Transaction ID: {invoice.razorpay_payment_id}<br/>"
        payment_text += f"Payment Date: {invoice.order.ordered_date.strftime('%d %b, %Y %H:%M')}"
        
        elements.append(Paragraph(payment_text, normal_style))
        elements.append(Spacer(1, 30))
        
        # Thank You Message
        thank_you_style = ParagraphStyle(
            'ThankYou',
            parent=styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor('#198754'),
            alignment=TA_CENTER,
            spaceAfter=20,
        )
        elements.append(Paragraph("<b>Thank You for Your Purchase!</b>", thank_you_style))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=TA_CENTER,
        )
        elements.append(Paragraph("This is a computer-generated invoice and does not require a signature.", footer_style))
        elements.append(Paragraph("For any queries, please contact us at support@dairy.com or call +91 1234567890", footer_style))
        elements.append(Paragraph("© 2025 Dairy Products. All rights reserved.", footer_style))
        
        # Build PDF
        pdf.build(elements)
        
        # Get the value of the BytesIO buffer and write it to the response
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Invoice_{invoice.invoice_number}.pdf"'
        
        return response
        
    except Invoice.DoesNotExist:
        messages.error(request, 'Invoice not found.')
        return redirect('orders')
    except Exception as e:
        messages.error(request, f'Error downloading invoice: {str(e)}')
        return redirect('orders')