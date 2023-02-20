from django.contrib.auth.models import AbstractUser
from django.db import models

USER_TYPE_CHOICES = (
    ('shop', 'Магазин'),
    ('buyer', 'Покупатель'),
)

ORDER_STATUS_CHOICES = (
    ('basket', 'В корзине'),
    ('accepted', 'Принят'),
    ('payed', 'Оплачен'),
    ('posted', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('returned', 'Возвращён'),
    ('cancelled', 'Отменён'),
    ('filling', 'Собирается'),
)


class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    user_type = models.CharField(verbose_name='Тип пользователя',
                                 choices=USER_TYPE_CHOICES,
                                 max_length=5,
                                 default='buyer')
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Пользователь'


class Shop(models.Model):
    name = models.CharField(max_length=30, verbose_name='Название')
    url = models.URLField(verbose_name='Ссылка')
    filename = models.CharField(max_length=40, verbose_name='Имя файла')

    class Meta:
        verbose_name = 'Магазин'


class Category(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    shops = models.ManyToManyField(Shop, verbose_name='Магазин')
    name = models.CharField(max_length=120, verbose_name='Название')

    class Meta:
        verbose_name = 'Категория'


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    name = models.CharField(max_length=150, verbose_name='Название')

    class Meta:
        verbose_name = 'Продукт'


class ProductInfo(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Продукт', related_name='product_infos')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, verbose_name='Магазин', related_name='product_infos')
    name = models.CharField(max_length=170, verbose_name='Наименование')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.PositiveIntegerField(verbose_name='Цена')
    price_rrc = models.PositiveIntegerField(verbose_name='Рекомендуемая розничная цена')

    class Meta:
        verbose_name = 'Информация по продукту'


class Parameter(models.Model):
    name = models.CharField(max_length=60, verbose_name='Название параметра')

    class Meta:
        verbose_name = 'Параметр'


class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo, on_delete=models.CASCADE, verbose_name='Информация')
    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE, verbose_name='Параметр')
    value = models.CharField(max_length=70, verbose_name='Значение')

    class Meta:
        verbose_name = 'Параметр продукта'


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='order', blank=True)
    dt = models.DateTimeField(verbose_name='Дата заказа', auto_now=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES)

    class Meta:
        verbose_name = 'Заказ'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name='Заказ', on_delete=models.CASCADE, related_name='ordered_items')
    product = models.ForeignKey(ProductInfo, on_delete=models.CASCADE, verbose_name='Продукт', related_name='ordered_items')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, verbose_name='Магазин',  related_name='order_item')
    quantity = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Пункт заказа'


class Contact(models.Model):
    type = models.CharField(max_length=50, verbose_name='Тип контакта')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Заказчик', related_name='contact', blank=True)
    value = models.CharField(max_length=150, verbose_name='Значение')

    class Meta:
        verbose_name = 'Контакт'

