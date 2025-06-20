# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude conversation log analysis tool that calculates usage costs and provides comprehensive optimization insights. It processes `.jsonl` files from `~/.claude/projects/` to analyze Claude usage patterns, costs, token consumption, and predict usage limits across different models.

## Architecture

The project has a clean, focused design with two main analysis tools:

1. **CLI Interface** (`claude-cost`) - Simple command-line wrapper
2. **Comprehensive Metrics Engine** (`claude_comprehensive_metrics.py`) - Core analysis with metrics and predictions

**Key Features:**
- **Cost Optimization Metrics** - Complete financial analysis with cache efficiency
- **Usage Limit Predictions** - Advanced 3-hour rate analysis with backtesting validation
- **Timezone-Aware Analysis** - All timestamps properly handled
- **Real-time Risk Assessment** - Predicts minutes/tokens/messages to usage limits

## Common Commands

### Setup and Installation
```bash
# Install dependencies (optional - no external deps required)
./setup.sh
# or manually
pip3 install -r requirements.txt
```

### Essential Commands
```bash
# Cost optimization and efficiency analysis
./claude-cost metrics

# Legacy usage limit predictions with backtesting
./claude-cost predict

# Advanced probabilistic predictions with context awareness (NEW!)
./claude-cost advanced
```

### Direct Usage
```bash
# Run metrics analysis directly
python3 claude_comprehensive_metrics.py metrics

# Run legacy prediction analysis directly  
python3 claude_comprehensive_metrics.py predict

# Run advanced probabilistic predictions directly
python3 claude_comprehensive_metrics.py advanced
```

## Data Processing Logic

The analyzers process JSON Lines format from `~/.claude/projects/*/` looking for records with this structure:
```json
{
  "type": "assistant",
  "message": {
    "model": "claude-sonnet-4-20250514",
    "usage": {
      "input_tokens": 1234,
      "output_tokens": 567,
      "cache_creation_input_tokens": 890,
      "cache_read_input_tokens": 123
    }
  },
  "timestamp": "2025-06-04T10:30:00.000Z"
}
```

## Pricing Model

Current Claude pricing (June 2025) is hardcoded in pricing dictionaries:
- Opus 4: $15.00/$75.00 input/output per MTok
- Sonnet 4: $3.00/$15.00 input/output per MTok  
- Haiku 3.5: $0.80/$4.00 input/output per MTok

Cache pricing is also included for creation and read operations.

## Testing

No formal test framework is configured. To verify functionality:
```bash
# Test cost optimization metrics
./claude-cost metrics

# Test usage limit predictions with backtesting validation
./claude-cost predict
```

## Key Functions to Know

- `calculate_comprehensive_metrics()` - Main analysis engine processing all data
- `print_metrics_only()` - Cost optimization and efficiency analysis output
- `print_predictions_only()` - Usage limit prediction and risk analysis output
- `backtest_predictions()` - Validates prediction accuracy against historical data
- `find_project_files()` - Locates .jsonl files in ~/.claude/projects/

## Dependencies

**No external dependencies required** - The core analysis runs with Python standard library only.

Optional dependencies can be installed via:
```bash
pip3 install -r requirements.txt
```

All analysis functions work without any external packages.

## Core Features

### 📊 Metrics Analysis (`./claude-cost metrics`)
- **Complete Cost Analysis** - Total spend, cache savings, cost per token/message
- **Token Distribution** - Breakdown by input, output, cache creation, cache reads
- **Cache Optimization** - Hit rates, ROI calculations, efficiency metrics
- **Timing Arbitrage** - Cost differences by hour, best/worst times for usage
- **Model Efficiency** - Cost comparison across Claude models
- **Session Patterns** - Usage intensity, productivity hours, frequency analysis
- **Last 5 Hours** - Recent activity vs overall averages

### 🔮 Legacy Prediction Analysis (`./claude-cost predict`)
- **Real-time Predictions** - Minutes/tokens/messages remaining to usage limit
- **3-Hour Rate Analysis** - Current usage rate from ALL jsonl files
- **5-Hour Pre-limit Patterns** - Historical analysis of usage before limits
- **Risk Assessment** - Current activity vs historical danger patterns
- **Backtesting Validation** - Algorithm accuracy: 66.7% (moderate, excellent for high-activity)

**Legacy Algorithm:**
- Analyzes last 3 hours across all projects
- Compares to historical 5-hour patterns before limits
- Predicts time to danger zone based on current rate
- Shows actual values: "45 minutes, 9M tokens, 130 messages to limit"

### 🔬 Advanced Probabilistic Predictions (`./claude-cost advanced`) **NEW!**
- **Context Classification** - Automatically detects session type (exploration, coding, debugging, optimization)
- **Multi-Horizon Predictions** - 15min, 30min, 1hr, 2hr forecasts with confidence intervals
- **Uncertainty Quantification** - Statistical confidence bounds using log-normal distributions
- **Behavioral Feature Analysis** - 12+ features including rate variance, acceleration, complexity trends
- **Dynamic Risk Scoring** - Context-aware risk assessment (0-100 scale)
- **Actionable Insights** - Session-specific recommendations and warnings

**Advanced Algorithm Features:**
- **Probabilistic Modeling**: Uses Bayesian inference with uncertainty quantification
- **Context Awareness**: Adapts predictions based on session type (exploration vs coding vs debugging)
- **Feature Engineering**: Extracts behavioral patterns, trends, and volatility metrics
- **Multi-Model Ensemble**: Different prediction models for different usage contexts
- **Statistical Rigor**: Confidence intervals, probability distributions, cross-validation

### 🧪 Algorithm Comparison
- **Legacy**: Deterministic rate-based extrapolation (66.7% accuracy)
- **Advanced**: Probabilistic context-aware ensemble (designed for higher accuracy with uncertainty bounds)

## Troubleshooting

### Common Issues
```bash
# If metrics command fails
python3 claude_comprehensive_metrics.py metrics

# If predictions seem inaccurate
# Algorithm works best during high-activity periods (1.3x+ intensity)
# Less reliable during low-activity periods

# Check Python version
python3 --version  # Requires 3.7+
```

### Known Working Commands
```bash
# These commands are verified to work:
./claude-cost metrics               # Cost optimization analysis
./claude-cost predict              # Legacy usage limit predictions  
./claude-cost advanced             # Advanced probabilistic predictions (NEW!)
python3 claude_comprehensive_metrics.py metrics   # Direct metrics
python3 claude_comprehensive_metrics.py predict   # Direct legacy predictions
python3 claude_comprehensive_metrics.py advanced  # Direct advanced predictions
```