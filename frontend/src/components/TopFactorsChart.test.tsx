import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import TopFactorsChart, { buildFactorData } from "./TopFactorsChart";

describe("buildFactorData", () => {
  it("ranks factors in the given order with descending weight", () => {
    expect(buildFactorData(["tenure_months", "contract_type", "monthly_charges"])).toEqual([
      { name: "tenure_months", rank: 1, weight: 3 },
      { name: "contract_type", rank: 2, weight: 2 },
      { name: "monthly_charges", rank: 3, weight: 1 },
    ]);
  });

  it("returns an empty array for no factors", () => {
    expect(buildFactorData([])).toEqual([]);
  });
});

describe("TopFactorsChart", () => {
  it("renders one bar per factor", () => {
    const { container } = render(
      <TopFactorsChart factors={["tenure_months", "contract_type_month-to-month", "monthly_charges"]} />
    );
    expect(container.querySelectorAll(".recharts-bar-rectangle")).toHaveLength(3);
  });

  it("renders nothing when there are no factors", () => {
    const { container } = render(<TopFactorsChart factors={[]} />);
    expect(container).toBeEmptyDOMElement();
  });
});
