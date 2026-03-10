export function formatCurrency(value: number): string {
  if (value >= 1_000_000_000) return `$${(value / 1_000_000_000).toFixed(1)}B`;
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `$${(value / 1_000).toFixed(0)}K`;
  return `$${value.toFixed(0)}`;
}

export const methodNames: Record<string, string> = {
  comps: "Comparable Company Analysis",
  dcf: "Discounted Cash Flow",
  last_round: "Last Round (Market-Adjusted)",
};

export const methodEntries = Object.entries(methodNames) as [string, string][];

export const barColors: Record<string, { bg: string; border: string }> = {
  comps: { bg: "bg-blue-200", border: "border-blue-400" },
  dcf: { bg: "bg-emerald-200", border: "border-emerald-400" },
  last_round: { bg: "bg-amber-200", border: "border-amber-400" },
};
