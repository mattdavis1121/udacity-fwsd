from app import db
from app.models import *

db.create_all()

# Add categories
guitars = Category(name='Guitars')
candy_bars = Category(name='Candy Bars')
db.session.add(guitars)
db.session.add(candy_bars)
db.session.commit()

# Add products
# (All descriptions from Wikipedia)
les_paul = Product(name='Gibson Les Paul',
                  description=('A solid body electric guitar that was first '
                               'sold by the Gibson Guitar Corporation in 1952. '
                               'The Les Paul was designed by Gibson president '
                               'Ted McCarty, factory manager John Huis and '
                               'their team, along with guitarist/inventor '
                               'Les Paul.'),
                  category_id=guitars.id)
strat = Product(name='Fender Stratocaster',
               description=('A model of electric guitar designed in 1954 by '
                            'Leo Fender, Bill Carson, George Fullerton, and '
                            'Freddie Tavares. It is a double-cutaway guitar, '
                            'with an extended top "horn" shape for balance.'),
               category_id=guitars.id)
tele = Product(name='Fender Telecaster',
              description=('The first commercially successful solid-body '
                           'electric guitar. Its simple yet effective design '
                           'and revolutionary sound broke ground and set '
                           'trends in electric guitar manufacturing and '
                           'popular music.'),
              category_id=guitars.id)
snickers = Product(name='Snickers',
                   description=('Snickers is a brand name chocolate bar made by '
                                'the American company Mars, Incorporated. '
                                'Consisting of nougat topped with caramel and '
                                'peanuts, enrobed in milk chocolate, Snickers has '
                                'annual global sales of $2 billion.'),
                   category_id=candy_bars.id)
hershey = Product(name='Hershey Bar',
                  description=('The Hershey Milk Chocolate Bar (commonly '
                               'called the Hershey Bar) is the flagship '
                               'chocolate bar manufactured by the Hershey '
                               'Company. It is often referred by Hershey as '
                               '"The Great American Chocolate Bar." The '
                               'Hershey Milk Chocolate Bar was first sold in '
                               '1900, followed by the Hershey Milk Chocolate '
                               'with Almonds variety, which began production '
                               'in 1908. Circular candies made of Hershey milk '
                               'chocolate, called Hershey Drops, were released '
                               'in 2010.'),
                  category_id=candy_bars.id)
twix = Product(name='Twix',
               description=('Twix is a chocolate bar made by Mars, Inc., '
                            'consisting of biscuit applied with other '
                            'confectionery toppings and coatings (most '
                            'frequently caramel and milk chocolate). Twix bars '
                            'are packaged with two or four bars in a package. '
                            'Miniature and bite-size Twix are also available.'),
               category_id=candy_bars.id)
candy_bars.products.append(snickers)
candy_bars.products.append(hershey)
candy_bars.products.append(twix)
guitars.products.append(les_paul)
guitars.products.append(strat)
guitars.products.append(tele)
db.session.add(guitars)
db.session.add(candy_bars)
db.session.commit()
