from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.db import models
from django.db.models import Exists, OuterRef
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.signals import user_logged_in
from allauth.account.models import EmailAddress


class UserSet(models.QuerySet):
    def add_verified(self):
        return self.annotate(verified=Exists(EmailAddress.objects.filter(user_id=OuterRef('id'), verified=True)))


class User(AbstractUser):

    # # AbstractUser Fields
    # username = models.CharField
    # first_name = models.CharField
    # last_name = models.CharField
    # email = models.EmailField
    # is_staff = models.BooleanField
    # is_active = models.BooleanField
    # date_joined = models.DateTimeField

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(_('Name of User'), blank=True, max_length=255)
    objects = UserSet.as_manager()

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})


class UserLogin(models.Model):
    """Represent users' logins, one per record"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='logins')
    timestamp = models.DateTimeField(auto_now_add=True)


def update_user_login(sender, user, **kwargs):
    user.logins.create()
    user.save()


user_logged_in.connect(update_user_login)
