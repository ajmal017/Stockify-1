from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Company(models.Model):
    NYSE = 'NY'
    NASDAQ = 'NDQ'

    EX_TYPE = (
        (NYSE, 'NYSE'),
        (NASDAQ, 'NASDAQ'),
    )
    company_id = models.AutoField(primary_key=True)
    symbol = models.CharField(max_length=10, unique=True)
    manager_id = models.ForeignKey(
        User, related_name="company", null=True, on_delete=models.SET_NULL
    )
    companyName = models.CharField(max_length=500)
    sector = models.CharField(max_length=500, null=True)
    industry = models.CharField(max_length=500, null=True)
    employees = models.IntegerField(null=True)
    homePage = models.URLField(max_length=1000, blank=True)
    description = models.CharField(max_length=3000, blank=True)
    exchange = models.CharField(
        max_length=100,
        choices=EX_TYPE,
        default=NASDAQ
    )

    @classmethod
    def model_field_exists(cls, field):
        try:
            cls._meta.get_field(field)
            return True
        except models.FieldDoesNotExist:
            return False
    models.Model.field_exists = model_field_exists


class StockDetails(models.Model):
    stock_id = models.OneToOneField(Company, primary_key=True,
                                    related_name='stock_detail', on_delete=models.PROTECT)
    current_price = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateTimeField(editable=False, auto_now_add=True)
    openBid = models.DecimalField(max_digits=6, decimal_places=2)
    closeBid = models.DecimalField(max_digits=6, decimal_places=2)
    volume = models.IntegerField()
    dayRange = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)


class CartItem(models.Model):
    stock = models.ForeignKey(Company, on_delete=models.PROTECT, unique=False, null=False)
    quantity = models.IntegerField()
