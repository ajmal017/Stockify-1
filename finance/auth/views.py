from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from .forms import RegistrationForm, SigninForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout, login
from django.views.decorators.debug import sensitive_post_parameters, sensitive_variables
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
@sensitive_post_parameters()
@csrf_exempt
def register(request):
    """
    Renders the registration form for the user. If the submit button is pressed, then the
    user is registered in the database. Checks for valid input as well as valid passwords.
    :param request: the type of request by the client
    :return: render of the registration form
    """
    if request.method == 'GET':
        form = RegistrationForm()

    elif request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            p1 = form.cleaned_data.get('p1')
            p2 = form.cleaned_data.get('p2')
            if p1 == p2:
                user = User.objects.create_user(form.cleaned_data.get('username'),
                                           form.cleaned_data.get('email'),
                                           p1)
                user.first_name = form.cleaned_data.get('first_name')
                user.last_name = form.cleaned_data.get('last_name')
                user.profile.user_type = form.cleaned_data.get('user_type')
                user.save()

                return HttpResponseRedirect('/auth/signin')
            else:
                return HttpResponse('Passwords did not match', status=400)
        else:
            return HttpResponse('Invalid registration request', status=400)
    else:
        return HttpResponse('Method not allowed on /auth/register', status=405)

    return render(request, 'auth/register.html', {'form': form}, status=200)

@csrf_exempt
@sensitive_post_parameters()
def signin(request):
    """
    Renders the sign in page with a form for the username and password. Checks to make sure
    the user is in the database and authenticates, otherwise error message is shown
    :param request: the type of request by the client
    :return: render of the sign in page
    """
    if request.method == 'GET':
        form = SigninForm()

    elif request.method == 'POST':
        form = SigninForm(request.POST)

        if form.is_valid():
            u = form.cleaned_data.get('username')
            p = form.cleaned_data.get('p')
            user = authenticate(username=u, password=p)

            if user and user.is_active:
                login(request, user)

                return HttpResponseRedirect('/dashboard')
            else:
                return HttpResponse('Invalid credentials', status=401)

        else:
            return HttpResponse('Bad login form', status=400)

    else:
        return HttpResponse('Method not allowed on /auth/signin', status=405)

    return render(request, 'auth/signin.html', {'form': form}, status=200)

@csrf_exempt
@sensitive_variables()
def signout(request):
    """
    Signs out the user if they are already signed into their account. Checks to make sure
    user is signed in and logs them out.
    :param request: the type of request by the client
    :return: a confirmation that the user is signed out
    """
    if request.method == 'GET':
        if request.user.is_authenticated:
            logout(request)
            return render(request, 'home/index.html', status=200)

        else:
            return HttpResponse('Not logged in', status=200)

    else:
        return HttpResponse('Method not allowed on auth/signout', status=405)
