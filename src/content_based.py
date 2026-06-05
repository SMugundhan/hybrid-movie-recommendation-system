from sklearn.feature_extraction.text import CountVectorizer

from sklearn.metrics.pairwise import cosine_similarity

import os

import joblib

import glob

def build_content_similarity ( movies ):

    genre_columns = movies.columns [ 5 : ]

    movies [ 'genres' ] = movies [ genre_columns ].apply ( lambda x : ' '.join ( x.index [ x == 1 ] ), axis = 1 )

    cv = CountVectorizer ()

    movie_vectors = cv.fit_transform ( movies [ 'genres' ] )

    similarity = cosine_similarity ( movie_vectors )

    # checks if model exists

    existing = glob.glob ( 'model/similarity_v*.pkl' )

    version = ( len ( existing ) + 1 )

    similarity_path = ( f'model/similarity_v{version}.pkl' )

    # Dump

    joblib.dump ( similarity, similarity_path )

    print ( f' similarity matrix saved sucessfully : {similarity_path} ' )

    return similarity

def load_latest_similarity():

    similarity_files = glob.glob(
        'model/similarity_v*.pkl'
    )

    if len(similarity_files) == 0:

        raise FileNotFoundError(
            "No similarity matrix found"
        )

    latest_similarity = sorted(
        similarity_files
    )[-1]

    similarity = joblib.load(
        latest_similarity
    )

    print(
        f'Loaded: {latest_similarity}'
    )

    return similarity
