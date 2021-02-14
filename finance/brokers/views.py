from django.db import DatabaseError
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, QueryDict
from django.views.decorators.csrf import csrf_exempt
from dashboard.models import Order, OrderDetails
from django.contrib.auth.models import User
from rest_framework import serializers
from stocks.models import Company, StockDetails
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.debug import sensitive_post_parameters, sensitive_variables
from users.models import Profile
# DEPENDENCY ON DASHBOARD!!!
from dashboard.views import create_order_list
from dashboard.serializers import deserialize_user
from stocks.views import specificStock

# Create your views here.
def show_users(request):
    """ returns list of users managed by broker """
    try:
        user = User.objects.get(pk=request.user.id)
        profile = Profile.objects.get(pk=request.user.id)
    except ObjectDoesNotExist:
        return HttpResponse("user not found", status=404)
    if request.user.is_authenticated and user.profile.user_type == 'B':
        if request.method == 'GET':
            user_list = profile.managed_users.all().values()
            return render(request, 'brokers/customers.html', {"data": user_list, "broker": True}, status=200)
    return HttpResponse('not authorized', status=400)

def specific_customer(request, customer_id):
    """ shows specific customer profile """
    try:
        user = User.objects.get(pk=request.user.id)
        profile = Profile.objects.get(pk=request.user.id)
    except ObjectDoesNotExist:
        return HttpResponse("user not found", status=404)
    if request.user.is_authenticated and user.profile.user_type == 'B':
        try:
            customer = User.objects.get(pk=customer_id)
            if request.method == 'GET':
                if 'customer_id' in request.session:
                    del request.session['customer_id']
                order_list = create_order_list(Order.objects.filter(user_id=customer))
                renderData = {
                    "orders": order_list, "data": deserialize_user(customer), "broker": True
                }
                return render(request, 'brokers/customer_profile.html', renderData, status=200)
        except DatabaseError:
            return HttpResponseRedirect('/', status=404)
    return HttpResponse('not authorized', status=400)

@csrf_exempt
def place_order(request, customer_id):
    try:
        user = User.objects.get(pk=request.user.id)
    except ObjectDoesNotExist:
        return HttpResponse("user not found", status=404)
    if request.user.is_authenticated and user.profile.user_type == 'B':
        request.session['customer_id'] = customer_id
        return redirect('stocks:specificStock')
    return HttpResponse('not authorized', status=400)

@csrf_exempt
def view_order(request, customer_id, order_id):
    try:
        user = User.objects.get(pk=request.user.id)
    except ObjectDoesNotExist:
        return HttpResponse("user not found", status=404)
    if request.user.is_authenticated and user.profile.user_type == 'B':
        request.session['customer_id'] = customer_id
        return redirect('/dashboard/orders/' + str(order_id))
    return HttpResponse('not authorized', status=400)

