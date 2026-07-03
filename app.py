import email
from unicodedata import name

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

     ai_plan = generate_plan(
        name=user["name"],
        age=user["age"],
        height=user["height"],
        weight=user["weight"],
        bmi=user["bmi"],
        goal=user["goal"]
    )

    recommendation = ""
    diet_plan = ""
    workout_plan = ""

    try:
        recommendation = ai_plan.split("## Diet Plan")[0]
        recommendation = recommendation.replace("## AI Recommendation", "").strip()

        diet_plan = ai_plan.split("## Diet Plan")[1].split("## Workout Plan")[0].strip()

        workout_plan = ai_plan.split("## Workout Plan")[1].strip()

    except Exception:
        recommendation = ai_plan
        diet_plan = ""
        workout_plan = ""

    return render_template(
        "dashboard.html",
        name=user["name"],
        age=user["age"],
        weight=user["weight"],
        height=user["height"],
        goal=user["goal"],
        bmi=user["bmi"],
        bmi_category=user["bmi_category"],
        recommendation=recommendation,
        diet_plan=diet_plan,
        workout_plan=workout_plan
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
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return "Passwords do not match!"

        result = sign_up(email, password)

        if result.user:
            return redirect(url_for("profile", email=email))

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

    # Split AI response
    recommendation = ""
    diet_plan = ""
    workout_plan = ""

    try:
        recommendation = ai_plan.split("## Diet Plan")[0]
        recommendation = recommendation.replace("## AI Recommendation", "").strip()

        diet_plan = ai_plan.split("## Diet Plan")[1].split("## Workout Plan")[0].strip()

        workout_plan = ai_plan.split("## Workout Plan")[1].strip()

    except Exception:
        recommendation = ai_plan

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
    print("FULL AI PLAN:\n", ai_plan)
    print("Recommendation:", recommendation)
    print("Diet:", diet_plan)
    print("Workout:", workout_plan)
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
        ai_plan=ai_plan,
        recommendation=recommendation,
        diet_plan=diet_plan,
        workout_plan=workout_plan
    )

@app.route("/ai-coach")
def ai_coach():

    return render_template(
        "ai_coach.html",
        name=request.args.get("name"),
        bmi=request.args.get("bmi"),
        bmi_category=request.args.get("bmi_category"),
        goal=request.args.get("goal"),
        weight=request.args.get("weight"),
        height=request.args.get("height"),
       recommendation=request.args.get("recommendation"),
        diet_plan=request.args.get("diet_plan"),
        workout_plan=request.args.get("workout_plan")
    )

if __name__ == "__main__":
    app.run(debug=True)