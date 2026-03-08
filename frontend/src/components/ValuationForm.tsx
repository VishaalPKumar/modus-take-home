import { useState } from "react";
import { Methodology, ValuationRequest } from "../types";

interface Props {
  sectors: string[];
  onSubmit: (request: ValuationRequest) => void;
  loading: boolean;
}

export default function ValuationForm({ sectors, onSubmit, loading }: Props) {
  const [companyName, setCompanyName] = useState("");
  const [sector, setSector] = useState("");
  const [methods, setMethods] = useState<Set<Methodology>>(new Set());

  // Comps
  const [revenue, setRevenue] = useState("");

  // DCF
  const [dcfRevenue, setDcfRevenue] = useState("");
  const [growthRate, setGrowthRate] = useState("15");
  const [discountRate, setDiscountRate] = useState("10");
  const [terminalGrowthRate, setTerminalGrowthRate] = useState("3");
  const [profitMargin, setProfitMargin] = useState("15");

  // Last Round
  const [postMoneyValuation, setPostMoneyValuation] = useState("");
  const [roundDate, setRoundDate] = useState("");

  const toggleMethod = (m: Methodology) => {
    const next = new Set(methods);
    if (next.has(m)) next.delete(m);
    else next.add(m);
    setMethods(next);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const request: ValuationRequest = {
      company_name: companyName,
      sector,
      methodologies: Array.from(methods),
    };

    if (methods.has("comps")) {
      request.comps_input = { revenue: parseFloat(revenue) };
    }
    if (methods.has("dcf")) {
      request.dcf_input = {
        revenue: parseFloat(dcfRevenue || revenue),
        growth_rate: parseFloat(growthRate) / 100,
        discount_rate: parseFloat(discountRate) / 100,
        terminal_growth_rate: parseFloat(terminalGrowthRate) / 100,
        profit_margin: parseFloat(profitMargin) / 100,
      };
    }
    if (methods.has("last_round")) {
      request.last_round_input = {
        post_money_valuation: parseFloat(postMoneyValuation),
        round_date: roundDate,
      };
    }

    onSubmit(request);
  };

  const inputClass =
    "w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500";
  const labelClass = "block text-sm font-medium text-gray-700 mb-1";

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className={labelClass}>Company Name</label>
        <input
          className={inputClass}
          value={companyName}
          onChange={(e) => setCompanyName(e.target.value)}
          placeholder="e.g., Basis AI"
          required
        />
      </div>

      <div>
        <label className={labelClass}>Sector</label>
        <select
          className={inputClass}
          value={sector}
          onChange={(e) => setSector(e.target.value)}
          required
        >
          <option value="">Select a sector</option>
          {sectors.map((s) => (
            <option key={s} value={s}>
              {s.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className={labelClass}>Valuation Methodologies</label>
        <div className="space-y-2">
          {(
            [
              ["comps", "Comparable Company Analysis"],
              ["dcf", "Discounted Cash Flow"],
              ["last_round", "Last Round (Market-Adjusted)"],
            ] as [Methodology, string][]
          ).map(([id, name]) => (
            <label key={id} className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={methods.has(id)}
                onChange={() => toggleMethod(id)}
                className="rounded border-gray-300"
              />
              {name}
            </label>
          ))}
        </div>
      </div>

      {methods.has("comps") && (
        <fieldset className="rounded-md border border-gray-200 p-4 space-y-3">
          <legend className="text-sm font-semibold text-gray-600 px-1">
            Comparable Company Analysis
          </legend>
          <div>
            <label className={labelClass}>Annual Revenue ($)</label>
            <input
              className={inputClass}
              type="number"
              value={revenue}
              onChange={(e) => setRevenue(e.target.value)}
              placeholder="e.g., 10000000"
              required
            />
          </div>
        </fieldset>
      )}

      {methods.has("dcf") && (
        <fieldset className="rounded-md border border-gray-200 p-4 space-y-3">
          <legend className="text-sm font-semibold text-gray-600 px-1">
            Discounted Cash Flow
          </legend>
          <div>
            <label className={labelClass}>Annual Revenue ($)</label>
            <input
              className={inputClass}
              type="number"
              value={dcfRevenue || revenue}
              onChange={(e) => setDcfRevenue(e.target.value)}
              placeholder="e.g., 10000000"
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className={labelClass}>Growth Rate (%)</label>
              <input
                className={inputClass}
                type="number"
                value={growthRate}
                onChange={(e) => setGrowthRate(e.target.value)}
                step="0.1"
              />
            </div>
            <div>
              <label className={labelClass}>Discount Rate / WACC (%)</label>
              <input
                className={inputClass}
                type="number"
                value={discountRate}
                onChange={(e) => setDiscountRate(e.target.value)}
                step="0.1"
              />
            </div>
            <div>
              <label className={labelClass}>Terminal Growth (%)</label>
              <input
                className={inputClass}
                type="number"
                value={terminalGrowthRate}
                onChange={(e) => setTerminalGrowthRate(e.target.value)}
                step="0.1"
              />
            </div>
            <div>
              <label className={labelClass}>Profit Margin (%)</label>
              <input
                className={inputClass}
                type="number"
                value={profitMargin}
                onChange={(e) => setProfitMargin(e.target.value)}
                step="0.1"
              />
            </div>
          </div>
        </fieldset>
      )}

      {methods.has("last_round") && (
        <fieldset className="rounded-md border border-gray-200 p-4 space-y-3">
          <legend className="text-sm font-semibold text-gray-600 px-1">
            Last Round (Market-Adjusted)
          </legend>
          <div>
            <label className={labelClass}>Post-Money Valuation ($)</label>
            <input
              className={inputClass}
              type="number"
              value={postMoneyValuation}
              onChange={(e) => setPostMoneyValuation(e.target.value)}
              placeholder="e.g., 50000000"
              required
            />
          </div>
          <div>
            <label className={labelClass}>Round Date</label>
            <input
              className={inputClass}
              type="date"
              value={roundDate}
              onChange={(e) => setRoundDate(e.target.value)}
              required
            />
          </div>
        </fieldset>
      )}

      <button
        type="submit"
        disabled={loading || methods.size === 0}
        className="w-full rounded-md bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
      >
        {loading ? "Running Valuation..." : "Run Valuation"}
      </button>
    </form>
  );
}
