from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import Movie
from ..schemas import MovieSchema, MovieCreateSchema, MovieUpdateSchema

movies_bp = Blueprint("movies", "movies", url_prefix="/movies")


@movies_bp.get("")
@movies_bp.doc(security=[{"bearerAuth": []}])
@jwt_required()
@movies_bp.response(200, MovieSchema(many=True))
def list_movies():
    user_id = int(get_jwt_identity())
    movies = Movie.query.filter_by(user_id=user_id).order_by(Movie.id).all()
    return movies


@movies_bp.post("")
@movies_bp.doc(security=[{"bearerAuth": []}])
@jwt_required()
@movies_bp.arguments(MovieCreateSchema)
@movies_bp.response(201, MovieSchema)
def create_movie(data):
    user_id = int(get_jwt_identity())

    movie = Movie(
        title = data["title"].strip(),
        director = data["director"].strip(),
        year = data["year"],
        rating = data.get("rating"),
        watched = data["watched"],
        user_id = user_id,
    )
    db.session.add(movie)
    db.session.commit()
    return movie


@movies_bp.get("/<int:movie_id>")
@movies_bp.doc(security=[{"bearerAuth": []}])
@jwt_required()
@movies_bp.response(200, MovieSchema)
def get_movie(movie_id):
    user_id = int(get_jwt_identity())
    movie = Movie.query.filter_by(id=movie_id, user_id=user_id).first()
    if not movie:
        abort(404, message="not found")
    return movie


@movies_bp.put("/<int:movie_id>")
@movies_bp.doc(security=[{"bearerAuth": []}])
@jwt_required()
@movies_bp.arguments(MovieUpdateSchema)
@movies_bp.response(200, MovieSchema)
def update_movie(data, movie_id):
    user_id = int(get_jwt_identity())
    movie = Movie.query.filter_by(id=movie_id, user_id=user_id).first()
    if not movie:
        abort(404, message="not found")

    if "title" in data:
        movie.title = data["title"].strip()
    if "director" in data:
        movie.director = data["director"].strip()
    if "year" in data:
        movie.year = data["year"]
    if "rating" in data:
        movie.rating = data["rating"]
    if "watched" in data:
        movie.watched = data["watched"]

    db.session.commit()
    return movie


@movies_bp.delete("/<int:movie_id>")
@movies_bp.doc(security=[{"bearerAuth": []}])
@jwt_required()
@movies_bp.response(204)
def delete_movie(movie_id):
    user_id = int(get_jwt_identity())
    movie = Movie.query.filter_by(id=movie_id, user_id=user_id).first()
    if not movie:
        abort(404, message="not found")

    db.session.delete(movie)
    db.session.commit()
    return ""
