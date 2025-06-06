"""
Claude Cost - A comprehensive Claude usage analysis and optimization tool.

This package provides cost analysis, usage metrics, and limit prediction 
capabilities for Claude conversations.

Key Features:
- Zero external dependencies for core functionality
- Comprehensive cost analysis with cache optimization insights
- Advanced prediction algorithms with backtesting validation
- Real-time risk assessment for usage limit management
- Actionable optimization recommendations
"""

__version__ = "1.0.0"
__author__ = "Claude Cost Development Team"
__description__ = "Comprehensive Claude usage analysis and optimization tool"

# Core functionality
from .core import (
    calculate_comprehensive_metrics,
    find_project_files,
    DataProcessor,
    MetricsCalculator,
    PredictionAnalyzer
)

# Metrics and display
from .metrics import print_metrics_only, MetricsFormatter

# Legacy predictions
from .predictions import (
    print_predictions_only, 
    backtest_predictions,
    print_advanced_predictions
)

# Advanced predictions
from .advanced_predictions import (
    AdvancedPredictionEngine,
    AdvancedPredictionFormatter,
    SessionContext,
    PredictionResult,
    BehavioralFeatures,
    run_advanced_predictions,
    get_recent_messages_for_advanced_prediction,
    convert_legacy_patterns_to_advanced
)

# Data models and configuration
from .models import ComprehensiveMetrics, PRICING

# Public API - Main functions for library usage
__all__ = [
    # Core analysis
    "calculate_comprehensive_metrics",
    "find_project_files",
    
    # Display functions
    "print_metrics_only", 
    "print_predictions_only",
    "print_advanced_predictions",
    
    # Analysis engines (for advanced usage)
    "DataProcessor",
    "MetricsCalculator", 
    "PredictionAnalyzer",
    "MetricsFormatter",
    
    # Advanced prediction system
    "AdvancedPredictionEngine",
    "AdvancedPredictionFormatter",
    "run_advanced_predictions",
    "get_recent_messages_for_advanced_prediction",
    "convert_legacy_patterns_to_advanced",
    
    # Validation and testing
    "backtest_predictions",
    
    # Data structures
    "ComprehensiveMetrics",
    "PredictionResult", 
    "BehavioralFeatures",
    "SessionContext",
    
    # Configuration
    "PRICING",
]

# Library metadata
__title__ = "claude-cost"
__license__ = "MIT"
__copyright__ = "2025 Claude Cost Development Team"

# Version info for programmatic access
VERSION_INFO = {
    "major": 1,
    "minor": 0, 
    "patch": 0,
    "release": "stable"
}