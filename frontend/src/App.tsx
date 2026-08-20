import { useState } from "react";
import CustomerFeaturesForm from "./components/CustomerFeaturesForm";
import TopFactorsChart from "./components/TopFactorsChart";
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
      {result && (
        <section style={{ marginTop: "1.5rem" }}>
          <p>
            Churn probability: <strong>{(result.churn_probability * 100).toFixed(1)}%</strong>{" "}
            ({result.will_churn ? "likely to churn" : "likely to stay"})
          </p>
          <TopFactorsChart factors={result.top_factors} />
        </section>
      )}
    </main>
  );
}

export default App;
