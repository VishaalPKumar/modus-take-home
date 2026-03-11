export type Methodology = "comps" | "dcf" | "last_round";

export interface CompsInput {
  revenue: number;
}

export interface DCFInput {
  revenue: number;
  growth_rate?: number;
  discount_rate?: number;
  terminal_growth_rate?: number;
  projection_years?: number;
  profit_margin?: number;
}

export interface LastRoundInput {
  post_money_valuation: number;
  round_date: string; // ISO date string
}

export interface ValuationRequest {
  company_name: string;
  sector: string;
  methodologies: Methodology[];
  comps_input?: CompsInput;
  dcf_input?: DCFInput;
  last_round_input?: LastRoundInput;
}

export interface ValuationStep {
  description: string;
  detail: string;
}

export interface ValuationResult {
  methodology: Methodology;
  estimated_value: number;
  value_range: [number, number];
  assumptions: Record<string, string | number | boolean>;
  steps: ValuationStep[];
  citations: string[];
}

export interface ValuationReport {
  id: string;
  company_name: string;
  sector: string;
  results: ValuationResult[];
  created_at: string;
}

export interface SensitivityRequest {
  methodology: Methodology;
  sector?: string;
  comps_input?: CompsInput;
  dcf_input?: DCFInput;
  last_round_input?: LastRoundInput;
}

export interface SensitivityPoint {
  parameters: Record<string, number>;
  estimated_value: number;
}

export interface SensitivityResponse {
  methodology: Methodology;
  base_estimated_value: number;
  varied_parameters: string[];
  data_points: SensitivityPoint[];
}

export interface MethodologyInfo {
  id: Methodology;
  name: string;
  description: string;
  required_fields: string[];
}
