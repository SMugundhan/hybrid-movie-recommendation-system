import numpy as np

import pandas as pd

from sklearn.preprocessing import MinMaxScaler

def hybrid_recommendation ( user_id, liked_movies, ratings, movies, similarity, model ):

    watched_movies = ratings [ ratings [ 'user_id' ] == user_id ] [ 'movie_id' ].tolist()

    all_movies = ratings [ 'movie_id' ].unique()

    predictions = []

    for movie in all_movies:

        if movie not in watched_movies:

            pred = model.predict ( uid = user_id, iid = movie )

            predictions.append ( ( movie, pred.est ) )

    collab_df = pd.DataFrame ( predictions, columns = [ 'movie_id', 'collab_score' ] )

    content_score = np.zeros ( len ( movies ) )

    total_rating = 0

    for movie in liked_movies:

        idx = movies [ movies [ 'title' ] == movie ].index[0]

        rating = ratings [ ( ratings [ 'user_id' ] == user_id ) ][ 'rating' ].mean()

        content_score += ( similarity [idx] * rating )

        total_rating += rating

    content_score = ( content_score / total_rating )

    content_score = list ( enumerate ( content_score ) )

    content_df = pd.DataFrame ( content_score, columns = [ 'movie_index', 'content_score' ] )

    content_df[ 'movie_id' ] = movies [ 'movie_id' ]

    hybrid = pd.merge ( collab_df, content_df, on = 'movie_id' )

    scaler = MinMaxScaler ()

    hybrid [ 'collab_score' ] = scaler.fit_transform ( hybrid [ [ 'collab_score' ] ] )

    hybrid [ 'final_score' ] = ( 0.7 * hybrid [ 'collab_score' ] + 0.3 * hybrid [ 'content_score' ] )

    hybrid = hybrid.sort_values ( 'final_score', ascending = False )

    hybrid [ 'title' ] = movies [ 'title' ] 

    return hybrid.head ( 10 )
    
    