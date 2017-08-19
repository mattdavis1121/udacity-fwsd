import fresh_tomatoes
from media import Movie

# Generate instances of Movie()
toy_story = Movie('Toy Story', 'https://goo.gl/r5uzXR', 'https://youtu.be/KYz2wyBy3kc')
wall_e = Movie('WALL-E', 'https://goo.gl/ksQXAS ', 'https://www.youtube.com/watch?v=ZisWjdjs-gM')
up = Movie('Up', 'https://goo.gl/yqpWVU', 'https://www.youtube.com/watch?v=ORFWdXl_zJ4')

# Store all instances of Movie in a list
movies = [toy_story, wall_e, up]

# Open movies page
fresh_tomatoes.open_movies_page(movies)