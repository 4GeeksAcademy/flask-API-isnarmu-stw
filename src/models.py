from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship


db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    username: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    # realationship
    favorites: Mapped[list["Favorites"]] = relationship(back_populates="user")
    favoritesPlanet:  Mapped[list["FavoritesPlanet"]] = relationship(back_populates="user")
    favoritesCharacter:  Mapped[list["FavoritesCharacter"]] = relationship(back_populates="user")
    
    def serialize(self):
        return{
            "id": self.id,
            "email": self.email,
            "username": self.username
        }


class Planet(db.Model):
    __tablename__ = "planet"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    climate: Mapped[str] = mapped_column(String(100), nullable=False)
    terrain: Mapped[str] = mapped_column(String(100), nullable=False)
    population: Mapped[str] = mapped_column(String(100), nullable=False)

    # realationship
    favorites: Mapped[list["Favorites"]] = relationship(back_populates="planet")
    favoritesPlanet:  Mapped[list["FavoritesPlanet"]] = relationship(back_populates="planet")

    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "terrain": self.terrain,
            "population": self.population
        }

class Character(db.Model):

    __tablename__ = "character"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    gender: Mapped[str] = mapped_column(String(100), nullable=False)
    height: Mapped[str] = mapped_column(String(100), nullable=False)
    mass: Mapped[str] = mapped_column(String(20), nullable=False)

    favorites: Mapped[list["Favorites"]] = relationship(back_populates="character")
    favoritesCharacter: Mapped[list["FavoritesCharacter"]] = relationship(back_populates="character")

    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "height": self.height,
            "mass": self.mass
        }
    
class Favorites(db.Model):

    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    planet_id: Mapped[int] = mapped_column(ForeignKey('planet.id'), nullable=True)    
    character_id: Mapped[int] = mapped_column(ForeignKey('character.id'), nullable=True)    

    # realationship
    planet: Mapped["Planet"] = relationship(back_populates="favorites")
    character: Mapped["Character"] = relationship(back_populates="favorites")
    user: Mapped["User"] = relationship(back_populates="favorites")

# en algunas cosas pongo str porque a veces puede ser "unknown"    

class FavoritesPlanet(db.Model):
    __tablename__ = "favoritesPlanet"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    planet_id: Mapped[int] = mapped_column(ForeignKey('planet.id'), nullable=True)    

    # relationship
    planet: Mapped["Planet"] = relationship(back_populates="favoritesPlanet")
    user: Mapped["User"] = relationship(back_populates="favoritesPlanet")

    def serialize(self):
        return{
            "id": self.id,
             "user_id": self.user_id,
             "planet_id": self.planet_id,
        }


class FavoritesCharacter(db.Model):
    __tablename__ = "favoritesCharacter"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    character_id: Mapped[int] = mapped_column(ForeignKey('character.id'), nullable=True)    

    # relationship
    character: Mapped["Character"] = relationship(back_populates="favoritesCharacter")
    user: Mapped["User"] = relationship(back_populates="favoritesCharacter")
    
    def serialize(self):
        return{
            "id": self.id,
             "user_id": self.user_id,
             "character_id": self.character_id,
        }


