from sqlite3 import DatabaseError
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from stocks.models import Company, StockDetails, CartItem
from dashboard.models import Order, OrderDetails
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import RequestContext
from django.forms.models import model_to_dict
from django.views.generic import ListView, View, DetailView, TemplateView, FormView
from django.views.decorators.debug import sensitive_post_parameters, sensitive_variables
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from users.models import Profile
import json
import requests
import urllib.request
import re
import random
import bs4 as bs


# Create your views here.
@csrf_exempt
def specificStock(request):
    """ handles getting stock info, deleting stock, updating stock """''
    if request.method == 'GET':
        sector = Company.objects.values('sector').distinct()

        resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        soup = bs.BeautifulSoup(resp.text, 'lxml')
        table = soup.find('table', {'class': 'wikitable sortable'})
        tickers = []
        for row in table.findAll('tr')[1:]:
            ticker = row.findAll('td')[0].text
            tickers.append(ticker)

        sample = random.choices(tickers, k=5)
        for ticker in sample:
            if not Company.objects.filter(symbol=ticker.strip().lower()).exists():
                company_data = requests.get(
                    'https://cloud.iexapis.com/stable/stock/' + ticker.strip()
                    + '/company?token=pk_8eb2d1bd40044c2181ad3cd603509bcb')

                json_data = company_data.json()
                Company.objects.create(symbol=ticker.strip().lower(),
                                       companyName=json_data['companyName'],
                                       sector=json_data['sector'], industry=json_data['industry'],
                                       employees=json_data['employees'],
                                       homePage=json_data['website'],
                                       description=json_data['description'],
                                       exchange=json_data['exchange'])

        sectors = []
        for s in sector:
            sectors.append(s['sector'])

        return render(request, 'stocks/search.html', {'data': sectors}, status=200)

    elif request.method == 'POST':
        stock_ticker = request.POST['stock']

        #try:
        data = requests.get('https://cloud.iexapis.com/stable/stock/' + stock_ticker.lower()
                                  + '/quote?token=pk_8eb2d1bd40044c2181ad3cd603509bcb')

        price_data = data.json()
        if not Company.objects.filter(symbol=stock_ticker.lower()).exists():
            company_data = requests.get('https://cloud.iexapis.com/stable/stock/' + stock_ticker.lower()
                                        + '/company?token=pk_8eb2d1bd40044c2181ad3cd603509bcb')

            json_data = company_data.json()
            Company.objects.create(symbol=stock_ticker.lower(), companyName=json_data['companyName'],
                                   sector=json_data['sector'], industry=json_data['industry'],
                                   employees=json_data['employees'],
                                   homePage=json_data['website'], description=json_data['description'],
                                   exchange=json_data['exchange'])

        company_object = Company.objects.get(symbol=stock_ticker.lower())
        if StockDetails.objects.filter(stock_id=company_object).exists():
            stock_object = StockDetails.objects.get(stock_id=company_object)
            stock_object.openBid = price_data['open']
            stock_object.closeBid = price_data['close']
            stock_object.volume = price_data['latestVolume']
            stock_object.date = price_data['latestUpdate']
            stock_object.current_price = price_data['latestPrice']

        else:
            StockDetails.objects.create(stock_id=company_object, openBid=price_data['open'],
                                 closeBid=price_data['close'], volume=price_data['latestVolume'],
                                 date=price_data['latestUpdate'],
                                 current_price=price_data['latestPrice'])

        data = {
            "Company Name": price_data['companyName'],
            "Stock Ticker": price_data['symbol'],
            "Current Price": price_data['latestPrice'],
            "Open Price": price_data['open'],
            "Today's High": price_data['high'],
            "Today's Low": price_data['low'],
            "Volume": price_data['latestVolume'],
            "Market Cap": price_data['marketCap']
        }

        return render(request, 'stocks/stock_details.html', {'data': data,
                                                             'ticker': price_data['symbol']}, status=200)
    else:
        return HttpResponse("Method not allowed on /", status=405)


@csrf_exempt
def industry_search(request, industry):
    if request.user.is_authenticated:
        if request.method == 'GET':
            companies = Company.objects.filter(sector=industry).distinct()

            data = []
            for c in companies:
                data.append({'name': c.companyName, 'ticker': c.symbol})

            if not len(data) < 25:
                data = random.choices(data, k=25)
            return render(request, 'stocks/industry.html', {'industry': industry,
                                                            'data': data}, status=200)
        else:
            return HttpResponse('Not Allowed')
    else:
        return HttpResponse('User Not Authenticated')


@csrf_exempt
def view_cart(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            try:
                user = User.objects.get(pk=request.user.id)
            except ObjectDoesNotExist:
                return HttpResponse("user does not exist", status=404)
            items = user.profile.cart.all()

            data = []
            sum = 0

            for i in items:
                try:
                    stock = StockDetails.objects.get(stock_id=i.stock)
                except ObjectDoesNotExist:
                    continue

                url = i.stock.homePage
                if url.startswith('http'):
                    url = re.sub(r'https?://', '', url)

                if url.startswith('www.'):
                    url = re.sub(r'www.', '', url)

                sum += i.quantity * stock.current_price

                data.append({'company': i.stock.companyName, 'quantity': i.quantity,
                             'price': stock.current_price,
                             'total': i.quantity * stock.current_price,
                             'ticker': i.stock.symbol,
                             'image': url})

            return render(request, 'stocks/cart.html', {'data': data, 'sum': sum}, status=200)

        else:
            return HttpResponse('Not Allowed')
    else:
        return HttpResponse("Unauthorized: are you logged in?", status=400)

@csrf_exempt
def add_stock_to_cart(request, stock_ticker):
    if request.user.is_authenticated:
        if request.method == 'POST':
            shares = request.POST['shares']
            print('hi')

            if int(shares) < 1:
                return HttpResponse("Error: You must buy at least 1 share", status=400)

            try:
                user = User.objects.get(pk=request.user.id)
                company = Company.objects.get(symbol=stock_ticker.lower())
                #stock = StockDetails.objects.get(stock_id=company)
                if user.profile.cart.filter(stock=company).exists():
                    cart_item = user.profile.cart.get(stock=company)
                    cart_item.quantity = int(cart_item.quantity) + int(shares)
                    cart_item.save()

                    user.profile.cart.add(cart_item)
                else:
                    cart_item = CartItem.objects.create(stock=company, quantity=shares)
                    user.profile.cart.add(cart_item)

                return HttpResponseRedirect('/stocks/cart')

            except DatabaseError:
                return HttpResponse("Database Error", status=400)

        # elif request.method == 'POST':
        #     # for updating quantities
        #     return
    else:
        return HttpResponse("Unauthorized: are you logged in?", status=400)

@csrf_exempt
def remove_from_cart(request, stock_ticker):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(pk=request.user.id)
            company = Company.objects.get(symbol=stock_ticker.lower())
            cart_item = user.profile.cart.get(stock=company)
        except ObjectDoesNotExist:
            return HttpResponse("Cart error, please try again.", status=404)
        user.profile.cart.remove(cart_item)

        return HttpResponseRedirect('/stocks/cart')
    else:
        return HttpResponse("Unauthorized: are you logged in?", status=400)


@csrf_exempt
def place_order(request):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(pk=request.user.id)
            profile = Profile.objects.get(pk=request.user.id)
            if user.profile.user_type == 'B' and 'customer_id' in request.session:
                user = User.objects.get(pk=request.session['customer_id'])
            order = Order.objects.create(user_id=user, order_type='B')
            cart_items = request.user.profile.cart.all()

            for item in cart_items:
                stock = StockDetails.objects.get(stock_id=item.stock)
                order_details = OrderDetails.objects.create(order=order,
                                                            stock_id=item.stock,
                                                            quantity=item.quantity,
                                                            purchase_price=stock.current_price)

            request.user.profile.cart.all().delete()
            if 'customer_id' in request.session:
                del request.session['customer_id']
            return HttpResponseRedirect('/dashboard/orders/' + str(order.order_id))

        except DatabaseError:
            return HttpResponse("Database Error", status=400)
    else:
        return HttpResponse("Unauthorized: are you logged in?", status=400)
