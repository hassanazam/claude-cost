"""
Core analysis functions for Claude Cost.

This module contains the main logic for processing Claude conversation logs
and calculating comprehensive metrics and predictions.
"""

import json
import os
import glob
import statistics
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple
from collections import defaultdict, Counter
from statistics import mean, median, stdev

from .models import ComprehensiveMetrics, PRICING


def find_project_files() -> List[str]:
    """Find all .jsonl files in Claude projects directory."""
    home = os.path.expanduser("~")
    pattern = os.path.join(home, ".claude", "projects", "*", "*.jsonl")
    return glob.glob(pattern)


def detect_timezone(timestamps: List[datetime]) -> str:
    """Detect timezone from timestamp patterns."""
    if not timestamps:
        return "UTC"
    
    sample_ts = timestamps[0]
    if sample_ts.tzinfo:
        return str(sample_ts.tzinfo)
    
    return "UTC"


def calculate_comprehensive_metrics(files: List[str]) -> Tuple[ComprehensiveMetrics, Dict, List, float, float, float, int, int, float, float]:
    """Calculate all essential optimization metrics."""
    
    all_messages = []
    all_sessions = []
    limit_hits = []
    hourly_patterns = defaultdict(list)
    model_usage = defaultdict(list)
    token_size_buckets = {'small': [], 'medium': [], 'large': [], 'xlarge': []}
    all_timestamps = []
    last_5h_messages = []
    
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