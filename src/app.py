"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, Character, Favorites, FavoritesCharacter,FavoritesPlanet
from sqlalchemy import select


app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)

# CRUD USER --------------------------------

# CREATE user
@app.route("/user", methods=['POST'])
def create_user():

    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    new_user = User(username = username, email = email, password = password)
    db.session.add(new_user)
    db.session.commit()
    
    return ("Usuario creado")

# GET ALL
@app.route("/user", methods=['GET'])
def get_all_users():

#Guardamos todos los modelos de User en una variable
    users = db.session.execute(select(User)).scalars().all()
    print(users)

    return jsonify({"users": [user.serialize() for user in users]}), 200

# GET ONE

@app.route("/user/<int:user_id>", methods=['GET'])
def get_user(user_id):

    # Utilizamos el user_id para buscar una tabla User que lo tenga y lo guardamos En una variable

    user = db.session.get(User, user_id)
    print(user)
    if not user:
        return jsonify({"message": "user not found"}), 404
    return jsonify(user.serialize()), 200
# GET USER FAVORITE
@app.route("/user/favorites", methods=['GET'])
def get_user_favorite():
    favorites= db.session.execute(select(Favorites)).scalars().all()
    print(favorites)

    if not favorites:
        return jsonify({"message": "favorites not found"}), 404
    return jsonify({"favorites": [favorite.serialize() for favorite in favorites]}), 200

#Fin CRUD User ------------------

#CRUD Character ------------------
@app.route("/favorite/character/<int:character_id>", methods=['POST'])
def add_favorite_character(character_id):

    data = request.get_json()
    user_id = data.get("user_id")

    # comprobacion para ver si existen user y character

    if not user_id:
        return jsonify({"message": "user_id is required"}), 400
    if not db.session.get(User, user_id):
        return jsonify({"message": "User not found"}), 404
    if not db.session.get(Character, character_id):
        return jsonify({"message": "character not found"}), 404
    # Buscar o crear favoritos
    favorites_result = db.session.execute(select(Favorites).where(Favorites.user_id == user_id))
    favorites = favorites_result.scalar_one_or_none()

    if not favorites:
        favorites = Favorites(user_id=user_id)
        db.session.add(favorites)
        db.session.commit()

    # verificar si esta duplicado
    duplicate_check_result = db.session.execute(select(FavoritesCharacter).where(
        FavoritesCharacter.favorites_id == favorites.id,
        FavoritesCharacter.character_id == character_id))
    duplicate_check = duplicate_check_result.scalar_one_or_none()

    if duplicate_check:
        return jsonify({"message":"Already in favorites"}), 409
    # crear fav
    fav = FavoritesCharacter(favorites_id=favorites.id, character_id=character_id)

    db.session.add(fav)
    db.session.commit()

    return jsonify({"message":"Character added to favorites"}), 201


# DELETE method


@app.route("/favorite/character/<int:fav_id>", methods=['DELETE'])
def delete_favorite_character(fav_id):
    
    # buscar el favorito
    fav_result = db.session.execute(select(FavoritesCharacter).where(FavoritesCharacter.id == fav_id))
    favorite = fav_result.scalar_one_or_none()

    # comprobar qeu exxiste
    if not favorite:
        return jsonify({"message": "Favorite not found"}), 404
    
    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"message": "Favorite character deleted"}), 200

#GET ALL
@app.route("/character", methods=['GET'])

def get_all_characters():

    characters = db.session.execute(select(Character)).scalars().all()
    print(characters)

    return jsonify({"characters": [character.serialize() for character in characters]}), 200


#GET ONE

@app.route("/character/<int:character_id>", methods=['GET'])
def get_character(character_id):
    character = db.session.get(Character, character_id)
    print(character)
    if not character:
        return jsonify({"message": "character not found"}), 404
    return jsonify(character.serialize()), 200

#Fin CRUD Character ------------------

#CRUD Planet ------------------

@app.route("/favorite/planet/<int:planet_id>", methods=['POST'])
def add_favorite_planet(planet_id):

    data = request.get_json()
    user_id = data.get("user_id")

    # comprobacion existencia user y planet
    if not user_id:
        return jsonify({"message": "user_id is required"}), 400
    if not db.session.get(User, user_id):
        return jsonify({"message": "User not found"}), 404
    if not db.session.get(Planet, planet_id):
        return jsonify({"message": "planet not found"}), 404
    # buscar o crear fav
    favorites_result = db.session.execute(select(Favorites).where(Favorites.user_id == user_id))
    favorites = favorites_result.scalar_one_or_none()

    if not favorites:
        favorites = Favorites(user_id=user_id)
        db.session.add(favorites)
        db.session.commit()
    
    # verificar si esta duplicado
    duplicate_check_result = db.session.execute(select(FavoritesPlanet).where(
        FavoritesPlanet.favorites_id == favorites.id,
        FavoritesPlanet.planet_id == planet_id))
    duplicate_check = duplicate_check_result.scalar_one_or_none()

    if duplicate_check:
        return jsonify({"message":"Already in favorites"}), 409
    # crear fav
    fav = FavoritesPlanet(favorites_id=favorites.id, planet_id=planet_id)

    db.session.add(fav)
    db.session.commit()

    return jsonify({"message":"Planet added to favorites"}), 201

# DELETE planet favorite
@app.route("/favorite/planet/<int:fav_id>", methods=['DELETE'])
def delete_favorite_planet(fav_id):

    # buscar el favorito
    fav_result = db.session.execute(select(FavoritesPlanet).where(FavoritesPlanet.id == fav_id))
    favorite = fav_result.scalar_one_or_none()

    # comprobar qeu exxiste
    if not favorite:
        return jsonify({"message": "Favorite not found"}), 404
    
    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"message": "Favorite planet deleted"}), 200

#GET ALL
@app.route("/planet", methods=['GET'])
def get_all_planets():
    planets = db.session.execute(select(Planet)).scalars().all()
    print(planets)

    return jsonify({"planets": [planet.serialize() for planet in planets]}), 200
#GET ONE
@app.route("/planet/<int:planet_id>", methods=['GET'])
def get_planet(planet_id):
    planet = db.session.get(Planet, planet_id)
    print(planet)
    if not planet:
        return jsonify({"message": "planet not found"}), 404
    return jsonify(planet.serialize()), 200
    

#Fin CRUD Planet ------------------



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
