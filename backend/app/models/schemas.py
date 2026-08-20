from pydantic import BaseModel, Field


class CustomerFeatures(BaseModel):
    """Input features used by the churn model.

    Adjust these fields to match the dataset you train on
    (e.g. the Telco Customer Churn dataset).
    """

    tenure_months: int = Field(..., ge=0, description="Months as a customer")
    monthly_charges: float = Field(..., ge=0)
    total_charges: float = Field(..., ge=0)
    contract_type: str = Field(..., description="month-to-month | one_year | two_year")
    has_internet_service: bool
    has_tech_support: bool


class PredictionResponse(BaseModel):
    churn_probability: float = Field(..., ge=0, le=1)
    will_churn: bool
    top_factors: list[str] = []
