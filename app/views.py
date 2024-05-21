from django.db.models import Count
from django.http import JsonResponse, HttpResponse
from django_daraja.mpesa.core import MpesaClient
from django.shortcuts import render, redirect , get_object_or_404
from . models import Product, Cart, Customer, OrderPlaced, Wishlist, Payment
from django.views import View
from . forms import CustomerRegistrationForm, CustomerProfileForm
from django.contrib import messages
from django.db.models import Q



def index(request):
    cl = MpesaClient()
    # Use a Safaricom phone number that you have access to, for you to be able to view the prompt.
    phone_number = '0757467057'
    amount = 1
    account_reference = 'reference'
    transaction_desc = 'Description'
    callback_url = 'http://127.0.0.1:8000/';
    response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
    return HttpResponse(response)

def stk_push_callback(request):
        data = request.body
        
        return HttpResponse("STK Push in Django👋")

def payment_done(request):
    order_id=request.GET.get('order_id')
    payment_id=request.GET.get('payment_id')
    cust_id=request.GET.get('cust_id')
    user=request.user
    customer=Customer.objects.get(id=cust_id)
    Payment.Payment.objects.get(mpesa_order_id=order_id)
    Payment.paid = True
    Payment.mpesa_payment_id = payment_id
    Payment.save()
    cart=Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(user=user,customer=customer,product=c.product,quantity=c.quantity,payment=payment).save()
        c.delete()
    return redirect("orders")

def orders(request):
    totalitem = 0
    if request.user.is_authenticated:
       totalitem = len(Cart.objects.filter(user=request.user))
    orders_placed=OrderPlaced.objects.filters(user=request.user)
    return render(request, 'app/orders.html', locals())

def home(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'app/home.html',locals())

def about(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'app/about.html',locals())

def contact(request):
        totalitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(request, 'app/contact.html',locals())

class CategoryView(View):
    def get(self,request,val):
        totalitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        product = Product.objects.filter(category=val)
        title = Product.objects.filter(category=val).values('title')
        return render(request, "app/category.html",locals())

class CategoryTitle(View):
    def get(self,request,val):
        product = Product.objects.filter(title=val)
        title = Product.objects.filter(category=product[0].category).values('title')
        totalitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(request, "app/category.html",locals())



class ProductDetail(View):
    def get(self, request, pk):
        # Retrieve the product or return 404 if not found
        product = get_object_or_404(Product, pk=pk)

        # Check if the user is authenticated before querying the wishlist
        if request.user.is_authenticated:
            wishlist = Wishlist.objects.filter(product=product, user=request.user).exists()
        else:
            wishlist = False

        # Count total items in the cart
        totalitem = len(Cart.objects.filter(user=request.user)) if request.user.is_authenticated else 0

        # Pass the variables to the template
        return render(request, "app/productdetail.html", {
            'product': product,
            'wishlist': wishlist,
            'totalitem': totalitem
        })



class CustomerRegistrationView(View):
    def get(self,request):
        form = CustomerRegistrationForm()
        totalitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(request, 'app/customerregistration.html',locals())
    def post(self,request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Congratulations! user Registered Successfully")
        else:
            messages.warning(request,"Invalid Input Data")
        return render(request, 'app/customerregistration.html',locals())


class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        totalitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(request, 'app/profile.html',locals())
    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']

            reg = Customer(user=user,name=name,locality=locality,mobile=mobile,city=city,state=state,zipcode=zipcode)
            reg.save()
            messages.success(request, "Congratulations! Profile saved Successfully")
        else:
            messages.warning(request,"Invalid Input Data")

        return render(request, 'app/profile.html',locals())

def address(request):
    add = Customer.objects.filter(user=request.user)
    totalitem = 0
    if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'app/address.html',locals())

class updateAddress(View):
    def get(self,request,pk):
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)
        totalitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(request, 'app/updateAddress.html',locals())
    def post(self,request,pk):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            add = Customer.objects.get(pk=pk)
            add.name = form.cleaned_data['name']
            add.locality = form.cleaned_data['locality']
            add.city = form.cleaned_data['city']
            add.mobile = form.cleaned_data['mobile']
            add.state = form.cleaned_data['state']
            add.zipcode = form.cleaned_data['zipcode']
            add.save()
            messages.success(request, "Congratulations! Profile updated Successfully")
        else:
            messages.warning(request,"Invalid Input Data")
        return redirect("address")

def add_to_cart(request):
    user=request.user
    product_id=request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user,product=product).save()
    return redirect("/cart")

def show_cart(request):
    user=request.user
    cart = Cart.objects.filter(user=user)
    amount = 0
    for p in cart:
        value = p.quantity * p.product.discounted_price
        amount = amount + value
    totalamount = amount + 40
    totalitem = 0
    if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, "app/addtocart.html",locals())

class checkout(View):
    def get(self,request):
        totalitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        user=request.user
        add=Customer.objects.filter(user=user)
        cart_items=Cart.objects.filter(user=user)
        famount = 0
        for p in cart_items:
            value = p.quantity * p.product.discounted_price
            famount = famount + value
        totalamount = famount + 40
        return render(request, 'app/checkout.html',locals())


def plus_cart(request):
    if request.method == 'GET':
        prod_id=request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity+=1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 40
        data={
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':totalamount
        }
        return JsonResponse(data)
    
def minus_cart(request):
    if request.method == 'GET':
        prod_id=request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity-=1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 40
        data={
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':totalamount
        }
        return JsonResponse(data)
    
def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET.get('prod_id')  # Use get() to handle missing keys gracefully
        if prod_id:
            cart_item = Cart.objects.filter(product=prod_id, user=request.user).first()
            if cart_item:
                cart_item.delete()
                cart_items = Cart.objects.filter(user=request.user)
                amount = sum(item.quantity * item.product.discounted_price for item in cart_items)
                totalamount = amount + 40
                data = {
                    'amount': amount,
                    'totalamount': totalamount
                }
                return JsonResponse(data, safe=False)  # Include safe=False argument
            else:
                return JsonResponse({'error': 'Cart item not found'}, status=400)
        else:
            return JsonResponse({'error': 'Product ID not provided'}, status=400)

def plus_wishlist(request):
    if request.method == 'GET':
        prod_id = request.GET.get('prod_id')
        try:
            product = Product.objects.get(id=prod_id)
            wishlist, created = Wishlist.objects.get_or_create(user=request.user, product=product)
            if created:
                message = 'Wishlist item added successfully.'
            else:
                message = 'Item already in wishlist.'
            return JsonResponse({'message': message})
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Invalid product ID.'}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

def minus_wishlist(request):
    if request.method == 'GET':
        prod_id = request.GET.get('prod_id')
        try:
            product = Product.objects.get(id=prod_id)
            wishlist_item = Wishlist.objects.filter(user=request.user, product=product)
            if wishlist_item.exists():
                wishlist_item.delete()
                return JsonResponse({'message': 'Wishlist item removed successfully.'})
            else:
                return JsonResponse({'message': 'Item not found in wishlist.'})
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Invalid product ID.'}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)
    

    

