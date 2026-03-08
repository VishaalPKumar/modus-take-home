from abc import ABC, abstractmethod

from app.models import ValuationResult


class ValuationEngine(ABC):
    @abstractmethod
    def value(self, **kwargs) -> ValuationResult:
        ...
