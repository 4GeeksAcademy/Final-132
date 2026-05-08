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
    genres: Mapped[List[str]] = mapped_column(ARRAY(String(40)), nullable=False)
    platforms: Mapped[List[str]] = mapped_column(ARRAY(String(30)), nullable=False)
    average_rating: Mapped[float] = mapped_column(default=0.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    tier: Mapped[str] = mapped_column(Enum('S', 'A', 'B', 'C', 'D', 'F', 'Undefined', name='tier_enum'), nullable=False)
    
 #  Relaciones
    user_surveys: Mapped[List["UserSurvey"]] = relationship("UserSurvey", back_populates="game")
    game_lists: Mapped[List["UserGameList"]] = relationship("UserGameList", back_populates="game")
    comments: Mapped[List["Comment"]] = relationship("Comment", back_populates="game")
    tier_entries: Mapped[List["TierList"]] = relationship("TierList", back_populates="game")
    favorites: Mapped[List["Favorite"]] = relationship("Favorite", back_populates="game")
    add_games: Mapped[List["AddGame"]] = relationship("AddGame", back_populates="game")

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "release_date": self.release_date.isoformat(),
            "developer": self.developer,
            "publisher": self.publisher,
            "cover_img_url": self.cover_img_url,
            "genres": self.genres,
            "platforms": self.platforms,
            "average_rating": self.average_rating,
            "tier": self.tier
        }

class Profile(db.Model):
    id: Mapped[int] = mapped_column(ForeignKey('user.id'), primary_key=True)
    description: Mapped[str] = mapped_column(Text, default="No description", nullable=False)
    redes: Mapped[Optional[dict]] = mapped_column(JSON) #{"twitter":"...","youtube":"...",etc}
    avatar_url: Mapped[str] = mapped_column(String(255),default="imgurl", nullable=False)

# Relaciones
    user: Mapped["User"] = relationship("User", back_populates="profile")

    def serialize(self):
        return {
            "id": self.id,
            "description": self.description,
            "redes": self.redes,
            "avatar_url": self.avatar_url
        }

class UserSurvey(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)    
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'),nullable=False)    
    game_id: Mapped[int] = mapped_column(ForeignKey('game.id'),nullable=False)
    genres: Mapped[List[str]] = mapped_column(ARRAY(String(60)),nullable=False)
    platforms: Mapped[List[str]] = mapped_column(ARRAY(String(35)),nullable=False)
    play_style: Mapped[str] = mapped_column(String(20),nullable=False) #casul,hardcore,competitive
    favorite_themes: Mapped[List[str]] = mapped_column(ARRAY(String(50)),nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=False)

# Relaciones
    user: Mapped["User"] = relationship("User", back_populates="surveys")
    game: Mapped["Game"] = relationship("Game", back_populates="user_surveys")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "game_id": self.game_id,
            "genres": self.genres,
            "platforms": self.platforms,
            "play_style": self.play_style,
            "favorite_themes": self.favorite_themes,
            "completed_at": self.completed_at.isoformat()
        }


class UserGameList(db.Model):    
    id: Mapped[int] = mapped_column(primary_key=True)    
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'),nullable=False)    
    game_id: Mapped[int] = mapped_column(ForeignKey('game.id'),nullable=False)
    status: Mapped[str] = mapped_column(Enum('want_to_play', 'playing', 'completed', 'dropped', name='status_enum'),nullable=False)
    rating: Mapped[int] = mapped_column(default=0, nullable=False) #1-10 o 1-5  
    review: Mapped[str] = mapped_column(Text, default="no review", nullable=False)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    __table_args__ = (db.UniqueConstraint('user_id', 'game_id'),)

# Relaciones
    user: Mapped["User"] = relationship("User", back_populates= "game_lists")
    game: Mapped["Game"] = relationship("Game", back_populates= "game_lists")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "game_id": self.game_id,
            "status": self.status,
            "rating": self.rating,
            "review": self.review,
            "added_at": self.added_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

class Comment(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'),nullable=False)    
    game_id: Mapped[int] = mapped_column(ForeignKey('game.id'),nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    reply_id: Mapped[int] = mapped_column(ForeignKey('comment.id'), nullable=True) #Self-referential

# Relaciones
    user: Mapped["User"] = relationship("User", back_populates="comments")
    game: Mapped["Game"] = relationship("Game", back_populates="comments")
    replies: Mapped[List["Comment"]] = relationship("Comment", backref=db.backref("parent", remote_side=[id]))

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "game_id": self.game_id,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "reply_id": self.reply_id
        }

class TierList(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'),nullable=False)    
    game_id: Mapped[int] = mapped_column(ForeignKey('game.id'),nullable=False)
    score: Mapped[float] = mapped_column(default=0.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

# Relaciones
    user: Mapped["User"] = relationship("User", back_populates="tier_lists")
    game: Mapped["Game"] = relationship("Game", back_populates="tier_entries")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "game_id": self.game_id,
            "score": self.score,
            "created_at": self.created_at.isoformat()
        }

class Favorite(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'),nullable=False)
    game_id: Mapped[int] = mapped_column(ForeignKey('game.id'),nullable=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'game_id'),)

# Relaciones
    user: Mapped["User"] = relationship("User", back_populates="favorites")
    game: Mapped["Game"] = relationship("Game", back_populates="favorites")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "game_id": self.game_id
        }

class Ban(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    admin_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    ends: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)  #mirarlo??

# Relaciones
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="bans_received")
    admin: Mapped["User"] = relationship("User", foreign_keys=[admin_id], back_populates="bans_given")


class AddGame(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True) 
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    game_id: Mapped[int] = mapped_column(ForeignKey('game.id'), nullable=False)
    creator: Mapped[bool] = mapped_column(Boolean(), default=False, nullable=False)
    update: Mapped[bool] = mapped_column(Boolean(), default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    update_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=utcnow)  #mirarlo????
    body: Mapped[dict] = mapped_column(JSON, nullable=False)

# Relaciones
    user: Mapped["User"] = relationship("User", back_populates="add_games")
    game: Mapped["Game"] = relationship("Game", back_populates="add_games")
