from flask import Flask, flash, redirect, render_template, request, session, url_for
import os
from werkzeug.security import check_password_hash

from models.user import CutomerModel, AdminModel
from models.product import ProductModel
from models.order import OrderModel

app = Flask(__name__)

app.config["SECRET_KEY"] = os.urandom(16)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///ecommerce.db'

# Function to Authenticate Users based on roles, Only Admin Users can add/update Products and Admin can create Orders
def authenticate_user():
    current_user = session["email"]
    if AdminModel.find_by_email(current_user):
        return "Admin"
    elif CutomerModel.find_by_email(current_user):
        return "Customer"

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
                return redirect(url_for("all_products"))
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
            session["email"] = email
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
    auth = authenticate_user()

    if auth != "Admin":
        flash("Access Denied")
        return redirect(url_for("admin"))
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
        return redirect(url_for('all_products'))
    else:
        return render_template("addProduct.html")


@app.route("/products", methods=["GET", "POST"])
def all_products():
    
    products = ProductModel.find_all()
    if request.method == "POST":
        pass
        # Add to Cart
    else:
        if "cart" not in session:
            print("No cart")
            return render_template("allProducts.html", products=products)
        items = session["cart"]
        cart_items = {}
        amount = 0

        for item in items:
            product = ProductModel.find_by_id(item)
            amount += product.price
            print("amount")
            print(amount)
            if product.id in cart_items:
                cart_items[product.id]["qty"] +=1
            else:
                cart_items[product.id] = {"qty": 1, "name": product.name, "price": product.price}
                print(cart_items)
        return render_template("allProducts.html", products=products, cart=cart_items, total=amount)


@app.route("/add-to-cart/<int:product_id>")
def add_to_cart(product_id):
    if "cart" not in session:
        session["cart"] = []
    session["cart"].append(product_id)
    print(session["cart"])
    flash("Successfully Added to Cart, Proceed to Checkout or Continue Shopping")
    return redirect(url_for('all_products'))

@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == "__main__":
    from db import db
    db.init_app(app)
    app.run(port=5000, debug=True)