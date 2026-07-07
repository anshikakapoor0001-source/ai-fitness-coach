import email
from unicodedata import name

from flask import Flask, render_template, request, redirect, url_for, session

from services.bmi import calculate_bmi
from services.ai_recommendation import generate_plan
from database.database import save_user
from services.auth import sign_up, sign_in
from database.database import get_user_by_email
from services.form_analysis import start_camera
app = Flask(__name__)

app.secret_key = "ai_fitness_secret_key"

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

    # Store data in session (ALWAYS runs)
    session["recommendation"] = recommendation
    session["diet_plan"] = diet_plan
    session["workout_plan"] = workout_plan

    session["name"] = user["name"]
    session["bmi"] = user["bmi"]
    session["bmi_category"] = user["bmi_category"]
    session["goal"] = user["goal"]
    session["weight"] = user["weight"]
    session["height"] = user["height"]

    print("Session:", dict(session))  # Debug

    return redirect(url_for("dashboard"))  

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
    
    
@app.route("/dashboard")
def dashboard():

    return render_template(
        "dashboard.html",
        name=session.get("name"),
        bmi=session.get("bmi"),
        bmi_category=session.get("bmi_category"),
        goal=session.get("goal"),
        weight=session.get("weight"),
        height=session.get("height"),
        recommendation=session.get("recommendation"),
        diet_plan=session.get("diet_plan"),
        workout_plan=session.get("workout_plan")
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
        
        
        session["recommendation"] = recommendation
    session["diet_plan"] = diet_plan
    session["workout_plan"] = workout_plan

    session["name"] = name
    session["bmi"] = round(bmi, 2)
    session["bmi_category"] = bmi_category
    session["goal"] = goal
    session["weight"] = weight
    session["height"] = height

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
    return redirect(url_for("dashboard"))

@app.route("/ai-coach")
def ai_coach():

    print("Recommendation:", session.get("recommendation"))
    print("Diet:", session.get("diet_plan"))
    print("Workout:", session.get("workout_plan"))

    return render_template(
        "ai_coach.html",
        name=session.get("name"),
        bmi=session.get("bmi"),
        bmi_category=session.get("bmi_category"),
        goal=session.get("goal"),
        weight=session.get("weight"),
        height=session.get("height"),
        recommendation=session.get("recommendation"),
        diet_plan=session.get("diet_plan"),
        workout_plan=session.get("workout_plan")
    )
    
    
@app.route("/form-analysis")
def form_analysis():
    return render_template("form_analysis.html")

@app.route("/start-camera")
def start_camera_route():

    start_camera()

    return redirect(url_for("form_analysis"))

if __name__ == "__main__":
    app.run(debug=True)