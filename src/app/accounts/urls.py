from django.urls import path, include
from django.urls import re_path as url
from .views import (
    activate_language, login_view, register_user, activate, user_page_view, 
    change_password, password_changed, CheckEmailView, SuccessView, password_reset, 
    password_reset_done, password_reset_confirm, password_reset_complete)

from django.contrib.auth.views import (
    LogoutView, 
    # PasswordResetView, 
    # PasswordResetDoneView, 
    # PasswordResetConfirmView,
    # PasswordResetCompleteView
)
urlpatterns = [
    path('login/', login_view, name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    # path('accounts/login/', login_view, name="login"),
    path('password/', change_password, name="change_password"),
    path('passwordok/', password_changed, name="password_changed"),

    path('password_reset/', password_reset, name='password_reset'),
    path('password_reset/done/', password_reset_done, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),
    path('reset/done', password_reset_complete, name='password_reset_complete'),
    
    # path('password_reset/', PasswordResetView.as_view(template_name='passwords/password_reset.html'), name='password_reset'),
    # path('password_reset/done/', PasswordResetDoneView.as_view(template_name='passwords/password_reset_done.html'), name='password_reset_done'),
    # path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='passwords/password_reset_confirm.html'), name='password_reset_confirm'),
    # path('reset/done', PasswordResetCompleteView.as_view(template_name='passwords/password_reset_complete.html'), name='password_reset_complete'),
    # path("password_reset", password_reset, name="password_reset"),
    # path('reset/<uidb64>/<token>', passwordResetConfirm, name='password_reset_confirm'),
    
    path('register/', register_user, name="register"),
    path('user/', user_page_view, name="user_page"),
    path('activate/<uidb64>/<token>', activate, name='activate'),
    path('check-email/', CheckEmailView.as_view(), name="check_email"),
    path('success/', SuccessView.as_view(), name="success"),


        # path('i18n/', include('django.conf.urls.i18n')),
    path('languageactivate/<language_code>/', activate_language, name='activate_language'),
]
