from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from demo.models import User, Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem, Contact


@admin.register(User)
class UserAdmin(UserAdmin):
    model = User
    list_display = ['email', 'first_name', 'last_name', 'is_staff']


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'filename']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['category', 'name']


@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    list_display = ['product', 'shop', 'name', 'quantity', 'price', 'price_rrc']


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    list_display = ['product_info', 'parameter', 'value']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'dt', 'status']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'shop', 'quantity']


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['type', 'user', 'value']

