import { ValuationRequest, ValuationReport, MethodologyInfo } from "./types";

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

export async function getSectors(): Promise<string[]> {
  const resp = await fetch(`${BASE_URL}/sectors`);
  return resp.json();
}
