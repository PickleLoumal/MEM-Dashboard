"""
Refinitiv Data Platform (RDP) Integration
Cloud-based REST API for financial data
"""

from .models import (
    AnalystConsensus,
    BalanceSheetMetrics,
    FinancialContext,
    KeyMetrics,
    PricingData,
    ProfitabilityMetrics,
    SegmentData,
    ValuationMetrics,
)
from .rdp_client import RDPClient

__all__ = [
    "AnalystConsensus",
    "BalanceSheetMetrics",
    "FinancialContext",
    "KeyMetrics",
    "PricingData",
    "ProfitabilityMetrics",
    "RDPClient",
    "SegmentData",
    "ValuationMetrics",
]
