from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_manager
from flask import Flask
from sqlalchemy import ForeignKey


db = SQLAlchemy()
bcrypt = Bcrypt()


def connect_db(app):
    """Connects to db"""

    db.app = app
    db.init_app(app)


class User(db.Model):
    """User in the system"""

    __tablename__ = "users"

    # Added ForeignKey to user_id
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    
    
    
    # Added this line
    # backref is a relationship that allows you to access the user from the article
    articles = db.relationship("Article", back_populates="user")
    
    # Added this line
    
    # like = db.relationship("Likes", back_populates="user")

    # Added this line
    # likes = db.relationship("Like", backref="user")
    
    
    # likes = db.relationship("Like", back_populates="user")
    # likes = db.relationship('User', secondary='likes')

    @classmethod
    def signup(cls, first_name, last_name, email, username, pwd):
        """Signup user w/hashed password & return user"""

        hashed = bcrypt.generate_password_hash(pwd)

        hashed_utf8 = hashed.decode("utf8")

        user = User(first_name=first_name, last_name=last_name, email=email, username=username, password=hashed_utf8)
        # return cls(first_name=first_name, last_name=last_name, email=email, username=username, password=hashed_utf8)
        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists and password is correct.
        Return user if valid; else return false."""

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, pwd):
            return user
        else:
            return False


class LatestArticle(db.Model):
    """List latest articles from last 2 hours"""

    __tablename__ = "latest_articles"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.Text, nullable=False, unique=False)
    publishedAt = db.Column(db.DateTime, nullable=False, unique=False, default=datetime.utcnow)
    domain = db.Column(db.Text, nullable=False, unique=False)
    article_id = db.Column(db.Integer, nullable=False)
    site_type = db.Column(db.Text, nullable=False)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    urlToImage = db.Column(db.Text)
    content = db.Column(db.Text)

    def __repr__(self):
        latest_article = self
        return f"<Latest Article {latest_article.id} {latest_article.url} {latest_article.publishedAt} {latest_article.domain} {latest_article.article_id} {latest_article.site_type} {latest_article.title} {latest_article.urlToImage}{latest_article.content}>"


class TopArticle(db.Model):
    """List top article from past 30 days"""

    __tablename__ = "top_articles"
    """ __searchable__ = "top_articles" """

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, nullable=False, unique=False)
    publishedAt = db.Column(db.DateTime, nullable=False, unique=False, default=datetime.utcnow)
    site_type = db.Column(db.Text, nullable=False, unique=False)
    title = db.Column(db.Text, nullable=False, unique=False)
    description = db.Column(db.Text)
    title = db.Column(db.Text)
    urlToImage = db.Column(db.Text)
    content = db.Column(db.Text)

    def __repr__(self):
        top_article = self
        return f"<Top Article {top_article.id} {top_article.description} {top_article.title} {top_article.url} {top_article.publishedAt} {top_article.site_type} {top_article.title} {top_article.urlToImage}{top_article.content}>"

class WorldNews(db.Model):
    """ List World news articles -- from NewsAPI"""
    
    __tablename__ = "world_news"

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, nullable=False, unique=False)
    author = db.Column(db.Text, nullable=False, unique=False)
    publishedAt = db.Column(db.DateTime, nullable=False,
                            unique=False, default=datetime.utcnow)
    title = db.Column(db.Text, nullable=False, unique=False)
    description = db.Column(db.Text)
    urlToImage= db.Column(db.Text)
    content = db.Column(db.Text)
    
    def __repr__(self):
        world_new = self
        return f"<World New {world_new.id} {world_new.url}{world_new.author}{world_new.publishedAt}{world_new.title}{world_new.description}{world_new.urlToImage}{world_new.content}>"
    
    # def __repr__(self):
    #     return f'<World News {self.id} {self.url} {self.author} {self.publishedAt} {self.title} {self.description} {self.urlToImage} {self.content}>'
    


class Technology(db.Model):
    """List tech news -- from NewsAPI"""
    
    __tablename__ = "tech_news"
    
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, nullable=False, unique=False)
    author = db.Column(db.Text, nullable=False, unique=False)
    publishedAt = db.Column(db.DateTime, nullable=False,
                            unique=False, default=datetime.utcnow)
    title = db.Column(db.Text, nullable=False, unique=False)
    description = db.Column(db.Text)
    urlToImage = db.Column(db.Text)
    content = db.Column(db.Text)
    
    def __repr__(self):
        technology_article = self
        return f"<Technology Article {technology_article.id}{technology_article.url}{technology_article.author}{technology_article.publishedAt}{technology_article.title}{technology_article.description}{technology_article.urlToImage}{technology_article.content}"
class Business(db.Model):
    """List latest business News"""
    
    __tablename__ = "business_news"
    
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, nullable=False, unique=False)
    author = db.Column(db.Text, nullable=False, unique=False)
    publishedAt = db.Column(db.DateTime, nullable=False,
                            unique=False, default=datetime.utcnow)
    title = db.Column(db.Text, nullable=False, unique=False)
    description = db.Column(db.Text)
    urlToImage = db.Column(db.Text)
    content = db.Column(db.Text)
    
    def __repr__(self):
        business_article = self
        return f"<Business Article {business_article.id}{business_article.url}{business_article.author}{business_article.publishedAt}{business_article.title}{business_article.description}{business_article.urlToImage}{business_article.content}"
    
class USPolity(db.Model):
    """List political news from the U.S"""
    
    __tablename__ = "us_news"
    
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, nullable=False, unique=False)
    author = db.Column(db.Text, nullable=False, unique=False)
    publishedAt = db.Column(db.DateTime, nullable=False,
                            unique=False, default=datetime.utcnow)
    title = db.Column(db.Text, nullable=False, unique=False)
    description = db.Column(db.Text)
    urlToImage = db.Column(db.Text)
    content = db.Column(db.Text)
    
    def __repr__(self):
        us_pol = self
        return f"<U.S Politics {us_pol.id}{us_pol.url}{us_pol.author}{us_pol.publishedAt}{us_pol.title}{us_pol.description}{us_pol.urlToImage}{us_pol.content}"
    
class Science(db.Model):
    """List latest science news"""
    
    __tablename__ = "science_news"
    
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, nullable=False, unique=False)
    author = db.Column(db.Text, nullable=False, unique=False)
    publishedAt = db.Column(db.DateTime, nullable=False,
                            unique=False, default=datetime.utcnow)
    title = db.Column(db.Text, nullable=False, unique=False)
    description = db.Column(db.Text)
    urlToImage = db.Column(db.Text)
    content = db.Column(db.String(500))
    
    def __repr__(self):
        science_article = self
        return f"<Science Article {science_article.id}{science_article.url}{science_article.author}{science_article.publishedAt}{science_article.title}{science_article.description}{science_article.urlToImage}{science_article.content}"
    
class Health(db.Model):
    """List latest health news"""
    
    __tablename__ = "health_news"
    
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, nullable=False, unique=False)
    author = db.Column(db.Text, nullable=False, unique=False)
    publishedAt = db.Column(db.DateTime, nullable=False,
                            unique=False, default=datetime.utcnow)
    title = db.Column(db.Text, nullable=False, unique=False)
    description = db.Column(db.Text)
    urlToImage = db.Column(db.Text)
    content = db.Column(db.String(500))

    def __repr__(self):
        health_article = self
        return f"<Health Article {health_article.id}{health_article.url}{health_article.author}{health_article.publishedAt}{health_article.title}{health_article.description}{health_article.urlToImage}{health_article.content}"
class Sports(db.Model):
    """List sports news"""
    
    __tablename__ = "sports_news"
    
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, nullable=False, unique=False)
    author = db.Column(db.Text, nullable=False, unique=False)
    publishedAt = db.Column(db.DateTime, nullable=False,
                            unique=False, default=datetime.utcnow)
    title = db.Column(db.Text, nullable=False, unique=False)
    description = db.Column(db.Text)
    urlToImage = db.Column(db.Text)
    content = db.Column(db.String(500))
    
    def __repr__(self):
        sports_article = self
        return f"<Sports Article {sports_article.id}{sports_article.url}{sports_article.author}{sports_article.publishedAt}{sports_article.title}{sports_article.description}{sports_article.urlToImage}{sports_article.content}"
class Article(db.Model):
    
    __tablename__= "articles"
    
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text,  unique=True)
    author = db.Column(db.Text, unique=False)
    publishedAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    title = db.Column(db.Text, nullable=True, unique=False)
    description = db.Column(db.Text)
    urlToImage = db.Column(db.Text)
    content = db.Column(db.String(500))
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Added lines below to create a relationship to the User table
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"))
    article_id = db.Column(db.Integer, db.ForeignKey("articles.id", ondelete="cascade"))
    user = db.relationship("User", back_populates="articles")
    
    # like_id = db.Column(db.Integer, db.ForeignKey("likes.id"))
    # likes = db.relationship("Article", back_populates="likes")
    
    def __repr__(self):
        articles = self
        return f"<Article {articles.id}{articles.url}{articles.author}{articles.publishedAt}{articles.title}{articles.description}{articles.urlToImage}{articles.content}{articles.date_added}{articles.user_id}{articles.article_id}"



class Likes(db.Model):
    """Mapping user likes to article"""
    
    __tablename__ = "likes"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    article_id = db.Column(db.Integer, db.ForeignKey(
        "articles.id", ondelete="cascade"), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"))
 
    # article = db.relationship("Article", backref="like", lazy="select")
    # join condition with foreign key between  likes and articles
    # article = db.Column(db.Integer, db.ForeignKey("articles.id", ondelete="cascade"))
    
    # user = db.relationship("User", back_populates="likes")
   
    
    # article = db.relationship("Article", backref="like_id")
    
    # art_id = db.Column(db.Integer, db.ForeignKey("likes.id"), unique=True)
    
    
    # like_id = db.Column(db.Integer, db.ForeignKey("likes.id", ondelete="cascade"), unique=True)

    # article_id = db.relationship("Article", backref="likes")

    def __repr__(self):
        like = self
        return f"<Likes {like.id}{like.user_id}{like.article_id}"
    
    # def likes(self):
    #     """Show likes method"""
    #     return Like.query.filter_by(article_id=self.id).all()
    




