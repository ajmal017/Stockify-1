from django.urls import path
from . import views

app_name = 'stocks'
urlpatterns = [
    path('', views.specificStock, name='stock'),
    path('search', views.specificStock, name='specificStock'),
    path('cart/', views.view_cart, name='view'),
    path('cart/buy/<str:stock_ticker>', views.add_stock_to_cart, name='add'),
    path('cart/remove/<str:stock_ticker>', views.remove_from_cart, name='remove'),
    path('buy', views.place_order, name='buy'),
    path('search/industry/<str:industry>', views.industry_search, name='industry'),
]
