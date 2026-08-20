import { useState } from "react";
import CustomerFeaturesForm from "./components/CustomerFeaturesForm";
import { predictChurn, type CustomerFeatures, type PredictionResponse } from "./services/api";

function App() {
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [loading, setLoading] = useState(false);

  async function handlePredict(features: CustomerFeatures) {
    setLoading(true);
    try {
      const response = await predictChurn(features);
      setResult(response);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{ fontFamily: "sans-serif", padding: "2rem" }}>
      <h1>Customer Churn Predictor</h1>
      <CustomerFeaturesForm onSubmit={handlePredict} loading={loading} />
      {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
    </main>
  );
}

export default App;
