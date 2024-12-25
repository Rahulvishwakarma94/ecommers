from django.shortcuts import render, redirect
from account.forms import registerationform
from account.models import Account
from django.contrib import auth
from django.contrib.auth import login as user_login
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
# Create your views here.
def register(request):
    if request.method == "POST":
        form = registerationform(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']

            username = email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()

            current_site = get_current_site(request)
            email_subject = 'Please activate your account'
            message = render_to_string('account/verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            send_email=EmailMessage(email_subject,message,to=[email])
            send_email.send()

            return redirect('login')

        

    form = registerationform()

    context = {
        'forms': form,
    }


    return render(request,'account/register.html',context)


def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            user_login(request,user)
            user.save()
            return redirect('index')

    
    return render(request,'account/login.html')

def activate(request,uid64,token):
    try:
        uid = urlsafe_base64_decode(uid64).decode()
        user = Account._default_manager.get(id=uid)
        token = default_token_generator.check_token(user, token)
    except:
        user=None


    if user is not None and token :
        user.is_active = True
        user.save()
        return redirect('accounts:login')
    else:
        return redirect('accounts:register')