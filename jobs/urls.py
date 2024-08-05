from django.urls import path
from .views import product_list, product_data,upload_excel

urlpatterns = [
    path('products/', product_list, name='product_list'),
     path('', product_list, name='product_list'),
    path('products/data/', product_data, name='product_data'),
     path('products/upload_excel/', upload_excel, name='upload_excel'),
]
