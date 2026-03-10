import type { ValuationRequest, ValuationReport, MethodologyInfo, SensitivityRequest, SensitivityResponse } from "./types";

const BASE_URL = "/api";

export async function runValuation(
  request: ValuationRequest
): Promise<ValuationReport> {
  const resp = await fetch(`${BASE_URL}/valuations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!resp.ok) {
    const error = await resp.json().catch(() => ({ detail: resp.statusText }));
    throw new Error(error.detail || "Valuation failed");
  }
  return resp.json();
}

export async function getMethodologies(): Promise<MethodologyInfo[]> {
  const resp = await fetch(`${BASE_URL}/methodologies`);
  return resp.json();
}

export async function runSensitivity(
  request: SensitivityRequest
): Promise<SensitivityResponse> {
  const resp = await fetch(`${BASE_URL}/sensitivity`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!resp.ok) {
    const error = await resp.json().catch(() => ({ detail: resp.statusText }));
    throw new Error(error.detail || "Sensitivity analysis failed");
  }
  return resp.json();
}

export async function getSectors(): Promise<string[]> {
  const resp = await fetch(`${BASE_URL}/sectors`);
  return resp.json();
}

export async function exportPdf(reportId: string): Promise<void> {
  const resp = await fetch(`${BASE_URL}/valuations/${reportId}/export`);
  if (!resp.ok) throw new Error("Export failed");
  const blob = await resp.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `valuation_${reportId.slice(0, 8)}.pdf`;
  a.click();
  URL.revokeObjectURL(url);
}
