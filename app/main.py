import os

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import (
    init_db,
    save_user,
    save_plan,
    update_plan,
    get_user,
    get_plan_by_user,
    get_all_users,
)

from app.schemas import UserInput

from app.gemini_generator import (
    generate_workout_gemini,
    generate_nutrition_tip_with_flash,
    update_workout_plan,
)


# --------------------------------------------------
# FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="FitBuddy",
    description="AI Fitness Plan Generator",
    version="1.0.0",
)


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TEMPLATE_DIR = os.path.join(
    BASE_DIR,
    "templates",
)

STATIC_DIR = os.path.join(
    BASE_DIR,
    "static",
)


# --------------------------------------------------
# Templates and static files
# --------------------------------------------------

templates = Jinja2Templates(
    directory=TEMPLATE_DIR
)

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)


# --------------------------------------------------
# Startup
# --------------------------------------------------

@app.on_event("startup")
def startup_event():
    init_db()


# --------------------------------------------------
# Home page
# --------------------------------------------------

@app.get(
    "/",
    response_class=HTMLResponse
)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "error": None
        },
    )


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "ok",
        "service": "fitbuddy"
    }


# --------------------------------------------------
# Generate workout plan
# --------------------------------------------------

@app.post(
    "/generate-workout",
    response_class=HTMLResponse
)
def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
):

    try:

        user = UserInput(
            username=username.strip(),
            user_id=user_id.strip(),
            age=age,
            weight=weight,
            goal=goal.strip(),
            intensity=intensity.strip().lower(),
        )

        # Save user information
        save_user(user)

        # Generate workout plan
        workout_plan = generate_workout_gemini(user)

        # Generate nutrition/recovery tip
        nutrition_tip = generate_nutrition_tip_with_flash(user)

        # Save generated plan
        save_plan(
            user_id=user.user_id,
            workout_plan=workout_plan,
            nutrition_tip=nutrition_tip,
        )

        # Display result
        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "workout_plan": workout_plan,
                "nutrition_tip": nutrition_tip,
                "updated": False,
                "message": None,
            },
        )

    except Exception as exc:

        print(
            "GENERATE WORKOUT ERROR:",
            repr(exc)
        )

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": str(exc)
            },
            status_code=500,
        )


# --------------------------------------------------
# Submit feedback and update workout plan
# --------------------------------------------------

@app.post(
    "/submit-feedback",
    response_class=HTMLResponse
)
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
):

    try:

        user_id = user_id.strip()
        feedback = feedback.strip()

        # Find user
        user = get_user(user_id)

        if user is None:

            return HTMLResponse(
                content=f"USER NOT FOUND: {user_id}",
                status_code=400,
            )

        # Get the user's latest plan
        plan = get_plan_by_user(user_id)

        if plan is None:

            return HTMLResponse(
                content="NO FITNESS PLAN FOUND FOR THIS USER",
                status_code=400,
            )

        # Update workout plan using AI
        updated_plan = update_workout_plan(
            user=user,
            original_plan=plan.workout_plan,
            feedback=feedback,
        )

        # Save updated plan and feedback
        update_plan(
            user_id=user_id,
            feedback=feedback,
            updated_plan=updated_plan,
        )

        # Display updated plan
        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "workout_plan": updated_plan,
                "nutrition_tip": plan.nutrition_tip,
                "updated": True,
                "message": "Your fitness plan has been updated successfully.",
            },
        )

    except Exception as exc:

        print(
            "FEEDBACK ERROR:",
            repr(exc)
        )

        return HTMLResponse(
            content=f"FEEDBACK ERROR: {exc}",
            status_code=400,
        )


# --------------------------------------------------
# View all users
# --------------------------------------------------

@app.get(
    "/view-all-users",
    response_class=HTMLResponse
)
def view_all_users(request: Request):

    try:

        users = get_all_users()

        user_data = []

        for user in users:

            plan = get_plan_by_user(
                user.user_id
            )

            user_data.append(
                {
                    "user": user,
                    "plan": plan,
                }
            )

        return templates.TemplateResponse(
            request=request,
            name="all_users.html",
            context={
                "users": user_data
            },
        )

    except Exception as exc:

        print(
            "VIEW USERS ERROR:",
            repr(exc)
        )

        return HTMLResponse(
            content=f"ERROR: {exc}",
            status_code=500,
        )