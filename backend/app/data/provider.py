from abc import ABC, abstractmethod
from datetime import date

from app.data.mock_data import COMPARABLE_COMPANIES, NASDAQ_INDEX


class DataProvider(ABC):
    @abstractmethod
    def get_comparable_companies(self, sector: str) -> list[dict]:
        ...

    @abstractmethod
    def get_index_value(self, index_name: str, as_of_date: date) -> float | None:
        ...

    @abstractmethod
    def get_sectors(self) -> list[str]:
        ...


class MockDataProvider(DataProvider):
    def get_comparable_companies(self, sector: str) -> list[dict]:
        return [c for c in COMPARABLE_COMPANIES if c["sector"] == sector.lower()]

    def get_index_value(self, index_name: str, as_of_date: date) -> float | None:
        data_points = NASDAQ_INDEX.get(index_name.lower())
        if not data_points:
            return None
        # Find closest date
        closest = min(data_points, key=lambda dp: abs((dp[0] - as_of_date).days))
        return closest[1]

    def get_sectors(self) -> list[str]:
        return sorted(set(c["sector"] for c in COMPARABLE_COMPANIES))
