import json

from app import db

class CatalogModel(db.Model):
    # This line tells SQLAlchemy to not create a table from this model
    __abstract__ = True

    created_on = db.Column(db.DateTime, default=db.func.now())
    updated_on = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    @classmethod
    def count(cls):
        return len(cls.query.all())

class Product(CatalogModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    description = db.Column(db.Text)

    # Relationship to Category
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', cascade='all, delete-oprphan',
                                backref=db.backref('products', lazy='dynamic'))

    # Relationship to User
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # user = db.relationship('User', backref=dbbackref('user', lazy='dynamic'))

    def __init__(self, name, description, category_id):
        self.name = name
        self.description = description
        self.category_id = category_id
        # self.user_id = user_id

    def __repr__(self):
        return "{}: {}".format(self.name, self.description)

class Category(CatalogModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    # image_url = db.Column(db.String(300))

    # Relationship to User
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # user = db.relationship('User', backref=dbbackref('user', lazy='dynamic'))

    def __init__(self, name):
        self.name = name
        # self.user_id = user_id

    def __repr__(self):
        return "{} - {} products".format(self.name, len(self.products.all()))

    def get_products_count_string(self):
        count = len(self.products.all())
        if count == 1:
            return "1 product"
        else:
            return "{} products".format(count)

    def get_products(self):
        return self.products.all()

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

class User(CatalogModel):
    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, nullable=True)

    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email

    def to_json(self):
        return json.dumps({'id': self.id,
                           'name': self.name,
                           'email': self.email})

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    # @classmethod
    # def get(cls, user_id):
    #     return cls.query.get(user_id)

class CatalogEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Category):
            return {'id': obj.id, 'name': obj.name, 'products': obj.products.all()}
        if isinstance(obj, Product):
            return {'id': obj.id, 'name': obj.name, 'description': obj.description}
        return json.JSONEncoder.default(self, obj)

class CategoryEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Category):
            return {'id': obj.id, 'name': obj.name}
        return json.JSONEncoder.default(self, obj)

class ProductEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Product):
            return {'id': obj.id, 'name': obj.name, 'category': obj.category.name}
        return json.JSONEncoder.default(self, obj)
