import { useState, useEffect } from "react";
import ValuationForm from "./components/ValuationForm";
import ValuationResults from "./components/ValuationResults";
import { runValuation, getSectors } from "./api";
import type { ValuationRequest, ValuationReport } from "./types";

export default function App() {
  const [sectors, setSectors] = useState<string[]>([]);
  const [report, setReport] = useState<ValuationReport | null>(null);
  const [lastRequest, setLastRequest] = useState<ValuationRequest | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [sectorError, setSectorError] = useState<string | null>(null);

  useEffect(() => {
    getSectors()
      .then(setSectors)
      .catch(() => setSectorError("Failed to load sectors. Is the backend running?"));
  }, []);

  const handleSubmit = async (request: ValuationRequest) => {
    setLoading(true);
    setError(null);
    try {
      const result = await runValuation(request);
      setLastRequest(request);
      setReport(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-6 py-4">
          <h1 className="text-xl font-bold text-gray-900">VC Audit Tool</h1>
          <p className="text-sm text-gray-500">
            Fair value estimation for private portfolio companies
          </p>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Input Panel */}
          <div className="lg:col-span-4">
            <div className="sticky top-8 rounded-lg border border-gray-200 bg-white p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Company Details
              </h2>
              <ValuationForm
                sectors={sectors}
                onSubmit={handleSubmit}
                loading={loading}
              />
            </div>
          </div>

          {/* Results Panel */}
          <div className="lg:col-span-8">
            {sectorError && (
              <div className="rounded-md bg-yellow-50 border border-yellow-200 p-4 mb-6">
                <p className="text-sm text-yellow-700">{sectorError}</p>
              </div>
            )}
            {error && (
              <div className="rounded-md bg-red-50 border border-red-200 p-4 mb-6">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}
            {loading ? (
              <div className="rounded-lg border border-gray-200 bg-white p-6 space-y-4">
                <div className="h-6 w-48 bg-gray-200 rounded animate-pulse" />
                <div className="h-4 w-full bg-gray-200 rounded animate-pulse" />
                <div className="h-4 w-3/4 bg-gray-200 rounded animate-pulse" />
                <div className="h-32 w-full bg-gray-100 rounded animate-pulse mt-4" />
              </div>
            ) : report && lastRequest ? (
              <ValuationResults report={report} request={lastRequest} />
            ) : (
              <div className="rounded-lg border-2 border-dashed border-gray-200 p-12 text-center">
                <p className="text-gray-400 text-sm">
                  Select methodologies and run a valuation to see results
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
