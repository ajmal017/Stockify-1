from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.debug import sensitive_post_parameters, sensitive_variables
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
@csrf_exempt
def home(request):
    """
    Renders the homepage or returns not allowed depending on the type of request method
    :param request: the type of request by the client
    :return: render of the home page
    """
    if request.method == 'GET':
        if request.user.is_authenticated:
            return render(request, 'home/index_signed_in.html', status=200)
        else:
            return render(request, "home/index.html", status=200)
    else:
        return HttpResponse("Method not allowed on /", status=405)

@csrf_exempt
def contact(request):
    if request.method == 'GET':
        return render(request, "home/contact.html", status=200)

@csrf_exempt
def about(request):
    if request.method == 'GET':
        return render(request, "home/about.html", status=200)