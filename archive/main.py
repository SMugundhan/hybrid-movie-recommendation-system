from src.data_loader import load_data

from src.collabrative import ( train_svd_model, load_latest_svd_model )

from src.content_based import ( build_content_similarity, load_latest_similarity )

from src.hybrid import hybrid_recommendation

import os

from src.data_loader import load_data

ratings, movies, df = load_data ()

# SVD MODEL

try:

    model = load_latest_svd_model()

except FileNotFoundError:

    print( "Training new SVD model..." )

    model = train_svd_model( ratings )


# SIMILARITY MATRIX

try:

    similarity = load_latest_similarity()

except FileNotFoundError:

    print( "Building similarity matrix..." )

    similarity = build_content_similarity( movies )

user_id = 1

liked_movies = df [ ( df [ 'user_id' ] == user_id ) ].sort_values ( 'rating', ascending = False )['title'].head ( 5 ).tolist()

recommendations = hybrid_recommendation ( user_id, liked_movies, ratings, movies, similarity, model )

print ( recommendations )