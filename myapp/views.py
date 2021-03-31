from django.shortcuts import render,redirect
from .models import User,Contact,Product,Wishlist,Cart,Transaction
from django.core.mail import send_mail
from django.conf import settings
import random
from .paytm import generate_checksum, verify_checksum
from django.views.decorators.csrf import csrf_exempt


def initiate_payment(request):
    user=User.objects.get(email=request.session['email'])
    try:
        amount = int(request.POST['amount'])
    except:
        return render(request, 'index.html', context={'error': 'Wrong Accound Details or amount'})

    transaction = Transaction.objects.create(made_by=user,amount=amount)
    transaction.save()
    merchant_key = settings.PAYTM_SECRET_KEY

    params = (
        ('MID', settings.PAYTM_MERCHANT_ID),
        ('ORDER_ID', str(transaction.order_id)),
        ('CUST_ID', str("jigar93776@gmail.com")),
        ('TXN_AMOUNT', str(transaction.amount)),
        ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
        ('WEBSITE', settings.PAYTM_WEBSITE),
        # ('EMAIL', request.user.email),
        # ('MOBILE_N0', '9911223388'),
        ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
        ('CALLBACK_URL', 'http://localhost:8000/callback/'),
        # ('PAYMENT_MODE_ONLY', 'NO'),
    )

    paytm_params = dict(params)
    checksum = generate_checksum(paytm_params, merchant_key)

    transaction.checksum = checksum
    transaction.save()

    paytm_params['CHECKSUMHASH'] = checksum
    print('SENT: ', checksum)
    return render(request, 'redirect.html', context=paytm_params)

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        received_data = dict(request.POST)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                paytm_checksum = value[0]
            else:
                paytm_params[key] = str(value[0])
        # Verify checksum
        is_valid_checksum = verify_checksum(paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
        if is_valid_checksum:
            received_data['message'] = "Checksum Matched"
        else:
            received_data['message'] = "Checksum Mismatched"
            return render(request, 'callback.html', context=received_data)
        return render(request, 'callback.html', context=received_data)
# Create your views here.
def index(request):
	products=Product.objects.all()
	return render(request,'index.html',{'products':products})
def seller_index(request):
	return render(request,'seller_index.html')
def signup(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			msg="Email Id Already Registered"
			return render(request,'signup.html',{'msg':msg})
		except:
			if request.POST['password']==request.POST['cpassword']:
				User.objects.create(
					fname=request.POST['fname'],
					lname=request.POST['lname'],
					email=request.POST['email'],
					mobile=request.POST['mobile'],
					password=request.POST['password'],
					cpassword=request.POST['cpassword'],
					usertype=request.POST['usertype']
					)
				msg="Sign Up Successfull"
				return render(request,'login.html',{'msg':msg})
			else:
				msg="Password & Confirm Password Does Not Matched"
				return render(request,'signup.html',{'msg':msg})
	else:
		return render(request,'signup.html')
def login(request):
	if request.method=="POST":
		if request.POST['action']=="Login":
			try:
				user=User.objects.get(email=request.POST['email'],password=request.POST['password'])
				if user.usertype=="user":
					request.session['fname']=user.fname
					request.session['email']=user.email
					products=Product.objects.all()
					return render(request,'index.html',{'products':products})
				elif user.usertype=="seller":
					request.session['fname']=user.fname
					request.session['email']=user.email
					return render(request,'seller_index.html')
			except:
				msg="Email Or Password Is Incorrect"
				return render(request,'login.html',{'msg':msg})
		elif request.POST['action']=="Forgot Password":
			return render(request,'enter_email.html')

	else:
		return render(request,'login.html')
def logout(request):
	try:
		del request.session['email']
		del request.session['fname']
		return render(request,'login.html')
	except:
		return render(request,'login.html')
def change_password(request):
	if request.method=="POST":
		user=User.objects.get(email=request.session['email'])
		if user.password==request.POST['old_password']:
			if request.POST['npassword']==request.POST['cnpassword']:
				user.password=request.POST['npassword']
				user.cpassword=request.POST['npassword']
				user.save()
				return redirect('logout')
			else:
				msg="New Password & Confirm New Password Does Not Matched"
				return render(request,'change_password.html',{'msg':msg})
		else:
			msg="Old Password Is Incorrect"
			return render(request,'change_password.html',{'msg':msg})
	else:
		return render(request,'change_password.html')

def contact(request):
	Contact.objects.create(
			name=request.POST['name'],
			email=request.POST['email'],
			mobile=request.POST['mobile'],
			remarks=request.POST['remarks']
		)
	return render(request,'index.html')

def send_otp(request):
	email=request.POST['email']
	try:
		otp=random.randint(1000,9999)
		user=User.objects.get(email=email)
		subject = 'OTP For Forgot Password'
		message = "Hello User, Your OTP For Forgot Password Is : "+str(otp)
		email_from = settings.EMAIL_HOST_USER 
		recipient_list = [email,] 
		send_mail( subject, message, email_from, recipient_list )
		return render(request,'enter_otp.html',{'otp':otp,'email':email})
	except:
		msg="Email Is Not Exists"
		return render(request,'enter_email.html',{'msg':msg})

def verify_otp(request):
	email=request.POST['email']
	otp1=request.POST['otp1']
	otp2=request.POST['otp2']

	if otp1==otp2:
		return render(request,'new_password.html',{'email':email})
	else:
		msg="Entered OTP Is Invalid."
		return render(request,'enter_otp.html',{'otp':otp1,'email':email,'msg':msg})

def new_password(request):
	email=request.POST['email']
	npassword=request.POST['npassword']
	cnpassword=request.POST['cnpassword']

	user=User.objects.get(email=email)

	if npassword==cnpassword:
		user.password=npassword
		user.cpassword=npassword
		user.save()
		return redirect('login')
	else:
		msg="New Password & Confirm New Password Does Not Matched"
		return render(request,'new_password.html',{'email':email,'msg':msg})

def seller_add_product(request):
	if request.method=="POST":
		Product.objects.create(
				product_category=request.POST['product_category'],
				product_name=request.POST['product_name'],
				product_price=request.POST['product_price'],
				product_desc=request.POST['product_desc'],
				product_image=request.FILES['product_image']
			)
		msg="Product Added Successfully"
		return render(request,'seller_add_product.html',{'msg':msg})
	else:
		return render(request,'seller_add_product.html')

def seller_view_product(request):
	products=Product.objects.all()
	return render(request,'seller_view_product.html',{'products':products})

def seller_product_details(request,pk):
	product=Product.objects.get(pk=pk)
	main_price=int(product.product_price)+100
	return render(request,'seller_product_details.html',{'product':product,'main_price':main_price})

def seller_edit_product(request,pk):
	product=Product.objects.get(pk=pk)
	if request.method=="POST":
		product.product_name=request.POST['product_name']
		product.product_price=request.POST['product_price']
		product.product_desc=request.POST['product_desc']
		try:
			product.product_image=request.FILES['product_image']
			product.save()
			main_price=int(product.product_price)+100
			return render(request,'seller_product_details.html',{'product':product,'main_price':main_price})			
		except:
			product.save()
			main_price=int(product.product_price)+100
			return render(request,'seller_product_details.html',{'product':product,'main_price':main_price})			

	else:
		return render(request,'seller_edit_product.html',{'product':product})

def add_to_wishlist(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	
	wishlists=Wishlist.objects.filter(user=user,product=product)
	if wishlists:
		msg="Product Is Already In Your Wishlist"
		products=Product.objects.all()
		return render(request,'index.html',{'products':products,'msg':msg})
	else:
		Wishlist.objects.create(user=user,product=product)
		return redirect('index')

def mywishlist(request):
	user=User.objects.get(email=request.session['email'])
	wishlists=Wishlist.objects.filter(user=user)
	return render(request,'mywishlist.html',{'wishlists':wishlists})

def remove_from_wishlist(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	wishlist=Wishlist.objects.get(user=user,product=product)
	wishlist.delete()
	wishlists=Wishlist.objects.filter(user=user)
	return render(request,'mywishlist.html',{'wishlists':wishlists})

def add_to_cart(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	
	carts=Cart.objects.filter(user=user,product=product)
	if carts:
		msg="Product Is Already In Your Cart"
		products=Product.objects.all()
		return render(request,'index.html',{'products':products,'msg':msg})
	else:
		price=product.product_price
		price_qty=product.product_price
		Cart.objects.create(user=user,product=product,price=price,price_qty=price_qty)
		return redirect('index')

def mycart(request):
	net_price=0
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user)
	for i in carts:
		net_price=net_price+int(i.price_qty)
	return render(request,'mycart.html',{'carts':carts,'net_price':net_price})

def remove_from_cart(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	cart=Cart.objects.get(user=user,product=product)
	cart.delete()
	carts=cart.objects.filter(user=user)
	return render(request,'mycart.html',{'carts':carts})

def change_qty(request,pk):
	cart=Cart.objects.get(pk=pk)
	qty=request.POST['qty']
	cart.price_qty=int(qty)*int(cart.price)
	cart.qty=qty
	cart.save()
	return redirect('mycart')