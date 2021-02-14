from rest_framework import serializers

def deserialize_user(user):
    """
    Deserializes the user into JSON format to be returned
    in the method handling the request
    :param user: the user to convert into JSON
    :return: JSON object of the user
    """
    if user is None:
        return None

    else:
        return {
            'id': user.id, 'username': user.username, 'email': user.email,
            'first_name': user.first_name , 'last_name': user.last_name,
            'phone': user.profile.phone, 'country': user.profile.country,
            'description': user.profile.description, 'user_type': user.profile.user_type
        }


class UserSerializer(serializers.Serializer):
    """
    Serializer for a member that checks the user information
    """
    email = serializers.CharField(required=False, allow_blank=True, max_length=30, default="")
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=30, default="")
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=30, default="")
    phone = serializers.CharField(required=False, allow_blank=True, max_length=10, default="")
    country = serializers.CharField(required=False, allow_blank=True, max_length=50, default="")
    description = serializers.CharField(required=False, max_length=1000, allow_blank=True, default="")