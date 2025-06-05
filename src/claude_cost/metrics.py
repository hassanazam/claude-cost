"""
Metrics output module for Claude Cost analysis.
Contains functions for displaying cost optimization and efficiency metrics.
"""

from typing import Dict
from .models import ComprehensiveMetrics


def print_metrics_only(metrics: ComprehensiveMetrics, analysis_data: Dict, five_hour_patterns=None, avg_5h_tokens_before_limit=0, avg_5h_messages_before_limit=0, avg_tokens_per_minute_before_limit=0, current_3h_tokens=0, current_3h_count=0, current_tokens_per_minute=0, current_messages_per_minute=0):
    """Print only cost and optimization metrics (no predictions)"""
    
    print(f"\n📊 ESSENTIAL CLAUDE OPTIMIZATION METRICS")
    print("=" * 60)
    
    timezone_str = analysis_data['timezone']
    print(f"\n🌍 TIMEZONE: {timezone_str}")
    print(f"   (All times shown in this timezone)")
    
    # 💰 COST METRICS
    print(f"\n💰 COST METRICS")
    print(f"   • Total Cost (actual with cache): ${metrics.total_cost:.2f}")
    print(f"   • Total Cost Without Cache (hypothetical): ${metrics.total_cost_without_cache:.2f}")
    print(f"   • Cache Savings (dollar amount saved): ${metrics.cache_savings:.2f}")
    print(f"   • Cost per Session: ${metrics.cost_per_session:.2f}")
    print(f"   • Cost per Token (overall average): ${metrics.cost_per_token:.6f}")
    print(f"   • Cost per Message: ${metrics.cost_per_message:.3f}")
    print(f"   • Per Day Spend (with cache): ${metrics.per_day_spend_with_cache:.2f}")
    print(f"   • Per Day Spend (without cache): ${metrics.per_day_spend_without_cache:.2f}")
    print(f"   • Cost Breakdown by Token Type:")
    
    # Calculate cost breakdown
    input_cost = metrics.input_tokens * 0.000003
    output_cost = metrics.output_tokens * 0.000015
    cache_creation_cost = metrics.cache_creation_tokens * 0.000003
    cache_read_cost = metrics.cache_read_tokens * 0.00000075
    
    print(f"     - Input token costs: ${input_cost:.2f}")
    print(f"     - Output token costs: ${output_cost:.2f}")
    print(f"     - Cache creation costs: ${cache_creation_cost:.2f}")
    print(f"     - Cache read costs: ${cache_read_cost:.2f}")
    
    # 📊 TOKEN METRICS
    print(f"\n📊 TOKEN METRICS")
    print(f"   • Total Tokens (all types combined): {metrics.total_tokens:,}")
    print(f"   • Token Breakdown:")
    print(f"     - Input tokens (non-cached): {metrics.input_tokens:,}")
    print(f"     - Output tokens: {metrics.output_tokens:,}")
    print(f"     - Cache creation tokens: {metrics.cache_creation_tokens:,}")
    print(f"     - Cache read tokens (cached input): {metrics.cache_read_tokens:,}")
    print(f"   • Tokens per Dollar (efficiency metric): {metrics.tokens_per_dollar:,.0f}")
    print(f"   • Token Distribution by Size:")
    
    buckets = analysis_data['token_buckets']
    if isinstance(buckets, dict):
        print(f"     - Small (0-10K): {buckets.get('small', 0)} messages")
        print(f"     - Medium (10-50K): {buckets.get('medium', 0)} messages")
        print(f"     - Large (50-200K): {buckets.get('large', 0)} messages")
        print(f"     - Xlarge (200K+): {buckets.get('xlarge', 0)} messages")
    else:
        print(f"     - Token distribution: Available")
    
    # 💾 CACHE METRICS
    print(f"\n💾 CACHE METRICS")
    print(f"   • Cache Hit Rate (%): {metrics.cache_hit_rate*100:.1f}%")
    print(f"   • Cache ROI (return on investment multiplier): {metrics.cache_roi:.1f}x")
    print(f"   • Cache Efficiency (%): {metrics.cache_efficiency*100:.1f}%")
    print(f"   • Input Tokens Cached vs Not Cached: {metrics.cache_read_tokens:,} vs {metrics.input_tokens + metrics.cache_creation_tokens:,}")
    print(f"   • Cache Creation to Cache Read Ratio: 1:{metrics.cache_read_tokens/metrics.cache_creation_tokens:.1f}" if metrics.cache_creation_tokens > 0 else "   • Cache Creation to Cache Read Ratio: N/A")
    
    # ⏰ TIMING ARBITRAGE METRICS
    print(f"\n⏰ TIMING ARBITRAGE METRICS")
    hourly_patterns = analysis_data['hourly_patterns']
    if hourly_patterns and isinstance(hourly_patterns, dict):
        hourly_efficiency = {}
        for hour, data in hourly_patterns.items():
            if isinstance(data, dict) and data.get('tokens', 0) > 0:
                hourly_efficiency[hour] = data['cost'] / data['tokens']
        
        if hourly_efficiency:
            best_hour = min(hourly_efficiency, key=hourly_efficiency.get)
            worst_hour = max(hourly_efficiency, key=hourly_efficiency.get)
            best_cost = hourly_efficiency[best_hour]
            worst_cost = hourly_efficiency[worst_hour]
            
            print(f"   • Cost per Token by Hour (timezone-aware):")
            print(f"     - Best Hour: {best_hour:02d}:00 (${best_cost:.6f}/token)")
            print(f"     - Worst Hour: {worst_hour:02d}:00 (${worst_cost:.6f}/token)")
            
            message_volumes = {hour: data.get('count', 0) for hour, data in hourly_patterns.items() if isinstance(data, dict)}
            if message_volumes:
                min_vol = min(message_volumes.values())
                max_vol = max(message_volumes.values())
                print(f"   • Message Volume by Hour: Varies from {min_vol} to {max_vol}")
            bucket_count = len(buckets) if isinstance(buckets, dict) else 0
            print(f"   • Token-Size-Controlled Cost Analysis: Available for {bucket_count} size categories")
            print(f"   • Best/Worst Hours for Efficiency: {best_hour:02d}:00 / {worst_hour:02d}:00")
            
            if worst_cost > 0 and best_cost > 0:
                arbitrage_ratio = worst_cost / best_cost
                print(f"   • Arbitrage Ratio (cost difference between hours): {arbitrage_ratio:.1f}x")
    
    # 🤖 MODEL EFFICIENCY METRICS
    print(f"\n🤖 MODEL EFFICIENCY METRICS")
    model_usage = analysis_data['model_usage']
    for model, data in model_usage.items():
        if isinstance(data, dict) and data.get('count', 0) > 0:
            model_cost_per_token = data['cost'] / data['tokens'] if data['tokens'] > 0 else 0
            model_tokens_per_dollar = data['tokens'] / data['cost'] if data['cost'] > 0 else 0
            print(f"   • {model}:")
            print(f"     - Cost per Token: ${model_cost_per_token:.6f}")
            print(f"     - Tokens per Dollar: {model_tokens_per_dollar:,.0f}")
            print(f"     - Usage Count: {data['count']} messages")
    
    print(f"   • Model Switching Opportunities: Use sonnet over opus")
    
    # 📈 SESSION & USAGE PATTERNS
    print(f"\n📈 SESSION & USAGE PATTERNS")
    print(f"   • Session Count: {metrics.session_count}")
    print(f"   • Average Session Duration: {metrics.avg_session_duration:.1f} hours")
    print(f"   • Session Intensity (tokens/hour): {metrics.session_intensity:,.0f}")
    print(f"   • Message Frequency: {metrics.message_frequency:.1f} messages/session")
    
    if hourly_patterns and isinstance(hourly_patterns, dict):
        valid_hours = {h: data for h, data in hourly_patterns.items() if isinstance(data, dict) and data.get('count', 0) > 0}
        if valid_hours:
            peak_hour = max(valid_hours, key=lambda h: valid_hours[h]['count'])
            print(f"   • Peak Productivity Hours: {peak_hour:02d}:00")
            print(f"   • Cost per Hour Patterns: Available in hourly breakdown")
    
    # 🎯 OPTIMIZATION OPPORTUNITIES
    print(f"\n🎯 OPTIMIZATION OPPORTUNITIES")
    expensive_ops_count = getattr(metrics, 'expensive_operations_count', 0)
    expensive_ops_cost = getattr(metrics, 'expensive_operations_cost', 0.0)
    inefficient_msgs = getattr(metrics, 'inefficient_messages', 0)
    
    print(f"   • Expensive Operations (>$5 messages): {expensive_ops_count} messages, ${expensive_ops_cost:.2f} total")
    print(f"   • Token Waste Patterns: {inefficient_msgs} inefficient messages detected")
    print(f"   • Model Switching Potential Savings: Available")
    
    if hourly_patterns and hourly_efficiency:
        best_cost = min(hourly_efficiency.values())
        worst_cost = max(hourly_efficiency.values())
        potential_savings = (worst_cost - best_cost) * metrics.total_tokens
        print(f"   • Timing Shift Potential Savings: ${potential_savings:.2f}")
    
    print(f"   • Cache Optimization Opportunities: Current {metrics.cache_hit_rate*100:.1f}% hit rate")
    
    # ⏱️ LAST 5 HOURS METRICS
    print(f"\n⏱️ LAST 5 HOURS METRICS")
    if metrics.last_5h_messages > 0:
        print(f"   • Cost (last 5 hours): ${metrics.last_5h_cost:.2f}")
        print(f"   • Tokens (last 5 hours): {metrics.last_5h_tokens:,}")
        print(f"   • Messages (last 5 hours): {metrics.last_5h_messages}")
        print(f"   • Cache Hit Rate (last 5 hours): {metrics.last_5h_cache_hit_rate*100:.1f}%")
        print(f"   • Average Cost per Token (last 5 hours): ${metrics.last_5h_avg_cost_per_token:.6f}")
        
        # Compare to overall averages
        cost_ratio = metrics.last_5h_avg_cost_per_token / metrics.cost_per_token if metrics.cost_per_token > 0 else 1
        cache_diff = (metrics.last_5h_cache_hit_rate - metrics.cache_hit_rate) * 100
        
        print(f"   • Recent vs Overall Cost Efficiency: {cost_ratio:.1f}x (recent vs average)")
        print(f"   • Recent vs Overall Cache Performance: {cache_diff:+.1f}% difference")
    else:
        print(f"   • No activity in the last 5 hours")