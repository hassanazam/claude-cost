# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude conversation log analysis tool that calculates usage costs and provides insights. It processes `.jsonl` files from `~/.claude/projects/` to analyze Claude usage patterns, costs, and token consumption across different models.

## Architecture

The project has a modular design with five main analysis tools:

1. **CLI Interface** (`claude-cost`) - Command-line wrapper for all tools
2. **Rich Dashboard** (`claude_dashboard.py`) - Interactive terminal dashboard with visual layouts ✅ FIXED
3. **Simple Analyzer** (`claude_cost_simple.py`) - Lightweight analysis with no dependencies
4. **Detailed Analyzer** (`claude_cost_analyzer.py`) - Comprehensive text-based analysis
5. **Visual Analyzer** (`claude_cost_visualizer.py`) - Chart and graph generation
6. **Complete Suite** (`analyze_all.py`) - Runs all tools in sequence

## Common Commands

### Setup and Installation
```bash
# Install dependencies
./setup.sh
# or manually
pip3 install -r requirements.txt
```

### Running Analysis
```bash
# Quick analysis (recommended for testing)
python3 claude_cost_simple.py

# Rich terminal dashboard (FIXED - layout rendering issues resolved)
python3 claude_dashboard.py

# Detailed text analysis
python3 claude_cost_analyzer.py

# Visual analysis with charts
python3 claude_cost_visualizer.py

# Complete analysis suite
python3 analyze_all.py
```

### CLI Interface
```bash
# Quick commands via CLI wrapper
./claude-cost dashboard      # Rich terminal dashboard (FIXED)
./claude-cost quick          # Fast summary
./claude-cost detailed       # Full analysis  
./claude-cost visual         # Generate charts
./claude-cost screenshot     # Generate shareable dashboard image (NEW)
./claude-cost all           # Complete suite
./claude-cost setup         # Install deps
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
# Test with minimal dependencies
python3 claude_cost_simple.py

# Test the fixed dashboard (recommended)
python3 claude_dashboard.py

# Verify chart generation
python3 claude_cost_visualizer.py --save-dir ./test_charts --no-show
```

## Key Functions to Know

- `find_project_files()` - Locates .jsonl files in ~/.claude/projects/
- `analyze_file()` - Processes individual .jsonl files
- `calculate_cost()` - Computes costs from usage data
- `normalize_model_name()` - Maps model names to pricing keys

## Dependencies

Required for full functionality:
- rich (terminal dashboard - auto-installed)
- matplotlib (charts)
- pandas (data analysis)
- seaborn (enhanced visualizations)
- numpy (numerical operations)

The simple analyzer has no external dependencies for basic functionality.

## New Features

### Terminal Dashboard ✅ FIXED
- **Rich CLI interface** with beautiful terminal layouts
- **Real-time token tracking** (input, output, cache creation, cache reads)
- **Visual token distribution** with progress bars
- **Cache efficiency analytics** and ROI calculations
- **Project breakdown** with model usage
- **Cost breakdowns** by token type
- Auto-installs dependencies on first run
- **Fixed layout rendering issues** - panels now display correctly
- **Improved data access patterns** - resolved defaultdict inconsistencies
- **Enhanced visual hierarchy** - proper bordered panel structure

## Troubleshooting

### Dashboard Issues
If you encounter layout problems with the dashboard:

```bash
# Common fixes for dashboard issues:
1. Ensure rich library is installed: pip install rich
2. Update terminal size: resize terminal window
3. Check Python version: python3 --version (requires 3.7+)
4. Use fallback mode: python3 claude_dashboard_simple.py
```

### Recent Fixes Applied
- **Layout rendering**: Fixed "Layout()" display issue by restructuring Rich layout system
- **Data access**: Resolved defaultdict inconsistencies causing panel failures
- **Token visualization**: Fixed progress bar display in token distribution panel

### Screenshot Dashboard Feature ✨ NEW
A new screenshot generator creates beautiful, shareable dashboard images:

**Key Features:**
- **Privacy-First**: All project names anonymized using consistent hashing
- **Inspiring Metrics**: Shows productivity score, time saved, efficiency ratings
- **Visual Impact**: Beautiful charts, gradients, and professional layout
- **Social Sharing**: Ready-to-share dashboard screenshots for inspiration
- **High Quality**: 300 DPI output perfect for social media or reports

**Usage:**
```bash
# Generate screenshot
python3 claude_screenshot_generator.py
./claude-cost screenshot

# Output: claude_dashboard_screenshot.png
```

**Metrics Showcased:**
- Total AI investment and productivity score
- Model usage distribution and efficiency
- Cache optimization and cost savings  
- Anonymized project breakdown
- Time saved estimates and token insights

### Known Working Commands
```bash
# These commands are verified to work:
python3 claude_dashboard.py         # Fixed dashboard
python3 claude_screenshot_generator.py  # Screenshot generator
python3 claude_cost_simple.py       # Always reliable fallback
./claude-cost dashboard             # CLI wrapper for dashboard
./claude-cost screenshot            # CLI wrapper for screenshots
```