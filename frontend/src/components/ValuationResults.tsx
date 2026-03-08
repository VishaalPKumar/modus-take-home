import { ValuationReport, ValuationResult } from "../types";

const methodNames: Record<string, string> = {
  comps: "Comparable Company Analysis",
  dcf: "Discounted Cash Flow",
  last_round: "Last Round (Market-Adjusted)",
};

function formatCurrency(value: number): string {
  if (value >= 1_000_000_000) return `$${(value / 1_000_000_000).toFixed(1)}B`;
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `$${(value / 1_000).toFixed(0)}K`;
  return `$${value.toFixed(0)}`;
}

function ResultCard({ result }: { result: ValuationResult }) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">
          {methodNames[result.methodology]}
        </h3>
        <span className="text-2xl font-bold text-blue-600">
          {formatCurrency(result.estimated_value)}
        </span>
      </div>

      <div className="text-sm text-gray-500">
        Range: {formatCurrency(result.value_range[0])} —{" "}
        {formatCurrency(result.value_range[1])}
      </div>

      {/* Assumptions */}
      <div>
        <h4 className="text-sm font-semibold text-gray-700 mb-2">
          Key Assumptions
        </h4>
        <div className="rounded-md bg-gray-50 p-3">
          <dl className="grid grid-cols-2 gap-x-4 gap-y-1 text-sm">
            {Object.entries(result.assumptions).map(([key, value]) => (
              <div key={key} className="contents">
                <dt className="text-gray-500">
                  {key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
                </dt>
                <dd className="text-gray-900 font-medium">
                  {typeof value === "number"
                    ? value > 1000
                      ? formatCurrency(value)
                      : value
                    : String(value)}
                </dd>
              </div>
            ))}
          </dl>
        </div>
      </div>

      {/* Derivation Steps */}
      <div>
        <h4 className="text-sm font-semibold text-gray-700 mb-2">
          Audit Trail
        </h4>
        <ol className="space-y-2">
          {result.steps.map((step, i) => (
            <li key={i} className="text-sm">
              <div className="flex gap-2">
                <span className="flex-shrink-0 w-5 h-5 rounded-full bg-blue-100 text-blue-700 text-xs flex items-center justify-center font-medium">
                  {i + 1}
                </span>
                <div>
                  <p className="font-medium text-gray-800">
                    {step.description}
                  </p>
                  <p className="text-gray-500 mt-0.5 whitespace-pre-wrap">
                    {step.detail}
                  </p>
                </div>
              </div>
            </li>
          ))}
        </ol>
      </div>

      {/* Citations */}
      <div>
        <h4 className="text-sm font-semibold text-gray-700 mb-1">
          Data Sources
        </h4>
        <ul className="text-sm text-gray-500 list-disc list-inside">
          {result.citations.map((c, i) => (
            <li key={i}>{c}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default function ValuationResults({
  report,
}: {
  report: ValuationReport;
}) {
  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="rounded-lg border border-blue-200 bg-blue-50 p-5">
        <h2 className="text-lg font-semibold text-gray-900 mb-1">
          Valuation Summary — {report.company_name}
        </h2>
        <p className="text-sm text-gray-500 mb-4">
          Sector: {report.sector.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())} |
          Generated: {new Date(report.created_at).toLocaleString()} |
          Report ID: {report.id.slice(0, 8)}
        </p>

        {report.results.length > 1 && (
          <div className="grid grid-cols-3 gap-4">
            {report.results.map((r) => (
              <div key={r.methodology} className="text-center">
                <p className="text-xs text-gray-500 uppercase tracking-wide">
                  {methodNames[r.methodology]}
                </p>
                <p className="text-xl font-bold text-blue-600 mt-1">
                  {formatCurrency(r.estimated_value)}
                </p>
                <p className="text-xs text-gray-400">
                  {formatCurrency(r.value_range[0])} – {formatCurrency(r.value_range[1])}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Per-method details */}
      {report.results.map((result) => (
        <ResultCard key={result.methodology} result={result} />
      ))}
    </div>
  );
}
