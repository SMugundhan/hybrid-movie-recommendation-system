from pydantic import BaseModel

class Recommendation ( BaseModel ):

    movie : str

    score : float


class RecommendationResponse ( BaseModel ):

    model_version : str

    user_id : int

    recommendation_count : int

    recommendations : list [ Recommendation ]

    response_time : float