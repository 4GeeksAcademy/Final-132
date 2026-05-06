from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, DateTime, Date, Text, Enum, ForeignKey, JSON, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship 
from datetime import datetime, timezone
from typing import List, Optional

db = SQLAlchemy()

def utcnow(): 
    return datetime.now(timezone.utc)

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] =mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)
    is_admin : Mapped[bool] = mapped_column(Boolean(), default=False, nullable=False)

# Relaciones
    profile: Mapped["Profile"] = relationship("Profile", back_populates="user", uselist=False)
    surveys: Mapped[List["UserSurvey"]] = relationship("UserSurvey", back_populates="user")
    game_lists: Mapped[List["UserGameList"]] = relationship("UserGameList", back_populates="user")
    comments: Mapped[List["Comment"]] = relationship("Comment", back_populates="user")
    tier_lists: Mapped[List["TierList"]] = relationship("TierList", back_populates="user")
    favorites: Mapped[List["Favorite"]] = relationship("Favorite", back_populates="user")
    bans_given: Mapped[List["Ban"]] = relationship("Ban", foreign_keys="Ban.admin_id", back_populates="admin")
    bans_received: Mapped[List["Ban"]] = relationship("Ban", foreign_keys="Ban.user_id", back_populates="user")
    add_games: Mapped[List["AddGame"]] = relationship("AddGame", back_populates="user")

    def serialize(self):
        return {
            "id": self.id,
            "username":self.username,
            "email": self.email,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_admin": self.is_admin
            # do not serialize the password, its a security breach
        }
class Game (db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)  
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    release_date: Mapped[datetime] = mapped_column((Date), nullable=False)
    developer: Mapped[str] = mapped_column(String(100), nullable=False)
    publisher: Mapped[str] = mapped_column(String(100), nullable=False)
    cover_img_url: Mapped[str] = mapped_column(String(255), nullable=False)
    genres: Mapped[str] = mapped_column(ARRAY(String(40)), nullable=False)
    platforms: Mapped[List[str]] = mapped_column(ARRAY(String(30)), nulllable=False)
    average_rating: Mapped[float] = mapped_column(default=0.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    tier: Mapped[str] = mapped_column(Enum('S', 'A', 'B', 'C', 'D', 'F','Undifined', name='tier_enum'), nullable=False)
    
 # Relaciones
    user_surveys: Mapped[List["UserSurvey"]] = relationship("UserSurvey", back_populates="game")
    game_lists: Mapped[List["UserGameList"]] = relationship("UserGameList", back_populates="game")
    comments: Mapped[List["Comment"]] = relationship("Comment", back_populates="game")
    tier_entries: Mapped[List["TierList"]] = relationship("TierList", back_populates="game")
    favorites: Mapped[List["Favorite"]] = relationship("Favorite", back_populates="game")
    add_games: Mapped[List["AddGame"]] = relationship("AddGame", back_populates="game")
 

class Profile(db.Model):
    id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    description: Mapped[str] = mapped_column(Text, default="No description", nullable=False)
    redes: Mapped[Optional[dict]] = mapped_column(JSON) #{"twitter":"...","youtube":"...",etc}
    avatar_url: Mapped[str] = mapped_column(String(255),default="imgurl", ullable=False)

# Relaciones
    user: Mapped["User"] = relationship("User", back_populates="profile")

class UserSurvey(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)    
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'),nullable=False)    
    game_id: Mapped[int] = mapped_column(ForeignKey('games.id'),nullable=False)
    genres: Mapped[List[str]] = mapped_column(ARRAY(String(60)),nullable=False)
    platforms: Mapped[List[str]] = mapped_column(ARRAY(String(35)),nullable=False)
    play_style: Mapped[str] = mapped_column(String(20),nullable=False) #casul,hardcore,competitive
    favorite_themes: Mapped[List[str]] = mapped_column(ARRAY(String(50)),nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=False)

# Relaciones
    user: Mapped["User"] = relationship("User", back_populates="surveys")
    game: Mapped["Game"] = relationship("Game", back_populates="user_surveys")


class UserGameList(db.Model):    
    id: Mapped[int] = mapped_column(primary_key=True)    
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'),nullable=False)    
    game_id: Mapped[int] = mapped_column(ForeignKey('games.id'),nullable=False)
    status: Mapped[str] = mapped_column(Enum('want_to_play', 'playing', 'completed', 'dropped', name='status_enum'),nullable=False)
    rating: Mapped[int] = mapped_column(default="0", nullable=False) #1-10 o 1-5  
    review: Mapped[str] = mapped_column(Text, default="no review", nullable=False)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

# Relaciones
    user: Mapped["User"] = relationship("User", back_populates= "game_lists")
    game: Mapped["Game"] = relationship("Game", back_populate= "game_lists")


class Comment(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'),nullable=False)    
    game_id: Mapped[int] = mapped_column(ForeignKey('games.id'),nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    replay_id: Mapped[int] = mapped_column(ForeignKey('comments.id'), nullable=False) #Self-referential

# Relaciones
    user: Mapped["User"] = relationship("User", back_populates="comments")
    game: Mapped["Game"] = relationship("Game", back_populates="comments")
    replies: Mapped[List["Comment"]] = relationship("Comment", bacref=db.backref("parent", remote_side=[id])) #requiere nullable???


class TierList(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'),nullable=False)    
    game_id: Mapped[int] = mapped_column(ForeignKey('games.id'),nullable=False)
    score: Mapped[float] = mapped_column(default=Undifined, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

# Relaciones
    user: Mapped["User"] = relationship("User", back_populates="tier_lists")
    game: Mapped["Game"] = relationship("Game", back_populates="tier_entries")


class Favorite(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'),nullable=False)
    game_id: Mapped[int] = mapped_column(ForeignKey('games.id'),nullable=False)

# Relaciones
    user: Mapped["User"] = relationship("User", back_populates="favorites")
    game: Mapped["Game"] = relationship("Game", back_populates="favorites")

class Ban(db.Model):
    id: Mapped[int] = mapped_column(primay_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    admin_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    ends: Mapped[datetime] = mapped_column(DateTime(timezone=True), default="Perma", nullable=False)  #mirarlo??

# Relaciones
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="bans_received")
    admin: Mapped["User"] = relationship("User", foreign_keys=[admin_id], back_populates="bans_given")


class AddGame(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True) 
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    game_id: Mapped[int] = mapped_column(ForeignKey('games.id'), nullable=False)
    creator: Mapped[bool] = mapped_column(Boolean(), default=False, nullable=False)
    update: Mapped[bool] = mapped_column(Boolean(), default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    update_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=utcnow)  #mirarlo????
    body: Mapped[dict] = mapped_column(JSON, nullable=False)

# Relaciones
    user: Mapped["User"] = relationship("User", back_populates="add_games")
    game: Mapped["Game"] = relationship("Game", back_populates="add_games")












