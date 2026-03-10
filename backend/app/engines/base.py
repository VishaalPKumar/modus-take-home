from abc import ABC, abstractmethod

from app.models import ValuationResult


class ValuationEngine(ABC):
    @abstractmethod
    def value(self, **kwargs) -> ValuationResult:
        """Run the valuation engine and return a structured result.

        Uses ``**kwargs`` instead of a fixed signature so that each subclass
        can declare only the parameters it needs (e.g. ``dcf_input`` for DCF,
        ``sector`` + ``comps_input`` for Comps). This keeps the strategy
        pattern lightweight — callers dispatch through a uniform interface
        without needing a union input type or adapter layer. The tradeoff is
        that argument mismatches become runtime errors rather than type errors,
        but the small number of engines (3) and high test coverage make this
        acceptable.
        """
        ...
