from flask import Flask, render_template, request, redirect, url_for

from services.bmi import calculate_bmi
from services.ai_recommendation import generate_plan
from database.database import save_user

app = Flask(__name__)


# ----------------------------
# Login Page
# ----------------------------
@app.route("/")
def home():
    return render_template("login.html")


# ----------------------------
# Signup Page
# ----------------------------
@app.route("/signup")
def signup():
    return render_template("signup.html")


# ----------------------------
# Profile Page
# ----------------------------
@app.route("/profile")
def profile():
    return render_template("profile.html")


# ----------------------------
# Generate AI Plan
# ----------------------------
@app.route("/recommend", methods=["POST"])
def recommend():

    name = request.form["name"]
    age = int(request.form["age"])
    weight = float(request.form["weight"])
    height = float(request.form["height"])
    goal = request.form["goal"]

    bmi, bmi_category = calculate_bmi(weight, height)

    ai_plan = generate_plan(
        name=name,
        age=age,
        height=height,
        weight=weight,
        bmi=round(bmi, 2),
        goal=goal
    )

    save_user(
        name=name,
        age=age,
        weight=weight,
        height=height,
        bmi=round(bmi, 2),
        bmi_category=bmi_category,
        goal=goal
    )

    return render_template(
        "dashboard.html",
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