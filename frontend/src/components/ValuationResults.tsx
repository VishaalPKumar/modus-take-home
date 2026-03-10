import { useState } from "react";
import type { ValuationReport, ValuationRequest, ValuationResult, SensitivityResponse } from "../types";
import { runSensitivity, exportPdf } from "../api";
import { formatCurrency, methodNames } from "../utils";
import TriangulationView from "./TriangulationView";
import SensitivityTable from "./SensitivityTable";

function ResultCard({
  result,
  request,
}: {
  result: ValuationResult;
  request: ValuationRequest;
}) {
  const [sensitivity, setSensitivity] = useState<SensitivityResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSensitivity = async () => {
    if (sensitivity) {
      setSensitivity(null);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const resp = await runSensitivity({
        methodology: result.methodology,
        sector: request.sector,
        comps_input: result.methodology === "comps" ? request.comps_input : undefined,
        dcf_input: result.methodology === "dcf" ? request.dcf_input : undefined,
        last_round_input: result.methodology === "last_round" ? request.last_round_input : undefined,
      });
      setSensitivity(resp);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Sensitivity analysis failed");
    } finally {
      setLoading(false);
    }
  };

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

      {/* Sensitivity button + table */}
      <div className="border-t border-gray-100 pt-3">
        <button
          onClick={handleSensitivity}
          disabled={loading}
          className="text-sm font-medium text-blue-600 hover:text-blue-800 disabled:text-gray-400"
        >
          {loading ? "Loading..." : sensitivity ? "Hide Sensitivity" : "Show Sensitivity"}
        </button>
        {error && <p className="text-sm text-red-600 mt-1">{error}</p>}
        {sensitivity && <SensitivityTable data={sensitivity} />}
      </div>
    </div>
  );
}

export default function ValuationResults({
  report,
  request,
}: {
  report: ValuationReport;
  request: ValuationRequest;
}) {
  const [exporting, setExporting] = useState(false);

  const handleExport = async () => {
    setExporting(true);
    try {
      await exportPdf(report.id);
    } catch {
      // silently fail — the browser will show a download error
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="rounded-lg border border-blue-200 bg-blue-50 p-5">
        <div className="flex items-start justify-between mb-1">
          <h2 className="text-lg font-semibold text-gray-900">
            Valuation Summary — {report.company_name}
          </h2>
          <button
            onClick={handleExport}
            disabled={exporting}
            className="flex-shrink-0 inline-flex items-center gap-1.5 rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700 disabled:bg-blue-400"
          >
            {exporting ? "Exporting..." : "Export PDF"}
          </button>
        </div>
        <p className="text-sm text-gray-500 mb-4">
          Sector: {report.sector.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())} |
          Generated: {new Date(report.created_at).toLocaleString()} |
          Report ID: {report.id.slice(0, 8)}
        </p>

        {report.results.length > 1 && (
          <TriangulationView results={report.results} />
        )}
      </div>

      {/* Per-method details */}
      {report.results.map((result) => (
        <ResultCard key={result.methodology} result={result} request={request} />
      ))}
    </div>
  );
}
