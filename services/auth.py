from database.supabase_client import supabase


def sign_up(email, password):
    return supabase.auth.sign_up({
        "email": email,
        "password": password
    })


def sign_in(email, password):
    return supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })


def sign_out():
    return supabase.auth.sign_out()
