from django.urls import path
from . import views

app_name = 'dashboard'
urlpatterns = [
        path('', views.dashboard, name='dashboard'),
        path('profile', views.profile, name='profile'),
        path('orders', views.all_orders, name='orders'),
        path('orders/<int:order_id>', views.order_details, name='order_details'),
        path('company/search', views.search_company, name='search_company'),
        path('company/<int:company_id>', views.search_company_with_id, name='company_search'),
        path('company/<str:company_name>', views.search_company_with_ticker, name='companySpecific'),
]