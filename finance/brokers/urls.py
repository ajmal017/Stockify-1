from django.urls import path
from . import views

app_name = 'brokers'
urlpatterns = [
    path('', views.show_users, name='brokerboard'),
    path('<int:customer_id>', views.specific_customer, name='specific_customer'),
    path('buy/<int:customer_id>', views.place_order, name='order'),
    path('orders/<int:customer_id>/<int:order_id>', views.view_order, name='broker_order_details'),
]