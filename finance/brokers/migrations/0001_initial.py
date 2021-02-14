# Generated by Django 2.2.1 on 2019-06-01 05:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BrokerGroup',
            fields=[
                ('broker_id', models.AutoField(primary_key=True, serialize=False)),
                ('brokerName', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='brokerCustomers', to=settings.AUTH_USER_MODEL)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='broker', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
