import { Bar, BarChart, LabelList, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { TooltipProps } from "recharts";
import type { NameType, ValueType } from "recharts/types/component/DefaultTooltipContent";

// Single sequential hue: these bars are one series (ranked importance), not
// distinct categories, so color stays constant across all of them.
const BAR_COLOR = "#2a78d6";

interface TopFactorsChartProps {
  factors: string[];
}

interface FactorDatum {
  name: string;
  rank: number;
  weight: number;
}

export function buildFactorData(factors: string[]): FactorDatum[] {
  return factors.map((name, index) => ({
    name,
    rank: index + 1,
    // No true importance magnitude is available from the API (top_factors
    // is an ordered list of names only), so bar length encodes rank order,
    // not a real score. The axis stays unlabeled to avoid implying one.
    weight: factors.length - index,
  }));
}

function FactorTooltip({ active, payload }: TooltipProps<ValueType, NameType>) {
  if (!active || !payload || payload.length === 0) {
    return null;
  }
  const datum = payload[0].payload as FactorDatum;
  return (
    <div
      style={{
        background: "#fcfcfb",
        border: "1px solid #e1e0d9",
        borderRadius: 4,
        padding: "6px 10px",
        fontSize: 12,
        color: "#0b0b0b",
      }}
    >
      <strong>#{datum.rank}</strong> {datum.name}
    </div>
  );
}

function TopFactorsChart({ factors }: TopFactorsChartProps) {
  if (factors.length === 0) {
    return null;
  }

  const data = buildFactorData(factors);

  return (
    <div>
      <h3 style={{ margin: "0 0 0.25rem", fontSize: "1rem" }}>Top churn factors</h3>
      <p style={{ margin: "0 0 0.75rem", fontSize: "0.8rem", color: "#52514e" }}>
        The factors with the biggest impact on this customer's predicted churn risk (via SHAP), most to least influential.
      </p>
      <ResponsiveContainer width="100%" height={48 * data.length + 16}>
        <BarChart data={data} layout="vertical" margin={{ top: 4, right: 32, bottom: 4, left: 4 }}>
          <XAxis type="number" hide domain={[0, data.length]} />
          <YAxis
            type="category"
            dataKey="name"
            width={180}
            tickLine={false}
            axisLine={{ stroke: "#c3c2b7" }}
            tick={{ fill: "#0b0b0b", fontSize: 12 }}
          />
          <Tooltip content={<FactorTooltip />} cursor={{ fill: "rgba(42, 120, 214, 0.08)" }} />
          <Bar
            dataKey="weight"
            fill={BAR_COLOR}
            radius={[0, 4, 4, 0]}
            barSize={20}
            isAnimationActive={false}
          >
            <LabelList
              dataKey="rank"
              position="right"
              formatter={(rank: number) => `#${rank}`}
              style={{ fill: "#52514e", fontSize: 12 }}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default TopFactorsChart;
