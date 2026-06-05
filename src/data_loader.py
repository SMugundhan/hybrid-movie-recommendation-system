import pandas as pd

def load_data ():

    ratings_cols = [ 'user_id', 'movie_id', 'rating', 'timestamp' ]

    ratings = pd.read_csv ( './data/ml-100k/u.data', sep = '\t', names = ratings_cols )

    movie_cols = [
        'movie_id',
        'title',
        'release_date',
        'video_release',
        'IMDb_URL',
        'unknown',
        'Action',
        'Adventure',
        'Animation',
        'Children',
        'Comedy',
        'Crime',
        'Documentary',
        'Drama',
        'Fantasy',
        'Film_Noir',
        'Horror',
        'Musical',
        'Mystery',
        'Romance',
        'SciFi',
        'Thriller',
        'War',
        'Western'
    ]

    movies = pd.read_csv ( './data/ml-100k/u.item', sep = '|', encoding = 'latin-1', header = None, names = movie_cols )

    df = pd.merge ( ratings, movies, on = 'movie_id' )

    return ratings, movies, df