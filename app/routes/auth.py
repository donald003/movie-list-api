from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError
from ..extensions import db
from ..models import User
from ..schemas import RegisterSchema, UserSchema, LoginSchema, LoginResponseSchema

auth_bp = Blueprint("auth", "auth", url_prefix="/auth")


@auth_bp.post("/register")
@auth_bp.arguments(RegisterSchema)
@auth_bp.response(201, UserSchema)
def register(data):
    email = data["email"].strip().lower()
    user = User(email=email)
    user.set_password(data["password"])

    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(409, message="email already registered")

    return {"id": user.id, "email": user.email}


@auth_bp.post("/login")
@auth_bp.arguments(LoginSchema)
@auth_bp.response(200, LoginResponseSchema)
def login(data):
    email = data["email"].strip().lower()
    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(data["password"]):
        abort(401, "invalid credentials")

    token = create_access_token(identity=str(user.id))
    return {"access_token": token}
