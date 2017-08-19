from flask import Flask, render_template, request, redirect, flash, url_for
from flask_login import login_required, login_user, logout_user, current_user
from oauth2client import client, crypt

# This line imports our instance of Flask() which is
# created in /app/__init__.py
from app import app, db, login_manager
from models import *
from forms import *

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

###
#   Begin Category CRUD
###

@app.route('/', methods=('GET', 'POST'))
def index():
    categories = Category.query.all()
    user = current_user
    return render_template('index.html', categories=categories)

@app.route('/new-category/', methods=('GET', 'POST'))
@login_required
def new_category():
    form = NewCategory()
    if form.validate_on_submit():
        category = Category(form.name.data)
        db.session.add(category)
        db.session.commit()
        return redirect('/')
    return render_template('new-category.html', form=form)

@app.route('/edit-category/<category_id>', methods=('GET', 'POST'))
@login_required
def edit_category(category_id):
    category = Category.query.filter_by(id=category_id).first()
    form = NewCategory(obj=category)

    if form.validate_on_submit():
        form.populate_obj(category)
        db.session.add(category)
        db.session.commit()
        return redirect('/')

    return render_template('new-category.html', form=form)

@app.route('/delete-category/<category_id>')
@login_required
def delete_category(category_id):
    category = Category.query.filter_by(id=category_id).first()
    db.session.delete(category)
    db.session.commit()
    return redirect('/')

###
#   Begin Product CRUD
###

@app.route('/products/')
def show_all_products():
    products = Product.query.all()
    return render_template('products.html', products=products)

@app.route('/products/<category_name>/')
def show_category_products(category_name):
    cat = Category.query.filter_by(name=category_name).first()
    products = cat.get_products()
    return render_template('products.html', products=products)

@app.route('/new-product/', methods=('GET', 'POST'))
@login_required
def new_product():
    form = NewProduct()
    form.set_choices()

    if form.validate_on_submit():
        product = Product(form.name.data, form.description.data, form.category_id.data)
        db.session.add(product)
        db.session.commit()
        return redirect('/products/')
    else:
        flash_errors(form)
    return render_template('new-product.html', form=form)

@app.route('/edit-product/<product_id>', methods=('GET', 'POST'))
@login_required
def edit_product(product_id):
    product = Product.query.filter_by(id=product_id).first()
    form = NewProduct(obj=product)
    form.set_choices()

    if form.validate_on_submit():
        form.populate_obj(product)
        db.session.add(product)
        db.session.commit()
        return redirect('/products/')

    return render_template('new-product.html', form=form)

@app.route('/delete-product/<product_id>')
@login_required
def delete_product(product_id):
    product = Product.query.filter_by(id=product_id).first()
    db.session.delete(product)
    db.session.commit()
    return redirect('/')

@app.route('/login/', methods=('POST',))
def login():
    if not current_user.is_anonymous:
        return redirect(url_for('index'))

    token = request.form['idtoken']
    name = request.form['name']
    email = request.form['email']
    id = request.form['id']
    verify = google_verify_id_token(token)
    if id == verify:
        user = User.query.get(id)

        # If user doesn't exist, register in DB
        if not user:
            user = User(id, name, email)
            db.session.add(user)
            db.session.commit()

        login_user(user)
        return "signed in"
    else:
        return "failed sign in"

@app.route('/logout/', methods=('GET', 'POST'))
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


###
#   Begin API routes
###

def to_json(data, encoder=CatalogEncoder):
    if request.args.get('format'):
        return "<pre>{}</pre>".format(json.dumps(data, cls=encoder, sort_keys=True, indent=4))
    else:
        return json.dumps(data, cls=encoder)

@app.route('/api/all/')
def api_all():
    categories = Category.query.all()
    return to_json(categories)

@app.route('/api/categories/')
def api_categories():
    category_name = request.args.get('name')
    category_id = request.args.get('id')

    # Try lookup by name first, then fall back to ID
    if category_name:
        category = Category.query.filter_by(name=category_name).first()
        if not category:
            return "ERROR - Invalid category name. Use '/api/all' to get a complete list of data."
    elif category_id:
        category = Category.query.filter_by(id=category_id).first()
        if not category:
            return "ERROR - Invalid category ID. Use '/api/all' to get a complete list of data."
    else:
        # Don't call to_json because this is the only time when we'll use
        # a different encoder
        categories = Category.query.all()
        return to_json(categories, encoder=CategoryEncoder)

    return to_json(category)

@app.route('/api/products/')
def api_products():
    product_name = request.args.get('name')
    product_id = request.args.get('id')

    if product_name:
        product = Product.query.filter_by(name=product_name).first()
        if not product:
            return "ERROR - Invalid product name. Use '/api/products/' to get a complete list of products."
    elif product_id:
        product = Product.query.filter_by(id=product_id).first()
        if not product:
            return "ERROR - Invalid product ID. Use '/api/products/' to get a complete list of products."
    else:
        products = Product.query.all()
        return to_json(products, encoder=ProductEncoder)

    return to_json(product)

def google_verify_id_token(token):
    try:
        idinfo = client.verify_id_token(token, '339770546927-sfpsv2j6bv98vpj52b5hc856l23fn1ah.apps.googleusercontent.com')

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise crypt.AppIdentityError("Wrong issuer.")

    except crypt.AppIdentityError:
        # Invalid token
        pass
    userid = idinfo['sub']
    return userid
