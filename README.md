# Claude Cost

A comprehensive Claude usage analysis and optimization tool that calculates costs, provides optimization insights, and predicts usage limits. Processes `.jsonl` files from `~/.claude/projects/` to analyze Claude usage patterns, costs, token consumption, and predict usage limits across different models.

## Features

### 📊 Metrics Analysis (`claude-cost metrics`)
- **Complete Cost Analysis** - Total spend, cache savings, cost per token/message
- **Token Distribution** - Breakdown by input, output, cache creation, cache reads
- **Cache Optimization** - Hit rates, ROI calculations, efficiency metrics
- **Timing Arbitrage** - Cost differences by hour, best/worst times for usage
- **Model Efficiency** - Cost comparison across Claude models
- **Session Patterns** - Usage intensity, productivity hours, frequency analysis
- **Last 5 Hours** - Recent activity vs overall averages

### 🔮 Prediction Analysis (`claude-cost predict`)
- **Real-time Predictions** - Minutes/tokens/messages remaining to usage limit
- **3-Hour Rate Analysis** - Current usage rate from ALL jsonl files
- **5-Hour Pre-limit Patterns** - Historical analysis of usage before limits
- **Risk Assessment** - Current activity vs historical danger patterns
- **Backtesting Validation** - Algorithm accuracy: 66.7% (moderate, excellent for high-activity)

## Installation

### From PyPI (Recommended)

```bash
pip install claude-cost
```

### From Source

```bash
git clone https://github.com/your-username/claude-cost.git
cd claude-cost
pip install -e .
```

## Usage

```bash
# Cost optimization and efficiency analysis
claude-cost metrics

# Usage limit predictions with backtesting
claude-cost predict
```

### Python API

```python
from claude_cost import calculate_comprehensive_metrics, find_project_files
from claude_cost.metrics import print_metrics_only
from claude_cost.predictions import print_predictions_only

# Find Claude project files
files = find_project_files()

# Calculate comprehensive metrics
metrics, analysis_data, *additional_data = calculate_comprehensive_metrics(files)

# Display metrics
print_metrics_only(metrics, analysis_data, *additional_data)
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

## Data Processing

Processes JSON Lines format from `~/.claude/projects/*/` looking for records with:
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

## Key Insights

### Prediction Algorithm
- Analyzes last 3 hours across all projects
- Compares to historical 5-hour patterns before limits  
- Predicts time to danger zone based on current rate
- Shows actual values: "45 minutes, 9M tokens, 130 messages to limit"

### Backtesting Results
- **High-activity scenarios**: Perfect accuracy (0 minutes error)
- **Low-activity scenarios**: Poor accuracy (100-144% error)
- **Current confidence**: High for users with 1.3x+ intensity

## Package Structure

```
claude-cost/
├── src/claude_cost/
│   ├── __init__.py          # Package exports
│   ├── models.py            # Data models and pricing
│   ├── core.py              # Core analysis logic
│   ├── metrics.py           # Metrics display functions
│   ├── predictions.py       # Prediction and backtesting
│   └── cli.py               # Command-line interface
├── pyproject.toml           # Package configuration
├── README.md                # This file
└── LICENSE                  # MIT License
```

## Development

```bash
# Clone repository
git clone https://github.com/your-username/claude-cost.git
cd claude-cost

# Install in development mode
pip install -e .

# Run tests
claude-cost metrics
claude-cost predict
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