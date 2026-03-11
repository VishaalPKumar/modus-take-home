import type { SensitivityResponse } from "../types";
import { formatCurrency, formatLabel } from "../utils";

function formatPercent(value: number): string {
  return `${(value * 100).toFixed(0)}%`;
}

function cellColor(value: number, min: number, max: number): string {
  if (max === min) return "bg-white";
  const ratio = (value - min) / (max - min);
  if (ratio > 0.66) return "bg-green-100 text-green-900";
  if (ratio > 0.33) return "bg-yellow-50 text-yellow-900";
  return "bg-red-100 text-red-900";
}

function TwoDTable({ data }: { data: SensitivityResponse }) {
  // Build grid: rows = discount_rate, cols = growth_rate
  const discountRates = [...new Set(data.data_points.map((p) => p.parameters.discount_rate))].sort();
  const growthRates = [...new Set(data.data_points.map((p) => p.parameters.growth_rate))].sort();

  const lookup = new Map<string, number>();
  for (const pt of data.data_points) {
    lookup.set(`${pt.parameters.discount_rate}-${pt.parameters.growth_rate}`, pt.estimated_value);
  }

  const allValues = data.data_points.map((p) => p.estimated_value);
  const min = Math.min(...allValues);
  const max = Math.max(...allValues);

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-xs border-collapse">
        <thead>
          <tr>
            <th className="px-2 py-1.5 bg-gray-100 border border-gray-200 text-gray-600 font-medium">
              DR \ GR
            </th>
            {growthRates.map((gr) => (
              <th
                key={gr}
                className="px-2 py-1.5 bg-gray-100 border border-gray-200 text-gray-600 font-medium"
              >
                {formatPercent(gr)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {discountRates.map((dr) => (
            <tr key={dr}>
              <td className="px-2 py-1.5 bg-gray-50 border border-gray-200 font-medium text-gray-700">
                {formatPercent(dr)}
              </td>
              {growthRates.map((gr) => {
                const val = lookup.get(`${dr}-${gr}`);
                const isBase =
                  val != null && Math.abs(val - data.base_estimated_value) / (data.base_estimated_value || 1) < 0.001;
                return (
                  <td
                    key={gr}
                    className={`px-2 py-1.5 border border-gray-200 text-right font-mono ${
                      val != null ? cellColor(val, min, max) : "bg-gray-50 text-gray-300"
                    } ${isBase ? "ring-2 ring-blue-500 ring-inset" : ""}`}
                  >
                    {val != null ? formatCurrency(val) : "—"}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
      <div className="mt-1.5 flex items-center gap-3 text-xs text-gray-500">
        <span>Rows: Discount Rate</span>
        <span>Cols: Growth Rate</span>
        <span className="inline-block w-3 h-3 ring-2 ring-blue-500 rounded-sm" /> Base case
      </div>
    </div>
  );
}

function OneDTable({ data }: { data: SensitivityResponse }) {
  const paramName = data.varied_parameters[0];
  const allValues = data.data_points.map((p) => p.estimated_value);
  const min = Math.min(...allValues);
  const max = Math.max(...allValues);
  const isBase = (val: number) => Math.abs(val - data.base_estimated_value) / (data.base_estimated_value || 1) < 0.001;

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr>
            <th className="px-3 py-2 bg-gray-100 border border-gray-200 text-left text-gray-600 font-medium">
              {formatLabel(paramName)}
            </th>
            <th className="px-3 py-2 bg-gray-100 border border-gray-200 text-right text-gray-600 font-medium">
              Estimated Value
            </th>
          </tr>
        </thead>
        <tbody>
          {data.data_points.map((pt, i) => {
            const paramVal = pt.parameters[paramName];
            const highlighted = isBase(pt.estimated_value);
            return (
              <tr key={i}>
                <td
                  className={`px-3 py-1.5 border border-gray-200 font-mono ${
                    highlighted ? "bg-blue-50 font-semibold" : ""
                  }`}
                >
                  {formatCurrency(paramVal)}
                </td>
                <td
                  className={`px-3 py-1.5 border border-gray-200 text-right font-mono ${
                    cellColor(pt.estimated_value, min, max)
                  } ${highlighted ? "ring-2 ring-blue-500 ring-inset" : ""}`}
                >
                  {formatCurrency(pt.estimated_value)}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <div className="mt-1.5 text-xs text-gray-500">
        <span className="inline-block w-3 h-3 ring-2 ring-blue-500 rounded-sm mr-1" /> Base case
      </div>
    </div>
  );
}

export default function SensitivityTable({
  data,
}: {
  data: SensitivityResponse;
}) {
  const is2D = data.varied_parameters.length === 2;

  return (
    <div className="mt-4 space-y-2">
      <h4 className="text-sm font-semibold text-gray-700">
        Sensitivity Analysis
      </h4>
      {is2D ? <TwoDTable data={data} /> : <OneDTable data={data} />}
    </div>
  );
}
