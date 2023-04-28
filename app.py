


from audioop import mul
from cmath import log
from datetime import date
from lib2to3.pytree import convert
from flask import session, render_template, redirect, request, Flask, url_for, flash, jsonify
from sqlalchemy import create_engine, text
from functools import wraps
from datetime import date
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
        if ("user" in request.form):
            return redirect("/admin/userDetails")


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
        return redirect("/login")


@app.route("/admin/booking/editBookings/<int:id>", methods=['GET', 'POST'])
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

@app.route("/trips", methods = ['GET','POST'])
def trips():
    if (request.method == 'GET'):
        results = con.execute(text("SELECT source, id FROM trips"))
        return render_template("trips.html", data = convertResult(results), selected = "")

@app.route("/destinations")
def destinations():
    source = request.args.get("source")
    
    results = con.execute(text("SELECT destination FROM trips WHERE source = (:source)"),{"source": source})
    converted = convertResult(results)
    # for data in converted:
    #     data['source_time'] = str(data['source_time'])
    #     data['destination_time'] = str(data['destination_time'])
    # print(converted)
    return jsonify(converted)

@app.route("/getTrips")
def getTrips():
    source = request.args.get("source")
    destination = request.args.get("destination")
    multiplier = request.args.get("multiplier")
    print(source,destination)
    results = con.execute(text("SELECT * FROM trips WHERE source = (:source) AND destination = (:destination)"),{"source": source, "destination" : destination})
    converted = convertResult(results)
    for data in converted:
        data['source_time'] = str(data['source_time'])
        data['destination_time'] = str(data['destination_time'])
        data['price'] = data['price'] * int(multiplier)
    # print(converted)
    return jsonify(converted)

@app.route("/book", methods = ['POST'])
@login_required

def book():
   if request.method == "POST":
       if (session['id'] == 0):
           return "Can't BOOK"
       id = int(request.form.get("id"))
       multiplier = int(request.form.get("multiplier"))
       departure = request.form.get("date")
       seats = int(request.form.get("seats"))
       print(multiplier)
       print(id)
       print(departure)
       print(seats)
       
       result = con.execute(text("SELECT price FROM trips WHERE id = (:id)"),{"id": id})
       converted = convertResult(result)[0]
       price = converted['price']
       
       cost = price * int(multiplier) * int(seats)
       print(cost)
       booked = getSeats(id,departure)
       if (seats > 50):
           return "CANT BOOK MORE THAN 50"
       if (booked  + seats  > 50):
           return "SEATS FILLED : Available " + str(50 - booked)

       con.execute(text("INSERT INTO bookings (user_id, booking_id, cost, seats, departure) VALUES (:user_id, :booking_id, :cost, :seats, :departure)") ,{"user_id" : session['id'], "booking_id": id,"cost": cost,"seats": seats,"departure": departure})
       return "Booked"

def getSeats(trip_id, departure):
    print("HELLLLLLLLLLLLLLLLLLLLLLL")
    result = con.execute(text("SELECT SUM(seats) as 'booked' FROM bookings WHERE booking_id = (:trip_id) AND departure = (:departure)"),{"trip_id" : trip_id, "departure" : departure})
    
    
    if (result == None):
        return 0

    for r in result:
        print(r,"JJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJ")
        if (r[0] == None):
            return 0
        return r[0]
# @app.route("/bookSeat", methods=['POST'])
# @login_required
# def bookSeat():
    
@app.route("/userPage", methods=['GET', 'POST'])
@login_required
def userPage():
    if request.method == "GET":
        if (session['id'] == 0):
            return redirect("/login")
        return render_template("userPage.html", id=session['id'], name=session['user'])
    else:
        if ("logout" in request.form):
            session.pop('id', None)
            session.pop('user', None)
            return redirect("/login")

        if ("abc" in request.form):
            return "ABCCCCC"

@app.route("/admin/userDetails", methods = ["POST", "GET"])
@login_required

def userDetails():
    if request.method == 'GET':
        if (session['id'] == 0):
            result = con.execute(text("SELECT * FROM users"))
            converted  =  convertResult(result)
            print(converted)
            return render_template("userDetails.html", data = converted)
        return redirect("/login")
    
    return redirect("/login")


@app.route("/admin/userDetails/editDetails/<int:id>", methods=['POST','GET'])
@login_required

def editDetails(id):
    if (request.method == 'GET'):
        if (session['id'] == 0):
            print(id)
            result = con.execute(text("SELECT * FROM users WHERE id = (:id) "),{"id" : id})
            converted = convertResult(result)
            print(converted)
            return render_template("editDetails.html", email = converted[0]['email'], password  = converted[0]['password'])
        return redirect("/login")
    
    else:
        email = request.form.get("email")
        password = request.form.get("password")
        
        print(email)
        con.execute(text("UPDATE users SET email = (:mail) , password = (:password) WHERE id = (:id)"), {"mail": email, "password": password, "id": id})
        return redirect("/admin/userDetails")

    

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
