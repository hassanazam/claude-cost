"""
Command-line interface for Claude Cost.

This module provides the main CLI entry point for the claude-cost package.
"""

import argparse
import sys
import os

from .core import find_project_files, calculate_comprehensive_metrics
from .metrics import print_metrics_only
from .predictions import print_predictions_only, print_advanced_predictions, backtest_predictions


def safe_print(text):
    """Print text with proper Unicode handling for cross-platform compatibility."""
    try:
        print(text, flush=True)
    except UnicodeEncodeError:
        # Fallback for systems that can't handle Unicode
        fallback_text = text.encode('ascii', 'replace').decode('ascii')
        print(fallback_text, flush=True)


def main():
    """Main CLI entry point."""
    # Set UTF-8 encoding for stdout if possible
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except (AttributeError, OSError):  # nosec B110
            # Ignore encoding errors - fallback handling in safe_print()
            pass
    
    parser = argparse.ArgumentParser(
        description='Claude Cost - Comprehensive Claude usage analysis and optimization',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  claude-cost metrics         # Essential optimization metrics
  claude-cost predict         # Legacy usage limit predictions with backtesting
  claude-cost advanced        # Advanced probabilistic predictions with context awareness
        """
    )
    
    parser.add_argument('command', nargs='?', default='metrics',
                       choices=['metrics', 'predict', 'advanced'],
                       help='What to analyze (default: metrics)')
    
    args = parser.parse_args()
    
    if args.command == 'metrics':
        safe_print("📊 CLAUDE COMPREHENSIVE METRICS CALCULATOR")
        safe_print("🔒 Privacy-first design: Only processes usage metadata, never message content")
    elif args.command == 'predict':
        safe_print("🔮 CLAUDE USAGE LIMIT PREDICTOR (Legacy)")
        safe_print("🔒 Privacy-first design: Only processes usage metadata, never message content")
    else:
        safe_print("🔬 CLAUDE ADVANCED PROBABILISTIC PREDICTOR")
        safe_print("🔒 Privacy-first design: Only processes usage metadata, never message content")
    
    # Find and analyze files
    files = find_project_files()
    if not files:
        safe_print("❌ No Claude project files found")
        sys.exit(1)
    
    safe_print(f"📁 Analyzing {len(files)} files...")
    
    # Calculate metrics
    result = calculate_comprehensive_metrics(files)
    metrics, analysis_data = result[0], result[1]
    five_hour_patterns = result[2]
    avg_5h_tokens_before_limit = result[3]
    avg_5h_messages_before_limit = result[4]
    avg_tokens_per_minute_before_limit = result[5]
    current_3h_tokens = result[6]
    current_3h_count = result[7]
    current_tokens_per_minute = result[8]
    current_messages_per_minute = result[9]
    
    # Display results based on command
    if args.command == 'metrics':
        print_metrics_only(
            metrics, analysis_data, five_hour_patterns, 
            avg_5h_tokens_before_limit, avg_5h_messages_before_limit, 
            avg_tokens_per_minute_before_limit, current_3h_tokens, 
            current_3h_count, current_tokens_per_minute, current_messages_per_minute
        )
        safe_print(f"\n✅ COMPREHENSIVE METRICS ANALYSIS COMPLETE!")
        
    elif args.command == 'predict':
        print_predictions_only(
            metrics, analysis_data, five_hour_patterns,
            avg_5h_tokens_before_limit, avg_5h_messages_before_limit,
            avg_tokens_per_minute_before_limit, current_3h_tokens,
            current_3h_count, current_tokens_per_minute, current_messages_per_minute
        )
        
        # Run backtesting to validate prediction accuracy
        backtest_predictions(analysis_data['all_messages'], analysis_data['limit_hits'])
        safe_print(f"\n✅ PREDICTION ANALYSIS COMPLETE!")
        
    elif args.command == 'advanced':
        # Show advanced probabilistic predictions
        print_advanced_predictions(analysis_data, five_hour_patterns)
        safe_print(f"\n✅ ADVANCED PREDICTION ANALYSIS COMPLETE!")


if __name__ == "__main__":
    main()