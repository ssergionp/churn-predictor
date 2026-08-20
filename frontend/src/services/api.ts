import axios from "axios";

const API_BASE_URL = "http://localhost:8000/api";

export interface CustomerFeatures {
  tenure_months: number;
  monthly_charges: number;
  total_charges: number;
  contract_type: "month-to-month" | "one_year" | "two_year";
  has_internet_service: boolean;
  has_tech_support: boolean;
}

export interface PredictionResponse {
  churn_probability: number;
  will_churn: boolean;
  top_factors: string[];
}

export async function predictChurn(
  features: CustomerFeatures
): Promise<PredictionResponse> {
  const { data } = await axios.post<PredictionResponse>(
    `${API_BASE_URL}/predict`,
    features
  );
  return data;
}
