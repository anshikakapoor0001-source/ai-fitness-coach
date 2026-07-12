# Fitness AI Coach

A Flask web app that creates personalized diet and workout guidance, stores user profiles in Supabase, and offers browser-based exercise form analysis.

## Features

- Secure sign-up, sign-in, and sign-out through Supabase Auth
- Validated fitness profile and BMI classification
- Gemini-powered plan generation with a useful local fallback plan
- Responsive dashboard, AI coach view, and live rep counter
- Clear user-facing errors and protected app routes

## Setup

1. Use Python 3.13, matching `.python-version`.
2. Install dependencies with `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and supply the required values.
4. In Supabase, create a `users` table with `email` as a unique column and the profile fields used in `database/database.py`.
5. Start the app with `flask --app app run`.

For deployment, set `FLASK_ENV=production`, use a long unique `FLASK_SECRET_KEY`, and run behind a production WSGI server.

## Notes

The app provides general wellness guidance only; it is not medical advice. Form analysis uses the browser camera through `getUserMedia`, which works on `localhost` or HTTPS and requires camera permission.
