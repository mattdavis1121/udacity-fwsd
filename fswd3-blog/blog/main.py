import os

import webapp2
import jinja2

from security import *
from helpers import *
from models import *

from google.appengine.ext import ndb


# Jinja configs
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)
jinja_env.filters['blogpost_datetime_format'] = blogpost_datetime_format

# Begin Handlers
class Handler(webapp2.RequestHandler):
    def write(self, *args, **kwargs):
        self.response.out.write(*args, **kwargs)

    def render_str(self, template, **params):
        params['user'] = self.user
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kwargs):
        self.write(self.render_str(template, **kwargs))

    def set_secure_cookie(self, name, value):
        cookie_val = make_secure_val(value)
        self.response.headers.add_header('Set-Cookie', '{}={}; Path=/'.format(name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key.id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

class TestPage(Handler):
    def get(self):
        self.render('test.html', data=self.request.path)

class FrontPage(Handler):
    def get(self):
        blog_posts = BlogPost.query().order(-BlogPost.date).fetch()
        self.render('index.html', posts=blog_posts, title='Blog')

class NewPost(Handler):
    def get(self):
        if self.user:
            self.render('new_blog_post_form.html', post=None)
        else:
            return self.redirect('/blog/login')

    def post(self):
        if not self.user:
            return self.redirect('/blog/login')
        submission = self.request.get('submission')
        post_key = self.request.get('post_key')
        post = BlogPost.new_by_user(self.user)
        post.text=submission
        post.put()
        return self.redirect('/blog')

class EditPost(Handler):
    def get(self, post_key):
        post = BlogPost.by_urlsafe_key(post_key)
        self.render('new_blog_post_form.html', post=post)

    def post(self, post_key):
        submission = self.request.get('submission')
        form_post_key = self.request.get('post_key')
        post = BlogPost.by_urlsafe_key(post_key)

        # Short circuit if no user logged in or if logged
        # the post to be edited is not authored by logged in user
        if not self.user or not post.is_by_user(self.user):
            return self.redirect('/blog/login')

        post.text = submission
        post.put()
        return self.redirect('/blog')


class BlogPostPage(Handler):
    def get(self, post_key):
        post = BlogPost.by_urlsafe_key(post_key)
        if post:
            self.render("blog_post.html", post=post)
        else:
            return self.redirect('/blog')

    def post(self, post_key):
        # Handle likes
        form_post_key = self.request.get('post_key')
        post = BlogPost.by_urlsafe_key(form_post_key)
        if not self.user or post.liked_by_user(self.user) or post.is_by_user(self.user):
            return self.redirect('/blog/login')

        like_val = self.request.get('like-val') # Will always be 1 or -1
        if like_val == '1':
            self.user.like_post(post)
        elif like_val == '-1':
            self.user.dislike_post(post)

        self.render("blog_post.html", post=post)

class SignupPage(Handler):
    def get(self):
        self.render('signup_form.html', title='Sign Up')

    def post(self):
        error = False
        request_data_dict = {arg: self.request.get(arg) for arg in self.request.arguments()}
        username = request_data_dict['username']
        password = request_data_dict['password']
        verify = request_data_dict['verify-password']
        email = request_data_dict['email']

        params = {'username': username, 'email': email}

        if User.exists(username):
            params['error_username'] = "This username is already in use"
            error = True

        if not valid_username(username):
            params['error_username'] = "That's not a valid username"
            error = True

        if not valid_password(password):
            params['error_password'] = "That's not a valid password"
            error = True
        elif password != verify:
            params['error_verify'] = "Passwords do not match"
            error = True

        if not valid_email(email):
            params['error_email'] = "That's not a valid email"
            error = True

        if error:
            self.render('signup_form.html', title='Sign Up', **params)
        else:
            # Create new record in User table
            user = User.register(username, password, email)
            user.put()

            # Send back a header and redirect
            self.login(user)
            return self.redirect('/blog/welcome')


class RedirectToFrontPage(Handler):
    def get(self):
        return self.redirect('/blog')

class WelcomePage(Handler):
    def get(self):
        if self.user:
            self.render('welcome.html')
        else:
            return self.redirect('/blog/signup')

class LoginPage(Handler):
    def get(self):
        self.render('login_form.html')

    def post(self):
        error = False
        request_data_dict = {arg: self.request.get(arg) for arg in self.request.arguments()}
        username = request_data_dict['username']
        password = request_data_dict['password']

        user = User.by_name(username)

        params = {'username': username}

        if not user:
            params['error'] = "Invalid login"
            error = True
        elif not valid_pw(username, password, user.pw_hash):
            params['error'] = "Invalid login"
            error = True

        if error:
            self.render('login_form.html', title='Log In', **params)
        else:
            # Send back a header and redirect
            self.login(user)
            return self.redirect('/blog/welcome')

class LogoutPage(Handler):
    def get(self):
        if self.user:
            self.logout()
        return self.redirect('/blog/signup')

class DeletePost(Handler):
    def get(self, post_key):
        if not self.user:
            return self.redirect('/blog')
        post = BlogPost.by_urlsafe_key(post_key)
        if post and post.is_by_user(self.user):
            post.key.delete()
        self.redirect('/blog')


class Unimplemented(Handler):
    def get(self):
        self.render('unimplemented.html')

class EditComment(Handler):
    def post(self):
        comment_key = self.request.get('comment_key')
        edit_text = self.request.get('edit')
        comment = Comment.by_urlsafe_key(comment_key)

        if not self.user or not comment.is_by_user(self.user):
            return self.redirect('/blog/login')

        comment.text = edit_text
        comment.put()
        return self.redirect(self.request.referrer)

class DeleteComment(Handler):
    def post(self):
        comment_key = self.request.get('comment_key')
        comment = Comment.by_urlsafe_key(comment_key)

        if not self.user or not comment.is_by_user(self.user):
            return self.redirect('/blog/login')

        comment.delete()
        return self.redirect(self.request.referrer)


class NewComment(Handler):
    def post(self):
        if not self.user:
            return self.redirect('/blog/login')
        post = BlogPost.by_urlsafe_key(self.request.get('post_key'))
        comment_text = self.request.get('comment')
        comment = post.comment(self.user, comment_text)
        return self.redirect(self.request.referrer)



app = webapp2.WSGIApplication([
    ('/blog', FrontPage),
    ('/test', TestPage),
    ('/blog/newpost', NewPost),
    ('/blog/signup', SignupPage),
    ('/', RedirectToFrontPage),
    ('/blog/login', LoginPage),
    ('/blog/welcome', WelcomePage),
    ('/blog/logout', LogoutPage),
    ('/blog/account', Unimplemented),
    ('/blog/editcomment', EditComment),
    ('/blog/deletecomment', DeleteComment),
    ('/blog/newcomment', NewComment),
    webapp2.Route('/blog/deletepost/<post_key>', handler=DeletePost),
    webapp2.Route('/blog/edit/<post_key>', handler=EditPost),
    webapp2.Route('/blog/<post_key>', handler=BlogPostPage)
], debug=True)
