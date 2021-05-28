from django.shortcuts import render, redirect
from django.views import View
from .models import Customer, Product, Cart, OrderPlaced
from .form import CustomerRegistrationForm, CustomerProfileForm
from django.contrib import messages
from django.db.models import Q  
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required 
from django.utils.decorators import method_decorator 


class ProductView(View):

    def get(self, request):
        totalitem=0
        topwears = Product.objects.filter(category='TW')
        bottomwears = Product.objects.filter(category='BW')
        mobiles = Product.objects.filter(category='M')
        if request.user.is_authenticated:
            totalitem=len(Cart.objects.filter(user=request.user))
        return render(request, 'app/home.html', {'topwears': topwears, 'bottomewears': bottomwears, 'mobiles': mobiles,'totalitem':totalitem})


class ProductDetailView(View):
    def get(self, request, pk):
        totalitem=0
        product = Product.objects.get(pk=pk)
        item_already_in_cart=False
        if request.user.is_authenticated:
            totalitem=len(Cart.objects.filter(user=request.user))
            item_already_in_cart=Cart.objects.filter(Q(product=product.id)& Q(user=request.user)).exists()
        return render(request, 'app/productdetail.html', {'product': product ,'item_already_in_cart':item_already_in_cart,'totalitem':totalitem})



@login_required
def add_to_cart(request):
    totalitem=0
    user = request.user
    product_id = request.GET.get('prod_id')
    # print(product)
    product = Product.objects.get(id=product_id)
    Cart(user=user, product=product).save()
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
    return redirect('/cart',{'totalitem':totalitem})

@login_required
def show_cart(request):
    if request.user.is_authenticated:
        totalitem=0
        totalitem=len(Cart.objects.filter(user=request.user))
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0.0
        shipping_amount = 70.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user
                        == user]
        if cart_product:
            for p in cart_product:
                tempamount = (p.quantity*p.product.discounted_price)
                amount += tempamount
                totalamount = amount+shipping_amount
            return render(request, 'app/addtocart.html', {'carts': cart, 'totalamount': totalamount, 'amount': amount,'totalitem':totalitem})
        else:
            return render(request, 'app/emptycart.html',{'totalitem':totalitem})


def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity += 1
        c.save()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user
                        == request.user]
        for p in cart_product:
            tempamount = (p.quantity*p.product.discounted_price)
            amount += tempamount
        data = {'quantity': c.quantity,
                'amount': amount,
                'totalamount': amount+shipping_amount
                }
    return JsonResponse(data)


def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity -= 1
        c.save()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user
                        == request.user]
        for p in cart_product:
            tempamount = (p.quantity*p.product.discounted_price)
            amount += tempamount

        data = {'quantity': c.quantity,
                'amount': amount,
                'totalamount': amount+shipping_amount
                }
    return JsonResponse(data)

@login_required
def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user
                        == request.user]
        for p in cart_product:
            tempamount = (p.quantity*p.product.discounted_price)
            amount += tempamount
        data = {'amount': amount,
                'totalamount': amount + shipping_amount
                }
    return JsonResponse(data)

@login_required
def buy_now(request):
    return render(request, 'app/buynow.html')


@method_decorator(login_required,name='dispatch')
class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        totalitem=0
        if request.user.is_authenticated:
                totalitem=len(Cart.objects.filter(user=request.user))
        return render(request, 'app/profile.html', {'form': form,'totalitem':totalitem})

    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            usr = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            reg = Customer(user=usr, name=name, locality=locality,
                           city=city, zipcode=zipcode, state=state)
            reg.save()
            messages.success(
                request, 'Congratulations ! Profile Updated Succesfully')
            
                
        return render(request, 'app/profile.html', {'form': form, 'active': 'btn-primary'})

@login_required
def address(request):
    totalitem=0
    add = Customer.objects.filter(user=request.user)
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
    return render(request, 'app/address.html', {'add': add, 'active': 'btn-primary','totalitem':totalitem})

@login_required
def orders(request):
    totalitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
    op=OrderPlaced.objects.filter(user=request.user)
    return render(request, 'app/orders.html',{'orederplaced':op,'totalitem':totalitem})


@login_required
def mobile(request, data=None):
    totalitem=len(Cart.objects.filter(user=request.user))
    if data == None:
        mobiles = Product.objects.filter(category='M')
    elif data == 'Iphone' or data == 'samsung' or data == 'realme' or data == 'xiomi' or data == 'mi':
        mobiles = Product.objects.filter(category='M').filter(brand=data)
    elif data == 'below':
        mobiles = Product.objects.filter(
            category='M').filter(discounted_price__lt=10000)
    elif data == 'above':
        mobiles = Product.objects.filter(
            category='M').filter(discounted_price__gt=10000)
    return render(request, 'app/mobile.html', {'mobile': mobiles,'totalitem':totalitem})

@login_required
def topwear(request,data=None):
    totalitem=len(Cart.objects.filter(user=request.user))
    if data == None:
        topwear = Product.objects.filter(category='TW')
    elif data == 'spykr' or data == 'remand' or data == 'lee' or data == 'cooper' :
        topwear = Product.objects.filter(category='TW').filter(brand=data)
    elif data == 'below':
        topwear = Product.objects.filter(
            category='TW').filter(discounted_price__lt=500)
    elif data == 'above':
        topwear = Product.objects.filter(
            category='TW').filter(discounted_price__gt=500)
    return render(request, 'app/topwear.html', {'topwear': topwear,'totalitem':totalitem})

class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html', {'form': form})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Congratulation User Saved Succefully')
            form.save()
        return render(request, 'app/customerregistration.html', {'form': form})

@login_required
def checkout(request):
    user = request.user
    add = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)
    # product_name=Product.objects.filter(user=user)
    amount = 0.0
    shipping_amount = 70.0
    totalamount = 0.0
    cart_product = [p for p in Cart.objects.all() if p.user == request.user]    
    if cart_product:
        for p in cart_product:
            tempamount = (p.quantity*p.product.discounted_price)
            amount += tempamount
        totalamount=amount+shipping_amount
    return render(request, 'app/checkout.html', {'add': add,'totalamount':totalamount,'cart_items':cart_items})

@login_required
def payment_done(request):
    user=request.user
    custid=request.GET.get('custid')
    customer=Customer.objects.get(id=custid)
    cart=Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(user=user,customer=customer,product=c.product,quantity=c.quantity).save()
        c.delete()
    return redirect('orders')
