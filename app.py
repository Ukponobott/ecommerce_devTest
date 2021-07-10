from flask import Flask, flash, redirect, render_template, request, session, url_for
import os
from werkzeug.security import check_password_hash

from models.user import CutomerModel, AdminModel
from models.product import ProductModel
from models.order import OrderModel

app = Flask(__name__)

app.config["SECRET_KEY"] = os.urandom(16)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///ecommerce.db'


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

    # Get form data from the HTML FORM
        email = request.form["email"]
        password = request.form["password"]

        # Query the DB to check if the email exists
        user = CutomerModel.find_by_email(email)
        if user:
            print(user.email)

            # check if the password suplplied matches the one saved in the DB, log in user if yes and create a session, do otherwise if not
            if check_password_hash(user.password_hash, password):
                session["email"] = user.email
                return redirect("all_products")
            flash("wrong password")
            return render_template('index.html')
        else:
            flash("User does not exist")
            return render_template('index.html')
    else:
        return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]

        #Query th DB to check if email already exists
        if CutomerModel.find_by_email(email):
            flash("User already exists")
        else:
            # Use the Customer model to create a new customer with the data from the HTML form
            full_name = request.form["full_name"]
            password = request.form["password"]
            customer = CutomerModel(full_name=full_name, email=email, password=password)
            customer.save_to_db()
            flash("Registration Successful, please proceed to login")
            return redirect(url_for('index'))
    return render_template("signUp.html")


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        #Get the email and password from HTML Form, use admin@mail.com and 1234567890 as password for testing
        email = request.form["email"]
        password = request.form["password"]

        # check if it matches the default values and send appropaite response

        # email and password matches
        if email == "admin@mail.com" and password == "1234567890":
            return render_template("addProduct.html")

        # incorrect email and correct password
        elif email != "admin@mail.com" and password == "1234567890":
            flash("Email does not exist, please try again")
        # correct email and incorrect password
        elif email == "admin@mail.com" and password != "1234567890":
            flash("Wrong Password")

        # incorrect details
        elif email != "admin@mail.com" and password != "1234567890":
            flash("Invalid Credentials")
    else:
        return render_template("admin.html")


@app.route("/add-product", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        # Get the Product Data from the HTML Form
        name = request.form["name"]
        brand = request.form["brand"]
        price = request.form["price"]
        category = request.form["category"]
        colour = request.form["colour"]
        quantity = request.form["quantity"]

        # Use the Product Model to create a new Product using the parameters gotten from the HTML FORM 
        new_product = ProductModel(name=name, brand=brand, price=price, category=category, colour=colour, quantity=quantity)
        new_product.save_to_db()
        flash("New Product Added Successfully")
        return redirect('add_product') 
    else:
        return render_template("addProduct.html")

@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == "__main__":
    from db import db
    db.init_app(app)
    app.run(port=5000, debug=True)