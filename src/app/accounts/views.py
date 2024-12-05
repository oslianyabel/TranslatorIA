from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, update_session_auth_hash, get_user_model
from .forms import LoginForm, SignUpForm
from .models import UserBase, TranslationInfo_User, Saved_voices_user
from core.common.common import iso_code_2_dict

# from django.urls import reverse


from django.contrib import messages
from django.utils.translation import gettext as _
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
# from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.db.models.query_utils import Q
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect

from .tests import test1
from .token import account_activation_token

def empty_msgs(request):
    system_messages = messages.get_messages(request)
    for message in system_messages:
        # This iteration is necessary
        pass

def activate_language(request, language_code):
    next_url = request.GET.get("next", request.META.get('HTTP_REFERER', '/'))
    response = HttpResponseRedirect(next_url) if next_url else HttpResponse(status=404)
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language_code)
    return response

def login_view(request):
    # email1 = 'nileygf@gmail.com'
    # user = UserBase.objects.get(email=email1)
    # print(user)
    # user.delete()
    # set_pass = SetPasswordForm()
    # print(set_pass)

    empty_msgs(request)
    form = LoginForm(request.POST or None)
    msg = None
    if request.method == "POST":
        if form.is_valid():
            email = request.POST.get('email')
            password = request.POST.get('password')
            remember_me = request.POST.get('remember_me')
            # email = form.cleaned_data.get("email")
            # password = form.cleaned_data.get("password")
            user = authenticate(email=email, password=password)
            print(user.password, password)
            if user is not None: 
                if remember_me:
                    pass
                else:
                    # automatically close the session after the browser is closed.
                    request.session.set_expiry(0)
                    request.session.modified = True

                # next_url = request.GET.get('next')
                # if next_url:
                #     return redirect(next_url)
                login(request, user)
                print(request.user)
                return redirect("user_projects")
            
            else:
                msg = 'Invalid credentials'
                print(msg)
        else:
            # msg = print('Error validating the form')
            print(form.errors)
    # print(msg)
    return render(request, "accounts/Login.html", {'redirect_to': request.path, "form": form, "msg": msg})

@login_required(login_url="/accounts/login/")
def change_password(request):    
    empty_msgs(request)
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('password_changed')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'redirect_to': request.path, 'form': form})

@login_required(login_url="/accounts/login/")
def password_changed(request):
    empty_msgs(request)
    return render(request, 'password_change_done.html', {'redirect_to': request.path })

def password_reset(request):
    empty_msgs(request)
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        # print(form)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            user = get_user_model().objects.get(email=user_email)
            # print(user)

            if user:
                subject = "Password Reset request"
                from_email=settings.EMAIL_HOST_USER 
                message = render_to_string("passwords/request_password_reset.html", {
                    'user': user,
                    'domain': "yml-multilanguage.com:"+request.META['SERVER_PORT'], # TODO generalize
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                    "protocol": 'https' if request.is_secure() else 'http'
                })
                email = EmailMessage(subject, message, from_email, to=[user.email])
                if email.send():
                    messages.success(request,
                        """
                        <h2>Password reset sent</h2><hr>
                        <p>
                            We've emailed you instructions for setting your password, if an account exists with the email you entered. 
                            You should receive them shortly.<br>If you don't receive an email, please make sure you've entered the address 
                            you registered with, and check your spam folder.
                        </p>
                        """
                    )
                else:
                    print(f'Problem sending confirmation email to {user.email}')
                    messages.error(request, "Problem sending reset password email, <b>SERVER PROBLEM</b>")
            else: 
                print(f'Problem sending confirmation email to {user.email}')
                messages.error(request, "No associated user with that email.")
            return redirect('password_reset_done')

    form = PasswordResetForm()
    print(form)
    context={'redirect_to': request.path, "form": form}
    return render(request, "passwords/password_reset.html", context)

def password_reset_done(request):
    empty_msgs(request)
    return render(request, 'passwords/password_reset_done.html', {'redirect_to': request.path })

def password_reset_confirm(request, uidb64, token):
    empty_msgs(request)
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None
        

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = PasswordChangeForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been set. You may go ahead and <b>log in </b> now.")
                return redirect('home')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
            return redirect("password_reset_complete")
        form = PasswordChangeForm(user)
        return render(request, 'passwords/password_reset_confirm.html', {'redirect_to': request.path, 'form': form, 'validlink': True})
    elif user is not None:
        messages.error(request, "Link is expired")
        form = PasswordChangeForm(user)
        return render(request, 'passwords/password_reset_confirm.html', {'redirect_to': request.path, 'form': form, 'validlink': False})       
    
    messages.error(request, 'Something went wrong, redirecting back to Homepage')
    return redirect("landing")

def password_reset_complete(request):
    empty_msgs(request)
    return render(request, 'passwords/password_reset_complete.html', {'redirect_to': request.path })


def register_user(request):
    # email1 = 'nileygf@gmail.com'
    # user = UserBase.objects.get(email=email1)
    # print(user)
    # user.delete()
    empty_msgs(request)
    msg = None
    success = False
    # print("begin register")
    if request.method == "POST":
        print("POST recieved")

        try:
            user = UserBase.objects.get(email=request.POST.get('email', "test@mail.com"))
            if not user.is_active:
                # delete it
                # print(user)
                user.delete()
        except:
            pass

        form = SignUpForm(request.POST)
        print(request.POST)
        if form.is_valid():
            print("All fields are valid")
            try:
                user = form.save(commit=False)  
                user.is_active = False  
                user.save()  
                print("going to activate email ...")
                activateEmail(request, user, form.cleaned_data.get('email'))
                print("redirect to check email")
                return redirect('check_email')
            except Exception as er:
                print(er)
                user.delete()
        else:
            msg = 'Form is not valid'
            print(msg)
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"{field}: {error}")
                    error_messages.append(error)
            error = '\n'.join(error_messages)
            messages.error(request, error)
    else:
        form = SignUpForm()  
        # print(form)
    print(form.errors)
    return render(request, "accounts/Register.html", {'redirect_to': request.path, "form": form, "msg": msg, "success": success})
    
    # if request.method == "POST":
    #     form = SignUpForm(request.POST)
    #     # print(request.POST)
    #     # print(request.POST.get('email'))
    #     # print(request.POST.get('firstname'))
    #     # print(request.POST.get('lastname'))
    #     # print(request.POST.get('referral'))
    #     # generate random password 
    #     # form.password1 = "Anfgvf_0722"
    #     # form.password2 = "Anfgvf_0722"
    #     print(form.password1, form.password2)
    #     if form.is_valid():
    #         try:
    #             user = form.save(commit=False)  
    #             raw_password = "Anfgvf_0722" # UserBase.objects.make_random_password(...)
    #             user.set_password(raw_password)
    #             user.is_active = False  
    #             user.save()  
    #             print("activating user using email")
    #             activateEmail(request, user, form.cleaned_data.get('email'))
    #             print("going home")
    #             return redirect('home')
    #         except Exception as er:
    #             print(er)
    #             user.delete()

    #     else:
    #         msg = 'Form is not valid'
    #         print(form.errors)
    # else:
    #     form = SignUpForm()

    # return render(request, "Register.html", {"form": form, "msg": msg})

def activateEmail(request, user:UserBase, to_email):
    mail_subject = 'Activate your user account.'
    from_email='info@yml-multilanguage.com'  # TODO read from settings
    message = render_to_string('activate_account.html', {
        'user': user,
        'domain': "yml-multilanguage.com:"+request.META['SERVER_PORT'] , #//get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, from_email,to=[to_email])
    print("sending email:", email)
    if email.send():
        mail = _('Dear') +' <b>{user}</b>, '+_('please go to you email')+' <b>{to_email}</b> '+ \
            _('inbox and click on received activation link to confirm and complete the registration.')+\
            ' <b>'+_('Note:')+'</b> '+ _('Check your spam folder.')
        messages.success(request, mail)
        print(f'Confirmation email to {to_email} success')
    else:
        print(f'Problem sending confirmation email to {to_email}')
        messages.error(request, f'Problem sending confirmation email to {to_email}, check if you typed it correctly.')
        raise Exception()

def activate(request, uidb64, token):  
    # https://www.javatpoint.com/django-user-registration-with-email-confirmation
    User = get_user_model()  
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        # messages.success(request, 'Thank you for your email confirmation. Now you can login your account.')
        return redirect('success')
    else:
        messages.error(request, 'Activation link is invalid!')
    
    return redirect('register')

@login_required(login_url="/accounts/login/")
def user_page_view(request):
    user:UserBase = request.user
    # user_form = UserForm(instance=request.user)
    #profile_form = ProfileForm(instance=request.user.profile)
    translations = TranslationInfo_User.objects.filter(user=user,using_storage=True, to_show=True)
    voices = Saved_voices_user.objects.filter(user=user, to_show=True)
    voice_table = []
    # print(len(translations))
    # for tr in translations:
    #     print(tr.translation_info.source_language_sel)
    #     print(tr.translation_info.translated_language_sel)

    for v in voices:
        name = v.voice_name
        index = list(iso_code_2_dict.values()).index(v.language)
        language = list(iso_code_2_dict.keys())[index]
        voice_table.append((name, language))
    # print("translations",translations)
    context = {
        'translations' : translations,
        'cloned_voices' : voice_table,
        'segment' : 'page-user'
    }
    if len(translations) == 0:
        context['translations'] = 'None'
    if len(voice_table) == 0:
        context['cloned_voices'] = 'None'
    return render(request, 'page-user.html', context)

class CheckEmailView(TemplateView):
    template_name = 'check_email.html'
    # def get_context_data(self, **kwargs):
    #     context = {'redirect_to': request.path }
    #     return context

class SuccessView(TemplateView):
    template_name = 'success.html'
    # def get_context_data(self, **kwargs):
    #     context = {'redirect_to': request.path }
    #     return context
   