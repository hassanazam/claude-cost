# Claude Cost CLI

[![PyPI version](https://badge.fury.io/py/claude-cost.svg)](https://badge.fury.io/py/claude-cost)
[![Python Support](https://img.shields.io/pypi/pyversions/claude-cost.svg)](https://pypi.org/project/claude-cost/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/claude-cost)](https://pepy.tech/project/claude-cost)

🚀 **Command-line tool** for analyzing your AI usage costs, optimizing spending, and predicting usage limits. Get comprehensive insights into your AI conversation patterns with advanced metrics and probabilistic predictions.

**Why Use This CLI Tool:**
- 📊 **Zero external dependencies** - works out of the box
- 🔍 **Comprehensive cost analysis** with cache optimization insights  
- 🔮 **Advanced prediction algorithms** with backtesting validation
- ⚡ **Real-time risk assessment** for usage limit management
- 🎯 **Actionable optimization recommendations**
- 🔒 **Privacy-first design** - only processes usage metadata, never message content
- ⚡ **Fast CLI interface** - get insights in seconds

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

## Quick Start

### Install via pip

```bash
pip install claude-cost
```

### Run analysis commands

```bash
# Get comprehensive cost analysis and optimization insights
claude-cost metrics

# Predict usage limits with backtesting validation  
claude-cost predict

# Advanced probabilistic predictions with context awareness
claude-cost advanced
```

### Installation from source

```bash
git clone https://github.com/hassanazam/claude-cost.git
cd claude-cost
pip install -e .
```

## CLI Commands

### 📊 Cost Analysis
```bash
claude-cost metrics
```
Get detailed cost breakdowns, cache efficiency analysis, and optimization recommendations.

### 🔮 Usage Predictions 
```bash
claude-cost predict
```
Predict usage limits with backtesting validation (66.7% accuracy).

### 🔬 Advanced Predictions
```bash
claude-cost advanced
```
Context-aware predictions with confidence intervals and behavioral analysis.

### Example Output
```bash
$ claude-cost metrics
📊 CALCULATING COMPREHENSIVE METRICS...

💰 TOTAL COST ANALYSIS
   • Total Spend: $45.67
   • Cache Savings: $12.34 (21.3%)
   • Daily Average: $3.24

🎯 OPTIMIZATION INSIGHTS
   • Cache Hit Rate: 67.8% (Excellent)
   • Cost per 1K tokens: $0.045
   • Most efficient model: Sonnet 4

⏰ TIMING ANALYSIS
   • Peak usage: 14:00-16:00 (34% of spend)
   • Best efficiency: 09:00-11:00
```

## Python API (Optional)

While primarily a CLI tool, you can also use the Python API for custom integrations:

```python
from claude_cost import (
    calculate_comprehensive_metrics, 
    find_project_files,
    print_metrics_only,
    print_predictions_only
)

# Find project files and run analysis
files = find_project_files()
metrics, analysis_data, *additional_data = calculate_comprehensive_metrics(files)

# Display results
print_metrics_only(metrics, analysis_data, *additional_data)
print_predictions_only(metrics, analysis_data, *additional_data)
```

## Use Cases & Examples

### 📊 Daily Cost Monitoring
```bash
# Quick daily check
claude-cost metrics | head -20

# Focus on recent activity
claude-cost metrics | grep -A 5 "LAST 5 HOURS"

# Check cache efficiency
claude-cost metrics | grep "Cache Hit Rate"
```

### 🔍 Cost Optimization Workflow
```bash
# Step 1: Get comprehensive overview
claude-cost metrics

# Step 2: Check usage patterns and risks
claude-cost predict

# Step 3: Get advanced insights for planning
claude-cost advanced

# Automate daily checks
echo "claude-cost metrics | head -10" >> ~/.bashrc
```

### 🔮 Proactive Usage Management
```bash
# Check current risk level
claude-cost predict | grep "Risk Score"

# Get detailed predictions with context
claude-cost advanced

# Set up alerts (example with cron)
echo "0 */3 * * * claude-cost predict | grep 'HIGH RISK' && notify-send 'Usage Alert'" | crontab -
```

### 🔬 CI/CD Integration
```bash
# Add to your deployment pipeline
#!/bin/bash
echo "Checking AI usage costs..."
claude-cost metrics > usage_report.txt

# Alert if daily costs exceed threshold
DAILY_COST=$(claude-cost metrics | grep "Daily Average" | grep -o '\$[0-9.]\+')
if (( $(echo "$DAILY_COST > 50" | bc -l) )); then
    echo "⚠️ High daily costs detected: $DAILY_COST"
    exit 1
fi
```

### 💡 Cost Optimization Tips
```bash
# Get optimization recommendations
claude-cost metrics | grep -A 10 "OPTIMIZATION"

# Compare model efficiency
claude-cost metrics | grep "tokens per dollar"

# Find your peak usage times
claude-cost metrics | grep -A 5 "HOURLY PATTERNS"

# Check cache performance
claude-cost metrics | grep "Cache"
```

### 📊 Monitoring & Automation
```bash
# Create daily usage report
#!/bin/bash
DATE=$(date +%Y-%m-%d)
echo "=== Usage Report for $DATE ===" > report_$DATE.txt
claude-cost metrics >> report_$DATE.txt
claude-cost predict >> report_$DATE.txt

# Weekly cost summary
claude-cost metrics | grep "Daily Average" | tail -7

# Set up usage alerts
alias usage-check='claude-cost predict | head -5'
alias cost-check='claude-cost metrics | head -10'
```

### 🧪 Prediction Accuracy Testing
```bash
# Test prediction accuracy against historical data
claude-cost predict | grep "Accuracy"

# Compare prediction algorithms
claude-cost predict  # Legacy algorithm
claude-cost advanced # Advanced algorithm

# Validate prediction reliability
claude-cost metrics | grep "Risk Score"
```

### 📱 Monitoring Dashboard
```bash
# Create a simple monitoring script
#!/bin/bash
# save as ~/bin/ai-dashboard

echo "🤖 AI Usage Dashboard - $(date)"
echo "================================"
claude-cost metrics | head -15
echo ""
echo "🔮 Current Predictions:"
claude-cost predict | head -8
echo ""
echo "📊 Advanced Analysis:"
claude-cost advanced | head -10

# Make executable and run
chmod +x ~/bin/ai-dashboard
./ai-dashboard
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