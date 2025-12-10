from rest_framework import serializers
from ..models import User 
from django.contrib.auth import password_validation, hashers

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User 
        fields = [
            'id',
            'username',
            'email',
            'password',
            'confirm_password'
        ]

    def validate(self, data):
        password = data['password']
        confirm_password = data.pop('confirm_password', None)

        if password != confirm_password:
            raise serializers.ValidationError({
                'confirm_password': 'Passwords do not match.'
            })
        password_validation.validate_password(password)
        data['password'] = hashers.make_password(password)
        return data