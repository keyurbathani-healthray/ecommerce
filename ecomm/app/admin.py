from django.contrib import admin
from .models import Customer, Payment, Product, cart, OrderPlaced, whishlist, Invoice

# Register your models here.

@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ['id','title','discounted_price','category','product_image'] 

@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display = ['id','name','locality','city','mobile','zipcode','state']


@admin.register(cart)
class CartModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','product','quantity']


@admin.register(OrderPlaced)
class OrderPlacedModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','customer','product','quantity','ordered_date','status']

@admin.register(Payment)
class PaymentModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','amount','razorpay_order_id','razorpay_payment_status','razorpay_payment_id','paid']

@admin.register(whishlist)
class WishlistModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','product']

@admin.register(Invoice)
class InvoiceModelAdmin(admin.ModelAdmin):
    list_display = ['id','invoice_number','order','customer','total_amount','invoice_date','is_generated']
    list_filter = ['invoice_date','is_generated']
    search_fields = ['invoice_number','customer__name','delivery_mobile']
    readonly_fields = ['invoice_number','invoice_date']