from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required #un decorador es una función que llama a otra función
from django.contrib.admin.views.decorators import staff_member_required
from .models import Producto
from .queries import productos_collection
from .forms import ProductosForm
import os
import logging
logger=logging.getLogger(__name__)

def index(request):
    #logger.debug("Paso por aquí") #Depurar
    #logger.error("Mensaje de error")
    context={}
    return render(request, "etienda/index.html", context)

@staff_member_required
def nuevo(request):
    form=ProductosForm()
    if request.method == "POST":
        form=ProductosForm(request.POST, request.FILES)
        if form.is_valid():
            logger.debug(form.cleaned_data)
            logger.debug(request.FILES)

            producto = {				
                'nombre': form.cleaned_data['nombre'], 
                'precio': float(form.cleaned_data['precio']), 
                'descripción': form.cleaned_data['descripción'], 
                'categoría': form.cleaned_data['categoría'],
                'imágen': str(form.cleaned_data['imagen']), 
                'rating': {'puntuación': 0.0, 'cuenta': 1}
            }

            image_path = form.cleaned_data['imagen'].name
            dest = os.path.join('etienda/', image_path)
            with open(dest, 'wb') as destination_file:
                for chunk in form.cleaned_data['imagen'].chunks():
                    destination_file.write(chunk)      
            producto['imágen'] = dest
            prod = Producto(**producto)
            productos_collection.insert_one(prod.dict())#model_dump())
            messages.add_message(request, messages.INFO, "Producto añadido exitosamente")
            return redirect('index')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.add_message(request, messages.ERROR, f"Error en el campo '{form[field].label}': {error}")

    context={
        'form':form
    }
    return render(request, 'etienda/nuevo.html', context)


def ConsultaCategoria(categoria):
    #Traducimos la categoría al inglés
    if categoria == 'Joyas':
        categoria='jewelery'
    elif categoria == 'Electronica':
        categoria='electronics'
    elif categoria == 'Ropa de Hombre':
        categoria = "men's clothing"
    elif categoria == 'Ropa de Mujer':
        categoria = "women's clothing"

    lista_productos_cat = []
    for prod in productos_collection.find({'categoría':categoria}):
        lista_productos_cat.append(prod)
    return lista_productos_cat

def busq_cat(request, categoria):
    productos = ConsultaCategoria(categoria)
    for producto in productos:
        producto['id'] = str(producto['_id'])
    context={
        'categoria':categoria,
        'productos':productos,
    }
    return render(request, "etienda/categoria.html", context)


def buscar(request):
    busqueda = request.GET.get('busqueda', ' ')
    # Realiza una búsqueda en nombre, descripción y categoría
    resultados = productos_collection.find({
        '$or': [
            {'nombre': {'$regex': busqueda, '$options': 'i'}},  # Busca la palabra en el nombre (sin distinción entre mayúsculas y minúsculas)
            {'descripción': {'$regex': busqueda, '$options': 'i'}},  # Busca la palabra en la descripción
            {'categoría': {'$regex': busqueda, '$options': 'i'}}  # Busca la palabra en la categoría
        ]
    })

    context = {
        'resultados': resultados,
        'busqueda': busqueda
    }
    return render(request, 'etienda/resultados.html', context)


def resultados(request, busqueda):

    resultados = productos_collection.find({'nombre': {'$regex': busqueda, '$options': 'i'}})
    context = {
        'resultados': resultados,
        'busqueda': busqueda,
    }
    return render(request, "etienda/resultados.html", context)