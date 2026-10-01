from sqlalchemy import create_engine, Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

from app.config import DATABASE_URL


# Database setup
connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


# User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String(100), nullable=False)

    user_id = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    age = Column(Integer, nullable=False)

    weight = Column(Float, nullable=False)

    goal = Column(String(100), nullable=False)

    intensity = Column(String(50), nullable=False)

    plans = relationship(
        "Plan",
        back_populates="user",
        cascade="all, delete-orphan",
    )


# Plan model
class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    workout_plan = Column(Text, nullable=False)

    nutrition_tip = Column(Text, nullable=False)

    feedback = Column(Text, nullable=True)

    updated_plan = Column(Text, nullable=True)

    user = relationship(
        "User",
        back_populates="plans",
    )


# Initialize database
def init_db():
    Base.metadata.create_all(bind=engine)


# Save or update user
def save_user(user):
    db = SessionLocal()

    try:
        existing_user = (
            db.query(User)
            .filter(User.user_id == user.user_id)
            .first()
        )

        if existing_user:
            existing_user.username = user.username
            existing_user.age = user.age
            existing_user.weight = user.weight
            existing_user.goal = user.goal
            existing_user.intensity = user.intensity

            db.commit()
            db.refresh(existing_user)

            return existing_user

        db_user = User(
            username=user.username,
            user_id=user.user_id,
            age=user.age,
            weight=user.weight,
            goal=user.goal,
            intensity=user.intensity,
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user

    finally:
        db.close()


# Save fitness plan
def save_plan(user_id, workout_plan, nutrition_tip):
    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.user_id == user_id)
            .first()
        )

        if user is None:
            raise ValueError("User ID was not found.")

        plan = Plan(
            user_id=user.id,
            workout_plan=workout_plan,
            nutrition_tip=nutrition_tip,
        )

        db.add(plan)
        db.commit()
        db.refresh(plan)

        return plan

    finally:
        db.close()


# Update fitness plan after feedback
def update_plan(user_id, feedback, updated_plan):
    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.user_id == user_id)
            .first()
        )

        if user is None:
            raise ValueError("User ID was not found.")

        plan = (
            db.query(Plan)
            .filter(Plan.user_id == user.id)
            .order_by(Plan.id.desc())
            .first()
        )

        if plan is None:
            raise ValueError(
                "No fitness plan was found for this user."
            )

        plan.feedback = feedback
        plan.updated_plan = updated_plan

        db.commit()
        db.refresh(plan)

        return plan

    finally:
        db.close()


# Get user by User ID
def get_user(user_id):
    db = SessionLocal()

    try:
        return (
            db.query(User)
            .filter(User.user_id == user_id)
            .first()
        )

    finally:
        db.close()


# Get latest plan for a user
def get_plan_by_user(user_id):
    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.user_id == user_id)
            .first()
        )

        if user is None:
            return None

        return (
            db.query(Plan)
            .filter(Plan.user_id == user.id)
            .order_by(Plan.id.desc())
            .first()
        )

    finally:
        db.close()


# Get all users
def get_all_users():
    db = SessionLocal()

    try:
        return (
            db.query(User)
            .order_by(User.id.desc())
            .all()
        )

    finally:
        db.close()