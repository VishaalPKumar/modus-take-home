import type { Methodology } from "./types";

export function formatCurrency(value: number): string {
  if (!isFinite(value)) return "$—";
  if (value < 0) return "-" + formatCurrency(-value);
  if (value >= 1_000_000_000) return `$${(value / 1_000_000_000).toFixed(1)}B`;
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `$${(value / 1_000).toFixed(0)}K`;
  return `$${value.toFixed(0)}`;
}

export function formatLabel(snake: string): string {
  return snake.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export const methodNames: Record<Methodology, string> = {
  comps: "Comparable Company Analysis",
  dcf: "Discounted Cash Flow",
  last_round: "Last Round (Market-Adjusted)",
};

export const barColors: Record<Methodology, { bg: string; border: string }> = {
  comps: { bg: "bg-blue-200", border: "border-blue-400" },
  dcf: { bg: "bg-emerald-200", border: "border-emerald-400" },
  last_round: { bg: "bg-amber-200", border: "border-amber-400" },
};
