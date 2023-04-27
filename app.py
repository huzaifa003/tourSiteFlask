

import re
from flask import session, render_template, redirect, request, Flask, url_for, flash
from sqlalchemy import create_engine, text
from functools import wraps
# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)

# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.

app.secret_key = "xyz"

engine = create_engine(
    "mysql+mysqlconnector://root:@localhost/tour", echo=True)
con = engine.connect()


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect("login")

    return wrap


@app.route('/', methods=['GET'])
@login_required
# ‘/’ URL is bound with hello_world() function.
def hello_world():
    if request.method == "GET":
        return 'Hello World'


@app.route("/login", methods=['GET', 'POST'])
def login():
    if (request.method == "GET"):
        if ('user' in session):
            if (session['id'] == 0):
                return redirect("/admin")

            return redirect("/userPage")
        return render_template("login.html")
    else:

        email = request.form.get("email")
        password = request.form.get("password")

        if (email == 'admin@gmail.com' and password == 'admin'):
            session['user'] = 'email'
            session['id'] = 0
            return redirect("/admin")

        result = con.execute(text(
            "SELECT * FROM users WHERE email = (:mail)  and password = (:password)"), {"mail": email, "password": password})
        data = convertResult(result)
        if len(data) == 1:
            session['user'] = data[0]['email']
            session['id'] = data[0]['id']
            print(session['user'])

            return redirect("/login")

        return "Wrong Login name or password"


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if ('user' in session):
        return redirect("/login")
    else:
        if (request.method == "GET"):
            return render_template("signup.html")
        else:
            email = request.form.get("email")
            password = request.form.get("password")
            confirmpassword = request.form.get("confirmpassword")
            print(email)
            print(password)

            if (password != confirmpassword):
                return "PASSWORDS DO NOT MATCH"

            result = con.execute(
                text("SELECT * FROM users WHERE email = (:mail) "), {"mail": email})
            data = convertResult(result)
            if (len(data) > 0):
                return "THIS EMAIL ALREADY EXISTS"

            con.execute(text("INSERT INTO users (email,password) VALUES (:mail, :password)"), {
                        "mail": email, "password": password})
            return redirect("/login")


@app.route("/admin", methods=['GET', 'POST'])
@login_required
def admin():
    if request.method == "GET":
        if (session['id'] == 0):
            return render_template("admin.html")

        return redirect("/login")
    else:
        if ("logout" in request.form):
            session.pop('id', None)
            session.pop('user', None)
            return redirect("/login")

        if ("booking" in request.form):
            return redirect("/admin/booking")


@app.route("/admin/booking", methods=['GET', 'POST'])
@login_required
def bookingDetails():
    if request.method == 'GET':
        if (session['id'] == 0):
            result = con.execute(text("SELECT * FROM trips"))
            converted = convertResult(result)
            for i in converted:
                i['source_time'] = str(i['source_time'])
                i['destination_time'] = str(i['destination_time'])
            return render_template("booking.html", data=converted)
        return redirect("/login")
    else:
        if ("add" in request.form):
            source = request.form.get("source")
            destination = request.form.get("destination")
            source_time = request.form.get("source_time")
            destination_time = request.form.get("destination_time")
            price = request.form.get("price")

            print(source, source_time, destination_time, destination, price)
            print(type(source_time))

            con.execute(text("INSERT INTO trips (source, destination, source_time, destination_time, price) VALUES (:source, :destination, :source_time, :destination_time, :price)"), {
                        "source": source, "destination": destination, "source_time": source_time, "destination_time": destination_time, "price": price})

            return redirect("/admin/booking")


@app.route("/admin/bookings/editBookings/<int:id>", methods=['GET', 'POST'])
@login_required
def editBookings(id):
    if request.method == "GET":
        if (session['id'] == 0):
            print(id)
            result = con.execute(
                text("SELECT * FROM trips WHERE id = (:id) "), {"id": id})
            converted = convertResult(result)
            for i in converted:
                i['source_time'] = str(i['source_time'])[:-3]
                i['destination_time'] = str(i['destination_time'])[:-3]

                if (len(i['source_time']) < 5):
                    i['source_time'] = '0' + i['source_time']
                if (len(i['destination_time']) < 5):
                    i['destination_time'] = '0' + i['destination_time']

            print(converted)
            return render_template("editBookings.html", data=converted[0])
    else:
        if ("upd" in request.form):
            print("HELLLLLO")
            source = request.form.get("source")
            destination = request.form.get("destination")
            source_time = request.form.get("source_time")
            destination_time = request.form.get("destination_time")
            price = request.form.get("price")

            print(source, id)
            con.execute(text("UPDATE trips SET source = (:source), destination = (:destination), source_time = (:source_time), destination_time = (:destination_time), price = (:price) WHERE id = (:id)"), {
                "source": source, "destination": destination, "source_time": source_time, "destination_time": destination_time, "price": price, "id": id})
            flash("Updated successfully")
            
        if ("delete" in request.form):
            con.execute(text("DELETE FROM trips WHERE id = (:id)"),{"id": id})
            
        if ("upd" in request.form):
            print("YOOOOOOOO")
            
        return redirect("/admin/booking")


@app.route("/userPage", methods=['GET', 'POST'])
@login_required
def userPage():
    if request.method == "GET":
        if (session['id'] == 0):
            return redirect("/admin")
        return render_template("userPage.html", id=session['id'], name=session['user'])
    else:
        if ("logout" in request.form):
            session.pop('id', None)
            session.pop('user', None)
            return redirect("/login")

        if ("abc" in request.form):
            return "ABCCCCC"


def convertResult(result):
    resultList = []
    for data in result:
        resultList.append(dict(data))

    return resultList


# main driver function


if __name__ == '__main__':

    # run() method of Flask class runs the application
    # on the local development server.
    app.run(debug=True)
