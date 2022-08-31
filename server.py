# Import required libraries
from flask import *
from flask_mysql_connector import MySQL
from flask_mail import Mail, Message
import numpy
from datetime import datetime
import string
import random
import stripe
import pdfkit

#comment

# Setting up the server and what it needs to run
server = Flask(__name__)
mail = Mail(server)

secretKey = "QrfS1qPGtoCLoalDz6lmLPiqr6j6tG"
server.secret_key = secretKey

# Setting up the database stuff
server.config["MYSQL_USER"] = "root"
server.config["MYSQL_PASSWORD"] = "comsc"
server.config["MYSQL_DATABASE"] = "imageoptimteam10"

server.config['MAIL_SERVER']='smtp.gmail.com'
server.config['MAIL_PORT'] = 465
server.config['MAIL_USERNAME'] = 'imageoptim@gmail.com'
server.config['MAIL_PASSWORD'] = 'cbmfyubrerkjomio'
server.config['MAIL_USE_SSL'] = True
server.config['MAIL_DEFAULT_SENDER'] = 'imageoptim@gmail.com'
mail = Mail(server)
mysql = MySQL(server)

# Function used when reding an sql file with multiple lines
def executeLines(cursor, file):
    for line in file:
        cursor.execute(line)
    return cursor
    
stripe_keys = {
  'secret_key': "sk_test_51IjPMTEv60KpdeRfGSEhNju486aIoF3ZNOY25VaLKBidciqx8alrW4QcdyUEoMgkp6G0v2HjnrHRr3uwBfDQkbE400VuRiqqaL",
  'publishable_key': "pk_test_51IjPMTEv60KpdeRfbJkctVNLAemGOODp9UFdt0plqYT2r5WKLkYrVs6ATp3uQeZjyBY41dpyRd1f45YlGSFfH9BE003kOVgWWr"
}

stripe.api_key = stripe_keys['secret_key']


# Encryption function - "msgToEncrypt" should be an objectt of type "string"
# Encryption algorithms found at using the main answer:
# https://stackoverflow.com/questions/5131227/custom-python-encryption-algorithm
def encrypt(msgToEncrypt):
    encrypted = []
    for i, c in enumerate(msgToEncrypt):
        # The "ord" function is used to get the Unicode value which represents the input
        key_c = ord(secretKey[i % len(secretKey)])
        msg_c = ord(c)
        encrypted.append(chr((msg_c + key_c) % 127))
    return ''.join(encrypted)

def decrypt(msgToDecrypt):
    print("pre decrypt")
    passDecrypted = []
    for i, c in enumerate(msgToDecrypt):
        key_c = ord(secretKey[i % len(secretKey)])
        enc_c = ord(c)
        passDecrypted.append(chr((enc_c - key_c) % 127))
    print("post decrypt")
    return ''.join(passDecrypted)

def mysql_connection():
    conn = mysql.connection
    cur = conn.cursor()

    return cur

@server.route("/")
def adminHomeRoute():
    # For now, just loads the page without accessing or passing on any data]
    try:
        if session["admin"] == True:
            return render_template("AdminHome.html")
        else:
            # Code moved from old "home" route
            if "cart" in session:
                session["cart"] = session["cart"]
            else:
                session["cart"] = []
            cur = mysql.new_cursor(dictionary=False)
            cur = executeLines(
                cur, open("database_stuff/sql_scripts/ProductSelection.sql"))
            Product = cur.fetchall()
            return render_template("home.html", Product=Product)
    except:
        cur = mysql.new_cursor(dictionary=False)
        cur = executeLines(
            cur, open("database_stuff/sql_scripts/ProductSelection.sql"))
        Product = cur.fetchall()
        return render_template("home.html", Product=Product)


@server.route("/Products/<product_id>")
def view_products(product_id):

    if "cart" in session:
        session["cart"] = session["cart"]
    else:
        session["cart"] = []

    cur = mysql.new_cursor(dictionary=False)
    try:
        product_info = '''SELECT * FROM products where ProductID = %s ''' % product_id
        cur.execute(product_info)
        product_info = cur.fetchall()

        company_info = '''SELECT * FROM companytypes'''
        cur.execute(company_info)
        company_info = cur.fetchall()

        license_info = '''SELECT * FROM licenses'''
        cur.execute(license_info)
        license_info = cur.fetchall()

        return render_template('ProductPage.html', product_id=product_id, products=product_info, company_types=company_info,licenses = license_info)
    except:
        abort(500)


@server.route("/AddToCart", methods=["POST"])
def add_cart():
    flash("Item was added to cart", "success")
    productInfo = request.form["productInfo"]
    licenseType = request.form["licenseType"]
    companySize = request.form["companySize"]
    #get current session cart items
    userCart = session["cart"]
    item_id = len(userCart)
    #append new item to local variable
    userCart.append(tuple((item_id, productInfo, licenseType, companySize)))
    #update variable in session
    session["cart"] = userCart

    return redirect("/Cart")

@server.route("/RemoveFromCart/<item_to_remove>", methods=['GET', 'POST'])
def remove_cart(item_to_remove):
    flash("Item was deleted from cart", "success")
    #get current session cart items
    userCart = session["cart"]
    #Removing the item using a for loop
    for item in userCart:
        if int(item[0]) == int(item_to_remove):
                userCart.remove(item)

    return redirect("/Cart" )


@server.route("/Contact", methods=['GET', 'POST'])
def contact():
    if request.method == "POST":
        FirstName = "`" + request.form['fname'] + "`"
        LastName = "`" + request.form['lname'] + "`"
        Email = "`" + request.form['Email'] + "`"
        Number = "`" + request.form['number'] + "`"
        Message = "`" + request.form['message'] + "`"

        conn = mysql.connection
        cur = conn.cursor()
        cur.execute("INSERT INTO ContactLog (FirstName, LastName, Email, Number, Message) VALUES(%s, %s, %s, %s, %s)", (FirstName, LastName, Email, Number, Message))
        conn.commit()
        flash("Submission Successful", "success")
        return redirect ("/")
    return render_template ("Contact.html")


@server.route("/Cart", methods=['GET', 'POST'])
def view_cart():
    try:
        cur = mysql.new_cursor(dictionary=False)
        cart_info = session["cart"]
        cart_product_info = []
        total_price = 0

        for product in cart_info:
            print("item_id")
            item_id = product[0]
            product_id = product[1]
            license_type = product[2]
            company_id = product[3]

            # SELECT CURRENT PRODUCT INFO FROM DB
            product_information = '''SELECT * FROM products where ProductID = %s ''' % product_id
            cur.execute(product_information)
            product_information = cur.fetchall()

            # SELECT CURRENT PRODUCT COMPANY SIZE
            company_information = '''SELECT * FROM CompanyTypes WHERE SizeID = %s ''' % company_id
            cur.execute(company_information)
            company_information = cur.fetchall()

            license_information = '''SELECT * FROM licenses WHERE LicenseID = %s ''' % license_type
            cur.execute(license_information)
            license_information = cur.fetchall()

            product_price = product_information[0][1] + \
                company_information[0][2]

            # CREATE LIST OF TUPLES FOR NEW CART
            cart_product_info.append(
                tuple((product_information, license_type, company_information, product_price, item_id,license_information)))

            print(cart_product_info)

            total_price += product_price

        return render_template("Cart.html", isempty=False, cart=cart_product_info, price=total_price)
    except:
        return render_template("Cart.html", isempty=True, cart="Your cart is empty")


# Display Cart details on the Checkout page
@server.route("/Checkout")
def cart_info_checkout():


    cur = mysql.new_cursor(dictionary=False)
    cart_info = session["cart"]
    cart_product_info = []
    total_price = 0
    user_information = ""
    logged_in = False

    if "loggedin" in session:
        logged_in = True
        # SELECT CURRENT PRODUCT INFO FROM DB
        user_information = '''SELECT * FROM users WHERE UserID = %s ''' % session['UserID']
        cur.execute(user_information)
        user_information = cur.fetchall()
    else:
        user_information = ""


    for product in cart_info:
        product_id = product[1]
        license_type = product[2]
        company_id = product[3]

        # SELECT CURRENT PRODUCT INFO FROM DB
        product_information = '''SELECT * FROM products where ProductID = %s ''' % product_id
        cur.execute(product_information)
        product_information = cur.fetchall()

        # SELECT CURRENT PRODUCT COMPANY SIZE
        company_information = '''SELECT * FROM CompanyTypes WHERE SizeID = %s ''' % company_id
        cur.execute(company_information)
        company_information = cur.fetchall()

        license_information = '''SELECT * FROM licenses WHERE LicenseID = %s ''' % license_type
        cur.execute(license_information)
        license_information = cur.fetchall()

        product_price = product_information[0][1] + \
            company_information[0][2]

        # CREATE LIST OF TUPLES FOR NEW CART
        cart_product_info.append(
            tuple((product_information, license_type, company_information, product_price,license_information)))

        total_price += product_price

        # Take into account promoCode
        if "promoType" in session:
            if session["promoType"] == "percentage":
                total_price = total_price * session["promoValue"]
                print("Using percentage discount")
                print(total_price)
            elif session["promoType"] == "fixed":
                total_price = total_price - session["promoValue"]
                print("Using fixed discount")
                print(total_price)
    
    stripe_price = total_price * 100

    return render_template("Checkout.html",loggedin=logged_in, isempty=False, cart=cart_product_info, price=total_price, user = user_information,key=stripe_keys['publishable_key'],stripeprice=stripe_price)


# Function to generate random password
def randpass():
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for x in range(0,8))

# Function to find total cart price
def find_total_price():
    cur = mysql.new_cursor(dictionary=False)
    cart_info = session["cart"]
    total_price = 0
    for product in cart_info:
            product_id = product[1]
            company_id = product[3]

            # SELECT CURRENT PRODUCT INFO FROM DB
            product_information = '''SELECT * FROM products where ProductID = %s ''' % product_id
            cur.execute(product_information)
            product_information = cur.fetchall()

            # SELECT CURRENT PRODUCT COMPANY SIZE
            company_information = '''SELECT * FROM CompanyTypes WHERE SizeID = %s ''' % company_id
            cur.execute(company_information)
            company_information = cur.fetchall()

            product_price = product_information[0][1] + \
                company_information[0][2]

            total_price += product_price

            # Take into account promoCode
            if "promoType" in session:
                if session["promoType"] == "percentage":
                    total_price = total_price * session["promoValue"]
                elif session["promoType"] == "fixed":
                    total_price = total_price - session["promoValue"]

    return total_price


def order_complete(email, contactname, cart, password, accountexists):
    cur = mysql.new_cursor(dictionary=False)
    cart_product_info = []
    for product in cart:
        product_id = product[1]
        license_type = product[2]
        company_id = product[3]

        # SELECT CURRENT PRODUCT INFO FROM DB
        product_information = '''SELECT * FROM products where ProductID = %s ''' % product_id
        cur.execute(product_information)
        product_information = cur.fetchall()

        # SELECT CURRENT PRODUCT COMPANY SIZE
        company_information = '''SELECT * FROM CompanyTypes WHERE SizeID = %s ''' % company_id
        cur.execute(company_information)
        company_information = cur.fetchall()

        product_price = product_information[0][1] + \
            company_information[0][2]

        # CREATE LIST OF TUPLES FOR NEW CART
        cart_product_info.append(
            tuple((product_information, license_type, company_information, product_price)))

    total_price = find_total_price()
    newaccount = False
    if accountexists == False:
        newaccount = True
    else:
        newaccount = False
        password = ""

    msg = Message('ImageOptim - Order Confirmed', recipients=[])
    msg.add_recipient(email)
    msg.body = 'OrderComplete'
    msg.html = render_template('OrderEmail.html', cart = cart_product_info, name = contactname, price = total_price, new_account = newaccount, temppass = password)
    mail.send(msg)

    return redirect("/OrderComplete")


@server.route("/PromoSubmission", methods=["POST","GET"])
def submitPromoCode():
    # Create a cursor
    cur = mysql.new_cursor(dictionary=False)
    # Get all the promo codes from the database
    cur.execute("SELECT * FROM PromoCodes")
    promoCodes = cur.fetchall()
    # If the user is not logged in
    if "loggedin" not in session:
        # Flash that users need to be logged in to use Promo Codes
        flash("You must be logged in to use Promo Codes", "danger")
        # Redirect back to the checout page
        return redirect("/Checkout")
    # Else (the user is logged in)
    else:
        # Get the code entered from the table
        code = request.form["Discount"]
        print(code)
        # For each item in the tuple
        for item in promoCodes:
            print("Searching: " + str(item))
            # If the entered code is in this entry to the table
            if code in item:
                print("Correct Item Found")
                # If the correct user is logged in
                if item[4] == session['UserID']:
                    print("Correct User")
                    # If it's a percentage discount (the percentage value is not none)
                    if item[2] is not None:
                        print("Percentage Code")
                        # Update the session accordingly
                        session['promoType'] = "percentage"
                        session['promoValue'] = 1 - item[2]
                        print("Session Updated")
                    # Else-If it's a fixed discount (the fixed value is not none)
                    elif item[3] is not None:
                        print("Fixed Code")
                        # Update the session accordingly
                        session['promoType'] = "fixed"
                        session['promoValue'] = item[3]
                        print("Sesssion Updated")
                    # Alert the code was successful, and redirect the user back to the Checkout
                    flash("Code Successful", "success")
                    return redirect("/Checkout")
                # Else (the incorrect user is using the code)
                else:
                    # Alert the user with the appropriate error, and redirect them
                    flash("Incorrect User", "danger")
                    return redirect("/Checkout")
        # Alert the user with the appropriate error, and redirect them
        flash("Code not Found", "danger")
        return redirect("/Checkout")


@server.route("/Purchase", methods=["POST"])
def Add_PurchaseLog():

    conn = mysql.connection

    cur = conn.cursor()

    # Retrieving data from the form
    session['Contact_Email'] = request.form["ContactEmail"]
    session['Contact_Name'] = request.form["ContactName"]
    session['Company_Name'] = request.form["CompanyName"]
    session['Company_Address'] = request.form["Address"]
    session['Company_Region'] = request.form["Region"]



    # Connect to the database and create a cursor
    #cur = mysql.new_cursor(dictionary=False)
    # Get current session cart items
    cart_info = session["cart"]

    session['Company_Size'] = cart_info[0][2]

    now = datetime.now()

    bare_time = now.strftime("%d/%m/%y, %H:%M:%S")
    total_price = find_total_price()

    try:
        if "loggedin" in session:
            print("here")
            # Purchase Log Table Entries (PurchasePrice, PurchaseDate, Products_ProductID, Licenses_LicenseID, CompanyTypes_SizeID, Users_UserID)
            for product in cart_info:
                cur.callproc('CompletePurchase',[total_price, bare_time, product[1],product[2], product[3],session['UserID'],0])
            print("here")
            get_user = ''' SELECT * FROM Users WHERE UserID = %s ''' % session['UserID']
            cur.execute(get_user)
            get_user = cur.fetchall()
            print("here")

            order_complete('"' + get_user[0][1] + '"', get_user[0][4], cart_info, "", True)

        else:
            get_current_users = ''' SELECT * FROM Users '''
            cur.execute(get_current_users)
            users_current = cur.fetchall()
            AccountExists = False
            for item in users_current:
                if session['Contact_Email'] in item:
                    AccountExists = True
            if AccountExists == False:
                # Get a random password
                randPassword = randpass()
                # Store the encrypted password in a seperate variable
                encryptedRandPass = encrypt(randPassword)
                # Users Table Entries (UserEmail, UserPassword, CompanyName, ContactName, CompanyAddress, Countries_CountryID, CompanyTypes_SizeID)
                cur.callproc('CreateUser',[session['Contact_Email'],encryptedRandPass,session['Company_Name'],session['Contact_Name'],session['Company_Address'],session['Company_Region'], session['Company_Size']])
                get_user_id = '''SELECT UserID FROM users WHERE UserEmail = %s''' % "'" + session['Contact_Email'] + "'"
                cur.execute(get_user_id)
                get_user_id = cur.fetchall()
                session['UserID'] = get_user_id[0][0]
            else:
                print("here")
                get_user_id = '''SELECT UserID FROM users WHERE UserEmail = %s''' % "'" + session['Contact_Email'] + "'"
                cur.execute(get_user_id)
                print("here")
                get_user_id = cur.fetchall()
                session['UserID'] = get_user_id[0][0]
            for product in cart_info:
                print("here")
                cur.callproc('CompletePurchase',[total_price, bare_time, product[1],product[2], product[3],get_user_id[0][0],0])
            # Commit to the database
            conn.commit()

            get_user = ''' SELECT * FROM Users WHERE UserID = %s ''' % session['UserID']
            cur.execute(get_user)
            get_user = cur.fetchall()

            # Decrypt the password
            decryptpass = decrypt(get_user[0][2])
            print("decrypted")
            # Pass in the decryped password gotten for the current user, rather than the randPass
            order_complete('"' + get_user[0][1] + '"', get_user[0][4], cart_info, decryptpass, AccountExists)

        conn.commit()
        return redirect('/OrderComplete')
    except:
        print("hello")
        flash("Your order couldn't be completed", "danger")
        return redirect("/")


@server.route("/Payment", methods=["POST", "GET"])
def payment():
    cur = mysql.new_cursor(dictionary=False)
    cart_info = session["cart"]
    cart_product_info = []
    total_price = 0

    for product in cart_info:
        product_id = product[1]
        license_type = product[2]
        company_id = product[3]

        # SELECT CURRENT PRODUCT INFO FROM DB
        product_information = '''SELECT * FROM products where ProductID = %s ''' % product_id
        cur.execute(product_information)
        product_information = cur.fetchall()

        # SELECT CURRENT PRODUCT COMPANY SIZE
        company_information = '''SELECT * FROM CompanyTypes WHERE SizeID = %s ''' % company_id
        cur.execute(company_information)
        company_information = cur.fetchall()

        product_price = product_information[0][1] + \
            company_information[0][2]

        # CREATE LIST OF TUPLES FOR NEW CART
        cart_product_info.append(
            tuple((product_information, license_type, company_information, product_price)))

        total_price += product_price

    # Take into account promoCode
    if "promoType" in session:
        if session["promoType"] == "percentage":
            total_price = total_price * session["promoValue"]
            print("Using percentage discount")
            print(total_price)
        elif session["promoType"] == "fixed":
            total_price = total_price - session["promoValue"]
            print("Using fixed discount")
            print(total_price)
    UserTuple = (session['Contact_Email'],session['Company_Name'],session['Contact_Name'],session['Company_Address'],session['Company_Region'], session['Company_Size'])

    amount = 500

    customer = stripe.Customer.create(
        email='customer@example.com',
        source=request.form['stripeToken']
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency='usd',
    )



    return render_template("Payment.html",isempty=False, cart=cart_product_info, price=total_price, user = UserTuple,amount=amount)

@server.route("/OrderComplete", methods=['POST','GET'])
def ordercomplete():
    conn= mysql.connection
    cur = conn.cursor()
    session['OrderComplete'] = True
    try:
        if session['OrderComplete'] == True:
            print("here")
            session.pop("cart")
            cur = mysql.new_cursor(dictionary=False)
            latest_order = '''SELECT * FROM purchaselog WHERE Users_UserID = %s ORDER BY PurchaseID DESC LIMIT 1''' % session['UserID']
            cur.execute(latest_order)
            latest_order = cur.fetchall()

            latest_product = '''SELECT * FROM products WHERE ProductID = %s''' % latest_order[0][3]
            cur.execute(latest_product)
            latest_product = cur.fetchall()

            session['OrderComplete'] = False
            return render_template("OrderConfirmed.html", order=latest_order, product=latest_product)
        else:
            flash("Your order couldn't be completed", "danger")
            return redirect("/")
    except:
        return redirect("/")




@server.route("/Invoice/<order_id>")
def getinvoicedata(order_id):

    # Connect to the database and create a cursor
    cur = mysql.new_cursor(dictionary=False)

    # Get Invoice data from the Purchaselog table
    InvData = '''SELECT * FROM purchaselog WHERE PurchaseID = %s''' % (order_id)
    cur.execute(InvData)
    InvData = cur.fetchall()


    # Get the PurchaseID
    InvId = InvData[0][0]
    # Get the User's email
    cur.execute("SELECT UserEmail FROM Users WHERE UserID = %s" % InvData[0][6])
    InvEmail = cur.fetchall()
    # Get the Product's name
    cur.execute("SELECT ProductName FROM Products WHERE ProductID = %s" % InvData[0][3])
    InvProduct = cur.fetchall()
    # Get the Contact's Name
    cur.execute("SELECT ContactName FROM Users WHERE UserID = %s" % InvData[0][6])
    InvContact = cur.fetchall()
    # Get the Company's name
    cur.execute("SELECT CompanyName FROM Users WHERE UserID = %s" % InvData[0][6])
    InvCompanyName = cur.fetchall()
    # Get the Company's Address
    cur.execute("SELECT CompanyAddress FROM Users WHERE UserID = %s" % InvData[0][6])
    InvCompanyAddress = cur.fetchall()
    # Get the Company Size
    cur.execute("SELECT SizeType FROM CompanyTypes WHERE SizeID = %s" % InvData[0][5])
    InvCompanySize = cur.fetchall()
    # Get the LicensePaymentType
    cur.execute("SELECT LicenseType FROM Licenses WHERE LicenseID = %s" % InvData[0][4])
    InvLicense = cur.fetchall()
    # Get whether the purchase is VAT Applicable
    cur.execute("SELECT VATApplicable FROM Countries WHERE CountryID = (SELECT Countries_CountryID FROM Users WHERE UserID = %s)" % InvData[0][6])
    InvVAT = cur.fetchall()
    # Get the PurchaseDate
    InvDate = InvData[0][2]
    # Get the Purhcase Price
    InvPrice = InvData[0][1]

    RenderInv = render_template("/Invoice.html", InvId=InvId, Email=InvEmail, Product=InvProduct, Contact=InvContact,
    CompanyName=InvCompanyName, CompanyAddress=InvCompanyAddress, CompanySize=InvCompanySize, License=InvLicense,
    Date=InvDate, Vat=InvVAT, InvPrice=InvPrice)

    Invpdf = pdfkit.from_string(RenderInv, False)

    response = make_response(Invpdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline'; 'filename=invoice.pdf'

    return response


@server.route("/Login", methods=["POST", "GET"])
def login():
    if "loggedin" in session:
        return redirect("/Account")
    else:
        if request.method == "POST":
            cur = mysql.new_cursor(dictionary=False)
            email = request.form["email"]
            # Get the encrypted version of the password to check against the database
            # since all database passwords are encrypted
            password = encrypt(request.form["password"])
            logged_in = (email, password)
            query_email = "'" + request.form["email"] + "'"

            try:
                user_info = '''SELECT * FROM Users WHERE UserEmail = %s''' % query_email
                cur.execute(user_info)
                user_info = cur.fetchall()
                if user_info[0][1:3] == logged_in:
                    session["admin"] = user_info[0][6]
                    session["loggedin"] = True
                    session["email"] = email
                    session["UserID"] = user_info[0][0]
                    if "cart" in session:
                        session["cart"] = session["cart"]
                    else:
                        session["cart"] = []
                    return redirect("/Account")
                else:
                    flash("Incorrect Credentials", "danger")
                    return redirect('/Login')
            except:
                flash("Incorrect Credentials", "danger")
                return render_template("Login.html")
        else:
            return render_template("Login.html")


@server.route("/Logout")
def logout():
    session.clear()
    flash("You've Been Logged Out", "success")
    return redirect("/")


@server.route("/Account")
def my_account():
    cur = mysql.new_cursor(dictionary=False)

    account_info = '''SELECT * FROM Users WHERE UserID = %s''' % session[
        "UserID"]
    cur.execute(account_info)
    account_info = cur.fetchall()

    # # Decrypt the user's password for display
    # decrypted = []
    # for i, c in enumerate(account_info[0][2]):
    #     key_c = ord(secretKey[i % len(secretKey)])
    #     enc_c = ord(c)
    #     decrypted.append(chr((enc_c - key_c) & 127))
    # account_info[0][2] = ''.join(decrypted)

    country_info = '''SELECT * FROM countries WHERE CountryID = %s''' % account_info[0][7]
    cur.execute(country_info)
    country_info = cur.fetchall()

    company_info = '''SELECT * FROM CompanyTypes WHERE SizeID = %s''' % account_info[0][8]
    cur.execute(company_info)
    company_info = cur.fetchall()

    order_info = '''SELECT * FROM PurchaseLog WHERE Users_UserID = %s''' % account_info[0][0]
    cur.execute(order_info)
    order_info = cur.fetchall()

    return render_template('MyAccount.html', account=account_info, company=company_info, country=country_info, orders=order_info)

@server.route("/ChangePassword" ,methods=['POST','GET'])
def change_password():
    if request.method == 'POST':
        try:
            # Encrypt the entered new password
            new_password = encrypt(request.form['new_password'])
            query_new_password = "'" + new_password + "'"
            conn = mysql.connection
            # Update password
            cur = conn.cursor()
            update_password = '''UPDATE Users SET UserPassword = %s WHERE UserID = %s''' % (query_new_password, session['UserID'])
            cur.execute(update_password)
            conn.commit()
            flash("Password Has Been Updated", "success")
            return redirect("/Account")
        except:
            flash("Password Was Not Updated", "danger")
            return redirect("/Account")
    else:
        flash("Password Was Not Updated", "danger")
        return redirect("/Account")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ADMIN ROUTES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Admin PurchaseLog
@server.route("/PurchaseLog")
def adminPurchaseRoute():
    if session["admin"] == True:
        # Connect to the database
        cur = mysql.new_cursor(dictionary=False)
        # Select all from the PuchaseLog database
        cur.execute("SELECT * FROM PurchaseLog")
        PurchaseLogData = cur.fetchall()
        # Create an empty array to store the data
        dataToSend = []
        # For each item in the list
        for x in range(len(PurchaseLogData)):
            # Get the PurchaseID from the data
            PurLogID = PurchaseLogData[x][0]
            # Get the User's email for the current Log from the database
            cur.execute("SELECT UserEmail FROM Users WHERE UserID = %s" % PurchaseLogData[x][6])
            PurEmail = cur.fetchall()
            # Get the product's name for the Current Log from the database
            cur.execute("SELECT ProductName FROM Products WHERE ProductID = %s" % PurchaseLogData[x][3])
            PurProduct = cur.fetchall()
            # Get the Company's name for the current Log from the database
            cur.execute("SELECT CompanyName FROM Users WHERE UserID = %s" % PurchaseLogData[x][6])
            PurCompanyName = cur.fetchall()
            # Get the Company Size for the current Log from the database
            cur.execute("SELECT SizeType FROM CompanyTypes WHERE SizeID = %s" % PurchaseLogData[x][5])
            PurCompanySize = cur.fetchall()
            # Get the LicensePaymentType for the current Log from the database
            cur.execute("SELECT LicenseType FROM Licenses WHERE LicenseID = %s" % PurchaseLogData[x][4])
            PurLicensePayment = cur.fetchall()
            # Get whether the purchase is VAT Applicable for the current Log from the database
            cur.execute("SELECT VATApplicable FROM Countries WHERE CountryID = (SELECT Countries_CountryID FROM Users WHERE UserID = %s)" % PurchaseLogData[x][6])
            PurVAT = cur.fetchall()
            # Get the PurchaseDate from the data
            PurDate = PurchaseLogData[x][2]
            # Get the Purhcase Price from the data
            PurPrice = PurchaseLogData[x][1]
            # Append the data to the array
            dataToSend.append([PurLogID, PurEmail, PurProduct, PurCompanyName, PurCompanySize, PurLicensePayment, PurVAT, PurDate, PurPrice])
        # Final Structure:
        # [[PurchaseID, UserEmail, ProductName, CompanyName, CompanySize, LicensePaymentType, VATApplicable, PurchaseDate, FullPrice]...]
        return render_template("AdminPurchaseLog.html", PurchaseData=dataToSend)
    else:
        # Redirects the user to the Home route
        return redirect("/Page/Home")

# Route for deleting a specified purchase
@server.route("/Delete/Purchase/<purchase_id>")
def deletePurchaseData(purchase_id):
    if session["admin"] == True:
        # Connect to the database and create a cursor
        conn= mysql.connection
        cur = conn.cursor()
        # Execute a delete all statement on the specified table
        cur.execute('''DELETE FROM PurchaseLog WHERE PurchaseID = %s;''' %
                    purchase_id)
        conn.commit()
        # Return a statement that the route was successful
        return("Route successful")
    else:
        return render_template("home.html")


# Admin User Log
@server.route("/UserLog")
def adminUserRoute():
    # Connect to the database
    cur = mysql.new_cursor(dictionary=False)
    # For now, just loads the page without accessing or passing on any data
    if session["admin"] == True:
        # Select the data
        cur.execute(
            "SELECT UserID, UserEmail, UserPassword, CompanyName, CompanyTypes_SizeID, UserID FROM Users;")
        # Pass the data into a variable
        userLogData = cur.fetchall()
        # Create the variable which will be passed to the site
        dataToSite = []
        # For each item in the variable
        for x in range(len(userLogData)):
            # Get the company type
            cur.execute(
                "SELECT SizeType FROM CompanyTypes WHERE SizeID = %s" % userLogData[x][4])
            companyTypeData = cur.fetchall()
            # Append the required data to the variable to send back
            dataToSite.append([userLogData[x][0], userLogData[x][1], userLogData[x][2], userLogData[x][3], companyTypeData])
        # Render the template for the UserLog admin page, sending in the acquired data
        return render_template("AdminUserLog.html", dataToSend=dataToSite)
    else:
        return render_template("home.html")

# Route for deleting a specified user
@server.route("/Delete/User/<user_id>")
def deleteUserData(user_id):
    if session["admin"] == True:
        # Connect to the database and create a cursor
        conn= mysql.connection
        cur = conn.cursor()
        # Execute a delete all statement on the specified table
        cur.execute('''DELETE FROM Users WHERE UserID = %s;''' % user_id)
        conn.commit()
        # Return a statement that the route was successful
        return("Route successful")
    else:
        return render_template("home.html")


# Route for new TableModification
@server.route("/TableModification")
def tableModification():
    if session["admin"] == True:
        # Create a cursor
        cur = mysql.new_cursor(dictionary=False)
        # Get all the data from the products table
        cur.execute("SELECT * FROM Products")
        productData = cur.fetchall()
        # Get all the data from the CompanyTypes table
        cur.execute("SELECT * FROM CompanyTypes")
        companyTypeData = cur.fetchall()
        # Get all the data from the Licenses table
        cur.execute("SELECT * FROM Licenses")
        licensesData = cur.fetchall()
        # Get all the data from the Countries table
        cur.execute("SELECT * FROM Countries")
        countriesData = cur.fetchall()
        # Render the template, passing in the necessary data
        return render_template("AdminTableModification.html", products=productData, companyTypes=companyTypeData, licenses=licensesData, countries=countriesData)
    else:
        return redirect("/")

# Route for populating the data of a specified table
@server.route("/Populate/<table_id>")
def populateTableData(table_id):
    if session["admin"] == True:
        # Connect to the database and create a cursor
        conn= mysql.connection
        cur = conn.cursor()
        # File to run
        file_to_run = "database_stuff/sql_scripts/database_population/" + table_id + ".sql"
        # Execute a delete all statement on the specified table
        cur = executeLines(cur, open(file_to_run))
        conn.commit()
        # Flash a successful statement
        flash("Population Successful", "success")
        # Return a statement that the route was successful
        return redirect("/TableModification")
    else:
        return redirect("/")

# Method for adding a product
@server.route("/AddProduct", methods=["POST"])
def addProduct():
    if session["admin"] == True:
        try:
            # Get the data from the form
            price = request.form["ProductPrice"]
            name = "'" + request.form["ProductName"] + "'"
            description = "'" + request.form["ProductDescription"] + "'"
            image = "'" + request.form["ProductImage"] + "'"

            # Create a cursor
            conn = mysql.connection
            cur = conn.cursor()
            # Get the length of the products table
            cur.execute("SELECT COUNT(*) FROM Products")
            productsLength = cur.fetchall()
            # Execute the statement
            cur.execute("INSERT INTO Products (ProductID, ProductPrice, ProductName, ProductDescription, ProductImage) VALUES (%s, %s, %s, %s, %s)" %((productsLength[0][0]+1), price, name, description, image))
            conn.commit()

            # Flash a successful statement
            flash("Insertion successful", "success")
            # Redirect back to the page
            return redirect("/TableModification")
        except:
            # Flash an error message
            flash("Error, insertion unsuccessful", "danger")
            # Redirect back to the page
            return redirect("/TableModification")
    else:
        return redirect("/")

# Route for adding a Company Type
@server.route("/AddCompanyType", methods=["POST"])
def addCompanyType():
    if session["admin"] == True:
        try:
            # Get the data from the form
            name = "'" + request.form["sizeType"] + "'"
            price = request.form["sizePrice"]

            # Create a cursor
            conn = mysql.connection
            cur = conn.cursor()
            # Get the length of the products table
            cur.execute("SELECT COUNT(*) FROM CompanyTypes")
            companyTypesLength = cur.fetchall()
            # Execute the statement
            cur.execute("INSERT INTO CompanyTypes (SizeID, SizeType, SizePriceAddon) VALUES (%s, %s, %s)" %((companyTypesLength[0][0]+1), name, price))
            conn.commit()

            # Flash a successful statement
            flash("Insertion successful", "success")
            # Redirect back to the page
            return redirect("/TableModification")
        except:
            # Flash an error message
            flash("Error, insertion unsuccessful", "danger")
            # Redirect back to the page
            return redirect("/TableModification")
    else:
        return redirect("/")

# Route for adding a License Type
@server.route("/AddLicense", methods=["POST"])
def addLicense():
    if session["admin"] == True:
        try:
            # Get the data from the form
            type = "'" + request.form["licenseType"] + "'"

            # Create a cursor
            conn = mysql.connection
            cur = conn.cursor()
            # Get the length of the products table
            cur.execute("SELECT COUNT(*) FROM Licenses")
            licensesLength = cur.fetchall()
            # Execute the statement
            cur.execute("INSERT INTO Licenses (LicenseID, LicenseType) VALUES (%s, %s)" %((licensesLength[0][0]+1), type))
            conn.commit()

            # Flash a successful statement
            flash("Insertion successful", "success")
            # Redirect back to the page
            return redirect("/TableModification")
        except:
            # Flash an error message
            flash("Error, insertion unsuccessful", "danger")
            # Redirect back to the page
            return redirect("/TableModification")
    else:
        return redirect("/")

# Route for adding a Country
@server.route("/AddCountry", methods=["POST"])
def addCountry():
    if session["admin"] == True:
        try:
            # Get the data from the form
            name = "'" + request.form["countryName"] + "'"
            vatApplicable = request.form["vatSelect"]

            # Create a cursor
            conn = mysql.connection
            cur = conn.cursor()
            # Get the length of the products table
            cur.execute("SELECT COUNT(*) FROM Countries")
            countriesLength = cur.fetchall()
            # Execute the statement
            cur.execute("INSERT INTO Countries (CountryID, CountryName, VATApplicable) VALUES (%s, %s, %s)" %((countriesLength[0][0]+1), name, vatApplicable))
            conn.commit()

            # Flash a successful statement
            flash("Insertion successful", "success")
            # Redirect back to the page
            return redirect("/TableModification")
        except:
            # Flash an error message
            flash("Error, insertion unsuccessful", "danger")
            # Redirect back to the page
            return redirect("/TableModification")
    else:
        return redirect("/")

# Route for deleting specific data item from the Product table
@server.route("/Delete/Products/<productID>")
def deleteProductData(productID):
    if session["admin"] == True:
        try:
            # Create a cursor
            conn = mysql.connection
            cur = conn.cursor()
            # Delete the specified item
            cur.execute("DELETE FROM Products WHERE ProductID = %s" %productID)
            conn.commit()
            # Flash a successful message
            flash("Deletion successful", "success")
            # Return to the page
            return redirect("/TableModification")
        except:
            # Flash an error message
            flash("Deletion could not be completed", "danger")
            # Redirect to the page
            return redirect("/TableModification")
    else:
        return redirect("/")

# Route for deleting specific data item from the Product table
@server.route("/Delete/CompanyType/<typeID>")
def deleteCompanyType(typeID):
    if session["admin"] == True:
        try:
            # Create a cursor
            conn = mysql.connection
            cur = conn.cursor()
            # Delete the specified item
            cur.execute("DELETE FROM CompanyTypes WHERE SizeID = %s" %typeID)
            conn.commit()
            # Flash a successful message
            flash("Deletion successful", "success")
            # Return to the page
            return redirect("/TableModification")
        except:
            # Flash an error message
            flash("Deletion could not be completed", "danger")
            # Redirect to the page
            return redirect("/TableModification")
    else:
        return redirect("/")

# Route for deleting specific data item from the Product table
@server.route("/Delete/Licenses/<licenseID>")
def deleteLicense(licenseID):
    if session["admin"] == True:
        #try:
            # Create a cursor
            conn = mysql.connection
            cur = conn.cursor()
            # Delete the specified item
            cur.execute("DELETE FROM Licenses WHERE LicenseID = %s" %licenseID)
            conn.commit()
            # Flash a successful message
            flash("Deletion successful", "success")
            # Return to the page
            return redirect("/TableModification")
        #except:
            # Flash an error message
            #flash("Deletion could not be completed", "danger")
            # Redirect to the page
            #return redirect("/TableModification")
    else:
        return redirect("/")

# Route for deleting specific data item from the Product table
@server.route("/Delete/Countries/<countryID>")
def deleteCountry(countryID):
    if session["admin"] == True:
        #try:
            # Create a cursor
            conn = mysql.connection
            cur = conn.cursor()
            # Delete the specified item
            cur.execute("DELETE FROM Countries WHERE CountryID = %s" %countryID)
            conn.commit()
            # Flash a successful message
            flash("Deletion successful", "success")
            # Return to the page
            return redirect("/TableModification")
        #except:
            # Flash an error message
            #flash("Deletion could not be completed", "danger")
            # Redirect to the page
            #return redirect("/TableModification")
    else:
        return redirect("/")

# Route for modifying a table's data
@server.route("/Modify/<tableID>", methods=["POST"])
def modifyData(tableID):
    if session["admin"] == True:
        #try:
            # Get the data from the form
            dataID = request.form["idToModify"]

            # If modifying the licenses table, there is only one field that can be changed
            # So the "field" variable is hardcoded
            if tableID == "Licenses":
                field = "LicenseType"
            # Else the field is whatever they chose
            else:
                field = request.form["itemToModify"]

            # If they are modifying a price, then the query variable does not need to be surrounded
            # in quotation marks
            if "Price" in field:
                data = request.form["dataToAdd"]
            else:
                data = "'" + request.form["dataToAdd"] + "'"

            # If modifying the Countries table
            if tableID == "Countries":
                # If modifying the "VATApplicable" field
                if field == "VATApplicable":
                    # If they entered "Yes"
                    if data == "Yes":
                        # Set the data to "True"
                        data = True
                    # Else set it to "False"
                    else:
                        data = False

            if tableID == "Products":
                idColName = "`ProductID`"
            elif tableID == "CompanyTypes":
                idColName = "`SizeID`"
            elif tableID == "Licenses":
                idColName = "`LicenseID`"
            elif tableID == "Countries":
                idColName = "`CountryID`"

            # Create a cursor
            conn = mysql.connection
            cur = conn.cursor()

            # Insert the change into the "Audit" table - was going to be done with StoredProcedure/Trigger
            # but couldn't get it to work in time, so doing this instead
            print("SELECT %s FROM %s WHERE %s = %s" %(("`"+field+"`"), ("`"+tableID+"`"), idColName, dataID))
            cur.execute("SELECT %s FROM %s WHERE %s = %s" %(("`"+field+"`"), ("`"+tableID+"`"), idColName, dataID))
            oldData = cur.fetchall()
            cur.execute("INSERT INTO Audits (TableAltered, RecordPrimKey, FieldAltered, OldData, NewData) VALUES (%s, %s, %s, %s, %s)" %(("'"+tableID+"'"), dataID, ("'"+field+"'"), oldData[0][0], data))
            conn.commit()

            # Execute the Update
            cur.execute('''UPDATE %s SET %s = %s WHERE %s = %s''' %(("`"+tableID+"`"), ("`"+field+"`"), data, idColName, dataID))
            conn.commit()

            # Flash a success statement
            flash("Update successful", "success")
            # Redirect back to the page
            return redirect("/TableModification")
        #except:
            #flash("Error, Modification Unsuccessful", "danger")
            #return redirect("/TableModification")
    else:
        return redirect("/")


# Routes for adding and removing PromoCodes
@server.route("/PromoCodes")
def promoCodes():
    if session["admin"] == True:
        # Create a cursor
        cur = mysql.new_cursor(dictionary=False)
        # Get all the Promo Codes
        cur.execute("SELECT * FROM PromoCodes")
        adminPromoData = cur.fetchall()
        # Render the template, along with the required data
        return render_template("AdminPromoCodes.html", data = adminPromoData)
    else:
        return render_template("home.html")

@server.route("/PromoCodes/Add", methods = ["POST"])
def addCode():
    # Create a cursor
    conn= mysql.connection
    cur = conn.cursor()

    # Get the data from the form
    code = request.form["code"]
    queryCode = "'" + code + "'"
    type = request.form["type"]
    discount = request.form["discountValue"]
    user = request.form["validUser"]

    # If the type is percentage
    if type == "percentage":
        cur.execute('''INSERT INTO PromoCodes (PromoCode, DiscountPercent, ValidUser) VALUES (%s, %s, %s)''' %(queryCode, discount, user))
        conn.commit()
    # Else-If the type is fixed
    elif type == "fixed":
        cur.execute('''INSERT INTO PromoCodes (PromoCode, SetDiscount, ValidUser) VALUES (%s, %s, %s)''' %(queryCode, discount, user))
        conn.commit()

    # Email the user their code data
    # Get the user's name and email from the database
    cur.execute("SELECT UserEmail, ContactName FROM Users WHERE UserID = %s" %user)
    userData = cur.fetchall()
    # Send the email
    msg = Message('ImageOptim - Promo Code Available', recipients=[])
    msg.add_recipient(userData[0][0])
    msg.body = 'PromoCodeAvailable'
    msg.html = render_template('PromoCodeEmail.html', name=userData[0][1], type=type, code=code, discount=discount)
    mail.send(msg)

    # Flash that the insertion was successful
    flash("Insertion Successful", "success")
    # Redirect back to the page
    return redirect("/PromoCodes")

@server.route("/Delete/PromoCode/<codeID>")
def deleteCode(codeID):
    if session["admin"] == True:
        # Create a cursor
        conn= mysql.connection
        cur = conn.cursor()
        cur.execute("DELETE FROM PromoCodes WHERE PromoID = %s" % codeID)
        conn.commit()
        flash("Deletion successful", "success")
        return redirect("/PromoCodes")
    else:
        return render_template("home.html")


# Server Route for Admin Contact log
@server.route("/ContactLog")
def adminContactLog():
    if session["admin"] == True:
        # Create a cursor
        cur = mysql.new_cursor(dictionary=False)
        # Get the data from the Database
        cur.execute("SELECT * FROM ContactLog")
        contactLogData = cur.fetchall()
        # Render the template
        return render_template("AdminContactLog.html", contactData = contactLogData)
    else:
        return redirect("/")

# Delete Contact Log
@server.route("/Delete/ContactLog/<contactID>")
def deleteContactLog(contactID):
    if session["admin"] == True:
        # Create a cursor
        conn = mysql.connection
        cur = conn.cursor()
        # Delete the selected log
        cur.execute("DELETE FROM ContactLog WHERE ContactID = %s" %contactID)
        conn.commit()
        # Redirect back to the page
        return redirect("/ContactLog")
    else:
        return redirect("/")

@server.route("/Audits")
def auditPage():
    if session["admin"] == True:
        # Create a cursor
        cur = mysql.new_cursor(dictionary=False)
        # Select the data from the "Audits" table
        cur.execute("SELECT * FROM Audits")
        auditData = cur.fetchall()
        # Render the template
        return render_template("/AdminAudits.html", data=auditData)
    else:
        return redirect("/")

@server.route("/Delete/Audit/<auditID>")
def deleteAuditData(auditID):
    if session["admin"] == True:
        # Create a cursor
        conn = mysql.connection
        cur = conn.cursor()
        # Delete the data
        cur.execute("DELETE FROM Audits WHERE AuditID = %s" %auditID)
        conn.commit()
        # Redirect back to the page
        return redirect("/Audits")
    else:
        return redirect("/")


# Error handling for error 500 (internal server error)
@server.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_code=500), 500

# Error handling for error 404 (page not found)
@server.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404), 404


if __name__ == "__main__":
    server.run(debug=True)
