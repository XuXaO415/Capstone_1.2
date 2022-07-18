import os

##############################################################################

# from flask import *
from flask import Flask, get_flashed_messages, jsonify, redirect, render_template, flash, session, g, url_for
from datetime import datetime
from flask_login import current_user, LoginManager, login_user, login_required, logout_user, user_logged_in
import requests
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from flask_debugtoolbar import DebugToolbarExtension
from flask_bootstrap import Bootstrap

from newsapi import NewsApiClient


import pdb
#################################################################################
from forms import UserAddForm, LoginForm, UserEditForm
from flask_wtf import FlaskForm
from models import Article, db, connect_db, User, Article, Likes,  LatestArticle, TopArticle, WorldNews, Technology, Business, USPolity, Science, Health
#######################################ß##########################################
# from secrets import api_key
from dotenv import load_dotenv
load_dotenv()
#################################################################################

app = Flask(__name__)

bootstrap = Bootstrap(app)
moment = Moment(app)

CURR_USER_KEY = "curr_user"

app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ.get('DATABASE_URL', 'postgresql:///nea_db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('API_KEY', 'SECRET_KEY')


toolbar = DebugToolbarExtension(app)

connect_db(app)


##############################################################################
# Add user to g
##############################################################################

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

##############################################################################
# User login
##############################################################################

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id

##############################################################################
# User logout
##############################################################################
@app.route('/logout')
def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
        
        return redirect(url_for('login'))
     
##############################################################################
# Homepage
##############################################################################
@app.route("/", methods=["GET", "POST"])
def homepage():
    """Homepage"""
    API_SECRET_KEY = os.getenv('API_SECRET_KEY')

    res = requests.get(
        f"https://newsapi.org/v2/everything?q=latin-america&q=asia&q=europe&language=en&sortBy=popularity&pageSize=5&domains=apnews.com,reuters.com,npr.org,bbc.com,economist.com,wsj.com,politifact.com,thebureauinvestigates.com&apiKey={API_SECRET_KEY}")

  # avoid KeyError world_new when saving to db
    # pdb.set_trace()
    world_new = save_article(res)

    # world_new = world_new.get(res)
    
    res = requests.get(
        f"https://newsapi.org/v2/everything?q=top-news&language=en&sortBy=publishedAt&pageSize=5&domains=apnews.com,reuters.com,npr.org,economist.com,wsj.com,bbc.com,politifact.com,thebureauinvestigates.com&apiKey={API_SECRET_KEY}")

    latest_article = save_article(res)
    
    return render_template("index.html", world_news=world_new, latest_articles=latest_article)
    # return render_template("index.html", world_news=res, latest_articles=res)

##############################################################################
# User signup
##############################################################################

@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Handle user registration"""
    
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    
    form = UserAddForm()
    
    if form.validate_on_submit():
        try:
            user = User.signup(
                first_name = form.username.data,
                last_name = form.last_name.data,
                email = form.email.data,
                username = form.username.data,
                pwd = form.password.data,
                
            )
            db.session.add(user)
            db.session.commit()
            get_flashed_messages()
            flash("Successfully signed up!")
            
        except IntegrityError:
            flash("Sorry, that username is already taken", "error")
            return render_template("users/signup.html", form=form)
        
        do_login(user)
        return redirect('/')
    
    else:
        return render_template('/users/signup.html', form=form)
##############################################################################
# Login form
##############################################################################
        
@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login"""
        
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)
        
        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")
        
        flash("Invalid credentials.", "danger")
        
    return render_template('users/login.html', form=form)



##############################################################################
# User profile
##############################################################################
@app.route("/users/<int:user_id>")
def show_user_profile(user_id):

    user = User.query.get_or_404(user_id)

    return render_template('users/profile.html', user=user)


##############################################################################
# User profile edit form
##############################################################################
@app.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
def edit_user(user_id):
    """Edit user profile"""
    
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = g.user
    form = UserEditForm(obj=g.user)

        
    if form.validate_on_submit():
        if User.authenticate(form.username.data, form.email.data, form.password.data):

            user.username = form.username.data
            user.email = form.email.data
            user.password = form.password.data
        
            db.session.add(g.user)
            db.session.commit()   
           
            
            flash("Your profile has been updated.", "success")
            return redirect(f"/users/{g.user.id}")
        else: 
            flash("Incorrect password", "danger")
            return redirect(f"/users/{g.user.id}")
    else:
        return render_template("users/edit.html", form=form, user_id=user_id)
    
##############################################################################
# Delete User
##############################################################################
@app.route("/users/delete", methods=["POST"])
def delete_user():
    """Delete user"""
    
    
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    do_logout()
    flash (f"Your account has successfully been deleted", "success")
    
    db.session.delete(g.user)
    db.session.commit()
    return redirect("/signup")


##############################################################################
# User Favorite
##############################################################################
@app.route("/users/favorites/<int:likes_id>", methods=["GET", "POST"])
def add_likes(likes_id):
    """Enables a user to like an article"""

    if not g.user:
        flash("You are not the authorized user of this account", "danger")
        return redirect("/")

    if Likes.query.filter_by(user_id=g.user.id, article_id=likes_id).first():
        flash("You have already liked this article", "danger")
        return redirect("/")
    
    else:
        add_like = Likes(user_id=g.user.id, article_id=likes_id)
        db.session.add(add_like)
        db.session.commit()
        flash("You have successfully liked this article", "success")
        return redirect("/users/favorites/")
    
    
 
##############################################################################
# User Favorites
##############################################################################


@app.route("/users/favorites/", methods=["GET", "POST"])
def user_favorite():
    """Shows a list of user's liked articles"""


    # articles = Likes.query.filter_by(user_id=g.user.id).order_by(Likes.id.desc()).group_by(Likes.article_id).all()
    # print(Likes.id)
    
    articles = Likes.query.with_entities(Likes.article_id, Likes.user_id, Likes.id, Likes.timestamp,
                                         Likes.timestamp, Article.content, Article.title, Article.urlToImage, Article.description, Article.publishedAt, Article.author, Article.url,
                                         Article.date_added).filter_by(user_id=g.user.id).distinct().join(Article).order_by(Likes.id.desc()).all()
        
    likes = []
        
    for article in articles:
        like = Article.query.filter_by(id=article.article_id).first()
      
        likes.append(like)
        # likes.append(article.article_id)
      

    
    return render_template("/users/favorite.html", articles=articles)
            
    
    # article = (Likes
    #         .query
    #         .order_by(Likes.id)
    #         .order_by(Likes.user_id)
    #         .order_by(Likes.article_id)
    #         .order_by(Likes.timestamp.desc())
    #         .all())
    


    # # #likes query to get all likes and order by date_added desc, id
    # like = (Article
    #         .query
    #         .order_by(Article.id)
    #         .order_by(Article.user_id)
    #         .order_by(Article.like_id)
    #         .order_by(Article.content)
    #         .order_by(Article.date_added.desc())
    #         .order_by(Article.title)
    #         .order_by(Article.description)
    #         .all())
    

    
    # # like = Likes.query.all()
    
    # """List all liked articles"""
    # # like = (Likes
    # #          .query
    # #          .order_by(Likes.id)
    # #          .order_by(Likes.article_id)
    # #          .order_by(Likes.user_id)
    # #          .all())
    

    # return render_template("/users/favorite.html", articles=article, likes=like)

##############################################################################
# Delete favorite story
##############################################################################

@app.route("/users/delete/<int:likes_id>", methods=["GET", "POST"])
def delete_like(likes_id):
    """Current logged in user can delete their favorite story"""
        
    if not g.user:
        flash("You are not the authorized user of this account", "danger")
        return redirect("/")
    
    # delete_like = Likes.query.get_or_404(likes_id)
    # pdb.set_trace()
    
    # if Likes.query.filter_by(user_id=g.user.id, article_id=likes_id).first():
    
    if Likes.query.all():
        # delete_like = Likes.query.filter_by(user_id=g.user.id, article_id=likes_id).first()
        delete_like = Likes.query.filter_by(
            user_id=g.user.id, article_id=likes_id).first()
        db.session.delete(delete_like)
        db.session.commit()
        # pdb.set_trace()
        flash("You have successfully deleted this article", "success")
        return redirect("/users/favorites")
    
    else:
        return redirect("/")
   
    # remove_article = Article.query.filter_by(id=id).first()
    # remove_like = Article(user_id=g.user.id, article_id=id)

    
    # """remove from likes table article_id"""
 
    # remove_like = Like(user_id=g.user.id, article_id=like_id)
    # # pdb.set_trace()

    # # remove_article = Article.query.filter_by(id=id).first()
    # # delete_article = Like.query.filter_by(article_id=id).first()
    
    # db.session.delete(remove_like)
    # # db.session.delete(delete_article)
    # db.session.commit()
    
    # return redirect(f"/users/favorites")

##############################################################################
# Upon successful logout, redirects user to login page
##############################################################################

@app.route("/logout")
def logout():

    do_logout()
    flash("You have successfully logged out", "success")
    
    return redirect(url_for("login"))


##############################################################################
# Super simple 404 page
##############################################################################

@app.errorhandler(404)
def page_not_found(e):
    """404 Not Found"""
    return render_template("404.html"), 404

##############################################################################
# save_article function that saves the articles to the database
##############################################################################
def save_article(res):
    """Save article to database"""
    
    # pdb.set_trace()
    # if not g.user:
    #     flash("You are not the authorized user of this account", "danger")
    #     return redirect("/")
    
    
    # articles = res.json()['articles']

    # for article in articles:
    #     if existing_art := Article.query.filter_by(url=article['url']).first():
    #         article['id'] = existing_art.id

    #     else:
    #         new_art = Article(url=article['url'], author=article['author'],  title=article['title'],
    #                           description=article['description'], urlToImage=article['urlToImage'], content=article['content'])

    #         db.session.add(new_art)
    #         db.session.commit()

    #         article['id'] = new_art.id
    # return articles

    # articles = res.json()['articles']

    # for article in articles:
    #     existing_art = Article.query.filter_by(url=article['url']).first()
    #     if not existing_art:
    #         new_art = Article(url=article['url'], author=article['author'],  title=article['title'],
    #                           description=article['description'], urlToImage=article['urlToImage'], content=article['content'])

    #         db.session.add(new_art)
    #         db.session.commit()

    #         article['id'] = new_art.id
    #     else:
    #         article['id'] = existing_art.id

    # return articles
    
    articles = res.json()['articles']

    for article in articles:
        try:
            if existing_art := Article.query.filter_by(url=article['url']).first():
                article['id'] = existing_art.id
                print(dir(existing_art))

            else:
                new_art = Article(url=article['url'], author=article['author'],  title=article['title'],
                                  description=article['description'], urlToImage=article['urlToImage'], content=article['content'])

                db.session.add(new_art)
                db.session.commit()

                article['id'] = new_art.id
        except Exception as e:
            print(e)
    return articles


##############################################################################

# def save_article(res):
#     articles = res.json()['articles']
#     # save_article(res)
#     for article in res.json()['articles']:
#         # try:
#             if existing_art := Article.query.filter_by(url=article['url']).first():
#                 article['id'] = existing_art.id

#             else:
#                 new_art = Article(url=article['url'], author=article['author'],  title=article['title'],
#                                   description=article['description'], urlToImage=article['urlToImage'], content=article['content'])

#                 db.session.add(new_art)
#                 db.session.commit()

#                 article['id'] = new_art.id
#         # except KeyError as e:
#         # except NameError as e:
#         # except TypeError as e:
 
#             # print(e)
#             return articles
#         # return res.json()['articles']

    
    

##############################################################################
# Homepage quick link that displays latest news
##############################################################################
@app.route("/latest_articles", methods =["GET", "POST"])
def show_latest_articles():
    """Shows a list of latest articles from API"""
    
 
    API_SECRET_KEY = os.getenv('API_SECRET_KEY')
    
    url = ('https://newsapi.org/v2/top-headlines?' 'language=en' 'qinTitle=query' 'apiKey={API_SECRET_KEY}')
    res = requests.get(url)


    res = requests.get(
        f"https://newsapi.org/v2/top-headlines?category=general&country=us&pageSize=10&apiKey={API_SECRET_KEY}")

    latest_article = save_article(res)

    # return render_template("latest_articles.html", latest_articles=latest_article)
    return render_template("latest_articles.html", articles=latest_article)
##############################################################################

@app.route("/world_news", methods=["GET", "POST"])
def show_world_news():
    """Show world news"""
    API_SECRET_KEY = os.getenv('API_SECRET_KEY')
    
    url = ('https://newsapi.org/v2/top-headlines?' 'language=en' 'qinTitle=query' 'pageSize=20' 'apiKey={API_SECRET_KEY}')
    res = requests.get(url)
    
    res = requests.get(
        f"https://newsapi.org/v2/top-headlines?q=international&language=en&pageSize=15&apiKey={API_SECRET_KEY}")
    
    # pdb.set_trace()
    world_new = save_article(res)
    
    return render_template("article_list.html", articles=world_new, title='World News')
##############################################################################
# Page link displays tech news
##############################################################################

@app.route("/technology", methods=["GET", "POST"])
def show_tech_news():
    """Show news related to technology"""
    API_SECRET_KEY = os.getenv('API_SECRET_KEY')
    res = requests.get(
        f"https://newsapi.org/v2/top-headlines?category=technology&country=us&pageSize=15&apiKey={API_SECRET_KEY}")
    
    tech_news = save_article(res)
    
    return render_template("article_list.html", articles=tech_news, title='Technology')
    
##############################################################################
# Page link that displays business news
##############################################################################
@app.route("/business", methods=["GET","POST"])
def show_business_news():
    """Show news related to business"""
    API_SECRET_KEY = os.getenv('API_SECRET_KEY')
    
    res = requests.get(
        f"https://newsapi.org/v2/top-headlines?category=business&country=us&pageSize=15&apiKey={API_SECRET_KEY}")
    
    business_news = save_article(res)
 
    return render_template("article_list.html", articles=business_news, title='Business')

##############################################################################
# Page link that displays US news
##############################################################################
@app.route("/us_news", methods=["GET", "POST"])
def show_us_news():
    """Show news related to U.S"""
    API_SECRET_KEY = os.getenv('API_SECRET_KEY')
    res = requests.get(
        f"https://newsapi.org/v2/top-headlines?country=us&pageSize=15&apiKey={API_SECRET_KEY}")
    
    national_news = save_article(res)
    
    return render_template("article_list.html", articles=national_news, title='U.S News')

##############################################################################
# Page link that displays science news
##############################################################################
@app.route("/science", methods=["GET", "POST"])
def show_science_news():
    """Show news related to science"""
    API_SECRET_KEY = os.getenv('API_SECRET_KEY')
    res = requests.get(
        f"https://newsapi.org/v2/top-headlines?category=science&country=us&pageSize=15&apiKey={API_SECRET_KEY}")
    
    science_news = save_article(res)

    return render_template("article_list.html", articles=science_news, title='Science')

##############################################################################
# Pag link that displays health news
##############################################################################
@app.route("/health", methods=["GET", "POST"])
def show_health_news():
    """Show news related to health"""
    API_SECRET_KEY = os.getenv('API_SECRET_KEY')
    res = requests.get(
        f"https://newsapi.org/v2/top-headlines?category=health&country=us&pageSize=15&apiKey={API_SECRET_KEY}")
    
    health_news = save_article(res)

    return render_template("article_list.html", articles=health_news, title='Health')
##############################################################################
# Search box for all news
##############################################################################
@app.route("/search", methods=["GET","POST"])
def search_all_articles():
    """Search for articles"""
   
    HOST = os.getenv('HOST')
    API_KEY = os.getenv('API_KEY')
    API_SECRET_KEY = os.getenv('API_SECRET_KEY')
    
    # pdb.set_trace()
    querystring = {
        "query": requests.args['q'], "sort_by": "relevant", "use_lucene_syntax": "true"}
  
    
    latestquery = {
        "query": requests.args['q'],  "sort_by": "recent", "use_lucene_syntax": "true"}
    
    # res = requests.get(
    #     "https://api.newsapi.org/v2/everything", params=querystring, headers={"X-Api-Key": API_SECRET_KEY})
    
    
    # querytitle = {
    #     "query": "+title:\"China Is Mining Bitcoin Underground: Report\"",
    #               "sort_by": "recent", "use_lucene_syntax": "true"}

    
    headers = {
        'x-rapidapi-host': HOST,
        'x-rapidapi-key': API_KEY
    }
    
    url = ('https://newsapi.org/v2/everything?'
           'qinTitle=query'
           'apiKey={API_SECRET_KEY}')

    relevant_response = requests.get("https://api-hoaxy.p.rapidapi.com/articles", headers=headers,
                            params=querystring)
    
    recent_response = requests.get("https://api-hoaxy.p.rapidapi.com/articles", headers=headers,
                            params=latestquery)
    
    response = requests.get(url)
    print(response.json())
    
    title_requests = response.json()['articles']
    print(title_requests)
    
    
    relevant_articles = relevant_response.json()
    rel_art = relevant_articles['articles'][0:10]
    
    recent_articles = recent_response.json()
    rec_art = recent_articles['articles'][0:10]

    
    for art in rel_art:
        res = requests.get(f"https://newsapi.org/v2/top-headlines?country=us&apiKey={API_SECRET_KEY}"
        # res = requests.get(f"https://newsapi.org/v2/everything?qinTitle=China Is Mining Bitcoin Underground: Report&apiKey={API_SECRET_KEY}"
                                    )
        print(res.json()['articles'][0]['description'])
        art['description'] = res.json()['articles'][0]['description']
        
        for art in rec_art:
            res = requests.get(f"https://newsapi.org/v2/top-headlines?country=us&apiKey={API_SECRET_KEY}"
            # res = requests.get(f"https://newsapi.org/v2/everything?qinTitle=China Is Mining Bitcoin Underground: Report&apiKey={API_SECRET_KEY}"
                                        )
            print(res.json()['articles'][0]['description'])
            art['description'] = res.json()['articles'][0]['description']
            
    return render_template("top_articles.html", articles=rel_art, title='Search Results', articles2=rec_art)


    
    # title_request = response.json()
    # print (response.text)

    # # return jsonify(top_articles)
   
    # return render_template("top_articles.html", top_articles=relevant_articles['articles'][0:10],
    #                        new_articles=recent_articles['articles'][0:10], titlequery=title_request)


    # return render_template("latest_articles.html", latest_articles=recent_articles['articles'][0:10], titlequery=title_request)
##############################################################################
@ app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req


##############################################################################
