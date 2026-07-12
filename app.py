import logging
import re
from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session, url_for

from config import Config
from database.database import get_user_by_email, save_user
from services.ai_recommendation import generate_plan
from services.auth import sign_in, sign_out, sign_up
from services.bmi import calculate_bmi
from services.diet import get_diet_plan
from services.form_analysis import EXERCISES, exercise_choices
from services.workout import get_workout_plan


app = Flask(__name__)
app.config.from_object(Config)
app.logger.setLevel(logging.INFO)


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("user_email"):
            flash("Please sign in to continue.", "warning")
            return redirect(url_for("home"))
        return view(*args, **kwargs)

    return wrapped_view


def safe_text(value, field_name, max_length=80):
    value = (value or "").strip()
    if not value:
        raise ValueError(f"{field_name} is required.")
    if len(value) > max_length:
        raise ValueError(f"{field_name} must be {max_length} characters or fewer.")
    return value


def valid_email(value):
    email = safe_text(value, "Email", 254).lower()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise ValueError("Enter a valid email address.")
    return email


def profile_from_form():
    name = safe_text(request.form.get("name"), "Name")
    goal = request.form.get("goal")
    valid_goals = {"Weight Loss", "Muscle Gain", "Maintain Fitness"}
    if goal not in valid_goals:
        raise ValueError("Please choose a valid fitness goal.")

    try:
        age = int(request.form.get("age", ""))
        weight = float(request.form.get("weight", ""))
        height = float(request.form.get("height", ""))
    except (TypeError, ValueError) as error:
        raise ValueError("Enter valid numbers for age, height, and weight.") from error

    if not 13 <= age <= 100:
        raise ValueError("Age must be between 13 and 100.")
    if not 30 <= weight <= 350:
        raise ValueError("Weight must be between 30 and 350 kg.")
    if not 100 <= height <= 250:
        raise ValueError("Height must be between 100 and 250 cm.")

    return {"name": name, "age": age, "weight": weight, "height": height, "goal": goal}


def split_plan(plan, goal, bmi_category):
    """Return dependable plan sections even if the model varies its formatting."""
    sections = re.split(r"^##\s+", plan.strip(), flags=re.MULTILINE)
    parsed = {}
    for section in sections:
        if not section.strip():
            continue
        heading, _, content = section.partition("\n")
        parsed[heading.strip().lower()] = content.strip()

    recommendation = parsed.get("ai recommendation", plan.strip())
    diet_plan = parsed.get("diet plan", "\n".join(get_diet_plan(goal, bmi_category)))
    workout_plan = parsed.get("workout plan", "\n".join(get_workout_plan(goal)))
    return recommendation, diet_plan, workout_plan


def store_profile(profile, bmi, bmi_category, recommendation, diet_plan, workout_plan):
    session.update(
        {
            "name": profile["name"],
            "bmi": bmi,
            "bmi_category": bmi_category,
            "goal": profile["goal"],
            "weight": profile["weight"],
            "height": profile["height"],
            "recommendation": recommendation,
            "diet_plan": diet_plan,
            "workout_plan": workout_plan,
        }
    )


@app.route("/")
def home():
    if session.get("user_email"):
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    try:
        email = valid_email(request.form.get("email"))
    except ValueError as error:
        flash(str(error), "danger")
        return redirect(url_for("home"))
    password = request.form.get("password") or ""
    if not password:
        flash("Password is required.", "danger")
        return redirect(url_for("home"))

    try:
        result = sign_in(email, password)
    except Exception:
        app.logger.exception("Sign-in request failed")
        flash("We could not sign you in right now. Please try again.", "danger")
        return redirect(url_for("home"))

    if not getattr(result, "user", None):
        flash("Invalid email or password.", "danger")
        return redirect(url_for("home"))

    session.clear()
    session["user_email"] = email
    try:
        user = get_user_by_email(email)
    except Exception:
        app.logger.exception("Could not fetch user profile")
        flash("Signed in, but we could not load your profile. Please try again.", "warning")
        return redirect(url_for("profile"))

    if not user:
        return redirect(url_for("profile"))

    profile = {
        "name": user["name"],
        "age": user["age"],
        "weight": user["weight"],
        "height": user["height"],
        "goal": user["goal"],
    }
    try:
        plan = generate_plan(**profile, bmi=user["bmi"])
        recommendation, diet_plan, workout_plan = split_plan(plan, profile["goal"], user["bmi_category"])
    except Exception:
        app.logger.exception("Could not refresh AI plan")
        recommendation = "Your profile is ready. Start with small, sustainable steps each day."
        diet_plan = "\n".join(get_diet_plan(profile["goal"], user["bmi_category"]))
        workout_plan = "\n".join(get_workout_plan(profile["goal"]))
        flash("Your AI plan could not be refreshed, so we prepared a starter plan.", "warning")

    store_profile(profile, user["bmi"], user["bmi_category"], recommendation, diet_plan, workout_plan)
    return redirect(url_for("dashboard"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")

    try:
        email = valid_email(request.form.get("email"))
    except ValueError as error:
        flash(str(error), "danger")
        return redirect(url_for("signup"))
    password = request.form.get("password") or ""
    confirm_password = request.form.get("confirm_password") or ""
    if password != confirm_password:
        flash("Passwords do not match.", "danger")
        return redirect(url_for("signup"))
    if len(password) < 8:
        flash("Use a password with at least 8 characters.", "danger")
        return redirect(url_for("signup"))

    try:
        result = sign_up(email, password)
    except Exception:
        app.logger.exception("Sign-up request failed")
        flash("We could not create your account. Please try again.", "danger")
        return redirect(url_for("signup"))

    if not getattr(result, "user", None):
        flash("We could not create your account. The email may already be registered.", "danger")
        return redirect(url_for("signup"))

    if getattr(result, "session", None):
        session.clear()
        session["user_email"] = email
        flash("Account created. Complete your profile to receive your plan.", "success")
        return redirect(url_for("profile"))

    flash("Account created. Check your email to confirm it, then sign in.", "success")
    return redirect(url_for("home"))


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", email=session["user_email"])


@app.route("/dashboard")
@login_required
def dashboard():
    if not session.get("name"):
        return redirect(url_for("profile"))
    return render_template("dashboard.html")


@app.route("/recommend", methods=["POST"])
@login_required
def recommend():
    try:
        profile = profile_from_form()
        bmi, bmi_category = calculate_bmi(profile["weight"], profile["height"])
        plan = generate_plan(**profile, bmi=bmi)
        recommendation, diet_plan, workout_plan = split_plan(plan, profile["goal"], bmi_category)
    except ValueError as error:
        flash(str(error), "danger")
        return redirect(url_for("profile"))
    except Exception:
        app.logger.exception("Could not generate AI plan")
        bmi, bmi_category = calculate_bmi(profile["weight"], profile["height"])
        recommendation = "Your starter plan is ready. Build consistency first, then increase intensity gradually."
        diet_plan = "\n".join(get_diet_plan(profile["goal"], bmi_category))
        workout_plan = "\n".join(get_workout_plan(profile["goal"]))
        flash("We prepared a starter plan while the AI coach is unavailable.", "warning")

    try:
        save_user(
            email=session["user_email"],
            name=profile["name"],
            age=profile["age"],
            weight=profile["weight"],
            height=profile["height"],
            bmi=bmi,
            bmi_category=bmi_category,
            goal=profile["goal"],
        )
    except Exception:
        app.logger.exception("Could not save user profile")
        flash("Your plan is ready, but profile changes could not be saved yet.", "warning")

    store_profile(profile, bmi, bmi_category, recommendation, diet_plan, workout_plan)
    return redirect(url_for("dashboard"))


@app.route("/ai-coach")
@login_required
def ai_coach():
    if not session.get("name"):
        return redirect(url_for("profile"))
    return render_template("ai_coach.html")


@app.route("/form-analysis")
@login_required
def form_analysis():
    return render_template("form_analysis.html", exercises=exercise_choices(), exercise_config=EXERCISES)


@app.route("/logout", methods=["POST"])
def logout():
    try:
        sign_out()
    except Exception:
        app.logger.info("Remote sign-out could not be completed", exc_info=True)
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for("home"))


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(debug=False)
