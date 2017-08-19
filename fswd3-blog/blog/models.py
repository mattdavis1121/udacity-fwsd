from google.appengine.ext import ndb

from security import make_pw_hash

class BlogPost(ndb.Model):
    text = ndb.TextProperty(required=True)
    date = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def all_by_user(cls, user):
        return cls.query(ancestor=user.key).fetch()

    @classmethod
    def by_id(cls, post_id):
        try:
            post = cls.get_by_id(int(post_id))
        except ValueError:
            post = None
        return post

    @classmethod
    def by_urlsafe_key(cls, safekey):
        return ndb.Key(urlsafe=safekey).get()

    @classmethod
    def new_by_user(cls, user):
        return BlogPost(parent=user.key)

    def is_by_user(self, user):
        if not user:
            return False
        return self.key.parent() == user.key

    def get_author(self):
        return self.key.parent().get()

    def comment(self, user, text):
        comment = Comment(parent=self.key, user=user.key, text=text)
        comment.put()

    def get_likes(self):
        likes = Like.query(ancestor=self.key).fetch()
        return sum([like.like_type for like in likes])

    def get_comments(self):
        return Comment.query(ancestor=self.key).order(-Comment.date).fetch()

    def liked_by_user(self, user):
        if not user:
            return False
        likes = Like.query(ancestor=self.key).fetch()
        users = [like.user.get() for like in likes]
        if user in users:
            return True
        else:
            return False


class User(ndb.Model):
    name = ndb.StringProperty(required=True)
    pw_hash = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    signup_date = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def register(cls, name, pw, email=None):
        pw_hash = make_pw_hash(name, pw)
        return User(name=name, pw_hash=pw_hash, email=email)

    @classmethod
    def login(cls, name, pw):
        user = cls.by_name(name)
        if user and valid_pw(name, pw, user.pw_hash):
            return user

    @classmethod
    def by_id(cls, uid):
        return cls.get_by_id(uid)

    @classmethod
    def by_name(cls, name):
        return cls.query(cls.name == name).get()

    @classmethod
    def exists(cls, name):
        return True if cls.by_name(name) else False

    def like_post(self, post):
        like = Like(parent=post.key, user=self.key, like_type=1)
        like.put()

    def dislike_post(self, post):
        like = Like(parent=post.key, user=self.key, like_type=-1)
        like.put()

class Like(ndb.Model):
    user = ndb.KeyProperty(required=True, kind=User)
    like_type = ndb.IntegerProperty(required=True, choices=[-1,1])   # -1 for dislike, 1 for like
    date = ndb.DateTimeProperty(auto_now_add=True)

class Comment(ndb.Model):
    user = ndb.KeyProperty(required=True, kind=User)
    text = ndb.StringProperty(required=True)
    date = ndb.DateTimeProperty(auto_now_add=True)

    def get_author(self):
        return self.user.get()

    @classmethod
    def by_urlsafe_key(cls, safekey):
        return ndb.Key(urlsafe=safekey).get()

    def is_by_user(self, user):
        if not user:
            return False

        return self.user == user.key

    def delete(self):
        self.key.delete()
