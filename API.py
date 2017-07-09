import pymongo
from bson.objectid import ObjectId
from datetime import datetime,timedelta
from bson.son import SON
import pprint
import  math

from pymongo import MongoClient
client = MongoClient()

client = MongoClient('mongodb://localhost:27017/')
db = client['Facturacion']

# --------------------------- Clientes -----------------------------

def FindAllClientes():
    clientes = db.clientes
    return clientes.find({})

def getRangeOfClientes(pagina, itemsPorPagina):
    return db.clientes.find({}).skip((pagina-1)*itemsPorPagina).limit(itemsPorPagina)

def getTotalClientes():
    return db.clientes.find({}).count()

def insertNewCliente(nombre, pais):
    cliente = {"nombre": nombre, "pais": pais}
    clientes = db.clientes
    clientes.insert_one(cliente)


def removeCliente(id):
    print id
    clientes = db.clientes
    clientes.remove( {"_id": ObjectId(id)})



#------------------- PRODUCTOS ---------------------------------------

def FindAllProductos():
    productos = db.productos
    return productos.find({})

def getRangeOfProductos(pagina, itemsPorPagina):
    return db.productos.find({}).skip((pagina-1)*itemsPorPagina).limit(itemsPorPagina)

def getTotalProductos():
    return db.productos.find({}).count()

def insertNewProducto(nombre, precio, cantidad, suplidores):
    producto = {"nombre": nombre, "precio": precio, "CantidadDisponible": cantidad, "suplidores": suplidores}
    productos = db.productos
    productos.insert_one(producto)


def removeProducto(id):
    print id
    productos = db.productos
    productos.remove( {"_id": ObjectId(id)})


#-------------------- SUPLIDORES  ---------------------------------------

def FindAllSuplidores():
    suplidores = db.suplidores
    return suplidores.find({})

def getRangeOfSuplidores(pagina, itemsPorPagina):
    return db.suplidores.find({}).skip((pagina-1)*itemsPorPagina).limit(itemsPorPagina)

def getTotalSuplidores():
    return db.suplidores.find({}).count()

def insertNewSuplidor(nombre):
    suplidor = {"nombre": nombre}
    suplidores = db.suplidores
    suplidores.insert_one(suplidor)

def removeSuplidor(id):
    suplidores = db.suplidores
    suplidores.remove( {"_id": ObjectId(id)})

def suplirProducto(name,canti):
    el = db.productos.find_one({'nombre': name})
    db.productos.update({'nombre': name}, {'$set': {"CantidadDisponible": int(el['CantidadDisponible'])+int(canti)}}, upsert=False)


#------------------- Facturas ---------------------------------------

def FindAllFacturas():
    facturas = db.facturas
    return facturas.find({})

def getRangeOfFacturas(pagina, itemsPorPagina):
    return db.facturas.find({}).skip((pagina-1)*itemsPorPagina).limit(itemsPorPagina).sort("fecha",pymongo.DESCENDING)

def getTotalFacturas():
    return db.facturas.find({}).count()

def insertNewFactura(cliente, productos, total):
    factura = {"cliente": cliente, "productos": productos, "montoTotal": total, "anio": datetime.now().year, "mes": datetime.now().month, "dia": datetime.now().day}
    for p in productos:
        cantProd = db.productos.find_one({"nombre": p['nombre']})
        id = cantProd['nombre']
        cant = int(cantProd['CantidadDisponible']) - int(p['cantidad'])
        db.productos.update({'nombre':id},{'$set':{"CantidadDisponible": cant}}, upsert=False)

    facturas = db.facturas
    facturas.insert_one(factura)


def removeFactura(id):
    print id
    facturas = db.facturas
    facturas.remove( {"_id": ObjectId(id)})



#-------------------------- queeeeeeeryssssssss ---------------------------------

def ProductoPorYear(producto,year):
    CantidadPorMes =[]
    MesRes = []
    for i in list(range(1,13)):
        pipeline = [
            {"$match": {"anio": year}},
            {"$match": {"mes": i}},
        { "$unwind": "$productos"},
        { "$match": {'productos.nombre': producto}},
        {"$group": {
            "_id": "null",
            "count": { "$sum": 1}
        }}
           ]
        var = db.facturas.aggregate(pipeline)
        CantidadPorMes.append(list(var))
    for x in list(range(0, len(CantidadPorMes))):
        if CantidadPorMes[x] == []:
            MesRes.append(0)
        else:
            MesRes.append(CantidadPorMes[x][0]['count'])
    return MesRes


def ClientePorYear(cliente,year):
    CantidadPorMes =[]
    MesRes = []
    for i in list(range(1,13)):
        pipeline = [
            {"$match": {"anio": year}},
            {"$match": {"mes": i, "cliente": cliente}},
        {"$group": {
            "_id": {"cliente": cliente},
            "montoTotal": { "$sum": "$montoTotal"}
        }}
           ]
        var = db.facturas.aggregate(pipeline)
        CantidadPorMes.append(list(var))
    for x in list(range(0, len(CantidadPorMes))):
        if CantidadPorMes[x] == []:
            MesRes.append(0)
        else:
            MesRes.append(CantidadPorMes[x][0]['montoTotal'])
    return MesRes


def bestClienteEnFecha(mes,year):
    pipeline =   [
    {"$match": {"mes": int(mes), "anio": int(year)}},
     {"$group" : {
           "_id" : {"cliente": "$cliente"},
           "montoTotal": { "$sum": "$montoTotal" }
        }}
  ]
    var = db.facturas.aggregate(pipeline)
    bigger = {"montoTotal": 0}
    for el in list(var):
        print el
        if bigger["montoTotal"] < el["montoTotal"]:
            bigger = el
    return {"cliente": bigger["_id"]["cliente"], "montoTotal": bigger["montoTotal"]}



def bestProductoFecha(mes,year):
    productos = db.productos.find({})
    misProductos = list(productos)
    CantidadProductos =[]
    for pro in misProductos:
        print pro['nombre']
        pipeline = [
            {"$match": {"anio": int(year), "mes": int(mes)}},
        { "$unwind": "$productos"},
        { "$match": {'productos.nombre': str(pro['nombre'])}},
        {"$group": {
            "_id": "null",
            "count": { "$sum": 1}
        }}
           ]
        var = db.facturas.aggregate(pipeline)
        CantidadProductos.append([list(var), pro['nombre']])

    bigger = [{"count": 0}, CantidadProductos[0][1]]
    for x in list(range(0,len(CantidadProductos))):
       aux = CantidadProductos[x][0]
       if aux != []:
           if aux[0]['count'] > bigger[0]['count']:
               bigger = [{"count": aux[0]['count']}, CantidadProductos[x][1]]

    return {"cantidad": bigger[0]['count'], "producto": bigger[1]}


def EstimarInventario(producto,fecha):
    fechaActual = datetime.now()
    fechaEstimacion = fecha.split("-")

    #-- Diferencia de dias totales
    diasDeDiferencia = 0

    diasDeDiferencia += (int(fechaEstimacion[2]) - fechaActual.year)*365
    diasDeDiferencia += (int(fechaEstimacion[1]) - fechaActual.month)*30
    diasDeDiferencia += (int(fechaEstimacion[0])-fechaActual.day)

    #-- Mejor Suplidor
    prod = db.productos.find_one({"nombre": producto})
    mejorSuplidor = prod['suplidores'][0]
    for sup in prod['suplidores']:
        if sup['dias'] < mejorSuplidor['dias']:
            mejorSuplidor = sup


    #-- Cantidad Actual Disponible
    cantDisponible = prod["CantidadDisponible"]

    #-- Cantidad ventas Mes Pasado
    pipeline = [
        {"$match": {"anio": int(fechaActual.year), "mes": int(fechaActual.month - 1) }},
        {"$unwind": "$productos"},
        {"$match": {"productos.nombre": producto}},
        {"$group": {
            "_id": {"producto2": "$productos.nombre"},
            "total": {"$sum": "$productos.cantidad"}
        }}
    ]
    var = db.facturas.aggregate(pipeline)
    promedioVenta = float(list(var)[0]['total']) / 30
    promedioVenta = promedioVenta

    #-------------- Calculo

    VentasDiariasConError = math.ceil(promedioVenta + (promedioVenta*0.15))

    DiasDisponiblesEnRespaldo = int(int(cantDisponible) / VentasDiariasConError)

    fechaParaOrden = ""
    if diasDeDiferencia <= DiasDisponiblesEnRespaldo:
        fechaParaOrden = "El inventario actual es suficiente para esta fecha"
    else:
        diasAux = DiasDisponiblesEnRespaldo - int(mejorSuplidor['dias'])
        fecha =datetime.now() + timedelta(days=diasAux)
        fechaParaOrden = str(fecha.day)+"/"+str(fecha.month)+"/"+str(fecha.year)+" y se ordenaran "+str((diasDeDiferencia-DiasDisponiblesEnRespaldo)*VentasDiariasConError)+" unidades"

    return {"fechaParaOrden": fechaParaOrden, "VentasConError": VentasDiariasConError, "DiasDisponiblesConRespaldo": DiasDisponiblesEnRespaldo,
            "MejorSuplidor": mejorSuplidor['nombre'], "MejorSuplidorDelay": int(mejorSuplidor['dias']), "cantDisponible": int(cantDisponible),
            "promedioVenta": promedioVenta, "DiasDiferencia": diasDeDiferencia}
