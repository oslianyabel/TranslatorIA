from django.test import TestCase

from .models import UserBase
from django.contrib.auth.models import User


def test1():
    email1 = 'nileygf@gmail.com'
    email2 = 'arianpzv@gmail.com'
    user = UserBase.objects.get(email=email1)
    user.is_superuser = True
    user.is_staff = True
    print(user)
