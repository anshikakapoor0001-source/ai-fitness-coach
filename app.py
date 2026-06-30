from flask import Flask, render_template, request

from services.bmi import calculate_bmi
from services.ai_recommendation import generate_plan
from database.database import save_user, get_all_users

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("login.html")


@app.route("/recommend", methods=["POST"])
def recommend():

    name = request.form["name"]
    age = request.form["age"]
    weight = float(request.form["weight"])
    height = float(request.form["height"])
    goal = request.form["goal"]

    # Calculate BMI
    bmi, bmi_category = calculate_bmi(weight, height)

    # Generate AI recommendation
    ai_plan = generate_plan(
        name=name,
        age=age,
        height=height,
        weight=weight,
        bmi=round(bmi, 2),
        goal=goal
    )

    # Save user data to Supabase
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

@app.route("/dashboard")
def dashboard():

    users = get_all_users()

    total_users = len(users)

    avg_bmi = 0

    if total_users > 0:
        avg_bmi = round(
            sum(user["bmi"] for user in users) / total_users,
            2
        )

    healthy = len(
        [
            user
            for user in users
            if user["bmi_category"] == "Healthy"
        ]
    )

    return render_template(
        "dashboard.html",
        users=users,
        total_users=total_users,
        avg_bmi=avg_bmi,
        healthy=healthy
    )

if __name__ == "__main__":
    app.run(debug=True)