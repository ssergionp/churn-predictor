from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, String, func

from app.db import Base


class PredictionRecord(Base):
    """One saved churn prediction: the input features, the model's output,
    and when it was made.
    """

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)

    tenure_months = Column(Integer, nullable=False)
    monthly_charges = Column(Float, nullable=False)
    total_charges = Column(Float, nullable=False)
    contract_type = Column(String, nullable=False)
    has_internet_service = Column(Boolean, nullable=False)
    has_tech_support = Column(Boolean, nullable=False)

    churn_probability = Column(Float, nullable=False)
    will_churn = Column(Boolean, nullable=False)
    top_factors = Column(JSON, nullable=False, default=list)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
