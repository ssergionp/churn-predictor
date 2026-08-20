import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import CustomerFeaturesForm from "./CustomerFeaturesForm";

describe("CustomerFeaturesForm", () => {
  it("submits the edited feature values", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<CustomerFeaturesForm onSubmit={onSubmit} />);

    await user.clear(screen.getByLabelText(/tenure/i));
    await user.type(screen.getByLabelText(/tenure/i), "24");

    await user.clear(screen.getByLabelText(/monthly charges/i));
    await user.type(screen.getByLabelText(/monthly charges/i), "89.5");

    await user.clear(screen.getByLabelText(/total charges/i));
    await user.type(screen.getByLabelText(/total charges/i), "2148");

    await user.selectOptions(screen.getByLabelText(/contract type/i), "two_year");
    await user.click(screen.getByLabelText(/has tech support/i));

    await user.click(screen.getByRole("button", { name: /predict churn/i }));

    expect(onSubmit).toHaveBeenCalledWith({
      tenure_months: 24,
      monthly_charges: 89.5,
      total_charges: 2148,
      contract_type: "two_year",
      has_internet_service: true,
      has_tech_support: true,
    });
  });

  it("disables the submit button while loading", () => {
    render(<CustomerFeaturesForm onSubmit={vi.fn()} loading />);
    expect(screen.getByRole("button", { name: /predicting/i })).toBeDisabled();
  });
});
