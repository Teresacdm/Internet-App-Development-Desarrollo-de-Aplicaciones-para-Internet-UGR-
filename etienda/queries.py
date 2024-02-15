from pydantic import BaseModel, FilePath, Field, EmailStr
from pymongo import MongoClient
from pprint import pprint
from datetime import datetime
from typing import Any
from .models import Nota, Producto, Compra
from bson.objectid import ObjectId
import requests
import re
import os
import logging

logger = logging.getLogger(__name__)


# https://requests.readthedocs.io/en/latest/
def getProductos(api):
	response = requests.get(api)
	return response.json()

# Conexión con la BD				
# https://pymongo.readthedocs.io/en/stable/tutorial.html
client = MongoClient('mongo', 27017)

tienda_db = client.tienda                   # Base de Datos
productos_collection = tienda_db.productos  # Colección
# productos_collection.drop()					#Vacíamos la colección antes de trabajar con ella

def processData():
	# Obtener productos desde la base de datos
    output = list(productos_collection.find({})) 

    # Procesar los datos para que coincidan con ProductSchema
    processed_data = []
    for product in output:
        processed_product = {
            'id': str(product.get('_id')),
            'title': product.get('nombre'),
            'price': product.get('precio'),
            'description': product.get('descripción'),
            'category': product.get('categoría'),
            'image': product.get('imágen'),
            'rating': {'rate': product.get('rating').get('puntuación'), 'count': product.get('rating').get('cuenta')}
        }
        processed_data.append(processed_product)

    return processed_data

def getAllProducts(desde: int, hasta: int):
    # Obtener productos desde la base de datos
    data = processData()
    desired_data = []
    for p in data[desde: hasta]:
        desired_data.append(p)

    return desired_data


def getProduct(id):
	data = processData()
	for d in data:
		if (id == d['id']):
			output=d
	return output

def modifyProduct(id, payload):
    try:
        # payload['id']=ObjectId(id)
        if productos_collection.find_one({"_id": ObjectId(id)}) is None:
	        logger.error("No se encuentra el producto")

        title = payload.title
        price = payload.price
        description = payload.description
        category = payload.category
        rate = payload.rating.rate
        count = payload.rating.count

        # Actualizar los campos en la base de datos
        productos_collection.update_one(
            {"_id": ObjectId(id)},
            {
                "$set": {
                    'nombre': title,
                    'precio': price,
                    'descripción': description,
                    'categoría': category,
                    'rating': {'puntuación': rate, 'cuenta': count}
                }
            }
        )

        return True
    except Exception as e:
        logger.error(e)
        logger.error("Error al modificar el producto")        
        return False
	
def deleteProduct(id):
	try:
		out_product=getProduct(id)
		productos_collection.delete_one({'_id': ObjectId(id)})
		return out_product
	except Exception as e:
		logger.error(e)
		logger.error("Error al eliminar el producto")        
		return False
	
def createProduct(payload):
	try:
		title = payload.title
		price = payload.price
		description = payload.description
		category = payload.category
		rate = payload.rating.rate
		count = payload.rating.count
	
		producto = {				
			'nombre': title, 
			'precio': price, 
			'descripción': description, 
			'categoría': category,
			'imágen': None, 
			'rating': {'puntuación': rate, 'cuenta': count}
		}
		insert = productos_collection.insert_one(producto)
		out_product=getProduct(str(insert.inserted_id))
		
		return out_product
	except Exception as e:
		logger.error(e)
		logger.error("Error al crear el producto")        
	return False

def modifyRating(id, rating):
	try:
		if productos_collection.find_one({"_id": ObjectId(id)}) is None:
			logger.error("No se encuentra el producto")
			
		product = getProduct(id)
		old_rating = product.get('rating').get('rate')
		old_count = product.get('rating').get('count')
		new_count = old_count + 1
		new_rating = ((old_rating * old_count) + (rating * 1.0)) / new_count
    
		# Actualizar los campos en la base de datos
		productos_collection.update_one(
			{"_id": ObjectId(id)},
			{
				"$set": {
					'rating': {'puntuación': new_rating, 'cuenta': new_count}
				}
			}
		)
		return True
	except Exception as e:
		logger.error(e)
		logger.error("Error al modificar el producto")        
		return False
	
# productos = getProductos('https://fakestoreapi.com/products')
# for p in productos:
# 	url = p.get("image")				#Obtenemos la URL de la imagen para poder descargarla
# 	imagen = requests.get(url).content	#Descargamos la imagen
# 	dir='static/etienda/'						#Queremos meter las imágenes en la carpeta images
# 	nombre_img=p['image'].split('/')[-1]#A cada imagen le asignamos un nombre distinto
# 	ruta=os.path.join(dir, nombre_img)	#Especifico la ruta de la imagen utilizando os.path.join para unir el directorio con el nombre asignado
# 	with open(ruta, 'wb') as handler:	#open() abre el archivo de imagen en modo wb. 
# 		handler.write(imagen)			#write() escribe la imagen en el archivo.
# 	p['image']=nombre_img
	
# 	producto = {				#Creamos un diccionario como el de "dato" para traducir cada argumento de la api a su correspondiente de la clase Producto
# 		'nombre': p.get("title"), 
# 		'precio': float(p.get("price")), 
# 		'descripción': p.get("description"), 
# 		'categoría': p.get("category"),
# 		'imágen': p.get("image"), 
# 		'rating': {'puntuación': p["rating"].get("rate"), 'cuenta': p["rating"].get("count")}
# 	}

# 	prod = Producto(**producto)
# 	productos_collection.insert_one(prod.model_dump())	#Lo añadimos a la colección

#print(productos_collection.count_documents({}))
#relacion=[]	#Lista para guardar el id creado por mongodb de cada producto 
			#Como el id original está en orden desde 1, lo podremos relacionar con los elementos en orden de esta lista
#i=0

# lista_productos_ids = []
# for prod in productos_collection.find():
# 	#pprint(prod)
# 	#print(prod.get('_id'))   # Autoinsertado por mongo
# 	relacion.insert(i, prod.get('_id'))	#Insertamos cada id en orden en la lista
# 	i+=1
	#lista_productos_ids.append(prod.get('_id'))
	
# compras_collection = tienda_db.compras  # Colección
# compras_collection.drop()

# compras = getProductos('https://fakestoreapi.com/carts')
# compras_collection.insert_many(compras)


#Consulta: Productos electrónicos entre 100 y 200€ ordenados por precio

def ConsultaElectr():
	resp="\nEsta es la lista de los productos electronicos entre 100 y 200 euros ordenador por precio\n"
	for prod in productos_collection.find({'categoría' : "electronics",
										'precio' : { '$gt' :  100, '$lt' : 200}}).sort("precio"):
		resp+= "\n" + str(prod) 
	return resp
	
 
#Consulta: Productos que contengan la palabra 'pocket' en la descripción
def ConsultaPocket():
	resp="\nEsta es la lista de los productos que contienen la palabra pocket en la descripcion\n"
	for prod in productos_collection.find({'descripción': {"$regex" : "pocket", "$options" : "i"}}):
		resp+="\n" + str(prod) 
	return resp

#Consulta: Productos con puntuación mayor de 4
def ConsultaMayor4():
	resp="\nEsta es la lista de los productos con puntuacion mayor de 4\n"
	for prod in productos_collection.find({'rating.puntuación' : {"$gt": 4}}):
		resp+="\n" + str(prod) 
	return resp


#Consulta: Ropa de hombre, ordenada por puntuación
def ConsultaHombre():
	resp="\nEsta es la lista de los productos que pertenecen a la categoria de ropa de hombre, ordenados por puntuación\n"
	for prod in productos_collection.find({'categoría': {'$in': ['men\'s clothing']}}).sort('rating'):
		resp+="\n" + str(prod) 
	return resp

#Facturación total de la colección compras
def ConsultaFactTot():
	resp="\nFacturacion total: "
	fact_tot = 0.0
	for comp in compras_collection.find():	#Recorremos cada elemento de la colección
		tot_list=0.0						#Inicializamos a 0 la variable que va a calcular el total de cada compra
		for prod in comp["products"]:		#Recorremos la lista de productos adquiridos dentro de una compra
			precio_prod=0.0					#Inicializamos a 0 la variable donde vamos a guardar el precio de cada producto comprado
			id_prod=prod.get("productId")	#Averiguamos de qué producto se trata a través de su id
			id_db=relacion[id_prod-1]		#Utilizamos el array relación para obtener el id que mongodba ha asignado a dicho producto
			for p in productos_collection.find({'_id': id_db}) : #Una vez obtenido el id de mongodb, podemos buscarlo en la colección de productos
				precio_prod=p.get('precio')	#Guardamos el precio del producto
			tot_prod=precio_prod*prod.get("quantity")	#Multiplicamos el precio por la cantidad comprada
			tot_list+=tot_prod				#Por cada iteración en "products" se añade al total de la lista de esa compra
		fact_tot+=tot_list					#Por cada iteración en "compras_collection" se añade al total de toda la colección
	fact_tot = round(fact_tot, 2)			#Redondeamos a dos decimales para obtener los céntimos
	resp+=str(fact_tot)
	resp+= " euros"
	return resp

	
#Facturación por categoría del producto
def ConsultaFactCateg():
	resp="\nFacturacion total por categorias: "
	fact_cat = {}	#Creamos un diccionario donde guardaremos cada categoría
	for comp in compras_collection.find():
		for prod in comp["products"]:
			precio_prod = 0.0
			id_prod=prod.get("productId") #check
			id_db=relacion[id_prod-1]
			for p in productos_collection.find({'_id': id_db}) :
				precio_prod=p.get('precio')
				cat = p.get('categoría')		#Obtenemos tanto el precio como la categoría
				if cat in fact_cat:				#Si la categoría ya la habíamos creado antes, sumamos el precio de ese producto
					fact_cat[cat] += precio_prod*prod.get("quantity")
				else:							#Si no estaba creada entonces 
					fact_cat[cat] = precio_prod*prod.get("quantity") #inicializamos esa entrada del diccionario con nuestro primer producto de esa categoría

	for cat in fact_cat:	#Imprimimos cada una de las categorías
		resp += f"\nFacturación de la categoría {cat}: {round(fact_cat[cat], 2)} euros"
	return resp

