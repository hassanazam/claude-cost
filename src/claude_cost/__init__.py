"""
Claude Cost - A comprehensive Claude usage analysis and optimization tool.

This package provides cost analysis, usage metrics, and limit prediction 
capabilities for Claude conversations.
"""

__version__ = "1.0.0"
__author__ = "Claude Cost Development Team"
__description__ = "Comprehensive Claude usage analysis and optimization tool"

from .core import calculate_comprehensive_metrics, find_project_files
from .metrics import print_metrics_only
from .predictions import print_predictions_only, backtest_predictions
from .models import ComprehensiveMetrics, PRICING

__all__ = [
    "calculate_comprehensive_metrics",
    "find_project_files", 
    "print_metrics_only",
    "print_predictions_only",
    "backtest_predictions",
    "ComprehensiveMetrics",
    "PRICING",
]