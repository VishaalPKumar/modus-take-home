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
  if (!resp.ok) {
    const error = await resp.json().catch(() => ({ detail: resp.statusText }));
    throw new Error(error.detail || "Failed to fetch methodologies");
  }
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
  if (!resp.ok) {
    const error = await resp.json().catch(() => ({ detail: resp.statusText }));
    throw new Error(error.detail || "Failed to fetch sectors");
  }
  return resp.json();
}

export async function fetchPdfBlob(reportId: string): Promise<Blob> {
  const resp = await fetch(`${BASE_URL}/valuations/${reportId}/export`);
  if (!resp.ok) throw new Error("Export failed");
  return resp.blob();
}
