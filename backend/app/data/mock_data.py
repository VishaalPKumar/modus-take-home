from datetime import date

from app.models import ComparableCompany

COMPARABLE_COMPANIES: list[ComparableCompany] = [
    # Technology
    {"name": "Datadog", "sector": "technology", "revenue": 2_130_000_000, "ebitda": 450_000_000, "enterprise_value": 38_000_000_000},
    {"name": "Snowflake", "sector": "technology", "revenue": 2_810_000_000, "ebitda": -120_000_000, "enterprise_value": 55_000_000_000},
    {"name": "CrowdStrike", "sector": "technology", "revenue": 3_060_000_000, "ebitda": 520_000_000, "enterprise_value": 70_000_000_000},
    {"name": "Palantir", "sector": "technology", "revenue": 2_220_000_000, "ebitda": 390_000_000, "enterprise_value": 50_000_000_000},
    {"name": "MongoDB", "sector": "technology", "revenue": 1_680_000_000, "ebitda": 80_000_000, "enterprise_value": 18_000_000_000},
    # Fintech
    {"name": "Bill Holdings", "sector": "fintech", "revenue": 1_180_000_000, "ebitda": 150_000_000, "enterprise_value": 15_000_000_000},
    {"name": "Marqeta", "sector": "fintech", "revenue": 480_000_000, "ebitda": -30_000_000, "enterprise_value": 3_200_000_000},
    {"name": "Toast", "sector": "fintech", "revenue": 3_870_000_000, "ebitda": 200_000_000, "enterprise_value": 14_000_000_000},
    {"name": "Shift4", "sector": "fintech", "revenue": 2_700_000_000, "ebitda": 480_000_000, "enterprise_value": 8_500_000_000},
    # Healthcare
    {"name": "Veeva Systems", "sector": "healthcare", "revenue": 2_360_000_000, "ebitda": 900_000_000, "enterprise_value": 33_000_000_000},
    {"name": "Doximity", "sector": "healthcare", "revenue": 470_000_000, "ebitda": 210_000_000, "enterprise_value": 7_500_000_000},
    {"name": "Certara", "sector": "healthcare", "revenue": 360_000_000, "ebitda": 100_000_000, "enterprise_value": 3_800_000_000},
    {"name": "Phreesia", "sector": "healthcare", "revenue": 400_000_000, "ebitda": 20_000_000, "enterprise_value": 2_800_000_000},
    # Enterprise SaaS
    {"name": "Atlassian", "sector": "enterprise_saas", "revenue": 4_400_000_000, "ebitda": 600_000_000, "enterprise_value": 50_000_000_000},
    {"name": "HubSpot", "sector": "enterprise_saas", "revenue": 2_630_000_000, "ebitda": 350_000_000, "enterprise_value": 28_000_000_000},
    {"name": "Freshworks", "sector": "enterprise_saas", "revenue": 720_000_000, "ebitda": 40_000_000, "enterprise_value": 5_200_000_000},
    {"name": "ServiceNow", "sector": "enterprise_saas", "revenue": 9_600_000_000, "ebitda": 2_100_000_000, "enterprise_value": 175_000_000_000},
]

# Monthly Nasdaq Composite values (approximate, for mock purposes)
NASDAQ_INDEX: dict[str, list[tuple[date, float]]] = {
    "nasdaq": [
        (date(2023, 1, 1), 10_466),
        (date(2023, 4, 1), 12_227),
        (date(2023, 7, 1), 14_346),
        (date(2023, 10, 1), 13_219),
        (date(2024, 1, 1), 15_011),
        (date(2024, 4, 1), 15_927),
        (date(2024, 7, 1), 17_871),
        (date(2024, 10, 1), 18_095),
        (date(2025, 1, 1), 19_310),
        (date(2025, 4, 1), 18_750),
        (date(2025, 7, 1), 19_890),
        (date(2025, 10, 1), 20_150),
        (date(2026, 1, 1), 20_580),
        (date(2026, 3, 1), 20_820),
    ],
}
