from django.db import models

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

# Create your models here.

CATEGORY_CHOICES = [
    ('CR','Curd'),
    ('ML','Milk'),
    ('LS','Lassi'),
    ('MS','Milkshake'), 
    ('PN','Paneer'),
    ('GH','Ghee'),
    ('CZ','Cheese'),
    ('IC','Ice-Creams'),
]

STATE_CHOICES = [
    ('Andaman & Nicobar Islands', 'Andaman & Nicobar Islands'),
    ('Andhra Pradesh', 'Andhra Pradesh'),
    ('Arunachal Pradesh', 'Arunachal Pradesh'),
    ('Assam', 'Assam'),
    ('Bihar', 'Bihar'),
    ('Chandigarh', 'Chandigarh'),
    ('Chhattisgarh', 'Chhattisgarh'),
    ('Dadra & Nagar Haveli', 'Dadra & Nagar Haveli'),
    ('Daman & Diu', 'Daman & Diu'),
    ('Delhi', 'Delhi'),
    ('Goa', 'Goa'),
    ('Gujarat', 'Gujarat'),
    ('Haryana', 'Haryana'),
    ('Himachal Pradesh', 'Himachal Pradesh'),
    ('Jammu & Kashmir', 'Jammu & Kashmir'),
    ('Jharkhand', 'Jharkhand'),
    ('Karnataka', 'Karnataka'),
    ('Kerala', 'Kerala'),
    ('Lakshadweep', 'Lakshadweep'),
    ('Madhya Pradesh', 'Madhya Pradesh'),
    ('Maharashtra', 'Maharashtra'),
    ('Manipur', 'Manipur'),
    ('Meghalaya', 'Meghalaya'),
    ('Mizoram', 'Mizoram'),
    ('Nagaland', 'Nagaland'),
    ('Odisha', 'Odisha'),
    ('Puducherry', 'Puducherry'),
    ('Punjab', 'Punjab'),
    ('Rajasthan', 'Rajasthan'),
    ('Sikkim', 'Sikkim'),
    ('Tamil Nadu', 'Tamil Nadu'),
    ('Telangana', 'Telangana'),
    ('Tripura', 'Tripura'),
    ('Uttar Pradesh', 'Uttar Pradesh'),
    ('Uttarakhand', 'Uttarakhand'),
    ('West Bengal', 'West Bengal'),
]


STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Accepted', 'Accepted'),
    ('Packed', 'Packed'),
    ('On The Way', 'On The Way'),
    ('Delivered', 'Delivered'),
    ('Cancelled', 'Cancelled'),
]

class Product(models.Model):
    title = models.CharField(max_length=100)
    selling_price = models.FloatField()
    discounted_price = models.FloatField()
    description = models.TextField()
    composition = models.TextField(default='')
    prodapp = models.TextField(default='')
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    product_image = models.ImageField(upload_to='product')
    
    def __str__(self):
        return self.title
    
class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    locality = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    mobile = models.CharField(max_length=10)
    zipcode = models.CharField(max_length=10)
    state = models.CharField(choices=STATE_CHOICES, max_length=50)
    
    def __str__(self):
        return self.name
    
class cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    @property
    def total_cost(self):
        return self.quantity * self.product.discounted_price
    
    def __str__(self):
        return f"{self.quantity} of {self.product} for {self.user.username}"

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_status = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Payment id {self.id} by {self.user.username}"

class OrderPlaced(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    ordered_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, default="")  

    def __str__(self):
        return f"Order id {self.id} by customer  {self.customer.name}"


    @property
    def total_cost(self):
        return self.quantity * self.product.discounted_price
    

class whishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"Wishlist item {self.id} for {self.user.username}"


class Invoice(models.Model):
    """
    Invoice model to store invoice/bill details for delivered orders
    """
    invoice_number = models.CharField(max_length=100, unique=True)
    order = models.ForeignKey(OrderPlaced, on_delete=models.CASCADE, related_name='invoices')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    
    # Invoice Details
    invoice_date = models.DateTimeField(auto_now_add=True)
    
    # Product Details (stored for record keeping even if product changes)
    product_title = models.CharField(max_length=200)
    product_quantity = models.PositiveIntegerField()
    product_price = models.FloatField()
    
    # Payment Summary
    subtotal = models.FloatField()
    sgst = models.FloatField(default=0)  # 5%
    cgst = models.FloatField(default=0)  # 5%
    shipping_charge = models.FloatField(default=40)
    total_amount = models.FloatField()
    
    # Delivery Address (stored for record keeping)
    delivery_name = models.CharField(max_length=200)
    delivery_mobile = models.CharField(max_length=10)
    delivery_locality = models.CharField(max_length=200)
    delivery_city = models.CharField(max_length=50)
    delivery_state = models.CharField(max_length=50)
    delivery_zipcode = models.CharField(max_length=10)
    
    # Payment Details
    payment_method = models.CharField(max_length=50, default='Online Payment')
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Status
    is_generated = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-invoice_date']
        
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.customer.name}"
    
    def save(self, *args, **kwargs):
        # Auto-generate invoice number if not exists
        if not self.invoice_number:
            # Format: INV-YYYYMMDD-XXXX
            from django.utils import timezone
            date_str = timezone.now().strftime('%Y%m%d')
            last_invoice = Invoice.objects.filter(
                invoice_number__startswith=f'INV-{date_str}'
            ).order_by('-invoice_number').first()
            
            if last_invoice:
                last_number = int(last_invoice.invoice_number.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
                
            self.invoice_number = f'INV-{date_str}-{new_number:04d}'
        
        super().save(*args, **kwargs)