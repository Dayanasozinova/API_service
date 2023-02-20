from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import URLValidator
from django.http import JsonResponse
from requests import get
from rest_framework import viewsets, permissions, status, generics
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from yaml import Loader, load as load_yaml
from demo.models import User, ProductInfo, Shop, Category, Product, Parameter, ProductParameter, Order, OrderItem
from demo.serializers import UserSerializer, GroupSerializer, ProductInfoSerializer, OrderSerializer, \
    RegisterSerializer, ProductAddSerializer
from demo.tasks import send_email


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        message = "Successful registrainon!"
        send_email.delay(email, message)
        return self.create(request, *args, **kwargs)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class PriceUpdateView(APIView):

    def post(self, request, *args, **kwargs):
        url = request.data.get('url')
        if not request.user.is_authenticated:
            return JsonResponse({'403', 'Нужна аутентификация'})
        if not request.user.user_type == 'shop':
            return JsonResponse({'403', 'Действие для магазинов'})

        if url:
            try:
                URLValidator(url)
            except ValidationError as a:
                return JsonResponse({'400', str(a)})

            data = load_yaml(get(url).content, Loader=Loader)

            try:
                user = User.objects.get(id=request.user.id)
            except ObjectDoesNotExist as a:
                JsonResponse({'404', str(a)})
            shop, _ = Shop.objects.get_or_create(name=data['shop'], id_user=user)

            for category in data['categories']:
                category_object, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
                category_object.shops.add(shop.id)
                category_object.save()

            ProductInfo.objects.filter(shop=shop.id).delete()
            for item in data['goods']:
                try:
                    category = Category.objects.get(id=item['category'])
                except ObjectDoesNotExist as a:
                    JsonResponse({'404', str(a)})

                product, _ = Product.objects.get_or_create(category=category, name=item['name'])
                product_info, _ = ProductInfo.objects.get_or_create(product=product,
                                                                    shop=shop,
                                                                    external_id=item['id'],
                                                                    model=item['model'],
                                                                    price=item['price'],
                                                                    price_rrc=item['price_rrc'],
                                                                    quantity=item['quantity'])

                for name, value in item['parameters'].items():
                    parameter_object, _ = Parameter.objects.get_or_create(name=name)
                    ProductParameter.objects.create(product_info=product_info,
                                                    parameter=parameter_object,
                                                    value=value)
            return JsonResponse({'Status': status.HTTP_201_CREATED, 'data': request.data})
        return JsonResponse({'400', 'Цена с таким URL не найдена'})

    def get(self, *args, **kwargs):
        return JsonResponse({'Status': status.HTTP_200_OK, 'method': 'get'})


class CatalogViewSet(viewsets.ModelViewSet):
    queryset = ProductInfo.objects.all()
    serializer_class = ProductInfoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProductAddView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = ProductAddSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'403', 'Требуется авторизация'})

        try:
            user = User.objects.get(id=request.user.id)
        except ObjectDoesNotExist as a:
            JsonResponse({'Status': status.HTTP_404_NOT_FOUND, 'Error': str(a)})

        order, _ = Order.objects.get_or_create(user=user, status='basket')
        try:
            product = ProductInfo.objects.get(id=request.data['product'])
        except ObjectDoesNotExist as a:
            JsonResponse({'Status': status.HTTP_404_NOT_FOUND, 'Error': str(a)})
        add_item, _ = OrderItem.objects.get_or_create(order=order,
                                                      product=product,
                                                      shop=product.shop,
                                                      quantity=request.data['quantity'])

        return JsonResponse({'Status': status.HTTP_201_CREATED, 'data': request.data})


class ConfirmOrderView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': status.HTTP_403_FORBIDDEN, 'Error': 'Log in required.'})

        try:
            user = User.objects.get(id=request.user.id)
        except ObjectDoesNotExist as a:
            JsonResponse({'Status': status.HTTP_404_NOT_FOUND, 'Error': str(a)})
        try:
            order = Order.objects.get(user=user, status='basket')
        except ObjectDoesNotExist as a:
            JsonResponse({'Status': status.HTTP_404_NOT_FOUND, 'Error': str(a)})
        order.status = 'accepted'
        order.save()
        send_email.delay(user.email, 'Заказ успешно оформлен')
        return JsonResponse({'Status': status.HTTP_201_CREATED, 'data': request.data})


