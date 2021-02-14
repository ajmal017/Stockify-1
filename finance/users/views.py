from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, viewsets, serializers, status
from django.contrib.auth.models import User
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.exceptions import APIException
from .serializers import deserialize_user


# Create your views here.
class CsrfExempt(SessionAuthentication):
    """
    Overrides the CSRF checking to provide the same functionality
    as the csrf_exempt decorator when using rest framework
    """
    def enforce_csrf(self, request):
        return


class NotAuthenticated401Error(APIException):
    """
    Class containing the error code and error message if the
    user is not authenticated in the system
    """
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "unauthorized: user not authenticated"


class IsAuthenticated(permissions.BasePermission):
    """
    Overrides the default permission and checks if
    the user is properly authenticated in the system
    """
    def has_permission(self, request, view):
        """
        Checks the request to see if the user is authenticated
        :param request: the current request from the user
        :param view: the view set (not used)
        :return: a 401 error if the user is not authenticated
        """
        if not request.user.is_authenticated:
            raise NotAuthenticated401Error

        else:
            return True


class Users(APIView):
    authentication_classes = [CsrfExempt, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Handles the get request for the users
        :param request: the request from the user
        :return: a JSON array containing all the users
        """
        data = []

        for u in User.objects.all():
            data.append(deserialize_user(u))

        return Response(data, content_type='application/json')
