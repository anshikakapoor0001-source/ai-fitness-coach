from flask import Flask, render_template, request, redirect, url_for

from services.bmi import calculate_bmi
from services.ai_recommendation import generate_plan
from database.database import save_user
from services.auth import sign_up, sign_in
from database.database import get_user_by_email
app = Flask(__name__)
@app.route("/")
def home():
    return render_template("login.html")

# ----------------------------
# Login Page
# ----------------------------
@app.route("/login", methods=["POST"])
def login():

    email = request.form["email"]
    password = request.form["password"]

    result = sign_in(email, password)

    if not result.user:
        return "Invalid email or password!"

    user = get_user_by_email(email)

    if user:
        return render_template(
            "dashboard.html",
            name=user["name"],
            age=user["age"],
            weight=user["weight"],
            height=user["height"],
            goal=user["goal"],
            bmi=user["bmi"],
            bmi_category=user["bmi_category"],
            ai_plan=generate_plan(
                name=user["name"],
                age=user["age"],
                height=user["height"],
                weight=user["weight"],
                bmi=user["bmi"],
                goal=user["goal"]
            )
        )

    return redirect(url_for("profile", email=email))
# ----------------------------
# Signup Page
# ----------------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        result = sign_up(email, password)

        if result.user:
            return redirect(url_for("profile"))

        return "Signup Failed"

    return render_template("signup.html")


# ----------------------------
# Profile Page
# ----------------------------
@app.route("/profile")
def profile():

    email = request.args.get("email")

    return render_template(
        "profile.html",
        email=email
    )
# ----------------------------
# Generate AI Plan
# ----------------------------
@app.route("/recommend", methods=["POST"])
def recommend():

    # Get data from profile form
    email = request.form["email"]
    name = request.form["name"]
    age = int(request.form["age"])
    weight = float(request.form["weight"])
    height = float(request.form["height"])
    goal = request.form["goal"]

    # Calculate BMI
    bmi, bmi_category = calculate_bmi(weight, height)

    # Generate AI fitness plan
    ai_plan = generate_plan(
        name=name,
        age=age,
        height=height,
        weight=weight,
        bmi=round(bmi, 2),
        goal=goal
    )

    # Save user profile to Supabase
    save_user(
        email=email,
        name=name,
        age=age,
        weight=weight,
        height=height,
        bmi=round(bmi, 2),
        bmi_category=bmi_category,
        goal=goal
    )

    # Open dashboard
    return render_template(
        "dashboard.html",
        email=email,
        name=name,
        age=age,
        weight=weight,
        height=height,
        goal=goal,
        bmi=round(bmi, 2),
        bmi_category=bmi_category,
        ai_plan=ai_plan
    )


if __name__ == "__main__":
    app.run(debug=True)