from database.supabase_client import supabase


# ----------------------------------------
# Save or Update User Profile
# ----------------------------------------
def save_user(email, name, age, weight, height, bmi, bmi_category, goal):

    data = {
        "email": email,
        "name": name,
        "age": int(age),
        "weight": float(weight),
        "height": float(height),
        "bmi": float(bmi),
        "bmi_category": bmi_category,
        "goal": goal
    }

    response = (
        supabase
        .table("users")
        .upsert(data, on_conflict="email")
        .execute()
    )

    return response


# ----------------------------------------
# Get User By Email
# ----------------------------------------
def get_user_by_email(email):

    response = (
        supabase
        .table("users")
        .select("*")
        .eq("email", email)
        .execute()
    )

    if response.data:
        return response.data[0]

    return None


# ----------------------------------------
# Get All Users
# ----------------------------------------
def get_all_users():

    response = (
        supabase
        .table("users")
        .select("*")
        .order("id", desc=True)
        .execute()
    )

    return response.data