from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import admin
from .models import Product, ProductVariation
from django.core.exceptions import ValidationError
from django.contrib.admin.views.decorators import staff_member_required
import pandas as pd
from django.http import JsonResponse
from django.core import serializers
import os



def upload_excel(request):
    error_message = None
    if request.method == "POST":
        excel_file = request.FILES.get("excel_file")
        print(excel_file)
        
        if not excel_file:
            error_message = "No file selected."
        else:
            try:
                # Check file extension
                valid_extensions = ['.xls', '.xlsx']
                ext = os.path.splitext(excel_file.name)[1]
                if ext.lower() not in valid_extensions:

                    raise ValidationError('Unsupported file extension.')

                # Check MIME type
                valid_mime_types = [
                    'application/vnd.ms-excel',
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                ]
                if excel_file.content_type not in valid_mime_types:
                    raise ValidationError('Unsupported file type.')

                # Check file size
                if excel_file.size > 2 * 1024 * 1024:
                    raise ValidationError('File size exceeds 2 MB.')

                # Process the Excel file
                df = pd.read_excel(excel_file)

                for index, row in df.iterrows():
                    product_name = row["Product Name"]
                    variation_text = row["Variation"]
                    stock = row["Stock"]
                    lowest_price = row.get("Lowest Price", 0)  # Ensure lowest_price is provided

                    product, created = Product.objects.get_or_create(
                        name=product_name,
                        defaults={'lowest_price': lowest_price}
                    )

                    if not created:
                        # Update the lowest price if a new lower price is found
                        if product.lowest_price > lowest_price:
                            product.lowest_price = lowest_price
                        product.save()

                    product_variation, variation_created = ProductVariation.objects.get_or_create(
                        product=product,
                        variation_text=variation_text,
                        defaults={'stock': stock}
                    )
                    if not variation_created:
                        product_variation.stock += stock
                    product_variation.save()

                return redirect('/products/')
            except ValidationError as e:
                error_message = str(e)
                
    print("error messgae in back",error_message)
    return render(request, 'products/product_list.html', {'error_message': error_message})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})

def product_data(request):
    products = Product.objects.all()
    data = []
    for product in products:
        variations = product.variations.all()
        variation_list = [{"variation": var.variation_text, "stock": var.stock} for var in variations]
        data.append({
            "id": product.id,
            "name": product.name,
            "lowest_price": product.lowest_price,
            "variations": variation_list,
            "last_updated": product.last_updated.isoformat()  # Return ISO format
        })
    return JsonResponse({"data": data})