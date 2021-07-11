from flask import Flask, flash, redirect, render_template, request, session, url_for
import os
import json
import requests
from werkzeug.security import check_password_hash

from models.user import CutomerModel, AdminModel
from models.product import ProductModel
from models.order import OrderModel

app = Flask(__name__)

app.config["SECRET_KEY"] = os.urandom(16)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///ecommerce.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Function to Authenticate Users based on roles, Only Admin Users can add/update Products and Admin can create Orders
def authenticate_user():
    current_user = session["email"]
    if current_user == "admin@mail.com": # AdminModel.find_by_email(current_user):
        return "Admin"
    elif CutomerModel.find_by_email(current_user):
        return "Customer"


# Global Variables to Hold the CART ITEMs and Total Amount
# cart_items = {}
# amount = 0


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
            return redirect(url_for("admin_dashboard"))

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


@app.route("/dashboard", methods=["GET", "POST"])
def admin_dashboard():
    auth = authenticate_user()

    if auth == "Admin":
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
            return redirect(url_for('admin_dashboard'))
        else:
            products = ProductModel.find_all()
            return render_template("adminDashboard.html", products=products)
    else:
        flash("Access Denied")
        return redirect(url_for("admin"))

def cart_factory():
    items = session["cart"]
    cart_items = {}
    amount = 0
    if items:
        for item in items:
            product = ProductModel.find_by_id(item)
            amount += product.price
            print("amount")
            print(amount)
            if product.id in cart_items:
                cart_items[product.id]["qty"] +=1
            else:
                cart_items[product.id] = {"qty": 1, "name": product.name, "price": product.price}
    return [cart_items, amount]

@app.route("/products")
def all_products():
    # Query the DB to get all products
    products = ProductModel.find_all()
    customer = CutomerModel.find_by_email(session["email"])
    # Check if products have been previously added to cart and Cart variable is in Session
    if "cart" not in session:
        print("No cart")
        return render_template("products.html", products=products, cart={}, customer=customer)
    else:
    # Cart is in Session, set the value to a variable - items, iterate over the items and find the product id, calculate the price, qty and add it to cart items global variable
        data = cart_factory()
        return render_template("products.html", products=products, cart=data[0], total=data[1], customer=customer)


@app.route("/product/<int:product_id>", methods=["POST"])
def product(product_id):
    if authenticate_user() == "Admin":
        this_product = ProductModel.find_by_id(product_id)
        updated_qty = request.form["qty"]
        this_product.quantity = updated_qty
        this_product.save_to_db()
        flash("Product Quantity successfully updated")
        return redirect(url_for('admin_dashboard'))
    else:
        flash("Access Denied")
        return redirect(url_for("admin"))


@app.route("/add-to-cart/<int:product_id>")
def add_to_cart(product_id):
    # Check if Cart is present in session Variables / Set it if NOT available
    if "cart" not in session:
        session["cart"] = []
    # Cart is a list to hold all products added to cart, use the append method to add new products to the cart list data structure
    session["cart"].append(product_id)
    print(session["cart"])
    flash("Successfully Added to Cart, Proceed to Checkout or Continue Shopping")
    return redirect(url_for('all_products'))


@app.route("/<int:customer_id>/create-order", methods=["GET", "POST"])
def create_order(customer_id):
    if "email" in session:
        if authenticate_user() == "Customer":
            customer = CutomerModel.find_by_email(session["email"])

            data = cart_factory()
            cart = json.dumps(data[0])
            if request.method == "GET":
                print(data[0])
                return render_template("order.html", cart=data[0], customer=customer, total=data[1])
            else:
                #POST REQUEST
                order = OrderModel(customer_id, order_data=cart, status="Pending", amount=data[1], billing_adress=request.form["address"])
                order.save_to_db()

                # Update the inditouch vidual item quantities here

                flash("Order Created, Proceed to make Payment")
                return redirect(url_for('order_payment', order_id=order.id))
                # Redirect to Payment page
            
        else:
            flash("Access Denied")
            # Redirect to Login  
            return redirect(url_for("index")) 
    else:
            flash("Please Sign in to place an Order")
            # Redirect to Login  
            return redirect(url_for("index")) 


@app.route("/order/<int:order_id>/payment")
def order_payment(order_id):
    if authenticate_user() == "Customer":
        customer = CutomerModel.find_by_email(session["email"])
        order = OrderModel.find_by_id(order_id)

        url = "api.paystack.co"
        auth = "sk_test_8e81c920217c39de48c778ca688c97f23035f86a"
        params = {"email": customer.email,  "amount": order.amount, "metadata": order.order_data}
    

        res = requests.post("https://api.paystack.co/transaction/initialize", headers={'Authorization': 'Bearer {}'.format(auth), 'Content-Type': 'application/json'}, json=params)
        
        res = res.json()
        # return res
        auth_url = res["data"]["authorization_url"]
        reference = res["data"]["reference"]
        return redirect(auth_url)

        reference = request.args.get("reference")

        res1 = res = requests.get("https://api.paystack.co/transaction/verify/" + reference, headers={'Authorization': 'Bearer {}'.format(auth)})
        
        # return res1.json()
#         response = transaction.verify(reference)
#         if response[3]["status"] == "success":
#             order.status = "Paid" 
#             return render_template("payment.html", response=response)

#         elif response[3]["status"] == "failed":
#             order.status = "unpaid" 
#             return render_template("payment.html", response=response)
#     else:
#         flash("Please Login to continue")
#         return redirect(url_for('index'))


@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == "__main__":
    from db import db
    db.init_app(app)
    app.run(port=5000, debug=True)