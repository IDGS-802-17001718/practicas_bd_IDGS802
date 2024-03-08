from flask import Flask, request, render_template, Response, redirect, url_for
from flask_wtf.csrf import CSRFProtect
from flask import flash
from flask import g
import forms, json, os
from config import DevelopmentConfig
from models import db
from models import Alumnos, Profesores, Pizza
from io import open 
from datetime import datetime, timedelta
from sqlalchemy import func


app=Flask(__name__) 
app.config.from_object(DevelopmentConfig)
csrf=CSRFProtect()

@app.errorhandler(400)
def page_not_found(e):
    return render_template('404.html'),404

@app.route("/index", methods=["GET", "POST"])
def index():
    alum_form=forms.UserForm2(request.form)
    if request.method=='POST' and alum_form.validate():
        alum=Alumnos(nombre=alum_form.nombre.data,
                     apaterno=alum_form.apaterno.data,
                     email=alum_form.email.data)
        """ insert into alumnos values() """
        db.session.add(alum)
        db.session.commit()
    return render_template("index.html", form=alum_form)
@app.route("/profesores", methods=["GET", "POST"])
def profesores():
    prof_form=forms.UserProfesores(request.form)
    if request.method=='POST' and prof_form.validate():
        prof=Profesores(nombre=prof_form.nombre.data,
                     apaterno=prof_form.apaterno.data,
                     amaterno=prof_form.amaterno.data,
                     email=prof_form.email.data,
                     matricula=prof_form.matricula.data,
                     materia=prof_form.materia.data)
        """ insert into profesores values() """
        db.session.add(prof)
        db.session.commit()
    return render_template("profesores.html", form=prof_form)
@app.route("/ordenar_pizza", methods=["GET", "POST"])
def ordenar_pizza():
    pizza_form=forms.UserPizza(request.form)

    if request.method=='GET':
        subtotal_list = []
        with open("datos.txt", "r") as file:
            datos = json.load(file)
            for pedido in datos:
                subtotal = pedido["subtotal"]
                subtotal_list.append(subtotal)
        total = sum(subtotal_list)
        nombre = request.args.get("nombre")
        direccion = request.args.get("direccion")
        telefono = request.args.get("telefono")
        fecha = request.args.get("fecha")
        pizza=Pizza(nombre=nombre,
                     direccion=direccion,
                     telefono=telefono,
                     total=total,
                     create_date=fecha)
        db.session.add(pizza)
        db.session.commit()
        with open("datos.txt", "w") as file:
            file.write("")
    return redirect(url_for('pizzas'))

@app.route("/pizzas", methods=["GET", "POST"])
def pizzas():
    pizza_form=forms.UserPizza(request.form)
    pizza = Pizza.query.filter(db.func.day(Pizza.create_date) == datetime.now().day).all()
    if request.method == 'GET':
        filtro = request.args.get("filtro")
        print(filtro)
        if filtro == "dia":
            dia = request.args.get("selectDay")
            pizza = Pizza.query.filter(func.DAYOFWEEK(Pizza.create_date) == dia).all()
        elif filtro == "mes":
            mes = request.args.get("selectMonth")
            pizza = Pizza.query.filter(func.MONTH(Pizza.create_date) == mes).all()
        elif filtro == "fecha":
            fecha = request.args.get("selectDate")
            fecha_parseada = datetime.strptime(fecha, '%Y-%m-%d')
            pizza = Pizza.query.filter(Pizza.create_date >= fecha_parseada,
                                       Pizza.create_date < fecha_parseada + timedelta(days=1)).all()
    else:
        pizza = Pizza.query.filter(db.func.day(Pizza.create_date) == datetime.now().day).all()
    
    suma = 0
    for venta in pizza:
        suma += venta.total
    if os.path.exists("datos.txt"):
        with open("datos.txt", "r") as archivo:
            try:
                pedidos = json.load(archivo)
            except json.decoder.JSONDecodeError:
                pedidos = []
    else:
        pedidos = []
    return render_template("pizzas.html", form=pizza_form, pedidos=pedidos, ventas=pizza, suma=suma)
@app.route("/pizzas_list", methods=["GET", "POST"])
def pizzas_list():
    pizza_form=forms.UserPizza(request.form)

    if request.method=='GET':
        tamano = request.args.get("tamanoPizza")
        ingredientes = request.args.getlist("ingredientes")
        numPizzas = int(request.args.get("numPizzas"))

        if tamano == "chica":
            precio = 40
        elif tamano == "mediana":
            precio = 80
        elif tamano == "grande":
            precio = 120
        else:
            precio = 0
        # Sumar el precio de cada ingrediente
        for ingrediente in ingredientes:
            if ingrediente == "jamon":
                precio += 10
            elif ingrediente == "pina":
                precio += 10
            elif ingrediente == "champinones":
                precio += 10
        subtotal = precio * numPizzas

        # Cargar pedidos existentes desde datos.txt
        if os.path.exists("datos.txt"):
            with open("datos.txt", "r") as archivo:
                try:
                    pedidos = json.load(archivo)
                except json.decoder.JSONDecodeError:
                    pedidos = []
        else:
            pedidos = []

        # Agregar el nuevo pedido a la lista
        nuevo_pedido = {
            "tamano": tamano,
            "ingredientes": ingredientes,
            "numPizzas": numPizzas,
            "subtotal": subtotal
        }
        pedidos.append(nuevo_pedido)

        # Guardar la lista actualizada en datos.txt
        with open("datos.txt", "w") as archivo:
            json.dump(pedidos, archivo)
        return redirect(url_for('pizzas'))

    return render_template("pizzas.html", form=pizza_form)
@app.route("/eliminar_pizza", methods=["GET"])
def eliminar_pizza():
    pizza_form=forms.UserPizza(request.form)
    index = int(request.args.get("index"))

    if os.path.exists("datos.txt"):
        with open("datos.txt", "r") as archivo:
            try:
                pedidos = json.load(archivo)
            except json.decoder.JSONDecodeError:
                pedidos = []
    else:
        pedidos = []

    if 0 <= index < len(pedidos):
        del pedidos[index]

        with open("datos.txt", "w") as archivo:
            json.dump(pedidos, archivo)

    # Redirigir a la página principal
    return redirect(url_for('pizzas'))
    return render_template("pizzas.html", form=pizza_form, pedidos=pedidos)
@app.route("/eliminar_prof", methods=["GET", "POST"])
def eliminar_prof():
        prof_form=forms.UserProfesores(request.form)
        if request.method=='GET':
            id=request.args.get('id')
            prof=db.session.query(Profesores).filter(Profesores.id==id).first()
            prof_form.id.data=prof.id
            prof_form.nombre.data=prof.nombre
            prof_form.apaterno.data=prof.apaterno 
            prof_form.amaterno.data=prof.amaterno
            prof_form.email.data=prof.email
            prof_form.matricula.data=prof.matricula
            prof_form.materia.data=prof.materia
        if request.method=='POST':
            id=prof_form.id.data
            prof=Profesores.query.get(id)
            db.session.delete(prof)
            db.session.commit()
            return redirect(url_for('ABCProfesores'))
        return render_template("eliminar_prof.html", form=prof_form)
@app.route("/modificar_prof", methods=["GET", "POST"])
def modificar_prof():
    prof_form=forms.UserProfesores(request.form)
    if request.method=='GET':
        id=request.args.get('id')
        prof=db.session.query(Profesores).filter(Profesores.id==id).first()
        prof_form.id.data=prof.id
        prof_form.nombre.data=prof.nombre
        prof_form.apaterno.data=prof.apaterno 
        prof_form.amaterno.data=prof.amaterno
        prof_form.email.data=prof.email
        prof_form.matricula.data=prof.matricula
        prof_form.materia.data=prof.materia
    if request.method=='POST':
        id=prof_form.id.data
        prof=db.session.query(Profesores).filter(Profesores.id==id).first()
        prof.nombre=prof_form.nombre.data
        prof.apaterno=prof_form.apaterno.data
        prof.amaterno=prof_form.amaterno.data
        prof.email=prof_form.email.data
        prof.matricula=prof_form.matricula.data
        prof.materia=prof_form.materia.data
        db.session.add(prof)
        db.session.commit()
        return redirect(url_for('ABCProfesores'))
    render_template("modificar_prof.html")
def filtrar(pizza, pizza_form):
    suma = 0
    for venta in pizza:
        suma += venta.total
    if os.path.exists("datos.txt"):
        with open("datos.txt", "r") as archivo:
            try:
                pedidos = json.load(archivo)
            except json.decoder.JSONDecodeError:
                pedidos = []
    else:
        pedidos = []
    return render_template("pizzas.html", form=pizza_form, pedidos=pedidos, ventas=pizza, suma=suma)
@app.route("/ABC_Completo", methods=["GET", "POST"])
def ABDCompleto():
    create_form=forms.UserForm2(request.form)

    alumno=Alumnos.query.all()
    return render_template("ABC_Completo.html", alumno=alumno)

@app.route("/ABC_Profesores", methods=["GET", "POST"])
def ABCProfesores():
    create_form=forms.UserProfesores(request.form)
    profesores=Profesores.query.all()
    return render_template("ABC_Profesores.html", profesores=profesores)


@app.route("/alumnos", methods=["GET", "POST"])
def alumnos():
    nom=''
    alum_form=forms.UserForm(request.form)
    if request.method=='POST' and alum_form.validate():
        nom=alum_form.nombre.data
        apaterno=alum_form.apaterno.data
        amaterno=alum_form.amaterno.data
        edad=alum_form.edad.data
        email=alum_form.email.data
        mensaje='Bienvenido: {}'.format(nom)
        flash(mensaje)
        print('Apaterno: {}'.format(apaterno))
        print('Amaterno: {}'.format(amaterno))
        print('Edad: {}'.format(edad))
        print('Correo: {}'.format(email))
        return render_template("alumnos.html", form=alum_form, nom=nom)
    else:
        return render_template("alumnos.html", form=alum_form)
if __name__ == "__main__":
    csrf.init_app(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run()