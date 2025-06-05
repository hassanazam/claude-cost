# Claude Cost Analyzer

A comprehensive analysis tool for Claude conversation logs that calculates usage costs and provides detailed insights with a **powerful terminal dashboard** featuring rich visual layouts and real-time analytics.

## ✨ New Features

### 🚀 **Rich Terminal Dashboard** ✅ FIXED
- **Interactive CLI interface** with beautiful layouts and visual components
- **Real-time token tracking** (input, output, cache creation, cache reads)
- **Visual progress bars** and token distribution charts
- **Cache efficiency analytics** with ROI calculations
- **Auto-fallback** to simple mode when dependencies unavailable
- **Fixed layout rendering issues** for proper panel display

### 📊 **Enhanced Token Analytics**
- **Separate tracking** for all token types
- **Cache efficiency metrics** and cost savings analysis
- **Detailed cost breakdowns** by token category
- **Performance insights** across models and projects

## Features

- **🎯 Cost Analysis**: Calculate exact costs based on current Claude pricing (June 2025)
- **📁 Project Breakdown**: Analyze usage by project with detailed statistics
- **🤖 Model Comparison**: Compare usage across different Claude models (Opus 4, Sonnet 4, Haiku 3.5)
- **⚡ Cache Analytics**: Understand cache efficiency and savings potential
- **📈 Time-based Analysis**: Track usage trends over time
- **🎨 Rich Visualizations**: Terminal dashboard + charts and graphs
- **🛠 CLI Design Language**: Beautiful, consistent command-line interface

## Installation

```bash
# Quick setup - installs all dependencies
./setup.sh

# Or manually install
pip install -r requirements.txt
```

## Usage

### 🚀 **Terminal Dashboard (Recommended)**

```bash
# Launch interactive dashboard
./claude-cost dashboard

# Or run directly
python3 claude_dashboard.py
```

**Features:**
- 📊 Global overview with totals and date ranges
- 🤖 Model performance breakdown with efficiency metrics
- 🔤 Visual token distribution with progress bars
- 📁 Top projects ranked by cost
- ⚡ Cache analytics with ROI calculations
- **Auto-installs** rich library or falls back to simple mode

### 🔧 **Command Line Interface**

```bash
# Essential commands
./claude-cost dashboard      # 🚀 Rich terminal dashboard (NEW!)
./claude-cost quick          # Fast summary
./claude-cost detailed       # Full analysis with token breakdowns
./claude-cost visual         # Generate charts (requires matplotlib)
./claude-cost all           # Complete analysis suite
./claude-cost setup         # Install dependencies
./claude-cost help          # Show all options

# Analysis modes
./claude-cost summary        # Quick overview
./claude-cost projects       # Project breakdown
./claude-cost models         # Model usage comparison
```

### 📊 **Individual Analysis Tools**

#### 1. **Dashboard Mode** (Enhanced)
```bash
python3 claude_dashboard.py
```
Rich terminal interface with:
- Global cost and token overview
- Model performance comparison with cache efficiency
- Visual token distribution (input/output/cache)
- Top projects by cost
- Cache ROI analytics

#### 2. **Quick Summary** (No Dependencies)
```bash
python3 claude_cost_simple.py
```
Fast overview with key metrics:
- Total costs and token usage breakdown
- Top models and projects by cost
- Cache efficiency percentages
- Average costs per message

#### 3. **Detailed Analysis** (Enhanced)
```bash
python3 claude_cost_analyzer.py
```
Comprehensive breakdown with:
- **Separate token tracking** (input, output, cache creation, cache reads)
- **Detailed cost breakdowns** by token type
- Project-wise analysis with cache metrics
- Model comparison with efficiency ratings
- Time range analysis

#### 4. **Visual Analysis**
```bash
python3 claude_cost_visualizer.py

# Save charts without displaying
python3 claude_cost_visualizer.py --save-dir ./charts --no-show
```

#### 5. **Complete Analysis Suite**
```bash
python3 analyze_all.py
```

## 💰 Current Pricing (June 2025)

| Model | Input ($/MTok) | Output ($/MTok) | Cache Creation ($/MTok) | Cache Read ($/MTok) |
|-------|----------------|-----------------|-------------------------|---------------------|
| **Opus 4** | $15.00 | $75.00 | $18.75 | $1.50 |
| **Sonnet 4** | $3.00 | $15.00 | $3.75 | $0.30 |
| **Haiku 3.5** | $0.80 | $4.00 | $1.00 | $0.08 |

## 📈 Enhanced Output Examples

### Dashboard Mode (NEW - Rich Terminal Interface)
```
╭──────────────────────────────────────────────────────────────────────────────╮
│                         ⚡ CLAUDE COST DASHBOARD ⚡                          │
╰──────────────────────────────────────────────────────────────────────────────╯
╭───────────────────────────── 📊 Global Overview ─────────────────────────────╮
│ 🎯 Total Cost: $432.24                                                       │
│ 🔤 Total Tokens: 490,518,635                                                 │
│ 💬 Messages: 799                                                             │
│ 📁 Projects: 9                                                               │
│ 📅 Period: 2025-05-29 to 2025-06-04                                          │
│ 💰 Avg/Message: $0.5410                                                      │
╰──────────────────────────────────────────────────────────────────────────────╯
╭──────── 🤖 Model Performance ────────╮╭─────── 🔤 Token Distribution ────────╮
│ ┏━━━━━━┳━━━┳━━━━━━┳━━━━━┳━━━━━━┳━━━┓ ││ 🔵 Input:     █ 258,363 (0.1%)       │
│ ┃ Model┃ $  ┃ Input┃ Out┃ Cache┃ Eff┃ ││ 🟡 Output:    █ 1,442,550 (0.3%)     │
│ ┡━━━━━━╇━━━╇━━━━━━╇━━━━━╇━━━━━━╇━━━┩ ││ 🔴 Cache Cr:  █ 24,483,043 (5.0%)    │
│ │⚡Snt4│$$ │258,363│1.4M│24.5M │93%│ ││ 🟢 Cache Rd:  ████████████████████   │
╰──────────────────────────────────────╯╰──────────────────────────────────────╯
╭────────── 📁 Top Projects ───────────╮╭───────── ⚡ Cache Analytics ─────────╮
│ ┏━━━━━━━━━━━━━━┳━━━━┳━━━━┳━━━━━━━━━┓ ││ 💾 Cache Creation: $169.42           │
│ ┃ Project      ┃ Cost┃Msgs┃ Models  ┃ ││ ⚡ Cache Reads:    $221.64           │
│ ┡━━━━━━━━━━━━━━╇━━━━╇━━━━╇━━━━━━━━━┩ ││ 💰 Estimated Savings: $1994.74       │
│ │claude-cost   │$432│799 │⚡Sonnet4 │ ││ 📊 Cache ROI:      130.8%            │
╰──────────────────────────────────────╯╰──────────────────────────────────────╯
```

**Features:**
- Rich bordered panels with visual hierarchy
- Real-time data loading with progress indicators
- Interactive layout that adapts to terminal size
- Color-coded metrics and visual progress bars
- Fixed layout rendering for consistent display

### Detailed Analysis
```
📊 GLOBAL SUMMARY
Files processed: 56
Messages with usage data: 6,286
Projects: 9
Models used: claude-opus-4, claude-sonnet-4
Date range: 2025-05-29 to 2025-06-04

💰 GLOBAL COSTS BY MODEL

claude-sonnet-4:
  Input tokens: 158,405
  Output tokens: 1,078,020
  Cache creation tokens: 17,469,754
  Cache read tokens: 356,533,954
  Total tokens: 375,240,133
  Input cost: $0.48
  Output cost: $16.17
  Cache creation cost: $65.51
  Cache read cost: $106.96
  Total cost: $189.12

🎯 GLOBAL TOTALS
Total tokens: 449,370,816
Total cost: $412.51
```

## 🏗 Project Structure

```
claude-cost/
├── README.md                      # This file
├── requirements.txt               # Python dependencies (now includes rich)
├── setup.sh                      # Setup script
├── claude-cost                   # Enhanced CLI interface
├── claude_dashboard.py           # 🚀 Rich terminal dashboard (FIXED)
├── claude_dashboard_simple.py    # Simple dashboard fallback
├── analyze_all.py                # Complete analysis runner
├── claude_cost_simple.py         # Quick analysis (no deps)
├── claude_cost_analyzer.py       # Enhanced detailed analysis
├── claude_cost_visualizer.py     # Visual analysis with charts
├── CLAUDE.md                     # Development documentation
└── charts/                       # Generated visualizations
    ├── claude_usage_analysis.png
    ├── weekly_spending_trend.png
    └── model_comparison_radar.png
```

## 📋 Data Structure

The analyzer processes `.jsonl` files from `~/.claude/projects/` with enhanced token tracking:

```json
{
  "type": "assistant",
  "message": {
    "model": "claude-sonnet-4-20250514",
    "usage": {
      "input_tokens": 1234,           // Regular input processing
      "output_tokens": 567,           // Generated responses
      "cache_creation_input_tokens": 890,  // Creating cache entries
      "cache_read_input_tokens": 123       // Reading from cache
    }
  },
  "timestamp": "2025-06-04T10:30:00.000Z"
}
```

## 🔧 Requirements

### Core Functionality
- **Python 3.7+**
- No external dependencies for basic analysis

### Enhanced Features
- **rich** (terminal dashboard - auto-installed)
- **matplotlib** (charts and visualizations)
- **pandas** (data analysis)
- **seaborn** (enhanced visualizations)
- **numpy** (numerical operations)

## 🚀 Quick Start

1. **Clone and setup:**
   ```bash
   git clone <repository>
   cd claude-cost
   ./setup.sh
   ```

2. **Launch dashboard:**
   ```bash
   ./claude-cost dashboard
   ```

3. **Or try quick analysis:**
   ```bash
   ./claude-cost quick
   ```

## 💡 Key Insights

The enhanced analyzer provides powerful insights:

- **Cache Efficiency**: Track how effectively you're using Claude's caching
- **Cost Optimization**: Identify which projects and models are most expensive
- **Token Distribution**: Understand your usage patterns across token types
- **ROI Analysis**: Calculate savings from cache usage
- **Project Comparison**: Compare efficiency across different projects

## 🎯 CLI Design Principles

- **Visual Hierarchy**: Clear sections with emojis and consistent formatting
- **Progressive Disclosure**: From quick summaries to detailed breakdowns
- **Graceful Degradation**: Fallbacks when dependencies unavailable
- **Immediate Feedback**: Progress indicators and status messages
- **Actionable Insights**: Clear cost and efficiency metrics

## 🤝 Contributing

Feel free to submit issues and enhancement requests! Areas for contribution:
- Additional visualization modes
- Export formats
- Integration with CI/CD pipelines
- Custom reporting templates

## 📄 License

MIT License