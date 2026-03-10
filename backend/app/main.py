import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from app.data.provider import MockDataProvider
from app.models import SensitivityRequest, SensitivityResponse, ValuationReport, ValuationRequest
from app.pdf import generate_report_pdf
from app.service import ValuationService

logging.basicConfig(
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

app = FastAPI(title="VC Audit Tool", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

data_provider = MockDataProvider()
valuation_service = ValuationService(data_provider)

# In-memory store for retrieving past reports
_reports: dict[str, ValuationReport] = {}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/methodologies")
def get_methodologies():
    return [
        {
            "id": "comps",
            "name": "Comparable Company Analysis",
            "description": "Values a company by comparing to similar public companies using EV/Revenue multiples.",
            "required_fields": ["sector", "revenue"],
        },
        {
            "id": "dcf",
            "name": "Discounted Cash Flow",
            "description": "Projects future cash flows and discounts them to present value.",
            "required_fields": ["revenue", "growth_rate", "discount_rate"],
        },
        {
            "id": "last_round",
            "name": "Last Round (Market-Adjusted)",
            "description": "Adjusts last funding round valuation by public market index performance.",
            "required_fields": ["post_money_valuation", "round_date"],
        },
    ]


@app.get("/api/sectors")
def get_sectors():
    return data_provider.get_sectors()


@app.post("/api/valuations", response_model=ValuationReport)
def create_valuation(request: ValuationRequest):
    try:
        report = valuation_service.run(request)
    except ValueError as e:
        logger.warning("Valuation rejected: %s", e)
        raise HTTPException(status_code=400, detail=str(e))
    _reports[report.id] = report
    return report


@app.post("/api/sensitivity", response_model=SensitivityResponse)
def run_sensitivity(request: SensitivityRequest):
    try:
        return valuation_service.sensitivity(request)
    except ValueError as e:
        logger.warning("Sensitivity rejected: %s", e)
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/valuations/{report_id}", response_model=ValuationReport)
def get_valuation(report_id: str):
    report = _reports.get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@app.get("/api/valuations/{report_id}/export")
def export_valuation(report_id: str):
    report = _reports.get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    pdf_bytes = generate_report_pdf(report)
    filename = f"{report.company_name.replace(' ', '_')}_{report_id[:8]}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
