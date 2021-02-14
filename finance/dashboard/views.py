from django.db import DatabaseError
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, QueryDict
from django.views.decorators.csrf import csrf_exempt
from dashboard.models import Order, OrderDetails
from django.contrib.auth.models import User
from rest_framework import serializers
from stocks.models import Company, StockDetails
from django.forms.models import model_to_dict
from .serializers import deserialize_user
from . import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.debug import sensitive_post_parameters, sensitive_variables
from django.db.models import Count
import random
import json
import requests
import re
import bs4 as bs
import pickle

# Create your views here.
@csrf_exempt
def dashboard(request):
    """
    returns recent orders by user
    """
    if request.user.is_authenticated:
        if request.method == 'GET':
            user = ""
            orders = ""
            try:
                user = User.objects.get(pk=request.user.id)
                orders = Order.objects.filter(user_id=request.user)
            except ObjectDoesNotExist:
                return HttpResponse('Error occurred with user or recent orders', status=404)
            sold = 0
            order_list = []
            for o in orders:
                if str(o.order_type) == 'B':
                    if OrderDetails.objects.filter(order_id=o.order_id).exists():
                        details = OrderDetails.objects.filter(order_id=o.order_id)
                        total = 0
                        for item in details:
                            total += item.quantity * item.purchase_price
                        order_list.append({'order_id': o.order_id, 'order_type': 'BUY',
                                           'order_date': o.createdAt,
                                           'total': total})

                elif str(o.order_type) == 'S':
                    sold += 1
                    if OrderDetails.objects.filter(order_id=o.order_id).exists():
                        details = OrderDetails.objects.filter(order_id=o.order_id)
                        total = 0
                        for item in details:
                            total += item.quantity * item.purchase_price
                        order_list.append({'order_id': o.order_id, 'order_type': 'SELL',
                                           'order_date': o.createdAt,
                                           'total': total})
            renderBody = {'data': order_list, 'total': len(order_list), 'sold': sold, 'broker': False}
            if user.profile.user_type == 'B':
                renderBody['broker'] = True
            return render(request, 'dashboard/index.html', renderBody, status=200)

        else:
            return HttpResponse("Method not allowed on /", status=405)
    else:
        return HttpResponse("Unauthorized: Not Logged In", status=401)

@csrf_exempt
@sensitive_post_parameters()
def search_company(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            count = Company.objects.aggregate(count=Count('company_id'))['count']
            random_index = random.randint(15, count - 1)
            random_start_index = random_index - 15
            sample = Company.objects.all()[random_start_index: random_index]
            companies = []
            for s in sample:
                if len(s.companyName) < 1000:
                    companies.append({"name": s.companyName,
                                    "symbol": s.symbol})

            return render(request, 'dashboard/search.html', {'data': companies}, status=200)
        elif request.method == 'POST':
            if request.user.is_authenticated:
                try:
                    stock_ticker = request.POST['stock'].lower()
                    print(stock_ticker)
                    company = Company.objects.get(symbol=stock_ticker)
                except ObjectDoesNotExist:
                    return HttpResponse("Company does not exist.", status=404)

                company_prof = {
                    "Company Name": company.companyName,
                    "Stock Ticker": company.symbol.upper(), 'Sector': company.sector,
                    'Industry': company.industry,
                    'Employees': company.employees,
                    'Website': company.homePage, 'Exchange': company.exchange
                }
                return render(request, 'dashboard/company_details.html',
                              {"company": company_prof, 'Description': company.description, },
                              status=200)
        else:
            return HttpResponse("Method not allowed on /", status=405)

    else:
        return HttpResponse('user is not authenticated', status=400)

@csrf_exempt
@sensitive_post_parameters()
def search_company_with_id(request, company_id):
    try:
        company = Company.objects.get(pk=company_id)
    except ObjectDoesNotExist:
        return HttpResponse("Company does not exist in db yet", status=404)
    if request.method == 'GET':
        if request.user.is_authenticated:
            company_prof = {
                "Company Name": company.companyName,
                "Stock Ticker": company.symbol.upper(), 'Sector': company.sector,
                'Industry': company.industry,
                'Employees': company.employees,
                'Website': company.homePage, 'Exchange': company.exchange
            }
            return render(request, 'dashboard/company_details.html',
                          {"company": company_prof, 'Description': company.description, },
                          status=200)
        else:
            return HttpResponse('user is not authenticated', status=400)
    else:
        return HttpResponse("Method not allowed on /", status=405)

@csrf_exempt
@sensitive_post_parameters()
def search_company_with_ticker(request, company_name):
    """ renders company info, updates and deletes company """
    company = ""
    user = ""
    try:
        company = Company.objects.get(symbol=company_name)
    except ObjectDoesNotExist:
        return HttpResponse("Company does not exist in db yet", status=404)
    try:
        user = User.objects.get(user=request.user)
    except ObjectDoesNotExist:
        return HttpResponse("User does not exist", status=404)
    if request.method == 'GET':
        if request.user.is_authenticated:
            company_prof = {
                "Company Name": company.companyName,
                "Stock Ticker": company.symbol.upper(), 'Sector': company.sector, 'Industry': company.industry,
                'Employees': company.employees,
                'Website': company.homePage, 'Exchange': company.exchange
            }
            return render(request, 'dashboard/company_details.html',
                          {"company": company_prof, 'Description': company.description,}, status=200)
        else:
            return HttpResponse('user is not authenticated', status=400)
    elif request.method == 'PATCH':
        if (
            request.user.is_authenticated and 
            (company.manager_id == request.user.id or 
            User.objects.get(user=request.user).user_type == 'A')
        ):
            body = json.loads(request.body.decode('utf-8'))
            for key, value in body.items():
                if company.field_exists(key):
                    setattr(company, key, value)
            company.save()
            return JsonResponse(model_to_dict(company), safe=False)
    elif request.method == 'DELETE':
        if (
            request.user.is_authenticated and 
            User.objects.get(user=request.user).user_type == 'A'
            ):
            company.delete()
            return HttpResponse('Delete was successful')
        else:
            return HttpResponse('Permission denied.', status=400)
    else:
        return HttpResponse("method not allowed", status=400)


@csrf_exempt
@sensitive_variables()
def profile(request):
    """

    :param request:
    :return:
    """
    if request.user.is_authenticated:
        try:
            user = User.objects.get(pk=request.user.id)
            profile = Profile.objects.get(user=user)
        except ObjectDoesNotExist:
            return HttpResponse("user does not exist", status=404)
        if request.method == 'GET':
            renderBody = {"data": deserialize_user(user)}
            if user.profile.user_type == 'B':
                renderBody["broker"] = True
            return render(request, 'dashboard/profile.html', renderBody, status=200)

        elif request.method == 'PATCH' or request.method == 'POST':
            user = User.objects.get(pk=request.user.id)

            if request.method == 'PATCH':
                data = request.body.decode('utf-8')
                data = json.loads(data)
            else:
                data = request.POST

            serializer = serializers.UserSerializer(data=data)

            if serializer.is_valid():
                fname = serializer.data.get('first_name')
                lname = serializer.data.get('last_name')
                email = serializer.data.get('email')
                phone = serializer.data.get('phone')
                description = serializer.data.get('description')
                country = serializer.data.get('country')

                if email != "":
                    user.email = email

                if fname != "":
                    user.first_name = fname

                if lname != "":
                    user.last_name = lname

                if phone != "":
                    profile.phone = phone

                if description != "":
                    profile.message = description

                if country != "":
                    profile.country = country

            user.save()
            profile.save()
            renderBody = {"data": deserialize_user(user)}
            if user.profile.user_type == 'B':
                renderBody["broker"] = True
            return render(request, 'dashboard/profile.html', renderBody, status=200)

        elif request.method == 'DELETE':
            User.objects.get(pk=request.user.id).delete()

            return HttpResponse("User Account Deleted", status=405)

        else:
            return HttpResponse("Method not allowed on /", status=405)

    else:
        return HttpResponse("Unauthorized: Not Logged In", status=401)

@csrf_exempt
@sensitive_variables()
def all_orders(request):
    """

    :param request:
    :return:
    """
    if request.user.is_authenticated:
        if request.method == 'GET':
            try:
                user = User.objects.get(pk=request.user.id)
                orders = Order.objects.filter(user_id=request.user)
            except ObjectDoesNotExist:
                return HttpResponse("Error with user and/or recent orders.", status=404)
            order_list = create_order_list(orders)
            renderBody = {'data': order_list}
            if user.profile.user_type == 'B':
                renderBody["broker"] = True
            return render(request, 'dashboard/orders_table.html', renderBody, status=200)
        elif request.method == 'POST':
            order = Order.objects.create(user_id=request.user)

            return JsonResponse({'order_id': order.order_id, 'order_type': order.order_type,
                               'order_date': order.createdAt}, status=201)

        # PATCH is used to transfer and order to another user
        elif request.method == 'PATCH':
            data = request.body.decode('utf-8')
            data = json.loads(data)
            order_id = data['order_id']
            order_type = data['order_type']

            order = Order.objects.get(pk=order_id)
            order.order_type = order_type
            order.save()

            #order.user_id = data['user_id']
            return JsonResponse({'order_id': order.order_id, 'order_type': order.order_type,
                               'order_date': order.createdAt}, status=200)

        else:
            return HttpResponse("Method not allowed on /", status=405)

    else:
        return HttpResponse("Unauthorized: Not Logged In", status=401)


@csrf_exempt
@sensitive_post_parameters()
def order_details(request, order_id):
    """

    :param request:
    :param order_id:
    :return:
    """
    if request.user.is_authenticated:
        if request.method == 'GET':
            try:
                order = Order.objects.get(order_id=order_id)
                order_details = OrderDetails.objects.filter(order=order)
            except ObjectDoesNotExist:
                return HttpResponse("Order does not exist", status=404)

            if not order_details:
                return HttpResponse('Unable to get details for this order', status=401)

            data = []
            if str(order.order_type) == 'B':
                sum = 0
                for o in order_details:
                    order_id = o.order_id
                    sum += o.purchase_price * o.quantity
                    url = o.stock_id.homePage
                    if url.startswith('http'):
                        url = re.sub(r'https?://', '', url)

                    if url.startswith('www.'):
                        url = re.sub(r'www.', '', url)

                    data.append({'Order ID': o.order_id, 'date': o.createdAt, 'price': o.purchase_price,
                            'quantity': o.quantity, 'company': o.stock_id.companyName,
                            'total': o.purchase_price * o.quantity, 'image': url})

                return render(request, 'dashboard/order_details.html', {'data': data,
                                                                        'order_id': order_id,
                                                                        'sum': sum,
                                                                        'date': order.createdAt}, status=200)

            elif str(order.order_type) == 'S':
                sum = 0
                buy = 0
                for o in order_details:
                    order_id = o.order_id
                    buy += o.purchase_price * o.quantity
                    sum += o.sell_price * o.quantity
                    url = o.stock_id.homePage
                    if url.startswith('http'):
                        url = re.sub(r'https?://', '', url)

                    if url.startswith('www.'):
                        url = re.sub(r'www.', '', url)

                    data.append({'Order ID': o.order_id, 'date': o.createdAt, 'price': o.purchase_price,
                         'sell': order.editedAt, 'quantity': o.quantity, 'company': o.stock_id.companyName,
                         'total': o.sell_price * o.quantity, 'image': url, 'sell_price': o.sell_price})

                return render(request, 'dashboard/order_details_sold.html', {'data': data,
                                                                             'order_id': order_id,
                                                                             'sum': sum,
                                                                             'buy': buy,
                                                                             'date': order.editedAt,
                                                                             'net': sum - buy}, status=200)

        elif request.method == 'POST' or request.method == 'DELETE':
            try:
                order = Order.objects.get(order_id=order_id)
                order_details = OrderDetails.objects.filter(order=order)
            except ObjectDoesNotExist:
                return HttpResponse("Order does not exist", status=404)
            #company_object = Company.objects.get(pk=order_details.stock_id.company_id)

            for item in order_details:
                try:
                    company_object = Company.objects.get(pk=item.stock_id.company_id)
                except ObjectDoesNotExist:
                    continue
                data = requests.get('https://cloud.iexapis.com/stable/stock/' + company_object.symbol
                                    + '/quote?token=pk_8eb2d1bd40044c2181ad3cd603509bcb')

                price_data = data.json()

                if StockDetails.objects.filter(stock_id=company_object).exists():
                    stock_object = StockDetails.objects.get(stock_id=company_object)
                    stock_object.openBid = price_data['open']
                    stock_object.closeBid = price_data['close']
                    stock_object.volume = price_data['latestVolume']
                    stock_object.date = price_data['latestUpdate']
                    stock_object.current_price = price_data['latestPrice']

                else:
                    StockDetails.objects.create(stock_id=company_object, openBid=price_data['open'],
                                                closeBid=price_data['close'],
                                                volume=price_data['latestVolume'],
                                                date=price_data['latestUpdate'],
                                                current_price=price_data['latestPrice'])

                item.sell_price = price_data['latestPrice']
                item.save()

            order.order_type = 'S'
            order.save()

            return redirect('dashboard:orders')

        # Change so only brokers can patch orders
        elif request.method == 'PATCH':
            try:
                order = OrderDetails.objects.get(pk=order_id)
            except ObjectDoesNotExist:
                return HttpResponse("order does not exist", status=404)
            data = QueryDict(request.body)

            quantity = data['quantity']
            order.quantity = quantity

            if data['unit_price'] != "":
                if request.user.user_type == 'BROKER':
                    order.unit_price = data['purchase_price']

                else:
                    return HttpResponse("Unauthorized: must be a broker or admin", status=401)

            return JsonResponse(json.dumps(order), safe=False)

        else:
            return HttpResponse("Method not allowed on /", status=405)

    else:
        return HttpResponse("Unauthorized: Not Logged In", status=401)


def create_order_list(orders):
    order_list = []
    for o in orders:
        if str(o.order_type) == 'B':
            if OrderDetails.objects.filter(order_id=o.order_id).exists():
                details = OrderDetails.objects.filter(order_id=o.order_id)
                comp = 0
                shares = 0
                total = 0
                for item in details:
                    comp += 1
                    shares += item.quantity
                    total += item.purchase_price * item.quantity

                order_list.append({'order_id': o.order_id, 'order_type': 'BUY',
                                    'order_date': o.createdAt,
                                    'companies': comp,
                                    'sell': 'X',
                                    'shares': shares,
                                    'total': total})

        elif str(o.order_type) == 'S':
            if OrderDetails.objects.filter(order_id=o.order_id).exists():
                details = OrderDetails.objects.filter(order_id=o.order_id)
                comp = 0
                shares = 0
                buy = 0
                sell = 0
                for item in details:
                    comp += 1
                    shares += item.quantity
                    buy += item.purchase_price * item.quantity
                    sell += item.sell_price * item.quantity

                order_list.append({'order_id': o.order_id, 'order_type': 'SELL',
                                    'order_date': o.editedAt,
                                    'companies': comp,
                                    'sell': sell,
                                    'shares': shares,
                                    'total': buy})
    return order_list