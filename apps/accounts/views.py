from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login, logout
from rest_framework import status

from .models import Customer, CustomerAddress
from .serializers import (
    CustomerRegisterSerializer,
    CustomerLoginSerializer,
    CustomerProfileSerializer,
    CustomerAddressSerializer
)


# Register
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomerRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "Registration successful"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Login
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)  # Session-based login
            return Response({
                "message": "Login successful",
                "user": {
                    "customer_id": user.id,
                    "email": user.email
                }
            }, status=status.HTTP_200_OK)
        return Response({"message": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)



# Logout
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"detail": "Logout successful"}, status=status.HTTP_200_OK)


# Profile
class ProfileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user_id = request.query_params.get("user_id")
        if user_id:
            # Return single customer profile by ID
            customer = Customer.objects.filter(id=user_id).first()
            if not customer:
                return Response({"detail": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = CustomerProfileSerializer(customer)
            return Response({"items": [serializer.data]}, status=status.HTTP_200_OK)

        # No user_id: return all customer profiles
        customers = Customer.objects.all()
        serializer = CustomerProfileSerializer(customers, many=True)
        return Response({"items": serializer.data}, status=status.HTTP_200_OK)



# Customer Address
class CustomerAddressView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # যদি query param এ customer_id থাকে
        customer_id = request.query_params.get("customer_id")
        if customer_id:
            customer = Customer.objects.filter(id=customer_id).first()
            if not customer:
                return Response({"detail": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
            addresses = CustomerAddress.objects.filter(customer=customer)
        elif request.user.is_authenticated:
            # Logged-in user
            addresses = CustomerAddress.objects.filter(customer=request.user)
        else:
            # Guest user, provide email in query param
            email = request.query_params.get("email")
            if not email:
                return Response({"detail": "Email or customer_id query parameter required"}, status=status.HTTP_400_BAD_REQUEST)
            customer = Customer.objects.filter(email=email).first()
            if not customer:
                return Response({"detail": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
            addresses = CustomerAddress.objects.filter(customer=customer)

        serializer = CustomerAddressSerializer(addresses, many=True)
        return Response({
            "items": serializer.data,
            "count": addresses.count(),
            "hasMore": False,
            "limit": 25,
            "offset": 0
        }, status=status.HTTP_200_OK)
