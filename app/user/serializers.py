"""
This file implements a serializer widget to help translate
model config and state into and out of JSON so we can
communicate with the API.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for our user object"""
    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Create a new user with an encrypted PW"""
        return get_user_model().objects.create_user(**validated_data)
