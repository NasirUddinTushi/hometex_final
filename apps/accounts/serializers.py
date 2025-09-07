from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Customer, CustomerAddress

# Register Serializer
class CustomerRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Customer.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

# Login Serializer
class CustomerLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid email or password")
        data['user'] = user
        return data

# Profile Serializer
class CustomerProfileSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(source='id', read_only=True)
    created_at = serializers.DateTimeField(source='date_joined', read_only=True)

    class Meta:
        model = Customer
        fields = ['customer_id', 'first_name', 'last_name', 'email', 'created_at']

# Address Serializer
class CustomerAddressSerializer(serializers.ModelSerializer):
    address_id = serializers.IntegerField(source='id', read_only=True)
    customer_id = serializers.IntegerField(source='customer.id', read_only=True)

    class Meta:
        model = CustomerAddress
        fields = [
            'address_id',
            'customer_id',
            'address_type',
            'street_address',
            'city',
            'state',
            'postal_code',
            'country',
            'is_default'
        ]
