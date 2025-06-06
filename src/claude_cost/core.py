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


class DataProcessor:
    """Handles processing of Claude conversation log data."""
    
    def __init__(self):
        self.all_messages = []
        self.all_sessions = []
        self.limit_hits = []
        self.hourly_patterns = defaultdict(list)
        self.model_usage = defaultdict(list)
        self.token_size_buckets = {'small': [], 'medium': [], 'large': [], 'xlarge': []}
        self.all_timestamps = []
        self.last_5h_messages = []
        
        # Totals
        self.total_cost = 0.0
        self.total_tokens = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cache_creation_tokens = 0
        self.total_cache_read_tokens = 0
        
        self.current_session = None
        self.session_start = None
    
    def process_files(self, files: List[str]) -> None:
        """Process all JSONL files and extract message data."""
        print("📊 CALCULATING COMPREHENSIVE CLAUDE METRICS...")
        
        for file_path in files:
            self._process_single_file(file_path)
        
        # Add final session
        if self.current_session:
            self.all_sessions.append(self.current_session)
    
    def _process_single_file(self, file_path: str) -> None:
        """Process a single JSONL file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    self._process_line(line)
        except (FileNotFoundError, PermissionError):
            pass
    
    def _process_line(self, line: str) -> None:
        """Process a single line from JSONL file."""
        try:
            data = json.loads(line.strip())
            timestamp = self._extract_timestamp(data)
            
            if timestamp:
                self._handle_session_boundary(timestamp)
                self._check_for_limit_hits(data, timestamp)
            
            self._process_usage_data(data, timestamp)
            
        except (json.JSONDecodeError, KeyError, ValueError):
            pass
    
    def _extract_timestamp(self, data: dict) -> datetime:
        """Extract and parse timestamp from message data."""
        if 'timestamp' in data:
            timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
            self.all_timestamps.append(timestamp)
            return timestamp
        return None
    
    def _handle_session_boundary(self, timestamp: datetime) -> None:
        """Handle session boundary detection based on time gaps."""
        if self.session_start and (timestamp - self.session_start).total_seconds() > 3600:
            if self.current_session:
                self.all_sessions.append(self.current_session)
            self._start_new_session(timestamp)
        elif not self.current_session:
            self._start_new_session(timestamp)
    
    def _start_new_session(self, timestamp: datetime) -> None:
        """Start a new session."""
        self.current_session = {
            'start': timestamp, 
            'messages': [], 
            'total_cost': 0, 
            'total_tokens': 0
        }
        self.session_start = timestamp
    
    def _check_for_limit_hits(self, data: dict, timestamp: datetime) -> None:
        """
        Check if message indicates a usage limit hit using metadata only.
        
        Note: This method intentionally does NOT access message content 
        to protect user privacy and avoid PII exposure.
        """
        # Check for system-level indicators without accessing content
        if 'message' in data and isinstance(data['message'], dict):
            message = data['message']
            
            # Look for error codes or status indicators in metadata
            error_code = message.get('error_code')
            status = message.get('status')
            error_type = message.get('error_type', '').lower()
            
            # Check for usage limit indicators in metadata only
            is_usage_limit = (
                error_code in ['quota_exceeded', 'usage_limit_exceeded'] or
                status in ['limit_exceeded', 'quota_exceeded'] or
                error_type in ['usage_limit', 'quota_exceeded'] or
                # Check for missing usage data as potential indicator
                ('usage' not in message and 'error' in message)
            )
            
            if is_usage_limit and self.current_session:
                self.limit_hits.append({
                    'timestamp': timestamp,
                    'indicator': 'metadata_detected_limit',
                    'session_tokens': self.current_session['total_tokens'],
                    'session_messages': len(self.current_session['messages'])
                })
    
    def _process_usage_data(self, data: dict, timestamp: datetime) -> None:
        """Process message usage data and calculate costs."""
        if not (data.get('type') == 'assistant' and 
                'message' in data and 
                'usage' in data['message']):
            return
        
        model = data['message'].get('model', 'unknown')
        usage = data['message']['usage']
        
        # Extract token counts
        input_tokens = usage.get('input_tokens', 0)
        output_tokens = usage.get('output_tokens', 0)
        cache_creation_tokens = usage.get('cache_creation_input_tokens', 0)
        cache_read_tokens = usage.get('cache_read_input_tokens', 0)
        message_tokens = input_tokens + output_tokens + cache_creation_tokens + cache_read_tokens
        
        # Calculate costs
        message_cost = self._calculate_message_cost(
            model, input_tokens, output_tokens, cache_creation_tokens, cache_read_tokens
        )
        
        # Create message data object
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
        
        self._store_message_data(message_data, message_cost, message_tokens)
        self._categorize_message(message_data, model, message_tokens, message_cost)
    
    def _calculate_message_cost(self, model: str, input_tokens: int, output_tokens: int, 
                               cache_creation_tokens: int, cache_read_tokens: int) -> float:
        """Calculate cost for a single message."""
        if model not in PRICING:
            return 0.0
        
        pricing = PRICING[model]
        return (
            input_tokens / 1_000_000 * pricing['input'] +
            output_tokens / 1_000_000 * pricing['output'] +
            cache_creation_tokens / 1_000_000 * pricing['cache_creation'] +
            cache_read_tokens / 1_000_000 * pricing['cache_read']
        )
    
    def _store_message_data(self, message_data: dict, message_cost: float, message_tokens: int) -> None:
        """Store message data and update totals."""
        self.all_messages.append(message_data)
        
        # Check if message is from last 5 hours
        if message_data['timestamp']:
            current_time = datetime.now(message_data['timestamp'].tzinfo)
            five_hours_ago = current_time - timedelta(hours=5)
            if message_data['timestamp'] >= five_hours_ago:
                self.last_5h_messages.append(message_data)
        
        # Add to current session
        if self.current_session:
            self.current_session['messages'].append(message_data)
            self.current_session['total_cost'] += message_cost
            self.current_session['total_tokens'] += message_tokens
        
        # Accumulate totals
        self.total_cost += message_cost
        self.total_tokens += message_tokens
        self.total_input_tokens += message_data['input_tokens']
        self.total_output_tokens += message_data['output_tokens']
        self.total_cache_creation_tokens += message_data['cache_creation_tokens']
        self.total_cache_read_tokens += message_data['cache_read_tokens']
    
    def _categorize_message(self, message_data: dict, model: str, message_tokens: int, message_cost: float) -> None:
        """Categorize message by various criteria for analysis."""
        # Hourly patterns
        if message_data['timestamp']:
            self.hourly_patterns[message_data['timestamp'].hour].append(message_cost)
        
        # Model usage
        if message_tokens > 0:
            self.model_usage[model].append({
                'cost': message_cost,
                'tokens': message_tokens,
                'efficiency': message_tokens / message_cost if message_cost > 0 else 0
            })
        
        # Token size buckets
        if message_tokens <= 10000:
            self.token_size_buckets['small'].append(message_data)
        elif message_tokens <= 50000:
            self.token_size_buckets['medium'].append(message_data)
        elif message_tokens <= 200000:
            self.token_size_buckets['large'].append(message_data)
        else:
            self.token_size_buckets['xlarge'].append(message_data)


class MetricsCalculator:
    """Calculates comprehensive metrics from processed data."""
    
    def __init__(self, processor: DataProcessor):
        self.processor = processor
    
    def calculate_metrics(self) -> ComprehensiveMetrics:
        """Calculate all comprehensive metrics."""
        metrics = ComprehensiveMetrics()
        
        self._calculate_basic_metrics(metrics)
        self._calculate_cost_metrics(metrics)
        self._calculate_time_metrics(metrics)
        self._calculate_cache_metrics(metrics)
        self._calculate_session_metrics(metrics)
        self._calculate_limit_metrics(metrics)
        self._calculate_recent_metrics(metrics)
        
        return metrics
    
    def _calculate_basic_metrics(self, metrics: ComprehensiveMetrics) -> None:
        """Calculate basic token and cost totals."""
        metrics.total_cost = self.processor.total_cost
        metrics.total_tokens = self.processor.total_tokens
        metrics.input_tokens = self.processor.total_input_tokens
        metrics.output_tokens = self.processor.total_output_tokens
        metrics.cache_creation_tokens = self.processor.total_cache_creation_tokens
        metrics.cache_read_tokens = self.processor.total_cache_read_tokens
    
    def _calculate_cost_metrics(self, metrics: ComprehensiveMetrics) -> None:
        """Calculate cost-related metrics."""
        # Cost without cache (rough estimate using Sonnet pricing)
        metrics.total_cost_without_cache = (
            self.processor.total_input_tokens + 
            self.processor.total_cache_creation_tokens + 
            self.processor.total_cache_read_tokens
        ) * 0.000003 + self.processor.total_output_tokens * 0.000015
        
        # Calculate cache savings
        metrics.cache_savings = 0.0
        for model, usage_data in self.processor.model_usage.items():
            if model in PRICING:
                pricing = PRICING[model]
                cache_read_tokens_for_model = sum(
                    msg['cache_read_tokens'] for msg in self.processor.all_messages 
                    if msg['model'] == model
                )
                theoretical_cost = cache_read_tokens_for_model / 1_000_000 * pricing['input']
                actual_cost = cache_read_tokens_for_model / 1_000_000 * pricing['cache_read']
                metrics.cache_savings += (theoretical_cost - actual_cost)
        
        # Per-unit costs
        metrics.cost_per_session = (
            self.processor.total_cost / len(self.processor.all_sessions) 
            if self.processor.all_sessions else 0
        )
        metrics.cost_per_token = (
            self.processor.total_cost / self.processor.total_tokens 
            if self.processor.total_tokens > 0 else 0
        )
        metrics.cost_per_message = (
            self.processor.total_cost / len(self.processor.all_messages) 
            if self.processor.all_messages else 0
        )
        metrics.tokens_per_dollar = (
            self.processor.total_tokens / self.processor.total_cost 
            if self.processor.total_cost > 0 else 0
        )
    
    def _calculate_time_metrics(self, metrics: ComprehensiveMetrics) -> None:
        """Calculate time-based spending metrics."""
        if self.processor.all_timestamps:
            self.processor.all_timestamps.sort()
            days_span = max(1, (self.processor.all_timestamps[-1] - self.processor.all_timestamps[0]).days + 1)
            metrics.per_day_spend_with_cache = self.processor.total_cost / days_span
            metrics.per_day_spend_without_cache = metrics.total_cost_without_cache / days_span
        else:
            metrics.per_day_spend_with_cache = self.processor.total_cost
            metrics.per_day_spend_without_cache = metrics.total_cost_without_cache
    
    def _calculate_cache_metrics(self, metrics: ComprehensiveMetrics) -> None:
        """Calculate cache performance metrics."""
        total_input_like = (
            self.processor.total_input_tokens + 
            self.processor.total_cache_creation_tokens + 
            self.processor.total_cache_read_tokens
        )
        metrics.cache_hit_rate = (
            self.processor.total_cache_read_tokens / total_input_like 
            if total_input_like > 0 else 0
        )
        metrics.cache_roi = (
            metrics.cache_savings / (self.processor.total_cache_creation_tokens * 0.000003) 
            if self.processor.total_cache_creation_tokens > 0 else 0
        )
        metrics.cache_efficiency = metrics.cache_hit_rate * 100
    
    def _calculate_session_metrics(self, metrics: ComprehensiveMetrics) -> None:
        """Calculate session-related metrics."""
        metrics.session_count = len(self.processor.all_sessions)
        
        if self.processor.all_sessions:
            session_durations = []
            session_intensities = []
            
            for session in self.processor.all_sessions:
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
            metrics.message_frequency = len(self.processor.all_messages) / metrics.session_count
    
    def _calculate_limit_metrics(self, metrics: ComprehensiveMetrics) -> None:
        """Calculate usage limit related metrics."""
        metrics.total_limit_hits = len(self.processor.limit_hits)
        if self.processor.limit_hits:
            metrics.avg_tokens_before_limit = mean([hit['session_tokens'] for hit in self.processor.limit_hits])
            metrics.avg_messages_before_limit = mean([hit['session_messages'] for hit in self.processor.limit_hits])
    
    def _calculate_recent_metrics(self, metrics: ComprehensiveMetrics) -> None:
        """Calculate metrics for last 5 hours."""
        if self.processor.last_5h_messages:
            metrics.last_5h_cost = sum(msg['cost'] for msg in self.processor.last_5h_messages)
            metrics.last_5h_tokens = sum(msg['tokens'] for msg in self.processor.last_5h_messages)
            metrics.last_5h_messages = len(self.processor.last_5h_messages)
            
            # Calculate 5-hour cache hit rate
            last_5h_input_like = sum(
                msg['input_tokens'] + msg['cache_creation_tokens'] + msg['cache_read_tokens'] 
                for msg in self.processor.last_5h_messages
            )
            last_5h_cache_reads = sum(msg['cache_read_tokens'] for msg in self.processor.last_5h_messages)
            metrics.last_5h_cache_hit_rate = (
                last_5h_cache_reads / last_5h_input_like if last_5h_input_like > 0 else 0
            )
            
            # Calculate 5-hour average cost per token
            metrics.last_5h_avg_cost_per_token = (
                metrics.last_5h_cost / metrics.last_5h_tokens 
                if metrics.last_5h_tokens > 0 else 0
            )


class PredictionAnalyzer:
    """Analyzes usage patterns for limit predictions."""
    
    def __init__(self, processor: DataProcessor):
        self.processor = processor
        self.usage_limit_threshold = 9_000_000
    
    def analyze_five_hour_patterns(self) -> List[dict]:
        """Analyze 5-hour patterns before usage limits."""
        five_hour_patterns = []
        
        for hit in self.processor.limit_hits:
            if hit['timestamp']:
                five_hours_before = hit['timestamp'] - timedelta(hours=5)
                pre_limit_messages = [
                    msg for msg in self.processor.all_messages
                    if msg['timestamp'] and five_hours_before <= msg['timestamp'] < hit['timestamp']
                ]
                
                if pre_limit_messages:
                    pattern_data = {
                        'total_tokens': sum(msg['tokens'] for msg in pre_limit_messages),
                        'total_messages': len(pre_limit_messages),
                        'total_cost': sum(msg['cost'] for msg in pre_limit_messages),
                        'avg_tokens_per_minute': sum(msg['tokens'] for msg in pre_limit_messages) / (5 * 60),
                        'final_hour_tokens': sum(
                            msg['tokens'] for msg in pre_limit_messages[-60:]
                        ) if len(pre_limit_messages) > 60 else sum(
                            msg['tokens'] for msg in pre_limit_messages
                        ),
                        'limit_timestamp': hit['timestamp']
                    }
                    five_hour_patterns.append(pattern_data)
        
        return five_hour_patterns
    
    def get_current_three_hour_metrics(self) -> Tuple[int, int, float, float]:
        """Get current 3-hour activity metrics."""
        now = datetime.now(timezone.utc)
        three_hours_ago = now - timedelta(hours=3)
        
        current_3h_messages = [
            msg for msg in self.processor.all_messages
            if msg['timestamp'] and msg['timestamp'] >= three_hours_ago
        ]
        
        current_3h_tokens = sum(msg['tokens'] for msg in current_3h_messages)
        current_3h_count = len(current_3h_messages)
        current_tokens_per_minute = current_3h_tokens / 180.0 if current_3h_messages else 0
        current_messages_per_minute = current_3h_count / 180.0 if current_3h_messages else 0
        
        return current_3h_tokens, current_3h_count, current_tokens_per_minute, current_messages_per_minute
    
    def calculate_prediction_metrics(self, metrics: ComprehensiveMetrics, 
                                   five_hour_patterns: List[dict]) -> None:
        """Calculate prediction metrics for usage limits."""
        if not five_hour_patterns:
            metrics.minutes_to_next_limit = float('inf')
            metrics.tokens_to_next_limit = self.usage_limit_threshold
            metrics.current_session_risk_score = 0
            metrics.hours_to_next_limit = float('inf')
            return
        
        # Calculate averages from historical patterns
        avg_5h_tokens_before_limit = statistics.mean([p['total_tokens'] for p in five_hour_patterns])
        avg_tokens_per_minute_before_limit = statistics.mean([p['avg_tokens_per_minute'] for p in five_hour_patterns])
        
        current_3h_tokens, current_3h_count, current_tokens_per_minute, _ = self.get_current_three_hour_metrics()
        
        if avg_tokens_per_minute_before_limit > 0 and current_tokens_per_minute > 0:
            # Calculate danger threshold and predictions
            danger_threshold = avg_5h_tokens_before_limit * 0.8
            current_accumulated = current_3h_tokens
            
            if current_accumulated >= danger_threshold:
                # Already in danger zone
                remaining_to_limit = self.usage_limit_threshold
                minutes_to_limit = remaining_to_limit / current_tokens_per_minute
                tokens_to_limit = remaining_to_limit
            else:
                # Time to reach danger zone
                tokens_to_danger = danger_threshold - current_accumulated
                minutes_to_danger = tokens_to_danger / current_tokens_per_minute
                avg_time_from_pattern_to_limit = 60  # 1 hour average
                minutes_to_limit = minutes_to_danger + avg_time_from_pattern_to_limit
                tokens_to_limit = tokens_to_danger + (avg_time_from_pattern_to_limit * current_tokens_per_minute)
            
            metrics.minutes_to_next_limit = minutes_to_limit
            metrics.tokens_to_next_limit = int(tokens_to_limit)
            
            # Risk score
            risk_ratio = current_3h_tokens / (avg_5h_tokens_before_limit * 0.6) if avg_5h_tokens_before_limit > 0 else 0
            metrics.current_session_risk_score = min(100, risk_ratio * 100)
        else:
            metrics.minutes_to_next_limit = float('inf')
            metrics.tokens_to_next_limit = self.usage_limit_threshold
            metrics.current_session_risk_score = 0
        
        metrics.hours_to_next_limit = (
            metrics.minutes_to_next_limit / 60 
            if metrics.minutes_to_next_limit != float('inf') else float('inf')
        )


def calculate_comprehensive_metrics(files: List[str]) -> Tuple[ComprehensiveMetrics, Dict, List, float, float, float, int, int, float, float]:
    """
    Calculate all essential optimization metrics.
    
    This is the main entry point that coordinates the data processing,
    metrics calculation, and prediction analysis.
    
    PRIVACY NOTICE: This function only processes usage metadata (tokens, costs, 
    timestamps, models) and never accesses message content or PII.
    """
    # Process data
    processor = DataProcessor()
    processor.process_files(files)
    
    # Calculate metrics
    calculator = MetricsCalculator(processor)
    metrics = calculator.calculate_metrics()
    
    # Analyze predictions
    analyzer = PredictionAnalyzer(processor)
    five_hour_patterns = analyzer.analyze_five_hour_patterns()
    analyzer.calculate_prediction_metrics(metrics, five_hour_patterns)
    
    # Calculate additional prediction metrics for backward compatibility
    avg_5h_tokens_before_limit = (
        statistics.mean([p['total_tokens'] for p in five_hour_patterns])
        if five_hour_patterns else 0
    )
    avg_5h_messages_before_limit = (
        statistics.mean([p['total_messages'] for p in five_hour_patterns])
        if five_hour_patterns else 0
    )
    avg_tokens_per_minute_before_limit = (
        statistics.mean([p['avg_tokens_per_minute'] for p in five_hour_patterns])
        if five_hour_patterns else 0
    )
    
    current_3h_tokens, current_3h_count, current_tokens_per_minute, current_messages_per_minute = (
        analyzer.get_current_three_hour_metrics()
    )
    
    # Convert token size buckets to counts
    token_bucket_counts = {
        'small': len(processor.token_size_buckets['small']),
        'medium': len(processor.token_size_buckets['medium']),
        'large': len(processor.token_size_buckets['large']),
        'xlarge': len(processor.token_size_buckets['xlarge'])
    }
    
    return (
        metrics,
        {
            'hourly_patterns': dict(processor.hourly_patterns),
            'model_usage': dict(processor.model_usage),
            'token_buckets': token_bucket_counts,
            'timezone': detect_timezone(processor.all_timestamps),
            'limit_hits': processor.limit_hits,
            'all_messages': processor.all_messages
        },
        five_hour_patterns,
        avg_5h_tokens_before_limit,
        avg_5h_messages_before_limit,
        avg_tokens_per_minute_before_limit,
        current_3h_tokens,
        current_3h_count,
        current_tokens_per_minute,
        current_messages_per_minute
    )