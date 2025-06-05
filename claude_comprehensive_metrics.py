#!/usr/bin/env python3
"""
Claude Comprehensive Cost & Optimization Metrics Calculator
Implements all essential metrics for cost optimization, token efficiency, and limit avoidance
"""

import json
import os
import glob
import statistics
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple
from dataclasses import dataclass
from collections import defaultdict, Counter
from statistics import mean, median, stdev
import argparse

# Claude pricing (per million tokens)
PRICING = {
    'claude-opus-4-20250514': {'input': 15.00, 'output': 75.00, 'cache_creation': 18.75, 'cache_read': 1.50},
    'claude-sonnet-4-20250514': {'input': 3.00, 'output': 15.00, 'cache_creation': 3.75, 'cache_read': 0.30},
    'claude-haiku-3.5-20241022': {'input': 0.80, 'output': 4.00, 'cache_creation': 1.00, 'cache_read': 0.08}
}

@dataclass
class ComprehensiveMetrics:
    """Store all essential optimization metrics"""
    
    # Cost Metrics
    total_cost: float = 0.0
    total_cost_without_cache: float = 0.0
    cache_savings: float = 0.0
    cost_per_session: float = 0.0
    cost_per_token: float = 0.0
    cost_per_message: float = 0.0
    per_day_spend_with_cache: float = 0.0
    per_day_spend_without_cache: float = 0.0
    
    # Token Metrics
    total_tokens: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_tokens: int = 0
    cache_read_tokens: int = 0
    tokens_per_dollar: float = 0.0
    
    # Cache Metrics
    cache_hit_rate: float = 0.0
    cache_roi: float = 0.0
    cache_efficiency: float = 0.0
    
    # Session Metrics
    session_count: int = 0
    avg_session_duration: float = 0.0
    session_intensity: float = 0.0  # tokens/hour
    message_frequency: float = 0.0
    
    # Limit Metrics
    total_limit_hits: int = 0
    avg_tokens_before_limit: float = 0.0
    avg_messages_before_limit: float = 0.0
    
    # Prediction Metrics
    hours_to_next_limit: float = 0.0
    minutes_to_next_limit: float = 0.0
    tokens_to_next_limit: int = 0
    current_session_risk_score: float = 0.0
    
    # Last 5 Hours Metrics
    last_5h_cost: float = 0.0
    last_5h_tokens: int = 0
    last_5h_messages: int = 0
    last_5h_cache_hit_rate: float = 0.0
    last_5h_avg_cost_per_token: float = 0.0

def find_project_files() -> List[str]:
    """Find all .jsonl files"""
    home = os.path.expanduser("~")
    pattern = os.path.join(home, ".claude", "projects", "*", "*.jsonl")
    return glob.glob(pattern)

def detect_timezone(timestamps: List[datetime]) -> str:
    """Detect timezone from timestamp patterns"""
    if not timestamps:
        return "UTC"
    
    sample_ts = timestamps[0]
    if sample_ts.tzinfo:
        return str(sample_ts.tzinfo)
    
    return "UTC"

def calculate_comprehensive_metrics(files: List[str]) -> ComprehensiveMetrics:
    """Calculate all essential optimization metrics"""
    
    all_messages = []
    all_sessions = []
    limit_hits = []
    hourly_patterns = defaultdict(list)
    model_usage = defaultdict(list)
    token_size_buckets = {'small': [], 'medium': [], 'large': [], 'xlarge': []}
    all_timestamps = []
    last_5h_messages = []  # Track messages from last 5 hours
    
    # Totals
    total_cost = 0.0
    total_tokens = 0
    total_input_tokens = 0
    total_output_tokens = 0
    total_cache_creation_tokens = 0
    total_cache_read_tokens = 0
    
    current_session = None
    session_start = None
    
    print("📊 CALCULATING COMPREHENSIVE CLAUDE METRICS...")
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        
                        # Extract timestamp
                        timestamp = None
                        if 'timestamp' in data:
                            timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                            all_timestamps.append(timestamp)
                            
                            # Session boundary detection
                            if session_start and (timestamp - session_start).total_seconds() > 3600:
                                if current_session:
                                    all_sessions.append(current_session)
                                current_session = {'start': timestamp, 'messages': [], 'total_cost': 0, 'total_tokens': 0}
                                session_start = timestamp
                            elif not current_session:
                                current_session = {'start': timestamp, 'messages': [], 'total_cost': 0, 'total_tokens': 0}
                                session_start = timestamp
                        
                        # Check for limit hits
                        message_text = ""
                        if 'message' in data and isinstance(data['message'], dict):
                            if 'content' in data['message']:
                                if isinstance(data['message']['content'], str):
                                    message_text = data['message']['content'].lower()
                        
                        # Focus only on usage limits, not rate limits
                        usage_limit_indicators = ['usage limit', 'quota exceeded', 'limit exceeded']
                        for indicator in usage_limit_indicators:
                            if indicator in message_text and 'rate limit' not in message_text:
                                if current_session:
                                    limit_hits.append({
                                        'timestamp': timestamp,
                                        'indicator': indicator,
                                        'session_tokens': current_session['total_tokens'],
                                        'session_messages': len(current_session['messages'])
                                    })
                                break
                        
                        # Process usage data
                        if (data.get('type') == 'assistant' and 
                            'message' in data and 
                            'usage' in data['message']):
                            
                            model = data['message'].get('model', 'unknown')
                            usage = data['message']['usage']
                            
                            # Extract token counts
                            input_tokens = usage.get('input_tokens', 0)
                            output_tokens = usage.get('output_tokens', 0)
                            cache_creation_tokens = usage.get('cache_creation_input_tokens', 0)
                            cache_read_tokens = usage.get('cache_read_input_tokens', 0)
                            message_tokens = input_tokens + output_tokens + cache_creation_tokens + cache_read_tokens
                            
                            # Calculate costs
                            message_cost = 0.0
                            if model in PRICING:
                                pricing = PRICING[model]
                                message_cost = (
                                    input_tokens / 1_000_000 * pricing['input'] +
                                    output_tokens / 1_000_000 * pricing['output'] +
                                    cache_creation_tokens / 1_000_000 * pricing['cache_creation'] +
                                    cache_read_tokens / 1_000_000 * pricing['cache_read']
                                )
                            
                            # Store message data
                            message_data = {
                                'timestamp': timestamp,
                                'model': model,
                                'cost': message_cost,
                                'tokens': message_tokens,
                                'input_tokens': input_tokens,
                                'output_tokens': output_tokens,
                                'cache_creation_tokens': cache_creation_tokens,
                                'cache_read_tokens': cache_read_tokens,
                                'hour': timestamp.hour if timestamp else 0
                            }
                            
                            all_messages.append(message_data)
                            
                            # Check if message is from last 5 hours
                            if timestamp:
                                current_time = datetime.now(timestamp.tzinfo)
                                five_hours_ago = current_time - timedelta(hours=5)
                                if timestamp >= five_hours_ago:
                                    last_5h_messages.append(message_data)
                            
                            # Add to current session
                            if current_session:
                                current_session['messages'].append(message_data)
                                current_session['total_cost'] += message_cost
                                current_session['total_tokens'] += message_tokens
                            
                            # Accumulate totals
                            total_cost += message_cost
                            total_tokens += message_tokens
                            total_input_tokens += input_tokens
                            total_output_tokens += output_tokens
                            total_cache_creation_tokens += cache_creation_tokens
                            total_cache_read_tokens += cache_read_tokens
                            
                            # Hourly patterns
                            if timestamp:
                                hourly_patterns[timestamp.hour].append(message_cost)
                            
                            # Model usage
                            if message_tokens > 0:
                                model_usage[model].append({
                                    'cost': message_cost,
                                    'tokens': message_tokens,
                                    'efficiency': message_tokens / message_cost if message_cost > 0 else 0
                                })
                            
                            # Token size buckets
                            if message_tokens <= 10000:
                                token_size_buckets['small'].append(message_data)
                            elif message_tokens <= 50000:
                                token_size_buckets['medium'].append(message_data)
                            elif message_tokens <= 200000:
                                token_size_buckets['large'].append(message_data)
                            else:
                                token_size_buckets['xlarge'].append(message_data)
                    
                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue
        
        except (FileNotFoundError, PermissionError):
            continue
    
    # Add final session
    if current_session:
        all_sessions.append(current_session)
    
    # Calculate comprehensive metrics
    metrics = ComprehensiveMetrics()
    
    # Basic totals
    metrics.total_cost = total_cost
    metrics.total_tokens = total_tokens
    metrics.input_tokens = total_input_tokens
    metrics.output_tokens = total_output_tokens
    metrics.cache_creation_tokens = total_cache_creation_tokens
    metrics.cache_read_tokens = total_cache_read_tokens
    
    # Cost metrics
    metrics.total_cost_without_cache = (
        total_input_tokens + total_cache_creation_tokens + total_cache_read_tokens
    ) * 0.000003 + total_output_tokens * 0.000015  # Rough estimate using Sonnet pricing
    
    metrics.cache_savings = 0.0
    for model, usage_data in model_usage.items():
        if model in PRICING:
            pricing = PRICING[model]
            # Calculate what cache reads would cost as input tokens
            cache_read_tokens_for_model = sum(msg['cache_read_tokens'] for msg in all_messages if msg['model'] == model)
            theoretical_cost = cache_read_tokens_for_model / 1_000_000 * pricing['input']
            actual_cost = cache_read_tokens_for_model / 1_000_000 * pricing['cache_read']
            metrics.cache_savings += (theoretical_cost - actual_cost)
    
    metrics.session_count = len(all_sessions)
    metrics.cost_per_session = total_cost / len(all_sessions) if all_sessions else 0
    metrics.cost_per_token = total_cost / total_tokens if total_tokens > 0 else 0
    metrics.cost_per_message = total_cost / len(all_messages) if all_messages else 0
    metrics.tokens_per_dollar = total_tokens / total_cost if total_cost > 0 else 0
    
    # Time-based metrics
    if all_timestamps:
        all_timestamps.sort()
        days_span = max(1, (all_timestamps[-1] - all_timestamps[0]).days + 1)
        metrics.per_day_spend_with_cache = total_cost / days_span
        metrics.per_day_spend_without_cache = metrics.total_cost_without_cache / days_span
    else:
        metrics.per_day_spend_with_cache = total_cost
        metrics.per_day_spend_without_cache = metrics.total_cost_without_cache
    
    # Cache metrics
    total_input_like = total_input_tokens + total_cache_creation_tokens + total_cache_read_tokens
    metrics.cache_hit_rate = total_cache_read_tokens / total_input_like if total_input_like > 0 else 0
    metrics.cache_roi = metrics.cache_savings / (total_cache_creation_tokens * 0.000003) if total_cache_creation_tokens > 0 else 0
    metrics.cache_efficiency = metrics.cache_hit_rate * 100
    
    # Session metrics
    if all_sessions:
        session_durations = []
        session_intensities = []
        
        for session in all_sessions:
            if len(session['messages']) > 1:
                start_time = session['messages'][0]['timestamp']
                end_time = session['messages'][-1]['timestamp']
                if start_time and end_time:
                    duration_hours = (end_time - start_time).total_seconds() / 3600
                    session_durations.append(duration_hours)
                    if duration_hours > 0:
                        intensity = session['total_tokens'] / duration_hours
                        session_intensities.append(intensity)
        
        metrics.avg_session_duration = mean(session_durations) if session_durations else 0
        metrics.session_intensity = mean(session_intensities) if session_intensities else 0
        metrics.message_frequency = len(all_messages) / metrics.session_count
    
    # Limit metrics
    metrics.total_limit_hits = len(limit_hits)
    if limit_hits:
        metrics.avg_tokens_before_limit = mean([hit['session_tokens'] for hit in limit_hits])
        metrics.avg_messages_before_limit = mean([hit['session_messages'] for hit in limit_hits])
    
    # Last 5 hours metrics
    if last_5h_messages:
        metrics.last_5h_cost = sum(msg['cost'] for msg in last_5h_messages)
        metrics.last_5h_tokens = sum(msg['tokens'] for msg in last_5h_messages)
        metrics.last_5h_messages = len(last_5h_messages)
        
        # Calculate 5-hour cache hit rate
        last_5h_input_like = sum(msg['input_tokens'] + msg['cache_creation_tokens'] + msg['cache_read_tokens'] for msg in last_5h_messages)
        last_5h_cache_reads = sum(msg['cache_read_tokens'] for msg in last_5h_messages)
        metrics.last_5h_cache_hit_rate = last_5h_cache_reads / last_5h_input_like if last_5h_input_like > 0 else 0
        
        # Calculate 5-hour average cost per token
        metrics.last_5h_avg_cost_per_token = metrics.last_5h_cost / metrics.last_5h_tokens if metrics.last_5h_tokens > 0 else 0
    
    # 5-hour pattern analysis before usage limits
    five_hour_patterns = []
    for hit in limit_hits:
        if hit['timestamp']:
            # Find all messages in the 5 hours before this limit hit
            five_hours_before = hit['timestamp'] - timedelta(hours=5)
            pre_limit_messages = []
            
            for msg in all_messages:
                if msg['timestamp'] and five_hours_before <= msg['timestamp'] < hit['timestamp']:
                    pre_limit_messages.append(msg)
            
            if pre_limit_messages:
                pattern_data = {
                    'total_tokens': sum(msg['tokens'] for msg in pre_limit_messages),
                    'total_messages': len(pre_limit_messages),
                    'total_cost': sum(msg['cost'] for msg in pre_limit_messages),
                    'avg_tokens_per_minute': sum(msg['tokens'] for msg in pre_limit_messages) / (5 * 60),
                    'final_hour_tokens': sum(msg['tokens'] for msg in pre_limit_messages[-60:]) if len(pre_limit_messages) > 60 else sum(msg['tokens'] for msg in pre_limit_messages),
                    'limit_timestamp': hit['timestamp']
                }
                five_hour_patterns.append(pattern_data)
    
    # Calculate average 5-hour pattern before limits
    if five_hour_patterns:
        avg_5h_tokens_before_limit = statistics.mean([p['total_tokens'] for p in five_hour_patterns])
        avg_5h_messages_before_limit = statistics.mean([p['total_messages'] for p in five_hour_patterns])
        avg_tokens_per_minute_before_limit = statistics.mean([p['avg_tokens_per_minute'] for p in five_hour_patterns])
    else:
        avg_5h_tokens_before_limit = 0
        avg_5h_messages_before_limit = 0
        avg_tokens_per_minute_before_limit = 0
    
    # Predictive metrics (focus only on usage limits)
    usage_limit_threshold = 9_000_000  # Based on analysis of usage limits only
    
    # Current 3-hour rate analysis (always run, regardless of sessions)
    now = datetime.now(timezone.utc)
    three_hours_ago = now - timedelta(hours=3)
    current_3h_messages = []
    
    # Get ALL messages from last 3 hours across all files
    for msg in all_messages:
        if msg['timestamp'] and msg['timestamp'] >= three_hours_ago:
            current_3h_messages.append(msg)
    
    # Calculate current 3-hour metrics
    current_3h_tokens = sum(msg['tokens'] for msg in current_3h_messages) if current_3h_messages else 0
    current_3h_count = len(current_3h_messages)
    current_3h_cost = sum(msg['cost'] for msg in current_3h_messages) if current_3h_messages else 0
    
    # Calculate current rates (per hour and per minute)
    if current_3h_messages and len(current_3h_messages) > 0:
        # Use the full 3-hour window for rate calculation
        # This gives us the average rate over the complete 3-hour period
        actual_duration_hours = 3.0
        actual_duration_minutes = 180.0
        
        current_tokens_per_hour = current_3h_tokens / actual_duration_hours
        current_messages_per_hour = current_3h_count / actual_duration_hours
        current_tokens_per_minute = current_3h_tokens / actual_duration_minutes
        current_messages_per_minute = current_3h_count / actual_duration_minutes
    else:
        current_tokens_per_hour = current_tokens_per_minute = 0
        current_messages_per_hour = current_messages_per_minute = 0
    
    # Advanced prediction using current 3-hour rate vs 5-hour historical patterns
    if five_hour_patterns and avg_tokens_per_minute_before_limit > 0 and current_tokens_per_minute > 0:
        # Compare current rate to historical pre-limit rate
        rate_intensity = current_tokens_per_minute / avg_tokens_per_minute_before_limit
        
        # Estimate how much longer until we reach historical 5-hour pre-limit pattern
        historical_5h_total = avg_5h_tokens_before_limit
        
        # If we continue at current 3-hour rate, when will we hit the danger threshold?
        if current_tokens_per_minute > 0:
            # Time to reach 80% of historical 5-hour pattern (danger zone)
            danger_threshold = historical_5h_total * 0.8
            current_accumulated = current_3h_tokens
            
            if current_accumulated >= danger_threshold:
                # Already in danger zone - predict time to actual limit
                remaining_to_limit = usage_limit_threshold  # Assume we could hit limit
                minutes_to_limit = remaining_to_limit / current_tokens_per_minute
                tokens_to_limit = remaining_to_limit
                messages_to_limit = remaining_to_limit / (current_3h_tokens / current_3h_count) if current_3h_count > 0 else 0
            else:
                # Time to reach danger zone
                tokens_to_danger = danger_threshold - current_accumulated
                minutes_to_danger = tokens_to_danger / current_tokens_per_minute
                
                # Then add estimated time from danger to limit (based on historical patterns)
                avg_time_from_pattern_to_limit = 60  # Assume 1 hour average from danger to limit
                minutes_to_limit = minutes_to_danger + avg_time_from_pattern_to_limit
                tokens_to_limit = tokens_to_danger + (avg_time_from_pattern_to_limit * current_tokens_per_minute)
                messages_to_limit = tokens_to_limit / (current_3h_tokens / current_3h_count) if current_3h_count > 0 else 0
                
            metrics.minutes_to_next_limit = minutes_to_limit
            metrics.tokens_to_next_limit = int(tokens_to_limit)
            
            # Risk score based on current 3-hour accumulation vs historical patterns
            risk_ratio = current_3h_tokens / (historical_5h_total * 0.6) if historical_5h_total > 0 else 0  # 60% of 5h pattern
            metrics.current_session_risk_score = min(100, risk_ratio * 100)
        else:
            metrics.minutes_to_next_limit = float('inf')
            metrics.tokens_to_next_limit = usage_limit_threshold
            metrics.current_session_risk_score = 0
    else:
        # Fallback when no historical patterns or no current activity
        metrics.minutes_to_next_limit = float('inf')
        metrics.tokens_to_next_limit = usage_limit_threshold
        metrics.current_session_risk_score = 0
    
    metrics.hours_to_next_limit = metrics.minutes_to_next_limit / 60 if metrics.minutes_to_next_limit != float('inf') else float('inf')
    
    # Convert token size buckets to counts
    token_bucket_counts = {
        'small': len(token_size_buckets['small']),
        'medium': len(token_size_buckets['medium']),
        'large': len(token_size_buckets['large']),
        'xlarge': len(token_size_buckets['xlarge'])
    }
    
    return metrics, {
        'hourly_patterns': dict(hourly_patterns),
        'model_usage': dict(model_usage),
        'token_buckets': token_bucket_counts,
        'timezone': detect_timezone(all_timestamps),
        'limit_hits': limit_hits,
        'all_messages': all_messages
    }, five_hour_patterns, avg_5h_tokens_before_limit, avg_5h_messages_before_limit, avg_tokens_per_minute_before_limit, current_3h_tokens, current_3h_count, current_tokens_per_minute, current_messages_per_minute

def print_metrics_only(metrics: ComprehensiveMetrics, analysis_data: Dict, five_hour_patterns=None, avg_5h_tokens_before_limit=0, avg_5h_messages_before_limit=0, avg_tokens_per_minute_before_limit=0, current_3h_tokens=0, current_3h_count=0, current_tokens_per_minute=0, current_messages_per_minute=0):
    """Print all essential optimization metrics in the requested format"""
    
    print(f"\n📊 ESSENTIAL CLAUDE OPTIMIZATION METRICS")
    print("=" * 60)
    
    print(f"\n🌍 TIMEZONE: {analysis_data['timezone']}")
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
    input_cost = metrics.input_tokens / 1_000_000 * 3.0  # Approximate using Sonnet pricing
    output_cost = metrics.output_tokens / 1_000_000 * 15.0
    cache_creation_cost = metrics.cache_creation_tokens / 1_000_000 * 3.75
    cache_read_cost = metrics.cache_read_tokens / 1_000_000 * 0.30
    
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
    
    for size, messages in analysis_data['token_buckets'].items():
        if size == 'small':
            range_desc = "0-10K"
        elif size == 'medium':
            range_desc = "10-50K"
        elif size == 'large':
            range_desc = "50-200K"
        else:
            range_desc = "200K+"
        print(f"     - {size.title()} ({range_desc}): {len(messages)} messages")
    
    # 💾 CACHE METRICS
    print(f"\n💾 CACHE METRICS")
    print(f"   • Cache Hit Rate (%): {metrics.cache_hit_rate*100:.1f}%")
    print(f"   • Cache ROI (return on investment multiplier): {metrics.cache_roi:.1f}x")
    print(f"   • Cache Efficiency (%): {metrics.cache_efficiency:.1f}%")
    cached_tokens = metrics.cache_read_tokens
    not_cached_tokens = metrics.input_tokens + metrics.cache_creation_tokens
    print(f"   • Input Tokens Cached vs Not Cached: {cached_tokens:,} vs {not_cached_tokens:,}")
    cache_ratio = metrics.cache_read_tokens / metrics.cache_creation_tokens if metrics.cache_creation_tokens > 0 else 0
    print(f"   • Cache Creation to Cache Read Ratio: 1:{cache_ratio:.1f}")
    
    # ⏰ TIMING ARBITRAGE METRICS
    print(f"\n⏰ TIMING ARBITRAGE METRICS")
    
    # Calculate hourly efficiency and message volume
    hourly_efficiency = {}
    hourly_message_count = {}
    for hour, costs in analysis_data['hourly_patterns'].items():
        hour_messages = [msg for msg in analysis_data['all_messages'] if msg['hour'] == hour]
        hourly_message_count[hour] = len(hour_messages)
        if hour_messages:
            avg_cost_per_token = mean([msg['cost']/msg['tokens'] for msg in hour_messages if msg['tokens'] > 0])
            hourly_efficiency[hour] = avg_cost_per_token
    
    if hourly_efficiency:
        best_hour = min(hourly_efficiency.keys(), key=lambda h: hourly_efficiency[h])
        worst_hour = max(hourly_efficiency.keys(), key=lambda h: hourly_efficiency[h])
        arbitrage_ratio = hourly_efficiency[worst_hour] / hourly_efficiency[best_hour] if hourly_efficiency[best_hour] > 0 else 1
        
        min_volume = min(hourly_message_count.values()) if hourly_message_count else 0
        max_volume = max(hourly_message_count.values()) if hourly_message_count else 0
        
        print(f"   • Cost per Token by Hour (timezone-aware):")
        print(f"     - Best Hour: {best_hour:02d}:00 (${hourly_efficiency[best_hour]:.6f}/token)")
        print(f"     - Worst Hour: {worst_hour:02d}:00 (${hourly_efficiency[worst_hour]:.6f}/token)")
        print(f"   • Message Volume by Hour: Varies from {min_volume} to {max_volume}")
        print(f"   • Token-Size-Controlled Cost Analysis: Available for {len(analysis_data['token_buckets'])} size categories")
        print(f"   • Best/Worst Hours for Efficiency: {best_hour:02d}:00 / {worst_hour:02d}:00")
        print(f"   • Arbitrage Ratio (cost difference between hours): {arbitrage_ratio:.1f}x")
    else:
        print(f"   • Cost per Token by Hour: Insufficient data")
        print(f"   • Message Volume by Hour: Insufficient data")
        print(f"   • Token-Size-Controlled Cost Analysis: Insufficient data")
        print(f"   • Best/Worst Hours for Efficiency: Insufficient data")
        print(f"   • Arbitrage Ratio: Insufficient data")
    
    # 🚨 LIMIT DETECTION & PREDICTION
    print(f"\n🚨 LIMIT DETECTION & PREDICTION")
    print(f"   • Total Limit Hits: {metrics.total_limit_hits}")
    
    # Analyze limit types (focus only on usage limits)
    usage_limits = sum(1 for hit in analysis_data['limit_hits'] if 'usage limit' in hit['indicator'] or 'quota exceeded' in hit['indicator'] or 'limit exceeded' in hit['indicator'])
    print(f"   • Limit Types (usage limits only): {usage_limits} usage limit hits")
    
    print(f"   • Tokens Before Limit (average/median patterns): {metrics.avg_tokens_before_limit:,.0f} avg")
    print(f"   • Messages Before Limit: {metrics.avg_messages_before_limit:.0f} avg")
    
    # Time patterns and escalation analysis
    if analysis_data['limit_hits']:
        limit_hours = [hit['timestamp'].hour for hit in analysis_data['limit_hits'] if hit['timestamp']]
        if limit_hours:
            most_common_hour = max(set(limit_hours), key=limit_hours.count)
            print(f"   • Time Patterns of Limits: Most common at {most_common_hour:02d}:00")
        else:
            print(f"   • Time Patterns of Limits: No timestamp data available")
        
        # Calculate escalation patterns
        session_tokens_before_limits = [hit['session_tokens'] for hit in analysis_data['limit_hits'] if hit['session_tokens'] > 0]
        session_messages_before_limits = [hit['session_messages'] for hit in analysis_data['limit_hits'] if hit['session_messages'] > 0]
        
        if session_tokens_before_limits:
            avg_escalation_tokens = mean(session_tokens_before_limits)
            print(f"   • Cost Escalation Before Limits: Avg {avg_escalation_tokens:,.0f} tokens before hit")
        else:
            print(f"   • Cost Escalation Before Limits: No escalation data available")
        
        if session_messages_before_limits:
            avg_session_duration = mean(session_messages_before_limits) * 0.1  # Rough estimate
            print(f"   • Session Duration Before Limits: Avg {avg_session_duration:.1f}h before hit")
        else:
            print(f"   • Session Duration Before Limits: No duration data available")
    else:
        print(f"   • Time Patterns of Limits: No limit hits detected")
        print(f"   • Cost Escalation Before Limits: No limit hits to analyze")
        print(f"   • Session Duration Before Limits: No limit hits to analyze")
    
    # 🔮 PREDICTIVE LIMIT WARNINGS
    print(f"\n🔮 PREDICTIVE LIMIT WARNINGS:")
    
    # Display minutes if less than 2 hours, otherwise show hours
    if metrics.minutes_to_next_limit < 120 and metrics.minutes_to_next_limit != float('inf'):
        print(f"   • Minutes Left Before Next Usage Limit: {metrics.minutes_to_next_limit:.0f} minutes")
    else:
        if metrics.hours_to_next_limit == float('inf'):
            print(f"   • Hours Left Before Next Usage Limit: No active session")
        else:
            print(f"   • Hours Left Before Next Usage Limit: {metrics.hours_to_next_limit:.1f}h")
    
    print(f"   • Tokens Left Before Next Usage Limit: {metrics.tokens_to_next_limit:,}")
    print(f"   • Current Session Risk Score: {metrics.current_session_risk_score:.1f}%")
    
    burn_rate = metrics.per_day_spend_with_cache
    monthly_burn = burn_rate * 30
    print(f"   • Daily/Monthly Burn Rate vs Historical Limits: ${burn_rate:.2f}/day, ${monthly_burn:.2f}/month")
    
    # 🤖 MODEL EFFICIENCY METRICS
    print(f"\n🤖 MODEL EFFICIENCY METRICS")
    
    for model, usage_data in analysis_data['model_usage'].items():
        if usage_data:
            avg_efficiency = mean([data['efficiency'] for data in usage_data])
            total_cost = sum([data['cost'] for data in usage_data])
            total_tokens = sum([data['tokens'] for data in usage_data])
            cost_per_token = total_cost / total_tokens if total_tokens > 0 else 0
            tokens_per_dollar = total_tokens / total_cost if total_cost > 0 else 0
            
            model_name = model.replace('claude-', '').replace('-20250514', '').replace('-20241022', '')
            print(f"   • {model_name.title()}:")
            print(f"     - Cost per Token: ${cost_per_token:.6f}")
            print(f"     - Tokens per Dollar: {tokens_per_dollar:,.0f}")
            print(f"     - Usage Count: {len(usage_data)} messages")
    
    # Calculate model switching opportunities
    if len(analysis_data['model_usage']) > 1:
        efficiencies = [(model, mean([d['efficiency'] for d in data])) for model, data in analysis_data['model_usage'].items() if data]
        if efficiencies:
            best_model = max(efficiencies, key=lambda x: x[1])
            worst_model = min(efficiencies, key=lambda x: x[1])
            print(f"   • Model Switching Opportunities: Use {best_model[0].split('-')[1]} over {worst_model[0].split('-')[1]}")
    
    # 📈 SESSION & USAGE PATTERNS
    print(f"\n📈 SESSION & USAGE PATTERNS")
    print(f"   • Session Count: {metrics.session_count}")
    print(f"   • Average Session Duration: {metrics.avg_session_duration:.1f} hours")
    print(f"   • Session Intensity (tokens/hour): {metrics.session_intensity:,.0f}")
    print(f"   • Message Frequency: {metrics.message_frequency:.1f} messages/session")
    
    # Find peak productivity hour
    if analysis_data['hourly_patterns']:
        peak_hour = max(analysis_data['hourly_patterns'].keys(), 
                       key=lambda h: len(analysis_data['hourly_patterns'][h]))
        print(f"   • Peak Productivity Hours: {peak_hour:02d}:00")
    
    print(f"   • Cost per Hour Patterns: Available in hourly breakdown")
    
    # 🎯 OPTIMIZATION OPPORTUNITIES
    print(f"\n🎯 OPTIMIZATION OPPORTUNITIES")
    
    # Expensive operations
    expensive_ops = [msg for msg in analysis_data['all_messages'] if msg['cost'] > 5.0]
    expensive_cost = sum(msg['cost'] for msg in expensive_ops)
    print(f"   • Expensive Operations (>$5 messages): {len(expensive_ops)} messages, ${expensive_cost:.2f} total")
    
    # Token waste patterns
    low_efficiency_msgs = [msg for msg in analysis_data['all_messages'] 
                          if msg['tokens'] > 0 and (msg['cost']/msg['tokens']) > metrics.cost_per_token * 2]
    print(f"   • Token Waste Patterns: {len(low_efficiency_msgs)} inefficient messages detected")
    
    # Model switching savings
    if len(analysis_data['model_usage']) > 1:
        print(f"   • Model Switching Potential Savings: Available")
    
    # Timing shift savings
    if hourly_efficiency and len(hourly_efficiency) > 1:
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
    
    print(f"\n" + "=" * 60)
    
    # 🔮 PREDICTIVE LIMIT ALGORITHM
    print(f"\n🔮 PREDICTIVE LIMIT ALGORITHM")
    print(f"\nBased on your data patterns:")
    print(f"   • Usage Limit Threshold: ~9M tokens per session")
    
    if analysis_data['limit_hits']:
        limit_hours = [hit['timestamp'].hour for hit in analysis_data['limit_hits'] if hit['timestamp']]
        if limit_hours:
            most_common_hour = max(set(limit_hours), key=limit_hours.count)
            print(f"   • Time-based Pattern: Higher risk during {most_common_hour:02d}:00 {analysis_data['timezone']}")
    
    # Show 5-hour historical pattern analysis
    if five_hour_patterns:
        print(f"\n5-HOUR PRE-LIMIT PATTERNS (from {len(five_hour_patterns)} limit hits):")
        print(f"   • Average tokens in 5h before limit: {avg_5h_tokens_before_limit:,.0f}")
        print(f"   • Average messages in 5h before limit: {avg_5h_messages_before_limit:.0f}")
        print(f"   • Average token rate before limit: {avg_tokens_per_minute_before_limit:.0f}/min")
    
    # Show current 3-hour analysis (always displayed)
    print(f"\nCURRENT 3-HOUR ANALYSIS:")
    if current_3h_count > 0:
        print(f"   • Tokens (last 3 hours): {current_3h_tokens:,}")
        print(f"   • Messages (last 3 hours): {current_3h_count}")
        print(f"   • Current rate: {current_tokens_per_minute:.0f} tokens/min, {current_messages_per_minute:.1f} messages/min")
        
        # Compare current 3h vs historical 5h pattern
        if five_hour_patterns and avg_5h_tokens_before_limit > 0:
            pattern_ratio = current_3h_tokens / (avg_5h_tokens_before_limit * 0.6)  # 60% of 5h pattern
            risk_status = "⚠️ HIGH RISK" if pattern_ratio > 0.8 else "✅ SAFE"
            print(f"   • Current vs historical pattern: {pattern_ratio:.1f}x ({risk_status})")
            
            # Show rate comparison
            rate_comparison = current_tokens_per_minute / avg_tokens_per_minute_before_limit if avg_tokens_per_minute_before_limit > 0 else 0
            print(f"   • Rate intensity vs pre-limit average: {rate_comparison:.1f}x")
    else:
        print(f"   • No activity in the last 3 hours")
    
    print(f"\nCURRENT PREDICTIONS (based on 3-hour rate):")
    if metrics.minutes_to_next_limit == float('inf'):
        print(f"   • Minutes to Usage Limit: No current activity")
        print(f"   • Tokens to Usage Limit: {metrics.tokens_to_next_limit:,} tokens")
    else:
        print(f"   • Minutes to Usage Limit: {metrics.minutes_to_next_limit:.0f} minutes")
        print(f"   • Tokens to Usage Limit: {metrics.tokens_to_next_limit:,} tokens")
        if current_3h_count > 0:
            messages_to_limit = metrics.tokens_to_next_limit / (current_3h_tokens / current_3h_count) if current_3h_tokens > 0 else 0
            print(f"   • Messages to Usage Limit: {messages_to_limit:.0f} messages")
    print(f"   • Risk Score: {metrics.current_session_risk_score:.1f}%")

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

def print_predictions_only(metrics: ComprehensiveMetrics, analysis_data: Dict, five_hour_patterns=None, avg_5h_tokens_before_limit=0, avg_5h_messages_before_limit=0, avg_tokens_per_minute_before_limit=0, current_3h_tokens=0, current_3h_count=0, current_tokens_per_minute=0, current_messages_per_minute=0):
    """Print only prediction and limit analysis"""
    
    print(f"\n🔮 USAGE LIMIT PREDICTION ANALYSIS")
    print("=" * 60)
    
    timezone_str = analysis_data['timezone']
    print(f"\n🌍 TIMEZONE: {timezone_str}")
    print(f"   (All times shown in this timezone)")
    
    # 🚨 LIMIT DETECTION & PREDICTION
    print(f"\n🚨 LIMIT DETECTION & PREDICTION")
    print(f"   • Total Limit Hits: {metrics.total_limit_hits}")
    print(f"   • Limit Types (usage limits only): {metrics.total_limit_hits} usage limit hits")
    print(f"   • Tokens Before Limit (average/median patterns): {metrics.avg_tokens_before_limit:,.0f} avg")
    print(f"   • Messages Before Limit: {metrics.avg_messages_before_limit:.0f} avg")
    
    if analysis_data['limit_hits']:
        limit_hours = [hit['timestamp'].hour for hit in analysis_data['limit_hits'] if hit['timestamp']]
        if limit_hours:
            most_common_hour = max(set(limit_hours), key=limit_hours.count)
            print(f"   • Time Patterns of Limits: Most common at {most_common_hour:02d}:00")
    
    print(f"   • Cost Escalation Before Limits: Avg {metrics.avg_tokens_before_limit:,.0f} tokens before hit")
    
    session_duration_hours = metrics.avg_tokens_before_limit / 1000000 if metrics.avg_tokens_before_limit > 0 else 0
    print(f"   • Session Duration Before Limits: Avg {session_duration_hours:.1f}h before hit")
    
    # Show 5-hour historical pattern analysis
    if five_hour_patterns:
        print(f"\n5-HOUR PRE-LIMIT PATTERNS (from {len(five_hour_patterns)} limit hits):")
        print(f"   • Average tokens in 5h before limit: {avg_5h_tokens_before_limit:,.0f}")
        print(f"   • Average messages in 5h before limit: {avg_5h_messages_before_limit:.0f}")
        print(f"   • Average token rate before limit: {avg_tokens_per_minute_before_limit:.0f}/min")
    
    # Show current 3-hour analysis (always displayed)
    print(f"\nCURRENT 3-HOUR ANALYSIS:")
    if current_3h_count > 0:
        print(f"   • Tokens (last 3 hours): {current_3h_tokens:,}")
        print(f"   • Messages (last 3 hours): {current_3h_count}")
        print(f"   • Current rate: {current_tokens_per_minute:.0f} tokens/min, {current_messages_per_minute:.1f} messages/min")
        
        # Compare current 3h vs historical 5h pattern
        if five_hour_patterns and avg_5h_tokens_before_limit > 0:
            pattern_ratio = current_3h_tokens / (avg_5h_tokens_before_limit * 0.6)  # 60% of 5h pattern
            risk_status = "⚠️ HIGH RISK" if pattern_ratio > 0.8 else "✅ SAFE"
            print(f"   • Current vs historical pattern: {pattern_ratio:.1f}x ({risk_status})")
            
            # Show rate comparison
            rate_comparison = current_tokens_per_minute / avg_tokens_per_minute_before_limit if avg_tokens_per_minute_before_limit > 0 else 0
            print(f"   • Rate intensity vs pre-limit average: {rate_comparison:.1f}x")
    else:
        print(f"   • No activity in the last 3 hours")
    
    print(f"\nCURRENT PREDICTIONS (based on 3-hour rate):")
    if metrics.minutes_to_next_limit == float('inf'):
        print(f"   • Minutes to Usage Limit: No current activity")
        print(f"   • Tokens to Usage Limit: {metrics.tokens_to_next_limit:,} tokens")
    else:
        print(f"   • Minutes to Usage Limit: {metrics.minutes_to_next_limit:.0f} minutes")
        print(f"   • Tokens to Usage Limit: {metrics.tokens_to_next_limit:,} tokens")
        if current_3h_count > 0:
            messages_to_limit = metrics.tokens_to_next_limit / (current_3h_tokens / current_3h_count) if current_3h_tokens > 0 else 0
            print(f"   • Messages to Usage Limit: {messages_to_limit:.0f} messages")
    print(f"   • Risk Score: {metrics.current_session_risk_score:.1f}%")

def backtest_predictions(all_messages, limit_hits):
    """
    Backtest our prediction algorithm against historical data
    For each limit hit N, use data from limits 1 to N-1 to predict limit N
    """
    print(f"\n🧪 BACKTESTING PREDICTION ALGORITHM")
    print("=" * 60)
    
    if len(limit_hits) < 2:
        print("Need at least 2 limit hits for backtesting")
        return
    
    backtest_results = []
    
    for test_idx in range(1, len(limit_hits)):  # Start from 1 (need at least 1 previous limit)
        # Get the limit we're trying to predict
        target_limit = limit_hits[test_idx]
        target_timestamp = target_limit['timestamp']
        
        # Use only the previous limits (N-1) to build patterns
        training_limits = limit_hits[:test_idx]
        
        # Build 5-hour patterns from training data only
        training_patterns = []
        for hit in training_limits:
            if hit['timestamp']:
                five_hours_before = hit['timestamp'] - timedelta(hours=5)
                pre_limit_messages = []
                
                for msg in all_messages:
                    if msg['timestamp'] and five_hours_before <= msg['timestamp'] < hit['timestamp']:
                        pre_limit_messages.append(msg)
                
                if pre_limit_messages:
                    pattern_data = {
                        'total_tokens': sum(msg['tokens'] for msg in pre_limit_messages),
                        'total_messages': len(pre_limit_messages),
                        'avg_tokens_per_minute': sum(msg['tokens'] for msg in pre_limit_messages) / (5 * 60),
                    }
                    training_patterns.append(pattern_data)
        
        if not training_patterns:
            continue
            
        # Calculate training averages
        training_avg_tokens = statistics.mean([p['total_tokens'] for p in training_patterns])
        training_avg_rate = statistics.mean([p['avg_tokens_per_minute'] for p in training_patterns])
        
        # Now simulate our prediction algorithm at 3 hours before the target limit
        prediction_time = target_limit['timestamp'] - timedelta(hours=3)
        
        # Get the "current" 3-hour window as of prediction time
        three_hours_before_prediction = prediction_time - timedelta(hours=3)
        prediction_3h_messages = []
        
        for msg in all_messages:
            if msg['timestamp'] and three_hours_before_prediction <= msg['timestamp'] < prediction_time:
                prediction_3h_messages.append(msg)
        
        if not prediction_3h_messages:
            continue
            
        # Calculate prediction metrics
        pred_3h_tokens = sum(msg['tokens'] for msg in prediction_3h_messages)
        pred_3h_count = len(prediction_3h_messages)
        pred_tokens_per_minute = pred_3h_tokens / 180.0  # 3 hours = 180 minutes
        
        # Apply our prediction logic
        if training_avg_rate > 0 and pred_tokens_per_minute > 0:
            danger_threshold = training_avg_tokens * 0.8
            
            if pred_3h_tokens >= danger_threshold:
                # In danger zone - predict immediate limit
                predicted_minutes = 180  # Assume limit within 3 hours
            else:
                # Time to danger + buffer
                tokens_to_danger = danger_threshold - pred_3h_tokens
                minutes_to_danger = tokens_to_danger / pred_tokens_per_minute if pred_tokens_per_minute > 0 else float('inf')
                predicted_minutes = minutes_to_danger + 60  # Add 1 hour buffer
            
            # Calculate actual time to limit
            actual_minutes = (target_limit['timestamp'] - prediction_time).total_seconds() / 60
            
            # Store results
            error_minutes = abs(predicted_minutes - actual_minutes)
            error_percentage = (error_minutes / actual_minutes) * 100 if actual_minutes > 0 else 100
            
            backtest_results.append({
                'test_idx': test_idx,
                'training_limits': len(training_limits),
                'predicted_minutes': predicted_minutes,
                'actual_minutes': actual_minutes,
                'error_minutes': error_minutes,
                'error_percentage': error_percentage,
                'pred_3h_tokens': pred_3h_tokens,
                'pred_rate': pred_tokens_per_minute,
                'training_avg_tokens': training_avg_tokens,
                'target_timestamp': target_timestamp
            })
    
    # Display results
    if backtest_results:
        print(f"Tested {len(backtest_results)} predictions:")
        print()
        
        total_error = 0
        accurate_predictions = 0  # Within 30 minutes
        
        for i, result in enumerate(backtest_results):
            accuracy_status = "✅ ACCURATE" if result['error_minutes'] <= 30 else "❌ INACCURATE"
            if result['error_minutes'] <= 30:
                accurate_predictions += 1
                
            print(f"Test {i+1}: Limit at {result['target_timestamp'].strftime('%Y-%m-%d %H:%M')}")
            print(f"   • Training data: {result['training_limits']} previous limits")
            print(f"   • 3h activity: {result['pred_3h_tokens']:,} tokens, {result['pred_rate']:.0f} tok/min")
            print(f"   • Predicted: {result['predicted_minutes']:.0f} minutes to limit")
            print(f"   • Actual: {result['actual_minutes']:.0f} minutes to limit")
            print(f"   • Error: {result['error_minutes']:.0f} minutes ({result['error_percentage']:.1f}%) {accuracy_status}")
            print()
            
            total_error += result['error_percentage']
        
        # Summary statistics
        avg_error = total_error / len(backtest_results)
        accuracy_rate = (accurate_predictions / len(backtest_results)) * 100
        
        print(f"📊 BACKTESTING SUMMARY:")
        print(f"   • Total Tests: {len(backtest_results)}")
        print(f"   • Accurate Predictions (±30 min): {accurate_predictions}/{len(backtest_results)} ({accuracy_rate:.1f}%)")
        print(f"   • Average Error: {avg_error:.1f}%")
        
        if accuracy_rate >= 70:
            print(f"   • Algorithm Status: ✅ RELIABLE ({accuracy_rate:.1f}% accuracy)")
        elif accuracy_rate >= 50:
            print(f"   • Algorithm Status: ⚠️ MODERATE ({accuracy_rate:.1f}% accuracy)")
        else:
            print(f"   • Algorithm Status: ❌ NEEDS IMPROVEMENT ({accuracy_rate:.1f}% accuracy)")
    else:
        print("No valid backtest scenarios found")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Comprehensive Claude Cost & Optimization Metrics')
    parser.add_argument('command', nargs='?', default='metrics', choices=['metrics', 'predict'], 
                       help='Command to run: metrics (cost analysis) or predict (limit predictions)')
    args = parser.parse_args()
    
    if args.command == 'metrics':
        print("📊 CLAUDE COMPREHENSIVE METRICS CALCULATOR")
    else:
        print("🔮 CLAUDE USAGE LIMIT PREDICTOR")
    
    files = find_project_files()
    if not files:
        print("❌ No Claude project files found")
        return
    
    print(f"📁 Analyzing {len(files)} files...")
    
    metrics, analysis_data, five_hour_patterns, avg_5h_tokens_before_limit, avg_5h_messages_before_limit, avg_tokens_per_minute_before_limit, current_3h_tokens, current_3h_count, current_tokens_per_minute, current_messages_per_minute = calculate_comprehensive_metrics(files)
    
    if args.command == 'metrics':
        # Show comprehensive metrics without prediction sections
        print_metrics_only(metrics, analysis_data, five_hour_patterns, avg_5h_tokens_before_limit, avg_5h_messages_before_limit, avg_tokens_per_minute_before_limit, current_3h_tokens, current_3h_count, current_tokens_per_minute, current_messages_per_minute)
        print(f"\n✅ COMPREHENSIVE METRICS ANALYSIS COMPLETE!")
        
    elif args.command == 'predict':
        # Show only prediction-related analysis
        print_predictions_only(metrics, analysis_data, five_hour_patterns, avg_5h_tokens_before_limit, avg_5h_messages_before_limit, avg_tokens_per_minute_before_limit, current_3h_tokens, current_3h_count, current_tokens_per_minute, current_messages_per_minute)
        
        # Run backtesting to validate prediction accuracy
        backtest_predictions(analysis_data['all_messages'], analysis_data['limit_hits'])
        print(f"\n✅ PREDICTION ANALYSIS COMPLETE!")

if __name__ == "__main__":
    main()