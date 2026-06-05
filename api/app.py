import logging

from fastapi import FastAPI

from src.data_loader import load_data

from src.collabrative import ( load_latest_svd_model )

from src.content_based import ( load_latest_similarity )

from src.hybrid import ( hybrid_recommendation )

import time

import redis

import json

from api.config import ( REDIS_HOST, REDIS_PORT, CACHE_TTL )   # Refere notebook 16 for reference

from api.schemas import RecommendationResponse # Refere notebook 16

from fastapi import HTTPException

from contextlib import asynccontextmanager

# Initializations

ratings, movies, df = load_data()

request_count = 0

# Logger config

logging.basicConfig (filename = 'logs/api.log', level = logging.INFO, format = '%(asctime)s - %(levelname)s - %(message)s'  )

# CACHE_TTL = 400      # TTL --> Time To Live  refer day 14 notebook for more info        # Stretagy - > 1 TTL InValidation

cache_hits = 0

error_count = 0

redis_client = redis.Redis ( host = REDIS_HOST, port = REDIS_PORT, decode_responses = True ) 


    
#print ( "redis type", type ( redis_client ) )   # Debugging step

# print("HAS ATTRIBUTE", hasattr(redis_client, "scan_iter")) # Debugging step



# model, model_name = load_latest_svd_model()

# similarity = load_latest_similarity()


# @app.on_event ( "startup" ) # Refer day 12 notebook for more understanding of this

#def load_resources ():

 #   app.state.model, app.state.model_name = load_latest_svd_model()

  #  app.state.similarity = load_latest_similarity()

   # print ( " Resource loaded....... " )


@asynccontextmanager

async def lifespan ( app : FastAPI ):

    print ( "Loading resources...." )

    app.state.model, app.state.model_name = load_latest_svd_model ()

    app.state.similarity = load_latest_similarity ()

    yield

    print ( "Cleaning resources..." )

app = FastAPI ( lifespan = lifespan, title = " Movie Recommendation API ", description = " Hybrid Recommendation system using SVD, Content-Based Filtering and REDIS cache ", version = "1.0.0" )








@app.get ( "/", summary = "WELCOME" )

def home (  ):
    
    return { "message" : "Recommendation API is running" }


    

@app.get ( "/recommend/{user_id}", tags = [ "Recommendations" ], summary = "Get movie recommendation for a user", response_model = RecommendationResponse )

def recommend_movies ( user_id : int, n : int = 10 ):

    try:

        start = time.time ()

        global request_count

        global cache_hits

        global error_count

        request_count += 1

        cache_key = ( f"{app.state.model_name}:"
                      f"recommendations:{user_id}:{n}"      # Stretagy - > 2 Version Based InValidation
                    ) 

        cached_data = redis_client.get ( cache_key )
                
        if cached_data:

            cache_hits += 1

            logging.info ( f"Cache hit : { cache_key }" )

            return json.loads ( cached_data )

        # To treat every userID and its number of recomm diff

        user_data = df [ df [ 'user_id' ] == user_id ]

        if user_data.empty: # If user enters invalid user id this will get triggered

            # return { "status" : "error", "message" : "Invalid User name give range below 900" }   previous error handling

            raise HTTPException ( status_code = 404, detail = f"User {user_id} not found" )

        liked_movies = user_data.sort_values ( 'rating', ascending = False )['title'].head( 5 ).tolist()

        recommendations = hybrid_recommendation ( user_id, liked_movies, ratings, movies, app.state.similarity, app.state.model ).head ( n )

        output = []

        for _, row in recommendations.iterrows():

            movie_name = movies [ movies [ 'movie_id' ] == row [ 'movie_id' ] ]['title'].values [0]

            output.append ( { "movie" : movie_name, "score" : float ( row [ 'final_score' ] ) } )

        end = time.time()

        logging.info ( f"User = { user_id } | "
                       f" Recommendations = { n } | "
                        f" Response Time : { round ( end - start, 2 ) } sec " )

        response = { "model_version": app.state.model_name,"user_id" : user_id, "recommendation_count" : len ( output ), "recommendations" : output,         "response_time" : round ( end - start, 2 ) }

        redis_client.set ( cache_key, json.dumps ( response ), ex = CACHE_TTL )

        # print ( f"Response time : { end - start:.2f } sec" )

        return response

    except HTTPException:

        raise

    except Exception as e:   # this won't be invoked if wrong user_id cuz thats not an exception thats an bad input

        error_count += 1

        logging.error ( str( e ) )
        
        # return { 'status' : 'FAILED', 'error' : str ( e ) } Previous error handling

        raise HTTPException ( status_code = 500, detail = "Internal server Error" )




@app.get ( "/health", tags = [ "Monitoring" ], summary = "Check API health" )

def health():

    try:

        model_status = app.state.model is not None

        similarity_status = app.state.similarity is not None

        data_status = len ( df ) > 0

        overall_status = ( model_status and similarity_status and data_status )

        return { "status" : "healthy" if overall_status else "unhealthy", "model_loaded" : model_status, "Similarity_loaded" : similarity_status, "dataloaded" : data_status }

    except Exception as e:

        return { "status" : "unhealthy", "error" : str (e) }




@app.get ( "/cache-stats", tags = [ "Monitoring" ], summary = "View cached items" )

def cache_stats ():

    return { "cached_entries" : sum ( 1 for _ in redis_client.scan_iter () ) }




@app.get ( "/metrics", tags = [ "Monitoring" ], summary = "View API metrics" )

def metrics ():

    return { "total_requests" : request_count, "cache_hits" : cache_hits, "errors" : error_count, "cached_entries" : sum ( 1 for _ in redis_client.scan_iter () ) }




@app.get ( "/redis-keys", summary = "View keys details" )

def redis_keys ():

    return { "keys" : list ( redis_client.scan_iter () ) }



@app.get ( "/clear-cache", tags = [ "Monitoring" ], summary = "Remove cache", )

def clear_cache ():  # Stretagy - > 3 Manual InValidation

    count = 0

    for key in redis_client.scan_iter ():

        redis_client.delete ( key )

        count += 1

    return { "deleted_keys" : count }
