from pydantic import BaseModel

class PredictionResponse(BaseModel):

    churn_probability: float

    risk_level: str

    top_drivers: list

    recommendations: list