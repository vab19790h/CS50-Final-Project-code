import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

import math

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")


@app.route("/")
def index():
    """Show homepage"""

    return render_template("index.html")

@app.route("/about")
def about():

    return render_template("about.html")



@app.route("/forgot", methods=["GET", "POST"])

def forgot():
    inputValue = {}


    if request.method == "POST":

        if not request.form.get("first_name"):
            flash("➛  Must provide First name")
        else:
            first_name = request.form.get("first_name")
            inputValue["first_name"] = first_name

        if not request.form.get("last_name"):
            flash("➛  Must provide Last name")
        else:
            last_name = request.form.get("last_name")
            inputValue["last_name"] = last_name

        if not request.form.get("anime"):
            flash("➛  Must provide Favourite Animation Character")
        else:
            anime = request.form.get("anime")
            inputValue["anime"] = anime

        if not request.form.get("username"):
            flash("➛  Must provide username")

        else:
            username = request.form.get("username")
            inputValue["username"] = username

        if inputValue.keys() >= {"first_name", "last_name", "anime", "username"}:
            find = db.execute("SELECT * FROM users WHERE first_name = :first_name AND last_name = :last_name AND anime = :anime AND username = :username",
                                first_name=first_name, last_name=last_name, anime=anime, username=username)

            if len(find) == 1:
                flash("Found you in my database! Please enter your new password.")
                return render_template("change.html", inputValue=inputValue)


            else:
                flash("➛  Could not find your account in my database.")
                return render_template("forgot.html", inputValue=inputValue)

        else:
            return render_template("forgot.html", inputValue=inputValue)

    else:
        return render_template("forgot.html", inputValue=inputValue)


@app.route("/new_password", methods=["GET", "POST"])
def new_password():
    inputValue = {}

    if request.method == "POST":

        inputValue["first_name"] = request.form.get("first_name")
        inputValue["last_name"] = request.form.get("last_name")
        inputValue["anime"] = request.form.get("anime")
        username = request.form.get("username")
        inputValue["username"] = username

        if not request.form.get("new_password"):
            flash("➛  Must provide new password")
        else:
            password = request.form.get("new_password")
            inputValue["new_password"] = password

            if len(password) < 8 or len(password) > 20:
                flash("➛  The passowrd must be 8 to 20 characters long")
                return render_template("change.html", inputValue=inputValue)

            check = 3

            for number in password:
                if number.isdigit():
                    check -= 1
                    break

            for capital in password:
                if capital.isupper():
                    check -= 1
                    break

            for symbol in password:
                if not symbol.isdigit() and not symbol.isalpha():
                    check -= 1
                    break

            for space in password:
                if space == " ":
                    flash("➛  Spaces are not allowed in the password.")

            if check != 0:
                flash("➛  The Password must contain at least one uppercase letter, a number and a special character.")

            if not request.form.get("confirmation"):
                flash("➛  Must provide password (again)")

            else:
                confirmation = request.form.get("confirmation")
                inputValue["confirmation"] = confirmation

                if password != confirmation:
                    flash("Passwords do not match!")

                else:
                    if inputValue.keys() >= {"username", "confirmation", "new_password"}:
                        db.execute("UPDATE users SET hash = :password WHERE username = :username",
                                    password=generate_password_hash(password), username=username)
                        flash("Your password has been successfully changed!")
                        return render_template("login.html", inputValue=inputValue)

        return render_template("change.html", inputValue=inputValue)

    else:
        return render_template("change.html", inputValue=inputValue)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")



@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    inputValue = {}

    if request.method == "POST":

        if not request.form.get("first_name"):
            flash("➛  Must provide First name")
        else:
            first_name = request.form.get("first_name")
            inputValue["first_name"] = first_name

        if not request.form.get("last_name"):
            flash("➛  Must provide Last name")
        else:
            last_name = request.form.get("last_name")
            inputValue["last_name"] = last_name

        if not request.form.get("anime"):
            flash("➛  Must provide Favourite Animation Character")
        else:
            anime = request.form.get("anime")
            inputValue["anime"] = anime

        if not request.form.get("username"):
            flash("➛  Must provide username")
        else:
            username = request.form.get("username")
            inputValue["username"] = username

            if db.execute("SELECT * FROM users WHERE username = :username", username=username):
                flash(f"➛  The username, {username}  already exists.")

        if not request.form.get("password"):
            flash("➛  Must provide password")
        else:
            password = request.form.get("password")
            inputValue["password"] = password

            if len(password) < 8 or len(password) > 20:
                flash("➛  The passowrd must be 8 to 20 characters long")
                return render_template("register.html", inputValue=inputValue)


            check = 3

            for number in password:
                if number.isdigit():
                    check -= 1
                    break

            for capital in password:
                if capital.isupper():
                    check -= 1
                    break

            for symbol in password:
                if not symbol.isdigit() and not symbol.isalpha():
                    check -= 1
                    break
            for space in password:
                if space == " ":
                    flash("➛  Spaces are not allowed in the password.")
                    return render_template("register.html", inputValue=inputValue)

            if check != 0:
                flash("➛  The Password must contain at least one uppercase letter, a number and a special character.")
                return render_template("register.html", inputValue=inputValue)

            if not request.form.get("confirmation"):
                flash("➛  Must provide password (again)")
            else:
                confirmation = request.form.get("confirmation")
                inputValue["confirmation"] = confirmation

                if password != confirmation:
                    flash("Passwords do not match!")
                    return render_template("register.html", inputValue=inputValue)

        if inputValue.keys() >= {"username", "last_name", "first_name", "anime", "password", "confirmation"}:
            db.execute("INSERT INTO users (username, last_name, first_name, anime, hash) VALUES (:username, :last_name, :first_name, :anime, :password)",
                    username=username, last_name=last_name, first_name=first_name, anime=anime, password=generate_password_hash(password))

            return redirect("/login")

        return render_template("register.html", inputValue=inputValue)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html", inputValue=inputValue)


@app.route("/cg", methods=["GET", "POST"])
@login_required
def cg():
    if request.method == "POST":

        return redirect("/")

    else:
        return render_template("cg.html")

@app.route("/mi", methods=["GET", "POST"])
@login_required
def mi():
    """Sell shares of stock"""
    if request.method == "POST":
        return render_template("mi.html")

    else:
        return render_template("mi.html")


@app.route("/history")
@login_required
def history():

    user_history = db.execute("SELECT * FROM history WHERE id_users = :id_users;", id_users=session["user_id"])

    if not user_history:
        flash("You currently have no history to view.")

    return render_template("history.html", history=user_history)




# to save calculated values
answers = [["none"] * 3] * 5

def default_Ans():
    answers[0] = ["Area", "_____", "unit"]
    answers[1] = ["CG from left-end", "_____", "unit"]
    answers[2] = ["CG from bottom-end", "_____", "unit"]
    answers[3] = ["MI about x-asis (Ix)", "_____", "unit"]
    answers[4] = ["MI about y-asis (Iy)", "_____", "unit"]


def unit_shift(unit_ans):
    answers[0][2] = f"{unit_ans}\N{SUPERSCRIPT TWO}"
    answers[1][2] = unit_ans
    answers[2][2] = unit_ans
    answers[3][2] = f"{unit_ans}\N{SUPERSCRIPT FOUR}"
    answers[4][2] = f"{unit_ans}\N{SUPERSCRIPT FOUR}"


# for unit conversion
conversion_factor = {}

conversion_factor["mm.cm"] = float(1/10)
conversion_factor["mm.m"] = float(1/1000)
conversion_factor["mm.in"] = float(1/25.4)
conversion_factor["mm.ft"] = float(1/304.8)

conversion_factor["cm.mm"] = float(10)
conversion_factor["cm.m"] = float(1/100)
conversion_factor["cm.in"] = float(1/2.54)
conversion_factor["cm.ft"] = float(1/30.48)

conversion_factor["m.mm"] = float(1000)
conversion_factor["m.cm"] = float(100)
conversion_factor["m.in"] = float(1/0.0254)
conversion_factor["m.ft"] = float(1/0.3048)

conversion_factor["in.mm"] = float(25.4)
conversion_factor["in.cm"] = float(2.54)
conversion_factor["in.m"] = float(0.0254)
conversion_factor["in.ft"] = float(1/12)

conversion_factor["ft.mm"] = float(304.8)
conversion_factor["ft.cm"] = float(30.48)
conversion_factor["ft.m"] = float(0.3048)
conversion_factor["ft.in"] = float(12)







def circle_area(r, conversion):
    r = (r * conversion)
    return (math.pi * math.pow(r, 2))

def circle_MI(r, conversion):
    r = (r * conversion)
    return (math.pi/4 * math.pow(r, 4))

def rectangle_area(h, b, conversion):
    h = (h * conversion)
    b = (b * conversion)
    return (b * h)

def rectangle_MIx(h, b, conversion):
    h = (h * conversion)
    b = (b * conversion)
    return (b * math.pow(h, 3)/12)

def rectangle_MIy(h, b, conversion):
    h = (h * conversion)
    b = (b * conversion)
    return (h * math.pow(b, 3)/12)

def triangle_area(h, b, conversion):
    h = (h * conversion)
    b = (b * conversion)
    return (b * h/2)

def triangle_MIx(h, b, conversion):
    h = (h * conversion)
    b = (b * conversion)
    return (b * math.pow(h, 3)/36)


def triangle_CG_dist_left(h, b, inputValue, conversion, angle_opt):
    h = (h * conversion)
    b = (b * conversion)

    if "length_L" in inputValue:
        inputValue["length_L"] *= conversion
        angle_L = math.asin(h/ inputValue["length_L"])

        # if left-corner angle is less then 90 degrees
        if angle_opt == "<90":
            return (b/3 + h/(3 * math.tan(angle_L)))

        # if left-corner angle is more then 90 degrees
        if angle_opt == ">90":
            return (b/3 - h/(3 * math.tan(angle_L)))

    elif "length_R" in inputValue:
        inputValue["length_R"] *= conversion
        angle_R = math.asin(h/ inputValue["length_R"])

        # if right-corner angle is less then 90 degrees
        if angle_opt == "<90":
            return (2 * b/3 - h/(3 * math.tan(angle_R)))

        # if right-corner angle is more then 90 degrees
        if angle_opt == ">90":
            return (2 * b/3 + h/(3 * math.tan(angle_R)))

    elif "angle_L" in inputValue:
        angle_L = inputValue["angle_L"]
        angle_L = angle_L * math.pi/180
        return (b/3 + h/(3 * math.tan(angle_L)))

    elif "angle_R" in inputValue:
        angle_R = inputValue["angle_R"]
        angle_R = angle_R * math.pi/180
        return (2 * b/3 - h/(3 * math.tan(angle_R)))


def semicircle_CG_bottom(r, conversion):
    r = (r * conversion)
    return ((r * 4)/(3 * math.pi))

def semicircle_MIx(r, conversion):
    r = (r * conversion)
    return ((math.pi/ 8) - 8/(9 * math.pi)) * pow(r, 4)

def semicircle_MIy(r, conversion):
    r = (r * conversion)
    return ((1/ 8) * (math.pi * pow(r, 4)))


def semiperabola_area(a, b, conversion):
        a = (a * conversion)
        b = (b * conversion)
        return ((2/ 3) * (b * a))

def ellipse_MIx(a, b, conversion):
    a *= conversion
    b *= conversion
    return (math.pi * a * math.pow(b, 3))

def ellipse_MIy(a, b, conversion):
    a = a * conversion
    b = b * conversion
    return (math.pi * b * math.pow(a, 3)/4)

def i_beam_Area(d, bf, tf, tw, conversion):
    d *= conversion
    bf *= conversion
    tf *= conversion
    tw *= conversion
    return ((d * bf) - ((bf - tw) * (d - (2 * tf))))

def i_beam_MIy(d, bf, tf, tw, conversion):
    d *= conversion
    bf *= conversion
    tf *= conversion
    tw *= conversion

    mi_flange = tf * pow(bf, 3)/12
    mi_web = ((d - (2 * tf)) * pow(tw, 3))/12

    return (mi_web + 2 * mi_flange)

def i_beam_MIx(d, bf, tf, tw, conversion):
    d *= conversion
    bf *= conversion
    tf *= conversion
    tw *= conversion

    mi_outer = (bf * pow(d, 3))/12
    mi_inner = ((bf-tw) * pow((d - (2 * tf)), 3))/12

    return (mi_outer - mi_inner)


def trapezoid_Area(height, a, b, conversion):
    height *= conversion
    a *= conversion
    b *= conversion

    return (height * (a + b)/ 2)

def trapezoid_CG_dist_left(height, a, b, inputValue, conversion):
    height *= conversion
    a *= conversion
    b *= conversion

    left_angle = inputValue["left_angle"] * math.pi/180
    right_angle = inputValue["right_angle"] * math.pi/180

    left_length = abs(height/ math.tan(left_angle))
    right_length = abs(height/ math.tan(right_angle))

    # all section's area and dist of their CG from the left most end
    left_tri_A = height * left_length/ 2
    left_tri_CG_from_L = 2 * left_length/ 3
    right_tri_A = height * right_length/ 2


    if inputValue["left_angle"] > 90 and inputValue["right_angle"] < 90:
        middle_rect_A = height * (a - left_length)
        middle_rect_CG_from_L = left_length + (a - left_length)/ 2
        right_tri_CG_from_L = a + right_length/ 3

    elif inputValue["left_angle"] < 90 and inputValue["right_angle"] > 90:
        middle_rect_A = height * (a - right_length)
        middle_rect_CG_from_L = left_length + (a - right_angle)/ 2
        right_tri_CG_from_L = b + right_length/ 3

    elif inputValue["left_angle"] > 90 and inputValue["right_angle"] > 90:
        middle_rect_A = height * (b)
        middle_rect_CG_from_L = left_length + b/ 2
        right_tri_CG_from_L = left_length + b + right_length/ 3

    else:
        middle_rect_A = height * a
        middle_rect_CG_from_L = left_length + a/ 2
        right_tri_CG_from_L = left_length + a + right_length/ 3

    total_area = left_tri_A + middle_rect_A + right_tri_A

    return ((left_tri_CG_from_L * left_tri_A) + (middle_rect_CG_from_L * middle_rect_A) + (right_tri_CG_from_L * right_tri_A))/total_area

def trapezoid_CG_dist_bottom(height, a, b, inputValue, conversion):
    height *= conversion
    a *= conversion
    b *= conversion

    if inputValue.keys() >= {'left_angle', 'right_angle'}:
        left_angle = inputValue["left_angle"] * math.pi/180
        right_angle = inputValue["right_angle"] * math.pi/180

        left_length = abs(height/ math.tan(left_angle))
        right_length = abs(height/ math.tan(right_angle))

        # all section's area and dist of their CG from the bottom
        left_tri_A = height * left_length/ 2
        middle_rect_CG_from_B = height/ 2
        right_tri_A = height * right_length/ 2

        if inputValue["left_angle"] > 90 and inputValue["right_angle"] < 90:
            left_tri_CG_from_B = 2 * height/ 3
            middle_rect_A = height * (a - left_length)
            right_tri_CG_from_B = height/ 3

        elif inputValue["left_angle"] < 90 and inputValue["right_angle"] > 90:
            left_tri_CG_from_B = height/ 3
            middle_rect_A = height * (a - right_length)
            right_tri_CG_from_B = 2 * height/ 3

        elif inputValue["left_angle"] > 90 and inputValue["right_angle"] > 90:
            return height - ((height/ 3) * (2 * a + b)/ (a + b))

        else:
            return ((height/ 3) * (2 * a + b)/ (a + b))

        total_area = left_tri_A + middle_rect_A + right_tri_A

        return ((left_tri_CG_from_B * left_tri_A) + (middle_rect_CG_from_B * middle_rect_A) + (right_tri_CG_from_B * right_tri_A))/total_area

    else:
        return ((height/ 3) * (2 * a + b)/ (a + b))


@app.route("/circle", methods=["GET", "POST"])
def circle():
    session["do"] = "true"
    inputValue = {}
    inputValue["radius"] = 'radius (r)'
    default_Ans()

    if request.method == "POST":

        # to round answers
        round_to = 10
        if request.form.get("round"):
            inputValue["round"] = int(request.form.get("round"))
            round_to = inputValue["round"]

        # checking for unit input
        if not request.form.get("unit_input"):
            flash("➛  Please select the inputs' unit.")
        else:
            unit_input = request.form.get("unit_input")
            inputValue[f"{unit_input}_input"] = 'selected'

            # to convert the values as per selected units for answers
            conversion = 1
            if request.form.get("unit_ans") and unit_input != request.form.get("unit_ans"):
                unit_ans = request.form.get("unit_ans")
                conversion = conversion_factor[f"{unit_input}.{unit_ans}"]
                inputValue[f"{unit_ans}_ans"] = 'selected'
            else:
                unit_ans = unit_input

        # checking for radius input
        if not request.form.get("radius"):
                flash("➛  Please enter the radius (r). ")
                default_Ans()
        else:
            inputValue["radius"] = float(request.form.get("radius"))

        if request.form.get("unit_input") and request.form.get("radius"):
            unit_shift(unit_ans)
            answers[0][1] = round(circle_area(inputValue["radius"], conversion), round_to)
            answers[1][1] = round((inputValue["radius"] * conversion), round_to)
            answers[2][1] = round((inputValue["radius"] * conversion), round_to)
            answers[3][1] = round(circle_MI(inputValue["radius"], conversion), round_to)
            answers[4][1] = round(circle_MI(inputValue["radius"], conversion), round_to)
            if "user_id" in session:
                # pulling current time and date
                time = db.execute("SELECT CURRENT_TIMESTAMP;")
                db.execute("INSERT INTO history (id_users, shape, input_unit, r, h_OR_d, b_OR_bf, a, tf, tw, third_dim_type, third_dim_value, ans_unit, Area, CGL, CGB, MIx, MIy, angle_opt, time) VALUES (:id_users, :shape, :input_unit, :r, :hd, :bbf, :a, :tf, :tw, :third_dim_type, :third_dim_value, :ans_unit, :area, :cgl, :cgb, :mix, :miy, :angle_opt, :time)",
                            id_users=session["user_id"], shape="Circle", input_unit=unit_input, r=inputValue["radius"], hd="NA", bbf="NA", a="NA", tf="NA", tw="NA", third_dim_type="NA", third_dim_value="NA", ans_unit=unit_ans, area=answers[0][1], cgl=answers[1][1], cgb=answers[2][1], mix=answers[3][1], miy=answers[4][1], angle_opt="NA", time=time[0]['CURRENT_TIMESTAMP'])

        return render_template("circle.html", answers=answers, inputValue=inputValue)

    else:
        return render_template("circle.html", answers=answers, inputValue=inputValue)



@app.route("/rectangle", methods=["GET", "POST"])
def rectangle():
    inputValue = {}
    inputValue["height"] = 'height (h)'
    inputValue["width"] = 'width (b)'
    default_Ans()

    if request.method == "POST":

        # to round answers
        round_to = 10
        if request.form.get("round"):
            inputValue["round"] = int(request.form.get("round"))
            round_to = inputValue["round"]

        # checking for unit input
        if not request.form.get("unit_input"):
            flash("➛  Please select the inputs' unit.")
        else:
            unit_input = request.form.get("unit_input")
            inputValue[f"{unit_input}_input"] = 'selected'


            # to convert the values as per selected units for answers
            conversion = 1
            if request.form.get("unit_ans") and unit_input != request.form.get("unit_ans"):
                unit_ans = request.form.get("unit_ans")
                conversion = conversion_factor[f"{unit_input}.{unit_ans}"]
                inputValue[f"{unit_ans}_ans"] = 'selected'
            else:
                unit_ans = unit_input

        # checking for height input
        if not request.form.get("height"):
                flash("➛  Please enter the height (h). ")
                default_Ans()
        else:
            height = float(request.form.get("height"))
            inputValue["height"] = height

        # checking for width input
        if not request.form.get("width"):
                flash("➛  Please enter the width (b). ")
                default_Ans()
        else:
            width = float(request.form.get("width"))
            inputValue["width"] = width


        if request.form.get("unit_input") and request.form.get("height") and request.form.get("width"):
            unit_shift(unit_ans)
            answers[0][1] = round(rectangle_area(height, width, conversion), round_to)
            answers[1][1] = round((width * conversion/2), round_to)
            answers[2][1] = round((height * conversion/2), round_to)
            answers[3][1] = round(rectangle_MIx(height, width, conversion), round_to)
            answers[4][1] = round(rectangle_MIy(height, width, conversion), round_to)
            if "user_id" in session:
                # pulling current time and date
                time = db.execute("SELECT CURRENT_TIMESTAMP;")
                db.execute("INSERT INTO history (id_users, shape, input_unit, r, h_OR_d, b_OR_bf, a, tf, tw, third_dim_type, third_dim_value, ans_unit, Area, CGL, CGB, MIx, MIy, angle_opt, time) VALUES (:id_users, :shape, :input_unit, :r, :hd, :bbf, :a, :tf, :tw, :third_dim_type, :third_dim_value, :ans_unit, :area, :cgl, :cgb, :mix, :miy, :angle_opt, :time)",
                            id_users=session["user_id"], shape="Rectangle", input_unit=unit_input, r="NA", hd=height, bbf=width, a="NA", tf="NA", tw="NA", third_dim_type="NA", third_dim_value="NA", ans_unit=unit_ans, area=answers[0][1], cgl=answers[1][1], cgb=answers[2][1], mix=answers[3][1], miy=answers[4][1], angle_opt="NA", time=time[0]['CURRENT_TIMESTAMP'])

        return render_template("rectangle.html", answers=answers, inputValue=inputValue)

    else:
        return render_template("rectangle.html", answers=answers, inputValue=inputValue)


@app.route("/triangle", methods=["GET", "POST"])
def triangle():
    default_Ans()
    inputValue = {}
    inputValue["height"] = 'height (h)'
    inputValue["width"] = 'width (b)'
    inputValue["disabled"] = 'disabled'
    inputValue["min"] = "0"
    answers[4][0] = "none"
    answers[1][1] = "Must provide third Dimention"
    answers[1][2] = " "

    if request.method == "POST":

        # to round answers
        round_to = 10
        if request.form.get("round"):
            inputValue["round"] = int(request.form.get("round"))
            round_to = inputValue["round"]

        # checking for unit input
        if not request.form.get("unit_input"):
            flash("➛ Please select the inputs' unit.")
        else:
            unit_input = request.form.get("unit_input")
            inputValue[f"{unit_input}_input"] = 'selected'


            # to convert the values as per selected units for answers
            conversion = 1
            if request.form.get("unit_ans") and unit_input != request.form.get("unit_ans"):
                unit_ans = request.form.get("unit_ans")
                conversion = float(conversion_factor[f"{unit_input}.{unit_ans}"])
                inputValue[f"{unit_ans}_ans"] = 'selected'
            else:
                unit_ans = unit_input

        # checking for height input
        if not request.form.get("height"):
                flash("➛ Please enter the height (h).")
                default_Ans()
        else:
            height = float(request.form.get("height"))
            inputValue["height"] = height

        # checking for width input
        if not request.form.get("width"):
                flash("➛ Please enter the width (b). ")
                default_Ans()
        else:
            width = float(request.form.get("width"))
            inputValue["width"] = width

        # checking if third dimention is provided
        if request.form.get("value3_Type")  != "none":
            inputValue["disabled"] = ''
            value3_Type = request.form.get("value3_Type")
            # to keep it selected after submit
            inputValue[f"{value3_Type}_S"] = 'selected'

            if not request.form.get("value3"):
                flash(f"Since third dimention type is selected, Value of that dimention must be entered.")

            else:
                # to pass it on to the function that calculate CG distance
                inputValue[value3_Type] = float(request.form.get("value3"))

                # to pass it back to html to remember the recent input
                inputValue["value3"] = float(request.form.get("value3"))
                inputValue["disabled"] = " "

                if value3_Type == "length_L" or value3_Type == "length_R":

                    if height == inputValue["value3"]:
                        angle_opt = "none"
                        answers[1][1] = round((height * conversion/3), round_to)


                    elif not request.form.get("angle_opt"):
                        flash(f"Aproximate angle of the same side is required If one of the side length is provided")

                    else:
                        angle_opt = request.form.get("angle_opt")
                        answers[1][1] = round(triangle_CG_dist_left(height, width, inputValue, conversion, angle_opt), round_to)
                        inputValue[angle_opt] = "selected"


                else:
                    angle_opt = "none"
                    answers[1][1] = round(triangle_CG_dist_left(height, width, inputValue, conversion, angle_opt), round_to)

        else:
            answers[1][1] = "Must provide third Dimention"
            value3_Type = "NA"
            inputValue["value3"] = "NA"
            angle_opt = "NA"


        if request.form.get("unit_input") and request.form.get("height") and request.form.get("width"):
            unit_shift(unit_ans)

            if not isinstance(answers[1][1], float):
                answers[1][2] = " "

            answers[0][1] = round(triangle_area(height, width, conversion), round_to)
            cgl = answers[1][1]
            answers[2][1] = round((height * conversion/3), round_to)
            answers[3][1] = round(triangle_MIx(height, width, conversion), round_to)
            answers[4][0] = "none"

            if "user_id" in session:
                # pulling current time and date
                time = db.execute("SELECT CURRENT_TIMESTAMP;")
                db.execute("INSERT INTO history (id_users, shape, input_unit, r, h_OR_d, b_OR_bf, a, tf, tw, third_dim_type, third_dim_value, ans_unit, Area, CGL, CGB, MIx, MIy, angle_opt, time) VALUES (:id_users, :shape, :input_unit, :r, :hd, :bbf, :a, :tf, :tw, :third_dim_type, :third_dim_value, :ans_unit, :area, :cgl, :cgb, :mix, :miy, :angle_opt, :time)",
                            id_users=session["user_id"], shape="Triangle", input_unit=unit_input, r="NA", hd=height, bbf=width, a="NA", tf="NA", tw="NA", third_dim_type=value3_Type, third_dim_value=inputValue["value3"], ans_unit=unit_ans, area=answers[0][1], cgl=cgl, cgb=answers[2][1], mix=answers[3][1], miy="NA", angle_opt=angle_opt, time=time[0]['CURRENT_TIMESTAMP'])

        return render_template("triangle.html", answers=answers, inputValue=inputValue)

    else:
        return render_template("triangle.html", answers=answers, inputValue=inputValue)


@app.route("/trapezoid", methods=["GET", "POST"])
def trapezoid():

    inputValue = {}
    inputValue["display"] = "hidden"
    default_Ans()
    answers[1][0] = "none"
    answers[3][0] = "none"
    answers[4][0] = "none"

    if request.method == "POST":

        # to round answers
        round_to = 10
        if request.form.get("round"):
            inputValue["round"] = int(request.form.get("round"))
            round_to = inputValue["round"]

        # checking for unit input
        if not request.form.get("unit_input"):
            flash("➛  Please select the inputs' unit.")
        else:
            unit_input = request.form.get("unit_input")
            inputValue[f"{unit_input}_input"] = 'selected'

            # to convert the values as per selected units for answers
            conversion = 1

            if request.form.get("unit_ans") and unit_input != request.form.get("unit_ans"):
                unit_ans = request.form.get("unit_ans")
                conversion = conversion_factor[f"{unit_input}.{unit_ans}"]
                inputValue[f"{unit_ans}_ans"] = 'selected'
            else:
                unit_ans = unit_input

        # checking for height input
        if not request.form.get("height"):
            flash("➛  Please enter the value of height (h).")
            default_Ans()

        else:
            height = float(request.form.get("height"))
            inputValue["height"] = height

        # checking for width a input
        if not request.form.get("a"):
            flash("➛  Please enter the value of top width (a).")
            default_Ans()

        else:
            a = float(request.form.get("a"))
            inputValue["a"] = a

        # checking for width b input
        if not request.form.get("b"):
            flash("➛  Please enter the value of bottom width (b).")
            default_Ans()

        else:
            b = float(request.form.get("b"))
            inputValue["b"] = b

        if inputValue.keys() >= {'height', 'a', 'b'}:
            unit_shift(unit_ans)
            answers[0][1] = round(trapezoid_Area(height, a, b, conversion), round_to)
            answers[2][1] = round(trapezoid_CG_dist_bottom(height, a, b, inputValue, conversion), round_to)

            if "user_id" in session:
                # pulling current time and date
                time = db.execute("SELECT CURRENT_TIMESTAMP;")
                db.execute("INSERT INTO history (id_users, shape, input_unit, r, h_OR_d, b_OR_bf, a, tf, tw, third_dim_type, third_dim_value, ans_unit, Area, CGL, CGB, MIx, MIy, angle_opt, time) VALUES (:id_users, :shape, :input_unit, :r, :hd, :bbf, :a, :tf, :tw, :third_dim_type, :third_dim_value, :ans_unit, :area, :cgl, :cgb, :mix, :miy, :angle_opt, :time)",
                            id_users=session["user_id"], shape="Trapezoid", input_unit=unit_input, r="NA", hd=height, bbf=b, a=a, tf="NA", tw="NA", third_dim_type="NA", third_dim_value="NA", ans_unit=unit_ans, area=answers[0][1], cgl="NA", cgb=answers[2][1], mix="NA", miy="NA", angle_opt="NA", time=time[0]['CURRENT_TIMESTAMP'])

        return render_template("trapezoid.html", answers=answers, inputValue=inputValue)

    else:

        return render_template("trapezoid.html", answers=answers, inputValue=inputValue)



@app.route("/semicircle", methods=["GET", "POST"])
def semicircle():
    inputValue = {}
    inputValue["radius"] = 'radius (r)'
    default_Ans()

    if request.method == "POST":

        # to round answers
        round_to = 10
        if request.form.get("round"):
            inputValue["round"] = int(request.form.get("round"))
            round_to = inputValue["round"]

        # checking for unit input
        if not request.form.get("unit_input"):
            flash("➛  Please select the inputs' unit.")
        else:
            unit_input = request.form.get("unit_input")
            inputValue[f"{unit_input}_input"] = 'selected'

            # to convert the values as per selected units for answers
            conversion = 1
            if request.form.get("unit_ans") and unit_input != request.form.get("unit_ans"):
                unit_ans = request.form.get("unit_ans")
                conversion = conversion_factor[f"{unit_input}.{unit_ans}"]
                inputValue[f"{unit_ans}_ans"] = 'selected'
            else:
                unit_ans = unit_input

        # checking for radius input
        if not request.form.get("radius"):
                flash("➛  Please enter the radius (r). ")
                default_Ans()
        else:
            inputValue["radius"] = float(request.form.get("radius"))

        if request.form.get("unit_input") and request.form.get("radius"):
            unit_shift(unit_ans)
            answers[0][1] = round(circle_area(inputValue["radius"], conversion) /2, round_to)
            answers[1][1] = round((inputValue["radius"] * conversion), round_to)
            answers[2][1] = round(semicircle_CG_bottom(inputValue["radius"], conversion), round_to)
            answers[3][1] = round(semicircle_MIx(inputValue["radius"], conversion), round_to)
            answers[4][1] = round(semicircle_MIy(inputValue["radius"], conversion), round_to)
            if "user_id" in session:
                # pulling current time and date
                time = db.execute("SELECT CURRENT_TIMESTAMP;")
                db.execute("INSERT INTO history (id_users, shape, input_unit, r, h_OR_d, b_OR_bf, a, tf, tw, third_dim_type, third_dim_value, ans_unit, Area, CGL, CGB, MIx, MIy, angle_opt, time) VALUES (:id_users, :shape, :input_unit, :r, :hd, :bbf, :a, :tf, :tw, :third_dim_type, :third_dim_value, :ans_unit, :area, :cgl, :cgb, :mix, :miy, :angle_opt, :time)",
                            id_users=session["user_id"], shape="Semicircle", input_unit=unit_input, r=inputValue["radius"], hd="NA", bbf="NA", a="NA", tf="NA", tw="NA", third_dim_type="NA", third_dim_value="NA", ans_unit=unit_ans, area=answers[0][1], cgl=answers[1][1], cgb=answers[2][1], mix=answers[3][1], miy=answers[4][1], angle_opt="NA", time=time[0]['CURRENT_TIMESTAMP'])

        return render_template("semicircle.html", answers=answers, inputValue=inputValue)

    else:
        return render_template("semicircle.html", answers=answers, inputValue=inputValue)

@app.route("/semiparabola", methods=["GET", "POST"])
def semiparabola():
    inputValue = {}
    inputValue["b"] = 'vertical (b)'
    inputValue["a"] = 'horizontal (a)'
    default_Ans()
    answers[3][0] = "none"
    answers[4][0] = "none"

    if request.method == "POST":

        # to round answers
        round_to = 10
        if request.form.get("round"):
            inputValue["round"] = int(request.form.get("round"))
            round_to = inputValue["round"]

        # checking for unit input
        if not request.form.get("unit_input"):
            flash("➛  Please select the inputs' unit.")
        else:
            unit_input = request.form.get("unit_input")
            inputValue[f"{unit_input}_input"] = 'selected'


            # to convert the values as per selected units for answers
            conversion = 1
            if request.form.get("unit_ans") and unit_input != request.form.get("unit_ans"):
                unit_ans = request.form.get("unit_ans")
                conversion = conversion_factor[f"{unit_input}.{unit_ans}"]
                inputValue[f"{unit_ans}_ans"] = 'selected'
            else:
                unit_ans = unit_input

        # checking for height input
        if not request.form.get("b"):
                flash("➛  Please enter the value of vertical (b). ")
                default_Ans()
        else:
            b = float(request.form.get("b"))
            inputValue["b"] = b

        # checking for width input
        if not request.form.get("a"):
                flash("➛  Please enter the value of horizontal (a). ")
                default_Ans()
        else:
            a = float(request.form.get("a"))
            inputValue["a"] = a


        if request.form.get("unit_input") and request.form.get("b") and request.form.get("a"):
            unit_shift(unit_ans)
            answers[0][1] = round(semiperabola_area(b, a, conversion), round_to)
            answers[1][1] = round((a * 2 * conversion/5), round_to)
            answers[2][1] = round((b * 3 * conversion/8), round_to)
            if "user_id" in session:
                # pulling current time and date
                time = db.execute("SELECT CURRENT_TIMESTAMP;")
                db.execute("INSERT INTO history (id_users, shape, input_unit, r, h_OR_d, b_OR_bf, a, tf, tw, third_dim_type, third_dim_value, ans_unit, Area, CGL, CGB, MIx, MIy, angle_opt, time) VALUES (:id_users, :shape, :input_unit, :r, :hd, :bbf, :a, :tf, :tw, :third_dim_type, :third_dim_value, :ans_unit, :area, :cgl, :cgb, :mix, :miy, :angle_opt, :time)",
                            id_users=session["user_id"], shape="Semiparabola", input_unit=unit_input, r="NA", hd="NA", bbf=b, a=a, tf="NA", tw="NA", third_dim_type="NA", third_dim_value="NA", ans_unit=unit_ans, area=answers[0][1], cgl=answers[1][1], cgb=answers[2][1], mix="NA", miy="NA", angle_opt="NA", time=time[0]['CURRENT_TIMESTAMP'])

        return render_template("semiparabola.html", answers=answers, inputValue=inputValue)

    else:
        return render_template("semiparabola.html", answers=answers, inputValue=inputValue)

@app.route("/ellipse", methods=["GET", "POST"])
def ellipse():
    inputValue = {}
    inputValue["b"] = 'vertical (b)'
    inputValue["a"] = 'horizontal (a)'
    default_Ans()


    if request.method == "POST":

        # to round answers
        round_to = 10
        if request.form.get("round"):
            inputValue["round"] = int(request.form.get("round"))
            round_to = inputValue["round"]

        # checking for unit input
        if not request.form.get("unit_input"):
            flash("➛  Please select the inputs' unit.")
        else:
            unit_input = request.form.get("unit_input")
            inputValue[f"{unit_input}_input"] = 'selected'


            # to convert the values as per selected units for answers
            conversion = 1
            if request.form.get("unit_ans") and unit_input != request.form.get("unit_ans"):
                unit_ans = request.form.get("unit_ans")
                conversion = conversion_factor[f"{unit_input}.{unit_ans}"]
                inputValue[f"{unit_ans}_ans"] = 'selected'
            else:
                unit_ans = unit_input

        # checking for height input
        if not request.form.get("b"):
            flash("➛  Please enter the value of vertical (b).")
            default_Ans()

        else:
            b = float(request.form.get("b"))
            inputValue["b"] = b

        # checking for width input
        if not request.form.get("a"):
                flash("➛  Please enter the value of horizontal (a).")
                default_Ans()
        else:
            a = float(request.form.get("a"))
            inputValue["a"] = a


        if request.form.get("unit_input") and request.form.get("b") and request.form.get("a"):
            unit_shift(unit_ans)
            answers[0][1] = round((math.pi * b * a * conversion), round_to)
            answers[1][1] = round(a  * conversion, round_to)
            answers[2][1] = round(b * conversion, round_to)
            answers[3][1] = round(ellipse_MIx(a, b, conversion), round_to)
            answers[4][1] = round(ellipse_MIy(a, b, conversion), round_to)
            if "user_id" in session:
                # pulling current time and date
                time = db.execute("SELECT CURRENT_TIMESTAMP;")
                db.execute("INSERT INTO history (id_users, shape, input_unit, r, h_OR_d, b_OR_bf, a, tf, tw, third_dim_type, third_dim_value, ans_unit, Area, CGL, CGB, MIx, MIy, angle_opt, time) VALUES (:id_users, :shape, :input_unit, :r, :hd, :bbf, :a, :tf, :tw, :third_dim_type, :third_dim_value, :ans_unit, :area, :cgl, :cgb, :mix, :miy, :angle_opt, :time)",
                            id_users=session["user_id"], shape="Ellipse", input_unit=unit_input, r="NA", hd="NA", bbf=b, a=a, tf="NA", tw="NA", third_dim_type="NA", third_dim_value="NA", ans_unit=unit_ans, area=answers[0][1], cgl=answers[1][1], cgb=answers[2][1], mix=answers[3][1], miy=answers[4][1], angle_opt="NA", time=time[0]['CURRENT_TIMESTAMP'])

        return render_template("ellipse.html", answers=answers, inputValue=inputValue)

    else:
        return render_template("ellipse.html", answers=answers, inputValue=inputValue)



@app.route("/i_beam", methods=["GET", "POST"])
def i_beam():
    inputValue = {}
    default_Ans()


    if request.method == "POST":

        # to round answers
        round_to = 10
        if request.form.get("round"):
            inputValue["round"] = int(request.form.get("round"))
            round_to = inputValue["round"]

        # checking for unit input
        if not request.form.get("unit_input"):
            flash("➛  Please select the inputs' unit.")
        else:
            unit_input = request.form.get("unit_input")
            inputValue[f"{unit_input}_input"] = 'selected'


            # to convert the values as per selected units for answers
            conversion = 1
            if request.form.get("unit_ans") and unit_input != request.form.get("unit_ans"):
                unit_ans = request.form.get("unit_ans")
                conversion = conversion_factor[f"{unit_input}.{unit_ans}"]
                inputValue[f"{unit_ans}_ans"] = 'selected'
            else:
                unit_ans = unit_input

        # checking for height input
        if not request.form.get("d"):
            flash("➛  Please enter the value of vertical (d).")
            default_Ans()

        else:
            d = float(request.form.get("d"))
            inputValue["d"] = d

        # checking for width input
        if not request.form.get("bf"):
                flash("➛  Please enter the value of flange width (bf).")
                default_Ans()
        else:
            bf = float(request.form.get("bf"))
            inputValue["bf"] = bf

        # checking for flange thickness input
        if not request.form.get("tf"):
                flash("➛  Please enter the value of flange thickness (tf).")
                default_Ans()
        else:
            tf = float(request.form.get("tf"))
            inputValue["tf"] = tf

        # checking for web thickness input
        if not request.form.get("tw"):
                flash("➛  Please enter the value of web thickness (tw).")
                default_Ans()
        else:
            tw = float(request.form.get("tw"))
            inputValue["tw"] = tw

        if inputValue.keys() >= {'d', 'bf', 'tf', 'tw'}:
            unit_shift(unit_ans)
            answers[0][1] = round(i_beam_Area(d, bf, tf, tw, conversion), round_to)
            answers[1][1] = round(bf * conversion/2, round_to)
            answers[2][1] = round(d * conversion/2, round_to)
            answers[3][1] = round(i_beam_MIx(d, bf, tf, tw, conversion), round_to)
            answers[4][1] = round(i_beam_MIy(d, bf, tf, tw, conversion), round_to)
            if "user_id" in session:
                # pulling current time and date
                time = db.execute("SELECT CURRENT_TIMESTAMP;")
                db.execute("INSERT INTO history (id_users, shape, input_unit, r, h_OR_d, b_OR_bf, a, tf, tw, third_dim_type, third_dim_value, ans_unit, Area, CGL, CGB, MIx, MIy, angle_opt, time) VALUES (:id_users, :shape, :input_unit, :r, :hd, :bbf, :a, :tf, :tw, :third_dim_type, :third_dim_value, :ans_unit, :area, :cgl, :cgb, :mix, :miy, :angle_opt, :time)",
                            id_users=session["user_id"], shape="I-Beam", input_unit=unit_input, r="NA", hd=d, bbf=bf, a="NA", tf=tf, tw=tw, third_dim_type="NA", third_dim_value="NA", ans_unit=unit_ans, area=answers[0][1], cgl=answers[1][1], cgb=answers[2][1], mix=answers[3][1], miy=answers[4][1], angle_opt="NA", time=time[0]['CURRENT_TIMESTAMP'])

        return render_template("i_beam.html", answers=answers, inputValue=inputValue)

    else:
        return render_template("i_beam.html", answers=answers, inputValue=inputValue)



def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
