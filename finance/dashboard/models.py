from django.db import models
from django.contrib.auth.models import User
from stocks.models import Company


# Create your models here.
class Order(models.Model):
    """

    """
    BUY = 'B'
    SELL = 'S'

    TYPE = (
        (BUY, 'B'),
        (SELL, 'S')
    )

    order_id = models.AutoField(primary_key=True, unique=True)
    user_id = models.ForeignKey(User, related_name='order', on_delete=models.PROTECT)
    createdAt = models.DateTimeField(editable=False, auto_now_add=True)
    editedAt = models.DateTimeField(auto_now=True)
    order_type = models.CharField(
        max_length=10,
        choices=TYPE,
        default=BUY
    )

    
class OrderDetails(models.Model):
    """

    """
    order = models.ForeignKey(Order, unique=False, related_name='order_detail',
                              on_delete=models.PROTECT)
    stock_id = models.ForeignKey(Company, related_name='order_detail', on_delete=models.PROTECT, null=False, blank=False)
    purchase_price = models.DecimalField(blank=False, null=False, decimal_places=2, max_digits=10,
                                     default=0)
    sell_price = models.DecimalField(blank=False, null=False, decimal_places=2, max_digits=10,
                                         default=0)
    quantity = models.IntegerField(default=0, blank=False, null=False, max_length=10)
    createdAt = models.DateTimeField(editable=False, auto_now_add=True)
    editedAt = models.DateTimeField(auto_now=True)