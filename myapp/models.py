from django.db import models
from django.utils import timezone
# Create your models here.
class User(models.Model):

	fname=models.CharField(max_length=100)
	lname=models.CharField(max_length=100)
	email=models.CharField(max_length=100)
	mobile=models.CharField(max_length=100)
	password=models.CharField(max_length=100)
	cpassword=models.CharField(max_length=100)
	usertype=models.CharField(max_length=100,default="user")

	def __str__(self):
		return self.fname+" "+self.lname

class Contact(models.Model):

	name=models.CharField(max_length=100)
	email=models.CharField(max_length=100)
	mobile=models.CharField(max_length=100)
	remarks=models.TextField()

	def __str__(self):
		return self.name

class Product(models.Model):

	CHOICE=(
			('chair','chair'),
			('sofa','sofa'),
			('lamp','lamp'),
			('table','table'),
		)
	product_category=models.CharField(max_length=100,choices=CHOICE)
	product_name=models.CharField(max_length=100)
	product_price=models.CharField(max_length=100)
	product_desc=models.TextField()
	product_image=models.ImageField(upload_to="images/")

	def __str__(self):
		return self.product_name

class Wishlist(models.Model):

	user=models.ForeignKey(User,on_delete=models.CASCADE)
	product=models.ForeignKey(Product,on_delete=models.CASCADE)
	date=models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.user.fname+" - "+self.product.product_name

class Cart(models.Model):

	user=models.ForeignKey(User,on_delete=models.CASCADE)
	product=models.ForeignKey(Product,on_delete=models.CASCADE)
	date=models.DateTimeField(default=timezone.now)
	price=models.CharField(max_length=100,default="")
	qty=models.CharField(max_length=100,default="1")
	price_qty=models.CharField(max_length=100,default="")

	def __str__(self):
		return self.user.fname+" - "+self.product.product_name

class Transaction(models.Model):
	made_by=models.ForeignKey(User,on_delete=models.CASCADE)
	made_on = models.DateTimeField(auto_now_add=True)
	amount = models.IntegerField()
	order_id = models.CharField(unique=True, max_length=100, null=True, blank=True)
	checksum = models.CharField(max_length=100, null=True, blank=True)
	def save(self, *args, **kwargs):
		if self.order_id is None and self.made_on and self.id:
			self.order_id = self.made_on.strftime('PAY2ME%Y%m%dODR') + str(self.id)
		return super().save(*args, **kwargs)