from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from carts.models import Cart, CartItem
from carts.serializers import CartSerializer, CartItemSerializer, CartItemWriteSerializer


class IsSuperUserOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        if request.method in ['POST']:
            return True

        if request.user == 'GET' or request.user == 'PUT' or request.method == 'PATCH':
            return request.user == view.get_object().user

        return False


class BasePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'pageSize'


# class CartViewSet(viewsets.ModelViewSet):
#     permission_classes = [IsSuperUserOrReadOnly, IsAuthenticated]
#     queryset = Cart.objects.all().order_by('-id')
#     serializer_class = CartSerializer
#     pagination_class = BasePagination
#     # search_fields = ['user__username', 'product__name', 'product__price']
#     ordering_fields = '__all__'
#     #
#     # def get_queryset(self):
#     #     user = self.request.user
#     #     return Cart.objects.filter(user=user)
#
#
# class CartItemViewSet(viewsets.ModelViewSet):
#     permission_classes = [IsSuperUserOrReadOnly]
#     queryset = CartItem.objects.all()
#     serializer_class = CartItemSerializer
#
    # def create(self, request, *args, **kwargs):
    #     user = request.user
    #     cart = Cart.objects.filter(user=user)
    #
    #     if cart.exists():
    #         request.data['cart'] = cart.get().id
    #         return super().create(request, *args, **kwargs)
    #
    #     new_cart = CartSerializer(instance=user).data
    #     request.data['cart'] = new_cart.get().id
    #     return super().create(request, *args, **kwargs)
#
#     # def perform_create(self, serializer):
#     #     user = self.request.user
#     #     cart = Cart.objects.filter(user=user)
#     #
#     #     if cart.exists():
#     #         serializer['cart'] = cart.get().id
#     #         return super().perform_create(serializer)
#     #
#     #     new_cart = CartSerializer(instance=user).data
#     #     serializer['cart'] = new_cart.get().id
#     #     return super().perform_create(serializer)


class CartViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSuperUserOrReadOnly]
    pagination_class = BasePagination
    queryset = Cart.objects.all()
    serializer_class = CartSerializer


class CartItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSuperUserOrReadOnly]
    pagination_class = BasePagination
    queryset = CartItem.objects.all()
    serializer_class_by_actions = {
        "GET": CartItemSerializer,
        "POST": CartItemWriteSerializer,
    }

    def get_serializer_class(self):
        return self.serializer_class_by_actions[self.request.method]

    def create(self, request, *args, **kwargs):
        user = request.user
        cart = Cart.objects.filter(user=user)

        if cart.exists():
            request.data['cart'] = cart.get().id
            return super().create(request, *args, **kwargs)

        new_cart = CartSerializer(data={
            "user": request.user.id
        })
        if new_cart.is_valid():
            new_cart.save()
            request.data['cart'] = new_cart.instance.id
            return super().create(request, *args, **kwargs)

        return Response("Error", status=status.HTTP_400_BAD_REQUEST)
