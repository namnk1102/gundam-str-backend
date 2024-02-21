from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from .models import Order
from .serializers import OrderSerializer, CreateOrderSerializer


class IsSuperUserOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        return request.user and request.user.is_authenticated


class BasePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'pageSize'


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSuperUserOrReadOnly]
    pagination_class = BasePagination
    queryset = Order.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OrderSerializer
        return CreateOrderSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        with transaction.atomic():
            order_details = instance.order_details.all()
            for order_detail in order_details:
                product = order_detail.product
                quantity = order_detail.quantity
                product.quantity += quantity
                product.save()

            self.perform_destroy(instance)

        return Response(status=status.HTTP_204_NO_CONTENT)
