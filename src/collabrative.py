from surprise import SVD, Dataset, Reader

import joblib

import os

import glob

def train_svd_model ( ratings ):

    reader = Reader ( rating_scale = ( 1, 5 ) )

    data = Dataset.load_from_df ( ratings [ [ 'user_id', 'movie_id', 'rating' ] ], reader )

    trainset = data.build_full_trainset ()

    model = SVD()

    model.fit ( trainset )

    # Finds existing model

    existing_models = glob.glob ( 'model/svd_model_v*.pkl' )

    version = ( len ( existing_models ) + 1 )

    model_path = ( f'model/svd_model_v{version}.pkl' )

    # Save

    joblib.dump ( model, model_path )

    print ( f' SVD Model saved : { model_path }' )

    return model

def load_latest_svd_model():

    model_files = glob.glob(
        'model/svd_model_v*.pkl'
    )

    if len(model_files)==0:

        raise FileNotFoundError(
            "No SVD model found"
        )

    latest_model = sorted(
        model_files
    )[-1]

    model = joblib.load(
        latest_model
    )

    print(
        f'Loaded: {latest_model}'
    )

    return model, latest_model