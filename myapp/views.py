from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseNotAllowed
from django.shortcuts import render, redirect
from .models import CartItem, Category, ContactMessage, Saree, Comment
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
import random
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import Saree, Category , Suit
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import Profile
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetView
from django.contrib import messages
from django.urls import reverse_lazy
from random import shuffle
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import NewsletterSubscriber
def index(request):
    sarees = Saree.objects.filter(is_available=True).order_by('-date_added')[:8]
    comments = Comment.objects.filter(is_approved=True).order_by('-submitted_at')

    if request.method == 'POST':
        name = request.POST.get('name')
        mobile = request.POST.get('mobile')
        comment = request.POST.get('comment')

        if name and mobile and comment:
            
            Comment.objects.create(name=name, mobile=mobile, comment=comment)
            messages.success(request, "Thank you! Your comment has been submitted for approval.")
            return redirect('index')

    return render(request, 'index.html', {
        'sarees': sarees,
        'comments': comments
    })



def category(request):
    return render(request,'category_page.html')


def category_view(request,category_slug):
    category = get_object_or_404(Category, name__iexact=category_slug)
    products = Saree.objects.filter(category=category, is_available=True)
    # Get filter & sort values
    color = request.GET.get('color', '')
    fabric = request.GET.get('fabric', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort_by = request.GET.get('sort', '')
    show = request.GET.get('show', '12')  # default 12

    # Filtering
    if color:
        products = products.filter(description__icontains=color)
    if fabric:
        products = products.filter(description__icontains=fabric)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Sorting
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'name_asc':
        products = products.order_by('name')
    elif sort_by == 'name_desc':
        products = products.order_by('-name')

    # Pagination or Limit Show
    paginator = Paginator(products, int(show))
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'category_page.html', {
        'products': page_obj,
        'category': category,
        'color': color,
        'fabric': fabric,
        'min_price': min_price,
        'max_price': max_price,
        'sort': sort_by,
        'show': show,
        "category_slug": category_slug,
        'is_filtered': any([color, fabric, min_price, max_price])
    })
 

def product_detail(request, id):
    product = get_object_or_404(Saree, id=id)

    related_products = Saree.objects.filter(
        category=product.category
    ).exclude(id=product.id)[:10]

    sarees = list(Saree.objects.exclude(id=product.id)[:10])
    suits = list(Suit.objects.all()[:10])

    all_items = sarees + suits
    recommended_products = random.sample(sarees + suits, min(len(sarees + suits), 10))


    return render(request, 'product_detail.html', {
        'product': product,
        'related_products': related_products,
        'recommended_products': recommended_products,
    })
 
@login_required
def add_to_cart(request, product_type, product_id):
    if request.method == 'POST':
        if product_type == 'saree':
            product = get_object_or_404(Saree, id=product_id)
            cart_item, created = CartItem.objects.get_or_create(user=request.user, saree=product)
        elif product_type == 'suit':
            product = get_object_or_404(Suit, id=product_id)
            cart_item, created = CartItem.objects.get_or_create(user=request.user, suit=product)
        else:
            messages.error(request, "Invalid product type.")
            return redirect('index')

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        messages.success(request, "Item added to cart!")
        return redirect(request.META.get('HTTP_REFERER', '/'))

from django.contrib.auth.decorators import login_required
from .models import CartItem

@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.get_price() for item in cart_items)

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

@login_required
def update_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart_item = get_object_or_404(CartItem, user=request.user)

        # Check if product matches
        if cart_item.saree and cart_item.saree.id == product_id:
            cart_item.quantity = quantity
        elif cart_item.suit and cart_item.suit.id == product_id:
            cart_item.quantity = quantity
        cart_item.save()

    return redirect('cart')
    

@login_required
def remove_from_cart(request, product_id):
    if request.method == 'POST':
        CartItem.objects.filter(
            user=request.user,
            saree_id=product_id
        ).delete()

        CartItem.objects.filter(
            user=request.user,
            suit_id=product_id
        ).delete()

    return redirect('cart')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        mobile = request.POST['mobile']

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')

        if Profile.objects.filter(mobile=mobile).exists():
            messages.error(request, "Mobile number already used.")
            return redirect('signup')

        # ✅ Create user and profile
        user = User.objects.create_user(username=username, email=email, password=password)
        Profile.objects.create(user=user, mobile=mobile)

        messages.success(request, "Account created successfully! Please log in.")
        return redirect('login')

    return render(request, 'signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Invalid credentials.")
            return redirect('login')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')

# def verify_otp_view(request):
#     if request.method == 'POST':
#         entered_otp = request.POST['otp']
#         real_otp = request.session.get('otp')
#         temp_user = request.session.get('temp_user')

#         if entered_otp == real_otp:
#             # Create user account
#             user = User.objects.create_user(
#                 username=temp_user['username'],
#                 email=temp_user['email'],
#                 password=temp_user['password']
#             )
#             # Optional: Store mobile in a custom profile
#             messages.success(request, "Account created successfully.")
#             request.session.pop('otp')
#             request.session.pop('temp_user')
#             return redirect('login')
#         else:
#             messages.error(request, "Invalid OTP. Please try again.")
#             return redirect('verify_otp')

#     return render(request, 'verify_otp.html')
 
# def send_otp(mobile , otp):
#     otp = str(random.randint(100000, 999999))

#     url = "https://www.fast2sms.com/dev/bulkV2"
#     headers = {
#         "authorization": "1X5Y3beaPfAp2C0W96zIhRSwQUJrFjkqigOGmZtyB47KNLET8lSRYrxnmlTJ3vG5b0sa9uWV1KEN4M6c",
#         "Content-Type": "application/json"
#     }
#     payload = {
#         "route": "otp",
#         "variables_values": otp,
#         "numbers": mobile
#     }

#     response = requests.post(url, json=payload, headers=headers)
#     print(response.text)
#     return otp



def about(request):
    sarees = Saree.objects.all()[:8]
    return render(request, 'about.html', {
        'sarees': sarees,
    })


@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.get_price() for item in cart_items)
    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Save to DB
        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        send_mail(
            f"New Contact Message: {subject}",
            f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}",
            settings.EMAIL_HOST_USER,  # Pass it explicitly here
            [settings.EMAIL_HOST_USER],
            fail_silently=False
        )
        
        messages.success(request, 'Thank you! Your message has been sent successfully.')
        return redirect('contact')  # Make a success page if you want
    return render(request, 'contact.html')

@login_required
@login_required
def my_account(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, '✅ Password updated successfully.')
            return redirect('my_account')
        else:
            # Check for specific errors
            if 'old_password' in form.errors:
                messages.error(request, '❌ Your current password is incorrect.')
            elif 'new_password1' in form.errors:
                for error in form.errors['new_password1']:
                    if "This password is too short" in error:
                        messages.error(request, '❌ New password must be at least 8 characters.')
                    else:
                        messages.error(request, f'❌ {error}')
            elif 'new_password2' in form.errors:
                messages.error(request, '❌ Passwords do not match.')
            else:
                messages.error(request, '❌ Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'my_account.html', {'form': form})

class CustomPasswordResetView(PasswordResetView):
    form_class = PasswordResetForm
    template_name = 'accounts/password_reset.html'
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            messages.error(self.request, 'This email address is not registered with us.')
            return render(self.request, self.template_name, {'form': form})
        return super().form_valid(form)



def shop(request):
    sarees = list(Saree.objects.all())
    for s in sarees:
        s.category_slug = 'saree'

    suits = list(Suit.objects.all())
    for s in suits:
        s.category_slug = 'suit'

    all_products = sarees + suits
    shuffle(all_products)

    paginator = Paginator(all_products, 12)
    page = request.GET.get('page', 1)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            products = paginator.page(page)
        except:
            return JsonResponse({'products': []})

        data = []
        for p in products:
            data.append({
                'id': p.id,
                'name': p.name,
                'price': p.price,
                'image_url': p.image.url,
                'category_slug': p.category_slug
            })
        return JsonResponse({'products': data})

    products = paginator.page(1)
    return render(request, 'shop.html', {'products': products})

def wishlist(request):
    return render(request,'wishlist.html')




def subscribe_newsletter(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            if not NewsletterSubscriber.objects.filter(email=email).exists():
                NewsletterSubscriber.objects.create(email=email)
                messages.success(request, 'Thank you for subscribing!')
            else:
                messages.info(request, 'You are already subscribed.')
        else:
            messages.error(request, 'Please enter a valid email.')

    return redirect(request.META.get('HTTP_REFERER', '/'))
