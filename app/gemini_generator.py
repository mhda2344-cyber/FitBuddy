from google import genai
from google.genai import types

from app.config import (
    DEMO_MODE,
    GEMINI_API_KEY,
    GEMINI_MAX_OUTPUT_TOKENS,
    GEMINI_NUTRITION_MODEL,
    GEMINI_TEMPERATURE,
    GEMINI_WORKOUT_MODEL,
)


_client = None

if GEMINI_API_KEY:
    _client = genai.Client(
        api_key=GEMINI_API_KEY
    )


def _generate(
    prompt: str,
    model: str
) -> str:

    if not _client:

        raise RuntimeError(
            "GEMINI_API_KEY is not configured. "
            "Set it in .env or keep DEMO_MODE=true."
        )

    response = _client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=GEMINI_TEMPERATURE,
            max_output_tokens=GEMINI_MAX_OUTPUT_TOKENS,
        ),
    )

    text = (
        response.text
        if response.text
        else ""
    ).strip()

    if not text:

        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return text


def _demo_workout(user) -> str:

    return f"""
FITBUDDY 7-DAY PERSONALIZED WORKOUT PLAN

User: {user.username}
Age: {user.age}
Weight: {user.weight} kg
Goal: {user.goal}
Intensity: {user.intensity}


DAY 1 – FULL BODY

Warm-up:
5–10 minutes brisk walking and mobility.

Main workout:
• Squats – 3 sets × 12 reps
• Push-ups – 3 sets × 10 reps
• Rows – 3 sets × 12 reps
• Lunges – 3 sets × 10 reps per leg

Rest:
60–90 seconds between sets.

Cooldown:
5 minutes of gentle stretching.


DAY 2 – CARDIO

Warm-up:
5 minutes easy walking.

Main workout:
25–30 minutes of moderate cardio.

Cooldown:
5–10 minutes stretching.


DAY 3 – UPPER BODY

Warm-up:
Shoulder circles and light movement for 5–10 minutes.

Main workout:
• Push-ups – 3 × 10
• Rows – 3 × 12
• Shoulder press – 3 × 10
• Biceps curls – 3 × 12

Cooldown:
Upper-body stretching.


DAY 4 – RECOVERY / FLEXIBILITY

Easy walking for 15–20 minutes.

Add gentle yoga or mobility exercises.

Focus on recovery.


DAY 5 – LOWER BODY

Warm-up:
5–10 minutes walking and leg mobility.

Main workout:
• Squats – 3 × 12
• Glute bridges – 3 × 15
• Step-ups – 3 × 10 per leg
• Calf raises – 3 × 15

Cooldown:
Lower-body stretching.


DAY 6 – CORE + CARDIO

Warm-up:
5 minutes.

Main workout:
• Plank – 3 × 30 seconds
• Dead bug – 3 × 10 per side
• Bicycle crunches – 3 × 12 per side
• Comfortable cardio – 15–20 minutes

Cooldown:
Gentle stretching.


DAY 7 – REST / ACTIVE RECOVERY

Light walking and mobility.

Prioritize sleep, hydration,
and recovery.


SAFETY NOTE

This example is for general wellness.
It is not a medical diagnosis or treatment.

Adjust exercise difficulty to your experience
and stop if you experience pain or unusual symptoms.
"""


def _demo_tip(user) -> str:

    goal = user.goal.lower()

    if "muscle" in goal:

        return (
            "Include a protein-rich food in each "
            "main meal and stay hydrated after training."
        )

    if "weight" in goal or "fat" in goal:

        return (
            "Prioritize vegetables, adequate protein, "
            "water, and balanced portions rather than "
            "skipping meals."
        )

    return (
        "Stay hydrated, eat balanced meals, "
        "and give your body enough sleep and "
        "recovery time."
    )


def generate_workout_gemini(user) -> str:

    if DEMO_MODE:

        return _demo_workout(user)

    prompt = f"""
You are FitBuddy,
an AI fitness planning assistant.

Create a safe and structured
7-day workout plan.

USER INFORMATION

Name: {user.username}
Age: {user.age}
Weight: {user.weight} kg
Fitness goal: {user.goal}
Workout intensity: {user.intensity}


REQUIREMENTS

1. Give Day 1 through Day 7.

2. Include:
- Warm-up
- Main workout
- Exercises
- Sets and repetitions or duration
- Rest guidance
- Cooldown/recovery

3. Tailor the plan to:
- Fitness goal
- Workout intensity
- User age

4. Keep the plan practical
and easy to follow.

5. Use clear headings.

6. Do not claim to diagnose,
treat, or cure medical conditions.

7. Include appropriate recovery days.
"""

    return _generate(
        prompt,
        GEMINI_WORKOUT_MODEL
    )


def generate_nutrition_tip_with_flash(user) -> str:

    if DEMO_MODE:

        return _demo_tip(user)

    prompt = f"""
Give one concise nutrition or recovery tip
for a FitBuddy user.

Goal:
{user.goal}

Age:
{user.age}

Weight:
{user.weight} kg

Workout intensity:
{user.intensity}

The advice should:

- Be practical
- Support general wellness
- Complement exercise
- Be easy to understand
- Avoid medical claims
"""

    return _generate(
        prompt,
        GEMINI_NUTRITION_MODEL
    )


def update_workout_plan(
    original_plan: str,
    feedback: str,
    user
) -> str:

    if DEMO_MODE:

        return f"""
{original_plan}


========================================

UPDATED USING USER FEEDBACK

Feedback received:

{feedback}


Adjustment:

The workout plan has been revised to
emphasize the requested preference while
retaining a balanced 7-day structure.

Keep intensity appropriate for the user's
experience and allow adequate recovery.

This is general wellness guidance and is
not medical diagnosis or treatment.
"""

    prompt = f"""
You are updating a previously generated
FitBuddy workout plan.

USER INFORMATION

Name:
{user["username"]}

Age:
{user["age"]}

Goal:
{user["goal"]}

Intensity:
{user["intensity"]}


ORIGINAL PLAN

{original_plan}


USER FEEDBACK

{feedback}


TASK

Create a complete revised 7-day workout plan.

Do not return only the changed section.

Preserve useful parts of the original plan.

Incorporate the user's feedback.

Include:

- Day 1 through Day 7
- Warm-up
- Main workout
- Exercises
- Sets/repetitions or duration
- Rest
- Cooldown/recovery

Do not make medical diagnosis
or treatment claims.
"""

    return _generate(
        prompt,
        GEMINI_WORKOUT_MODEL
    )