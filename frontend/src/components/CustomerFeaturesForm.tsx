import { useState } from "react";
import type { FormEvent } from "react";
import type { CustomerFeatures } from "../services/api";

const CONTRACT_TYPES: CustomerFeatures["contract_type"][] = [
  "month-to-month",
  "one_year",
  "two_year",
];

const DEFAULT_VALUES: CustomerFeatures = {
  tenure_months: 0,
  monthly_charges: 0,
  total_charges: 0,
  contract_type: "month-to-month",
  has_internet_service: true,
  has_tech_support: false,
};

interface CustomerFeaturesFormProps {
  onSubmit: (features: CustomerFeatures) => void | Promise<void>;
  loading?: boolean;
}

function CustomerFeaturesForm({ onSubmit, loading = false }: CustomerFeaturesFormProps) {
  const [values, setValues] = useState<CustomerFeatures>(DEFAULT_VALUES);

  function handleChange<K extends keyof CustomerFeatures>(
    field: K,
    value: CustomerFeatures[K]
  ) {
    setValues((prev) => ({ ...prev, [field]: value }));
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit(values);
  }

  return (
    <form onSubmit={handleSubmit} style={{ display: "grid", gap: "1rem", maxWidth: 420 }}>
      <label>
        Tenure (months)
        <input
          type="number"
          min={0}
          required
          value={values.tenure_months}
          onChange={(e) => handleChange("tenure_months", Number(e.target.value))}
        />
      </label>

      <label>
        Monthly charges ($)
        <input
          type="number"
          min={0}
          step="0.01"
          required
          value={values.monthly_charges}
          onChange={(e) => handleChange("monthly_charges", Number(e.target.value))}
        />
      </label>

      <label>
        Total charges ($)
        <input
          type="number"
          min={0}
          step="0.01"
          required
          value={values.total_charges}
          onChange={(e) => handleChange("total_charges", Number(e.target.value))}
        />
      </label>

      <label>
        Contract type
        <select
          value={values.contract_type}
          onChange={(e) =>
            handleChange("contract_type", e.target.value as CustomerFeatures["contract_type"])
          }
        >
          {CONTRACT_TYPES.map((type) => (
            <option key={type} value={type}>
              {type}
            </option>
          ))}
        </select>
      </label>

      <label>
        <input
          type="checkbox"
          checked={values.has_internet_service}
          onChange={(e) => handleChange("has_internet_service", e.target.checked)}
        />
        Has internet service
      </label>

      <label>
        <input
          type="checkbox"
          checked={values.has_tech_support}
          onChange={(e) => handleChange("has_tech_support", e.target.checked)}
        />
        Has tech support
      </label>

      <button type="submit" disabled={loading}>
        {loading ? "Predicting..." : "Predict churn"}
      </button>
    </form>
  );
}

export default CustomerFeaturesForm;
