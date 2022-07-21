from app import app

from flask import redirect
from app import app, delete_user 
from unittest import TestCase
from models import User, db

app.config['TESTING'] = True
app.config['DEBUG'] = False
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']



class TestApp(TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True   
        
        
    def test_homepage(self):
        result = self.app.get('/')
        html = result.get_data(as_text=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn('article', html)     
        
    def test_homepage_status_code(self):
        result = self.app.get('/')
        html = result.get_data(as_text=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn('article', html)
        
    def test_nav_links(self):
        result = self.app.get('/latest_articles')
        html = result.get_data(as_text=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn('Latest Articles', html)

    def test_signup_page(self):
        result = self.app.get('/signup')
        html = result.get_data(as_text=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn('signup', html)
        
    def test_login_page(self):
        result = self.app.get('/login')
        html = result.get_data(as_text=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn('login', html)
        
    def test_favorites_page(self):
        result = self.app.get('/users/favorites')
        html = result.get_data(as_text=True)
        self.assertIn('/users/favorites', html)

    def test_profile_page(self):
        result = self.app.get('/users/1')
        html = result.get_data(as_text=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn('profile', html)
        
    # def test_add_like(self):
    #     res = self.app.post('/users/favorites/', data={'id': 1})
    #     html = res.get_data(as_text=True)
    #     self.assertEqual(res.status_code, 302)
    #     self.assertIn('/users/1', html)
    
 
  
    

  

    


 



        