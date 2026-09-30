from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import Movie

movies_bp = Blueprint("movies", __name__, url_prefix="/movies")


@movies_bp.get("")
@jwt_required()
def list_movies():
    user_id = int(get_jwt_identity())
    movies = Movie.query.filter_by(user_id=user_id).order_by(Movie.id).all()
    return [serialize(m) for m in movies], 200


@movies_bp.post("")
@jwt_required()
def create_movie():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    title = (data.get("title") or "").strip()
    director = (data.get("director") or "").strip()
    year = data.get("year")
    rating = data.get("rating")

    if not title or not director or not isinstance(year, int):
        return {"error": "title, director, and year are required"}, 400

    if rating is not None and not (1 <= rating <= 10):
        return {"error": "rating must be between 1 and 10"}, 400

    movie = Movie(
        title=title,
        director=director,
        year=year,
        rating=rating,
        user_id=user_id,
    )
    db.session.add(movie)
    db.session.commit()

    return serialize(movie), 201


@movies_bp.get("/<int:movie_id>")
@jwt_required()
def get_movie(movie_id):
    user_id = int(get_jwt_identity())
    movie = Movie.query.filter_by(id=movie_id, user_id=user_id).first()
    if not movie:
        return {"error": "not found"}, 404
    return serialize(movie), 200


@movies_bp.put("/<int:movie_id>")
@jwt_required()
def update_movie(movie_id):
    user_id = int(get_jwt_identity())
    movie = Movie.query.filter_by(id=movie_id, user_id=user_id).first()
    if not movie:
        return {"error": "not found"}, 404

    data = request.get_json(silent=True) or {}

    if "title" in data:
        movie.title = (data["title"] or "").strip()
    if "director" in data:
        movie.director = (data["director"] or "").strip()
    if "year" in data:
        if not isinstance(data["year"], int):
            return {"error": "year must be an integer"}, 400
        movie.year = data["year"]
    if "rating" in data:
        r = data["rating"]
        if r is not None and not (1 <= r <= 10):
            return {"error": "rating must be between 1 and 10"}, 400
        movie.rating = r
    if "watched" in data:
        movie.watched = bool(data["watched"])

    db.session.commit()
    return serialize(movie), 200


@movies_bp.delete("/<int:movie_id>")
@jwt_required()
def delete_movie(movie_id):
    user_id = int(get_jwt_identity())
    movie = Movie.query.filter_by(id=movie_id, user_id=user_id).first()
    if not movie:
        return {"error": "not found"}, 404

    db.session.delete(movie)
    db.session.commit()
    return "", 204


def serialize(movie):
    return {
        "id": movie.id,
        "title": movie.title,
        "director": movie.director,
        "year": movie.year,
        "rating": movie.rating,
        "watched": movie.watched,
    }