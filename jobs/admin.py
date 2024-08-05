
# Register your models here.
from django.contrib import admin
from .models import Product, ProductVariation

class ProductVariationInline(admin.TabularInline):
    model = ProductVariation
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductVariationInline]

admin.site.register(ProductVariation)
