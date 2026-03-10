import type { ValuationResult } from "../types";
import { barColors, formatCurrency, methodNames } from "../utils";

export default function TriangulationView({
  results,
}: {
  results: ValuationResult[];
}) {
  const allLows = results.map((r) => r.value_range[0]);
  const allHighs = results.map((r) => r.value_range[1]);
  const globalMin = Math.min(...allLows);
  const globalMax = Math.max(...allHighs);
  const spread = globalMax - globalMin;

  const estimates = results.map((r) => r.estimated_value);
  const mean = estimates.reduce((a, b) => a + b, 0) / estimates.length;
  const min = Math.min(...estimates);
  const max = Math.max(...estimates);

  // Convergence zone: overlap of all ranges
  const overlapLow = Math.max(...allLows);
  const overlapHigh = Math.min(...allHighs);
  const hasOverlap = overlapLow < overlapHigh;

  return (
    <div className="space-y-4">
      {/* Comparison table */}
      <div className="overflow-hidden rounded-lg border border-gray-200">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gray-50 text-left text-gray-600">
              <th className="px-4 py-2 font-medium">Method</th>
              <th className="px-4 py-2 font-medium text-right">Estimated Value</th>
              <th className="px-4 py-2 font-medium text-right">Range Low</th>
              <th className="px-4 py-2 font-medium text-right">Range High</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {results.map((r) => (
              <tr key={r.methodology}>
                <td className="px-4 py-2 font-medium text-gray-900">
                  {methodNames[r.methodology]}
                </td>
                <td className="px-4 py-2 text-right font-semibold text-blue-600">
                  {formatCurrency(r.estimated_value)}
                </td>
                <td className="px-4 py-2 text-right text-gray-500">
                  {formatCurrency(r.value_range[0])}
                </td>
                <td className="px-4 py-2 text-right text-gray-500">
                  {formatCurrency(r.value_range[1])}
                </td>
              </tr>
            ))}
            {/* Summary row */}
            <tr className="bg-gray-50 font-medium">
              <td className="px-4 py-2 text-gray-700">Summary</td>
              <td className="px-4 py-2 text-right text-gray-700">
                Mean: {formatCurrency(mean)}
              </td>
              <td className="px-4 py-2 text-right text-gray-500">
                Min: {formatCurrency(min)}
              </td>
              <td className="px-4 py-2 text-right text-gray-500">
                Max: {formatCurrency(max)}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Range bar visualization */}
      <div className="space-y-3">
        <h4 className="text-sm font-semibold text-gray-700">Range Comparison</h4>
        <div className="relative space-y-2">
          {/* Convergence zone overlay */}
          {hasOverlap && spread > 0 && (
            <div
              className="absolute inset-y-0 bg-green-100 border-l border-r border-green-300 opacity-50 z-0 rounded"
              style={{
                left: `${((overlapLow - globalMin) / spread) * 100}%`,
                width: `${((overlapHigh - overlapLow) / spread) * 100}%`,
              }}
            />
          )}
          {results.map((r) => {
            const leftPct = spread > 0 ? ((r.value_range[0] - globalMin) / spread) * 100 : 0;
            const widthPct = spread > 0 ? ((r.value_range[1] - r.value_range[0]) / spread) * 100 : 100;
            const pointPct = spread > 0 ? ((r.estimated_value - globalMin) / spread) * 100 : 50;
            const colors = barColors[r.methodology] ?? { bg: "bg-gray-200", border: "border-gray-400" };

            return (
              <div key={r.methodology} className="relative z-10">
                <div className="flex items-center gap-3">
                  <span className="w-20 text-xs text-gray-600 truncate flex-shrink-0">
                    {r.methodology === "last_round" ? "Last Round" : r.methodology.toUpperCase()}
                  </span>
                  <div className="relative flex-1 h-6">
                    {/* Bar */}
                    <div
                      className={`absolute top-1 h-4 rounded ${colors.bg} border ${colors.border}`}
                      style={{ left: `${leftPct}%`, width: `${widthPct}%` }}
                    />
                    {/* Point estimate marker */}
                    <div
                      className="absolute top-0 w-0.5 h-6 bg-gray-800"
                      style={{ left: `${pointPct}%` }}
                    />
                  </div>
                </div>
              </div>
            );
          })}
          {/* Scale labels */}
          <div className="flex justify-between text-xs text-gray-400 pl-23">
            <span className="ml-23">{formatCurrency(globalMin)}</span>
            <span>{formatCurrency(globalMax)}</span>
          </div>
        </div>
      </div>

      {/* Callout */}
      <div className="rounded-md bg-gray-50 border border-gray-200 px-4 py-3 text-sm text-gray-700">
        {hasOverlap ? (
          <>
            Methods converge between{" "}
            <span className="font-semibold text-green-700">
              {formatCurrency(overlapLow)}–{formatCurrency(overlapHigh)}
            </span>
          </>
        ) : (
          <>
            Methods diverge — spread is{" "}
            <span className="font-semibold text-amber-700">
              {formatCurrency(max - min)}
            </span>
          </>
        )}
      </div>
    </div>
  );
}
