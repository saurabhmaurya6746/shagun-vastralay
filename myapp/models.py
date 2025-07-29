from django.db import models
from django.db import models
from django.contrib.auth.models import User
class Category(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Saree(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='saree_images/')
    is_available = models.BooleanField(default=True)
    date_added = models.DateTimeField(auto_now_add=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    fabric = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name


class Suit(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='suit_images/')
    is_available = models.BooleanField(default=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Comment(models.Model):
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=15)

    def __str__(self):
        return self.user.username
 

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    saree = models.ForeignKey(Saree, on_delete=models.CASCADE, null=True, blank=True)
    suit = models.ForeignKey(Suit, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def get_product(self):
        return self.saree or self.suit

    def get_price(self):
        if self.saree:
            return self.saree.price * self.quantity
        elif self.suit:
            return self.suit.price * self.quantity
        return 0


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"

# myapp/models.py


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
