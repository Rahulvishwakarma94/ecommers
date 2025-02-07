from django.shortcuts import get_object_or_404, render,redirect
from account.forms import RegistrationForm, AccountForm, ProfileForm
from account.models import Account, UserProfile
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Email
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from django.http import HttpResponse
from carts.views import _cart_id
from carts.models import Cart, CartItem
from order.models import Order, OrderProduct, Payment


# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()

            # USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('account/verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            # messages.success(request, 'Thank you for registering with us. We have sent you a verification email to your email address [rathan.kumar@gmail.com]. Please verify it.')
            return redirect('/account/login/?command=verification&email='+email)
    else:
        form = RegistrationForm()
    context = {
        'form': form,
    }
    return render(request, 'account/register.html', context)


def login(request):
    if request.method == 'POST':
        username = request.POST['Username']
        password = request.POST['Password']

        user = auth.authenticate(request,username=username,password=password)
        
        if user is not None:

            try:
                session_cart_id = _cart_id(request)
                session_cart_items  = CartItem.objects.filter(cart__cart_id=session_cart_id)
                
                user_cart_items = CartItem.objects.filter(user=user)

                for session_item in session_cart_items:

                    matching_item = None
                    for user_item in user_cart_items:
                        if (session_item.product == user_item.product and list(session_item.variations.all()) == list(user_item.variations.all())):
                            matching_item = user_item
                            break
                
                    if matching_item:
                        matching_item.quantity += session_item.quantity
                        matching_item.save()
                    else:
                        # If no match found, assign the session item to the user
                        session_item.user = user
                        session_item.cart = None  # Disassociate from the session cart
                        session_item.save()

                Cart.objects.filter(cart_id=session_cart_id).delete()

            except Exception as e:
                print(f"Error merging cart: {e}")
                pass
 
            
            auth.login(request,user)
            next_url = request.GET.get('next','index')
            messages.success(request,"Login Success.")
            return redirect(next_url)
        else:
            messages.success(request,"Login Again.")
            return redirect('login')

    
    return render(request,'account/login.html')


def activate(request,uid64,token):
    try:
        userid = urlsafe_base64_decode(uid64).decode()
        user = Account._default_manager.get(id=userid)
        tokens = default_token_generator.check_token(user,token)
    except:
        user = None
    
    if user is not None and tokens:
        user.is_active = True
        user.save()
        return redirect('login')
    else:
        return redirect('register')


def logout(request):
    auth.logout(request)
    messages.info(request,'Logout Success! Login Again')
    return redirect('login')


@login_required(login_url = 'login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()

    userprofile = UserProfile.objects.get(user_id=request.user.id)
    context = {
        'orders_count': orders_count,
        'userprofile': userprofile,
    }
    return render(request, 'account/dashboard.html', context)

@login_required(login_url='login')
def change_password(request):
    if request.method == "POST":
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = request.user

        if not check_password(current_password,user.password):
            messages.error(request,'The Current Password is incorrect.')
            return redirect('change_password')
        
        if new_password != confirm_password:
            messages.success(request,'New password and confirm password do not match.')
            return redirect('change_password')
        
        user.set_password(new_password)
        user.save()

        messages.success(request,'Your password has been changed successfully.')
        return redirect('index')


    return render(request,'account/change_password.html')


@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'account/my_orders.html', context)


@login_required(login_url='login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity

    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    }
    return render(request, 'account/order_detail.html', context)


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # auth.logout(request)
                messages.success(request, 'Password updated successfully.')
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('change_password')
    return render(request, 'accounts/change_password.html')


@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = AccountForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
    else:
        user_form = AccountForm(instance=request.user)
        profile_form = ProfileForm(instance=userprofile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'account/edit_profile.html', context)


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # Reset password email
            mail_subject = 'Reset Your Password'
            current_site = get_current_site(request)
            message = render_to_string('account/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgotPassword')
    return render(request,'account/forgotPassword.html')


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('login')


def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')
    else:
        return render(request, 'account/resetPassword.html')
    
