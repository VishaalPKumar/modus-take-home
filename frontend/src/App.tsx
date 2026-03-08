import { useState, useEffect } from "react";
import ValuationForm from "./components/ValuationForm";
import ValuationResults from "./components/ValuationResults";
import { runValuation, getSectors } from "./api";
import { ValuationRequest, ValuationReport } from "./types";

export default function App() {
  const [sectors, setSectors] = useState<string[]>([]);
  const [report, setReport] = useState<ValuationReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getSectors().then(setSectors).catch(console.error);
  }, []);

  const handleSubmit = async (request: ValuationRequest) => {
    setLoading(true);
    setError(null);
    try {
      const result = await runValuation(request);
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
            {error && (
              <div className="rounded-md bg-red-50 border border-red-200 p-4 mb-6">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}
            {report ? (
              <ValuationResults report={report} />
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
