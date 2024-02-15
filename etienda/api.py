from ninja_extra import NinjaExtraAPI, api_controller, http_get
from ninja import Schema, Query, Form
from . import models, queries
from bson.json_util import dumps
from bson.objectid import ObjectId
import logging
from typing import List
from ninja.security import HttpBearer


logger = logging.getLogger(__name__)
		
api = NinjaExtraAPI()

class Rate(Schema):
	rate: float
	count: int
	
class ProductSchema(Schema):  # sirve para validar y para documentación
	id:    str
	title: str
	price: float
	description: str
	category: str
	image: str = None
	rating: Rate
	
	
class ProductSchemaIn(Schema):
	title: str
	price: float
	description: str
	category: str
	rating: Rate
	
	
class ErrorSchema(Schema):
	message: str


@api.get('/products', response=List[ProductSchema])
def Productos(request, desde: int=0, hasta: int=5):
    datos=queries.getAllProducts(desde, hasta)
    return 200, datos

@api.get('/products/{id}', response={202: ProductSchema, 404: ErrorSchema})
def ProductosId(request, id : str):
	try:
		resultado = queries.getProduct(id)
		return 202, resultado
	except Exception as e:
		logger.error(e)
		return 404, {"message": "No se ha encontrado el producto"}


@api.delete('/products/{id}', response={200 :ProductSchema, 404 : ErrorSchema})
def Eliminar_Producto(request, id : str):
	try:
		out_product=queries.deleteProduct(id)
		return 200, out_product
	except Exception as e:
		logger.error(e)
		return 404, {"message": "No se ha encontrado el producto"}


	
@api.post('/products', response={201 : ProductSchema, 400 : ErrorSchema})
def Crear_Producto(request, payload: ProductSchemaIn):
	try:
		out_product = queries.createProduct(payload)
		logger.debug(out_product)
		return 201, out_product
	except Exception as e:
		logger.error(e)
		return 400, {"message": "No se ha podido crear el producto"}
	
@api.put("/products/{id}", response = {202: ProductSchema, 404: ErrorSchema})
def Modificar_producto(request, id: str, payload: ProductSchemaIn):
	try:
		queries.modifyProduct(id, payload)
		out_product=queries.getProduct(id)
		return 202, out_product
	except:
		return 404, {'message': 'no encontrado'}
	
@api.put('/products/{id}/{rating}', response={202 : ProductSchema, 404 : ErrorSchema})
def Modificar_Rating(request, id : str, rating : int):
	try:
		queries.modifyRating(id, rating)
		out_product = queries.getProduct(id)
		return 202, out_product
	except:
		return 404, {"message": "No se ha encontrado el producto"}
	