import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorite

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/people', methods=['GET'])
def get_people():
    people_query = People.query.all()
    results = list(map(lambda x: x.serialize(), people_query))
    return jsonify(results), 200


@app.route('/people/<int:people_id>', methods=['GET'])
def get_single_people(people_id):
    person = People.query.get(people_id)
    if not person:
        return jsonify({"msg": "Personaje no encontrado"}), 404
    return jsonify(person.serialize()), 200


@app.route('/planets', methods=['GET'])
def get_planets():
    planets_query = Planet.query.all()
    results = list(map(lambda x: x.serialize(), planets_query))
    return jsonify(results), 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_single_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"msg": "Planeta no encontrado"}), 404
    return jsonify(planet.serialize()), 200


@app.route('/users', methods=['GET'])
def get_users():
    users_query = User.query.all()
    results = list(map(lambda x: x.serialize(), users_query))
    return jsonify(results), 200


@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    favorites = Favorite.query.filter_by(user_id=user_id).all()
    results = list(map(lambda x: x.serialize(), favorites))
    return jsonify(results), 200


@app.route('/favorite/planet/<int:planet_id>/user/<int:user_id>', methods=['POST'])
def add_fav_planet(planet_id, user_id):
    user = User.query.get(user_id)
    planet = Planet.query.get(planet_id)
    if not user or not planet:
        return jsonify({"msg": "Usuario o Planeta incorrecto"}), 404

    check = Favorite.query.filter_by(
        user_id=user_id, planet_id=planet_id).first()
    if check:
        return jsonify({"msg": "Ya es favorito"}), 400

    new_fav = Favorite(user_id=user_id, planet_id=planet_id)
    db.session.add(new_fav)
    db.session.commit()
    return jsonify({"msg": "Planeta añadido a favoritos"}), 200


@app.route('/favorite/people/<int:people_id>/user/<int:user_id>', methods=['POST'])
def add_fav_people(people_id, user_id):
    user = User.query.get(user_id)
    person = People.query.get(people_id)
    if not user or not person:
        return jsonify({"msg": "Usuario o Personaje incorrecto"}), 404

    check = Favorite.query.filter_by(
        user_id=user_id, people_id=people_id).first()
    if check:
        return jsonify({"msg": "Ya es favorito"}), 400

    new_fav = Favorite(user_id=user_id, people_id=people_id)
    db.session.add(new_fav)
    db.session.commit()
    return jsonify({"msg": "Personaje añadido a favoritos"}), 200


@app.route('/favorite/planet/<int:planet_id>/user/<int:user_id>', methods=['DELETE'])
def delete_fav_planet(planet_id, user_id):
    fav = Favorite.query.filter_by(
        user_id=user_id, planet_id=planet_id).first()
    if not fav:
        return jsonify({"msg": "Favorito no encontrado"}), 404

    db.session.delete(fav)
    db.session.commit()
    return jsonify({"msg": "Eliminado de favoritos"}), 200


@app.route('/favorite/people/<int:people_id>/user/<int:user_id>', methods=['DELETE'])
def delete_fav_people(people_id, user_id):
    fav = Favorite.query.filter_by(
        user_id=user_id, people_id=people_id).first()
    if not fav:
        return jsonify({"msg": "Favorito no encontrado"}), 404

    db.session.delete(fav)
    db.session.commit()
    return jsonify({"msg": "Eliminado de favoritos"}), 200


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
