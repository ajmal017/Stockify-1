from django.db import models
from django.contrib.auth.models import User
from dashboard.models import Order
from stocks.models import CartItem
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.
class Profile(models.Model):
    REQUIRED_FIELDS = ('user',)

    NORMAL = 'N'
    BROKER = 'B'
    ADMIN = 'A'

    USER_TYPE = (
        (NORMAL, 'Normal'),
        (BROKER, 'Broker'),
        (ADMIN, 'Admin'),
    )

    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    orders = models.ManyToManyField(Order, blank=True)
    managed_users = models.ManyToManyField(User, related_name='managed', blank=True)
    cart = models.ManyToManyField(CartItem, related_name='cart', blank=True)
    country = models.TextField(max_length=30, null=True, blank=True)
    phone = models.TextField(max_length=10, null=True, blank=True)
    description = models.TextField(max_length=1000, null=True, blank=True)
    user_type = models.CharField(
        max_length=2,
        choices=USER_TYPE,
        default=NORMAL,
    )


@receiver(post_save, sender=User)
def create(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Wallet(models.Model):
    wallet_id = models.ForeignKey(User, primary_key=True, unique=True, related_name='wallet', on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, null=False)
    lifetime_spend = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, null=False, blank=False)
