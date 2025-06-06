# Claude Cost

[![PyPI version](https://badge.fury.io/py/claude-cost.svg)](https://badge.fury.io/py/claude-cost)
[![Python Support](https://img.shields.io/pypi/pyversions/claude-cost.svg)](https://pypi.org/project/claude-cost/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/claude-cost)](https://pepy.tech/project/claude-cost)

A comprehensive Claude usage analysis and optimization tool that calculates costs, provides optimization insights, and predicts usage limits. Analyze your Claude conversations with advanced metrics, cost optimization insights, and probabilistic usage predictions.

**Key Benefits:**
- 📊 **Zero external dependencies** for core functionality
- 🔍 **Comprehensive cost analysis** with cache optimization insights  
- 🔮 **Advanced prediction algorithms** with backtesting validation
- ⚡ **Real-time risk assessment** for usage limit management
- 🎯 **Actionable optimization recommendations**
- 🔒 **Privacy-first design** - only processes usage metadata, never message content

## Features

### 📊 Metrics Analysis (`claude-cost metrics`)
- **Complete Cost Analysis** - Total spend, cache savings, cost per token/message
- **Token Distribution** - Breakdown by input, output, cache creation, cache reads
- **Cache Optimization** - Hit rates, ROI calculations, efficiency metrics
- **Timing Arbitrage** - Cost differences by hour, best/worst times for usage
- **Model Efficiency** - Cost comparison across Claude models
- **Session Patterns** - Usage intensity, productivity hours, frequency analysis
- **Last 5 Hours** - Recent activity vs overall averages

### 🔮 Legacy Prediction Analysis (`claude-cost predict`)
- **Real-time Predictions** - Minutes/tokens/messages remaining to usage limit
- **3-Hour Rate Analysis** - Current usage rate from ALL jsonl files
- **5-Hour Pre-limit Patterns** - Historical analysis of usage before limits
- **Risk Assessment** - Current activity vs historical danger patterns
- **Backtesting Validation** - Algorithm accuracy: 66.7% (moderate, excellent for high-activity)

### 🔬 Advanced Probabilistic Predictions (`claude-cost advanced`) **NEW!**
- **Context Classification** - Automatically detects session type (exploration, coding, debugging, optimization)
- **Multi-Horizon Predictions** - 15min, 30min, 1hr, 2hr forecasts with confidence intervals
- **Uncertainty Quantification** - Statistical confidence bounds using log-normal distributions
- **Behavioral Feature Analysis** - 12+ features including rate variance, acceleration, complexity trends
- **Dynamic Risk Scoring** - Context-aware risk assessment (0-100 scale)
- **Actionable Insights** - Session-specific recommendations and warnings

## Installation

### From PyPI (Recommended)

```bash
pip install claude-cost
```

### From Source

```bash
git clone https://github.com/hassanazam/claude-cost.git
cd claude-cost
pip install -e .
```

## Usage

```bash
# Cost optimization and efficiency analysis
claude-cost metrics

# Legacy usage limit predictions with backtesting
claude-cost predict

# Advanced probabilistic predictions with context awareness (NEW!)
claude-cost advanced
```

### Python API

```python
from claude_cost import (
    calculate_comprehensive_metrics, 
    find_project_files,
    print_metrics_only,
    print_predictions_only,
    backtest_predictions
)

# Find Claude project files
files = find_project_files()

# Calculate comprehensive metrics
metrics, analysis_data, *additional_data = calculate_comprehensive_metrics(files)

# Display cost optimization analysis
print_metrics_only(metrics, analysis_data, *additional_data)

# Display usage limit predictions
print_predictions_only(metrics, analysis_data, *additional_data)

# Run prediction backtesting
backtest_predictions(files)
```

### Advanced Usage

```python
from claude_cost.models import PRICING, ComprehensiveMetrics
from claude_cost.advanced_predictions import run_advanced_predictions

# Access pricing data
sonnet_pricing = PRICING['claude-sonnet-4-20250514']
print(f"Input: ${sonnet_pricing['input']}/MTok, Output: ${sonnet_pricing['output']}/MTok")

# Run advanced probabilistic predictions
run_advanced_predictions(files)

# Work with metrics objects
if isinstance(metrics, ComprehensiveMetrics):
    print(f"Total cost: ${metrics.total_cost:.2f}")
    print(f"Cache savings: ${metrics.cache_savings:.2f}")
```

## Sample Usage Scenarios

### 📊 Basic Cost Analysis
```python
import claude_cost

# Quick cost analysis
files = claude_cost.find_project_files()
metrics, analysis_data, *_ = claude_cost.calculate_comprehensive_metrics(files)

print(f"💰 Total spend: ${metrics.total_cost:.2f}")
print(f"💾 Cache savings: ${metrics.cache_savings:.2f}")
print(f"📊 Total tokens: {metrics.total_tokens:,}")
print(f"⚡ Tokens per dollar: {metrics.tokens_per_dollar:,.0f}")
```

### 🔍 Detailed Analytics Dashboard
```python
import claude_cost

# Complete analysis workflow
files = claude_cost.find_project_files()
print(f"Found {len(files)} Claude project files")

# Generate comprehensive metrics
result = claude_cost.calculate_comprehensive_metrics(files)
metrics, analysis_data = result[0], result[1]

# Display full metrics analysis
claude_cost.print_metrics_only(metrics, analysis_data)

# Key insights
print(f"\n📈 KEY INSIGHTS:")
print(f"Cache hit rate: {metrics.cache_hit_rate:.1%}")
print(f"Average session cost: ${metrics.cost_per_session:.2f}")
print(f"Daily spend: ${metrics.per_day_spend_with_cache:.2f}")
```

### 🔮 Usage Limit Predictions
```python
import claude_cost

# Get data for predictions
files = claude_cost.find_project_files()
result = claude_cost.calculate_comprehensive_metrics(files)
metrics, analysis_data = result[0], result[1]

# Legacy prediction system
claude_cost.print_predictions_only(metrics, analysis_data, *result[2:])

# Advanced probabilistic predictions
claude_cost.print_advanced_predictions(analysis_data, result[2])
```

### 🔬 Advanced Programmatic Usage
```python
from claude_cost import (
    DataProcessor, MetricsCalculator, AdvancedPredictionEngine,
    find_project_files, get_recent_messages_for_advanced_prediction
)

# Manual data processing for custom analysis
files = find_project_files()
processor = DataProcessor()
processor.process_files(files)

# Custom metrics calculation
calculator = MetricsCalculator(processor)
metrics = calculator.calculate_metrics()

# Advanced predictions with custom parameters
recent_messages = get_recent_messages_for_advanced_prediction(
    processor.all_messages, hours=3
)

engine = AdvancedPredictionEngine()
predictions = engine.generate_predictions(
    recent_messages, 
    historical_patterns=[],
    horizons=[15, 30, 60, 120]  # Custom time horizons
)

for horizon, pred in predictions.items():
    print(f"{horizon}min: {pred.mean_minutes:.0f}min (risk: {pred.risk_score:.0f}%)")
```

### 💡 Cost Optimization Analysis
```python
import claude_cost

files = claude_cost.find_project_files()
metrics, analysis_data, *_ = claude_cost.calculate_comprehensive_metrics(files)

# Analyze cost efficiency
print("🎯 OPTIMIZATION OPPORTUNITIES:")

# Cache analysis
if metrics.cache_hit_rate < 0.5:
    potential_savings = metrics.total_cost * (0.5 - metrics.cache_hit_rate) * 0.75
    print(f"💾 Improve cache usage: +${potential_savings:.2f} potential savings")

# Model efficiency
model_usage = analysis_data['model_usage']
for model, data in model_usage.items():
    if isinstance(data, dict):
        efficiency = data['tokens'] / data['cost'] if data['cost'] > 0 else 0
        print(f"🤖 {model}: {efficiency:,.0f} tokens/$")

# Recent activity analysis
if metrics.last_5h_cost > 0:
    recent_efficiency = metrics.last_5h_cost / metrics.last_5h_tokens
    overall_efficiency = metrics.cost_per_token
    efficiency_ratio = recent_efficiency / overall_efficiency if overall_efficiency > 0 else 1
    
    if efficiency_ratio > 1.2:
        print(f"⚠️  Recent usage 20% less efficient than average")
    elif efficiency_ratio < 0.8:
        print(f"✅ Recent usage 20% more efficient than average")
```

### 📊 Custom Metrics Extraction
```python
from claude_cost import DataProcessor, find_project_files
from datetime import datetime, timedelta

# Process data manually for custom analysis
processor = DataProcessor()
files = find_project_files()
processor.process_files(files)

# Extract custom insights
print("📈 CUSTOM ANALYSIS:")

# Most expensive sessions
expensive_sessions = [
    s for s in processor.all_sessions 
    if s['total_cost'] > 5.0
]
print(f"💸 Expensive sessions (>$5): {len(expensive_sessions)}")

# Peak usage hours
hourly_costs = {}
for msg in processor.all_messages:
    if msg['timestamp']:
        hour = msg['timestamp'].hour
        hourly_costs[hour] = hourly_costs.get(hour, 0) + msg['cost']

peak_hour = max(hourly_costs.keys(), key=lambda h: hourly_costs[h])
print(f"⏰ Peak cost hour: {peak_hour:02d}:00 (${hourly_costs[peak_hour]:.2f})")

# Model distribution
model_counts = {}
for msg in processor.all_messages:
    model = msg['model']
    model_counts[model] = model_counts.get(model, 0) + 1

print(f"🤖 Model usage:")
for model, count in sorted(model_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"   {model}: {count} messages")
```

### 🧪 Backtesting & Validation
```python
import claude_cost

# Run prediction accuracy validation
files = claude_cost.find_project_files()
result = claude_cost.calculate_comprehensive_metrics(files)
analysis_data = result[1]

# Validate prediction algorithms
claude_cost.backtest_predictions(
    analysis_data['all_messages'], 
    analysis_data['limit_hits']
)
```

### 📱 Integration Example
```python
# Example: Integration with monitoring system
import claude_cost
import json

def check_usage_status():
    """Check current Claude usage status for monitoring."""
    try:
        files = claude_cost.find_project_files()
        if not files:
            return {"status": "no_data", "cost": 0}
        
        result = claude_cost.calculate_comprehensive_metrics(files)
        metrics = result[0]
        
        # Risk assessment
        risk_level = "low"
        if metrics.last_5h_cost > 10:  # $10 in last 5 hours
            risk_level = "high"
        elif metrics.last_5h_cost > 5:   # $5 in last 5 hours
            risk_level = "medium"
        
        return {
            "status": "active",
            "total_cost": round(metrics.total_cost, 2),
            "last_5h_cost": round(metrics.last_5h_cost, 2),
            "cache_efficiency": round(metrics.cache_hit_rate * 100, 1),
            "risk_level": risk_level,
            "daily_spend": round(metrics.per_day_spend_with_cache, 2)
        }
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Usage monitoring
status = check_usage_status()
print(json.dumps(status, indent=2))
```

## Requirements

- **Python 3.7+**
- **No external dependencies** for core functionality

### Optional Dependencies

For enhanced visualization (install with `pip install claude-cost[viz]`):
- matplotlib>=3.5.0
- pandas>=1.3.0  
- seaborn>=0.11.0
- numpy>=1.21.0
- rich>=13.0.0

## Pricing Model

Current Claude pricing (June 2025):
- **Opus 4**: $15.00/$75.00 input/output per MTok
- **Sonnet 4**: $3.00/$15.00 input/output per MTok  
- **Haiku 3.5**: $0.80/$4.00 input/output per MTok

Cache pricing included for creation and read operations.

## Data Processing & Privacy

**🔒 Privacy-First Design:** Claude Cost only processes usage metadata and never accesses message content, ensuring complete privacy protection.

**Data Sources:** Processes JSON Lines format from `~/.claude/projects/*/` looking for records with:
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

**What We Process:**
- ✅ Usage metadata (token counts, model names, timestamps)
- ✅ Cost calculations and efficiency metrics
- ✅ Session patterns and timing data

**What We DON'T Process:**
- ❌ Message content or conversation text
- ❌ Personal information or PII
- ❌ User prompts or Claude responses
- ❌ Any sensitive data

## Algorithm Comparison

### 🧪 Legacy Algorithm (`claude-cost predict`)
- **Method**: Deterministic rate-based extrapolation
- **Analysis Window**: Last 3 hours across all projects
- **Accuracy**: 66.7% overall (excellent for high-activity periods)
- **Best For**: Real-time monitoring during intensive usage
- **Output**: "45 minutes, 9M tokens, 130 messages to limit"

### 🔬 Advanced Algorithm (`claude-cost advanced`) 
- **Method**: Probabilistic context-aware ensemble with Bayesian inference
- **Features**: 12+ behavioral patterns, context classification, uncertainty quantification
- **Accuracy**: Designed for higher accuracy with statistical confidence bounds
- **Best For**: Strategic planning and session optimization
- **Output**: Multi-horizon forecasts with confidence intervals and actionable insights

## Package Structure

```
claude-cost/
├── src/claude_cost/
│   ├── __init__.py             # Package exports and API
│   ├── models.py               # Data models and pricing
│   ├── core.py                 # Core analysis logic
│   ├── metrics.py              # Metrics display functions
│   ├── predictions.py          # Legacy prediction and backtesting
│   ├── advanced_predictions.py # Advanced probabilistic predictions
│   └── cli.py                  # Command-line interface
├── pyproject.toml              # Package configuration
├── README.md                   # This file
└── LICENSE                     # MIT License
```

## Development

```bash
# Clone repository
git clone https://github.com/hassanazam/claude-cost.git
cd claude-cost

# Install in development mode
pip install -e .

# Run tests
claude-cost metrics
claude-cost predict
claude-cost advanced
```

## Publishing to PyPI

```bash
# Build package
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

## Contributing

This tool is designed to be self-contained with minimal dependencies. When contributing:

1. Keep core functionality dependency-free
2. Test with real Claude conversation data
3. Maintain timezone-aware analysis
4. Preserve backtesting validation
5. Follow the existing package structure

## License

MIT License - see [LICENSE](LICENSE) file for details.