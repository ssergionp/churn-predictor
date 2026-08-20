import { useState } from "react";
import { predictChurn, type PredictionResponse } from "./services/api";

function App() {
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [loading, setLoading] = useState(false);

  async function handlePredict() {
    setLoading(true);
    try {
      // TODO: replace with real form values
      const response = await predictChurn({
        tenure_months: 3,
        monthly_charges: 95,
        total_charges: 285,
        contract_type: "month-to-month",
        has_internet_service: true,
        has_tech_support: false,
      });
      setResult(response);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{ fontFamily: "sans-serif", padding: "2rem" }}>
      <h1>Customer Churn Predictor</h1>
      <p>TODO: build the input form here (see components/).</p>
      <button onClick={handlePredict} disabled={loading}>
        {loading ? "Predicting..." : "Run sample prediction"}
      </button>
      {result && (
        <pre>{JSON.stringify(result, null, 2)}</pre>
      )}
    </main>
  );
}

export default App;
