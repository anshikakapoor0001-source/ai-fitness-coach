from database.supabase_client import supabase


def save_user(name, age, weight, height, bmi, bmi_category, goal):

    data = {
        "name": name,
        "age": int(age),
        "weight": float(weight),
        "height": float(height),
        "bmi": float(bmi),
        "bmi_category": bmi_category,
        "goal": goal
    }

    supabase.table("users").insert(data).execute()


def get_all_users():

    response = supabase.table("users").select("*").order("id", desc=True).execute()

    return response.data