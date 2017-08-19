from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, HiddenField
from wtforms.validators import DataRequired, NoneOf

from models import Category

class NewProduct(FlaskForm):
    name = StringField('product-name', validators=[DataRequired()])
    description = TextAreaField('product-description', validators=[DataRequired()])
    category_id = SelectField('category', default=0, coerce=int, validators=[DataRequired(), NoneOf([0], message='Select a category')])

    def set_choices(self):
        # Set default choice first...
        self.category_id.choices = [(0, '')]

        # Then append all available categories as choices
        self.category_id.choices += [(category.id, category.name) for category in Category.query.all()]


class NewCategory(FlaskForm):
    name = StringField('Category name', validators=[DataRequired()])
    # image_url = StringField('Image URL')
