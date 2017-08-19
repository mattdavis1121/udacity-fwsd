class Movie(object):
    """
    A class which defines movies

        Args:
            title (string) : the title of the movie
            poster_image_url (string) : a url (often shortened) pointing to the movie's box art
            trailer_youtube_url (string) : a youtube url pointing to the movie's trailer

    """

    def __init__(self, title, poster_image_url, trailer_youtube_url):
        self.title = title
        self.poster_image_url = poster_image_url
        self.trailer_youtube_url = trailer_youtube_url
