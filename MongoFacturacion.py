from flask import Flask, render_template, request, url_for, Response, redirect, json
from API import *
import math

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/home')
def dashboard():
    users = getRangeOfClientes(1, 5)
    productos = getRangeOfProductos(1, 5)
    suplidores = getRangeOfSuplidores(1,5)
    cantFacturas = getTotalFacturas()
    listSuplidores = FindAllSuplidores()
    listProductos = FindAllProductos()
    paises = ["Canada", "Espana", "Estados Unidos", "Republica Dominicana"]
    cantClientes = getTotalClientes()
    totalPaginasClientes = math.ceil(float(cantClientes) /5)
    paginasClientes = list(range(1,int(totalPaginasClientes+1)))

    cantProductos = getTotalProductos()
    totalPaginasProductos = math.ceil(float(cantProductos) / 5)
    paginasProductos = list(range(1, int(totalPaginasProductos + 1)))

    cantSuplidor = getTotalSuplidores()
    totalPaginasSuplidores = math.ceil(float(cantSuplidor) / 5)
    paginasSuplidores = list(range(1, int(totalPaginasSuplidores + 1)))

    return render_template("dashboard.html", clientes =users, productos=productos, paises= paises, cantidadClientes = cantClientes,
                           paginasClientes = paginasClientes, cantidadProductos = cantProductos, paginasProductos = paginasProductos,
                           cantidadFacturas = cantFacturas, suplidores = suplidores, paginasSuplidores = paginasSuplidores,
                           cantSuplidor = cantSuplidor, listSuplidores= listSuplidores, listProductos= listProductos)

@app.route('/estadisticas')
def estadisticas():
    productos = FindAllProductos()
    productos2 = FindAllProductos()
    clientes = FindAllClientes()
    years = [2010,2011,2012,2013,2014,2015,2016,2017]
    return render_template("estadisticas.html", productos=productos, productos2=productos2, years = years, clientes=clientes)



@app.route('/facturacion')
def facturacion():
    users = FindAllClientes()
    productos = FindAllProductos()
    facturas = getRangeOfFacturas(1, 50)
    cantFacturas = getTotalFacturas()
    totalPaginasFacturas = math.ceil(float(cantFacturas) / 50)
    paginasFacturas = list(range(1, int(totalPaginasFacturas + 1)))

    return render_template("facturacion.html", clientes = users, productos= productos, facturas= facturas, cantidadFacturas = cantFacturas, paginasFacturas = paginasFacturas)



@app.route('/clientes',methods = ['GET'])
def result():
   if request.method == 'GET':
      paises = [ "Canada","Espana", "Estados Unidos","Republica Dominicana"]
      users = FindAllClientes()
      return render_template("ajax/clientes.html", clientes = users, paises =paises)


@app.route('/addCliente', methods=['POST'])
def addUser():
    name = request.form.get('name')
    pais = request.form.get('pais')
    insertNewCliente(name,pais)
    return redirect("/home")

@app.route('/suplirProducto', methods=['POST'])
def supplyProduc():
    name = request.form.get('producto')
    cantidad = request.form.get('cantidad')
    suplirProducto(name,cantidad)
    return redirect("/home")

@app.route('/crearFactura', methods=['POST'])
def addFactura():
    name = request.form.get('cliente')
    listaProductosNombre = request.form.get('listaProductosNombre').split(",")
    listaProductosPrecio = request.form.get('listaProductosPrecio').split(",")
    listaProductosCantidad = request.form.get('listaProductosCantidad').split(",")
    print len(listaProductosCantidad)
    print len(listaProductosNombre)
    print len(listaProductosPrecio)
    listaProductos = []

    for i in list(range(0, len(listaProductosNombre))):
        ob = {"nombre": listaProductosNombre[i], "precio": float(listaProductosPrecio[i]), "cantidad": listaProductosCantidad[i]}
        listaProductos.append(ob)
    precioTotal = float(request.form.get('PrecioTotalin'))
    insertNewFactura(name,listaProductos,precioTotal)
    return redirect("/facturacion")

@app.route('/addProducto', methods=['POST'])
def addProducto():
    name = request.form.get('name')
    precio = request.form.get('precio')
    listaSuplidoresNombre = request.form.get('listaSuplidoresNombre').split(",")
    listaSuplidoresDias = request.form.get('listaSuplidoresDias').split(",")
    listaSuplidores = []

    for i in list(range(0, len(listaSuplidoresNombre))):
        ob = {"nombre": listaSuplidoresNombre[i], "dias": int(listaSuplidoresDias[i])}
        listaSuplidores.append(ob)
    cantidad = request.form.get('cantidad')
    insertNewProducto(name,precio,cantidad,listaSuplidores)
    return redirect("/home")

@app.route('/addSuplidor', methods=['POST'])
def addSuplidor():
    name = request.form.get('name')
    insertNewSuplidor(name)
    return redirect("/home")

@app.route('/clientes/remove/<id>', methods=['GET'])
def RouteRemoveUser(id):
    removeCliente(id)
    return redirect("/home")


@app.route('/suplidores/remove/<id>', methods=['GET'])
def RouteRemoveSup(id):
    removeSuplidor(id)
    return redirect("/home")

@app.route('/facturas/remove/<id>', methods=['GET'])
def RouteRemoveFactura(id):
    removeFactura(id)
    return redirect("/facturacion")

@app.route('/productos/remove/<id>', methods=['GET'])
def RouteRemoveProducto(id):
    removeProducto(id)
    return redirect("/home")

@app.route('/cargarDatosFacturas/<pag>', methods=['GET'])
def RouteAjaxPaginationFacturas(pag):
    users = getRangeOfFacturas(int(pag), 50)
    return render_template("ajax/facturas.html", facturas=users)


@app.route('/estadisticas/ProductosYear/<producto>/<year>', methods=['GET'])
def RouteEstadisticaProductoYear(producto,year):
    valores = ProductoPorYear(producto,int(year))
    return render_template("ajax/estadisticas/ProductoYear.html", valores = valores)

@app.route('/estadisticas/ClientesYear/<cliente>/<year>', methods=['GET'])
def RouteEstadisticaClienteYear(cliente,year):
    print cliente
    valores = ClientePorYear(cliente,int(year))
    print valores
    return render_template("ajax/estadisticas/ClienteYear.html", valores = valores)


@app.route('/estadisticas/BestCliente/<year>/<mes>', methods=['GET'])
def RouteEstadisticaBestCliente(year,mes):
    resultado = bestClienteEnFecha(mes,year)
    print resultado
    return render_template("ajax/estadisticas/BestCliente.html", year = year, mes = mes, resultado = resultado)


@app.route('/estadisticas/BestProducto/<year>/<mes>', methods=['GET'])
def RouteEstadisticaBestProducto(year,mes):
    resultado = bestProductoFecha(mes,year)
    print resultado
    return render_template("ajax/estadisticas/BestProducto.html", year = year, mes = mes, resultado = resultado)


@app.route('/estadisticas/EstimarInventario/<prod>/<fecha>', methods=['GET'])
def RouteEstadisticaEstimarInventario(prod,fecha):
    resultado = EstimarInventario(prod,fecha)
    print resultado
    return render_template("ajax/estadisticas/EstimarInventario.html", resultado = resultado, producto = prod, fecha=fecha)


@app.route('/cargarDatosClientes/<pag>', methods=['GET'])
def RouteAjaxPagination(pag):
    users = getRangeOfClientes(int(pag), 5)
    return render_template("ajax/clientes.html", clientes=users)

@app.route('/cargarDatosProductos/<pag>', methods=['GET'])
def RouteAjaxPaginationProducts(pag):
    productos = getRangeOfProductos(int(pag), 5)
    return render_template("ajax/productos.html", productos=productos)

@app.route('/cargarDatosSuplidores/<pag>', methods=['GET'])
def RouteAjaxPaginationSup(pag):
    productos = getRangeOfSuplidores(int(pag), 5)
    return render_template("ajax/suplidores.html", suplidores=productos)


if __name__ == '__main__':
    app.run()
