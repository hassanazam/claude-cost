"""
Metrics output module for Claude Cost analysis.
Contains functions for displaying cost optimization and efficiency metrics.
"""

from typing import Dict, Any, Optional
from .models import ComprehensiveMetrics


class MetricsFormatter:
    """Formats and displays comprehensive Claude usage metrics."""
    
    def __init__(self, metrics: ComprehensiveMetrics, analysis_data: Dict[str, Any]):
        self.metrics = metrics
        self.analysis_data = analysis_data
    
    def print_all_metrics(self, **kwargs) -> None:
        """Print complete metrics analysis."""
        self._print_header()
        self._print_timezone_info()
        self._print_cost_metrics()
        self._print_token_metrics()
        self._print_cache_metrics()
        self._print_timing_arbitrage_metrics()
        self._print_model_efficiency_metrics()
        self._print_session_patterns()
        self._print_optimization_opportunities()
        self._print_recent_activity()
    
    def _print_header(self) -> None:
        """Print main header."""
        print(f"\n📊 ESSENTIAL CLAUDE OPTIMIZATION METRICS")
        print("=" * 60)
    
    def _print_timezone_info(self) -> None:
        """Print timezone information."""
        timezone_str = self.analysis_data.get('timezone', 'UTC')
        print(f"\n🌍 TIMEZONE: {timezone_str}")
        print(f"   (All times shown in this timezone)")
    
    def _print_cost_metrics(self) -> None:
        """Print comprehensive cost analysis."""
        print(f"\n💰 COST METRICS")
        print(f"   • Total Cost (actual with cache): ${self.metrics.total_cost:.2f}")
        print(f"   • Total Cost Without Cache (hypothetical): ${self.metrics.total_cost_without_cache:.2f}")
        print(f"   • Cache Savings (dollar amount saved): ${self.metrics.cache_savings:.2f}")
        print(f"   • Cost per Session: ${self.metrics.cost_per_session:.2f}")
        print(f"   • Cost per Token (overall average): ${self.metrics.cost_per_token:.6f}")
        print(f"   • Cost per Message: ${self.metrics.cost_per_message:.3f}")
        print(f"   • Per Day Spend (with cache): ${self.metrics.per_day_spend_with_cache:.2f}")
        print(f"   • Per Day Spend (without cache): ${self.metrics.per_day_spend_without_cache:.2f}")
        
        self._print_cost_breakdown()
    
    def _print_cost_breakdown(self) -> None:
        """Print detailed cost breakdown by token type."""
        print(f"   • Cost Breakdown by Token Type:")
        
        # Calculate cost breakdown using estimated Sonnet pricing
        input_cost = self.metrics.input_tokens * 0.000003
        output_cost = self.metrics.output_tokens * 0.000015
        cache_creation_cost = self.metrics.cache_creation_tokens * 0.000003
        cache_read_cost = self.metrics.cache_read_tokens * 0.00000075
        
        print(f"     - Input token costs: ${input_cost:.2f}")
        print(f"     - Output token costs: ${output_cost:.2f}")
        print(f"     - Cache creation costs: ${cache_creation_cost:.2f}")
        print(f"     - Cache read costs: ${cache_read_cost:.2f}")
    
    def _print_token_metrics(self) -> None:
        """Print token usage statistics."""
        print(f"\n📊 TOKEN METRICS")
        print(f"   • Total Tokens (all types combined): {self.metrics.total_tokens:,}")
        print(f"   • Token Breakdown:")
        print(f"     - Input tokens (non-cached): {self.metrics.input_tokens:,}")
        print(f"     - Output tokens: {self.metrics.output_tokens:,}")
        print(f"     - Cache creation tokens: {self.metrics.cache_creation_tokens:,}")
        print(f"     - Cache read tokens (cached input): {self.metrics.cache_read_tokens:,}")
        print(f"   • Tokens per Dollar (efficiency metric): {self.metrics.tokens_per_dollar:,.0f}")
        
        self._print_token_distribution()
    
    def _print_token_distribution(self) -> None:
        """Print token size distribution."""
        print(f"   • Token Distribution by Size:")
        
        buckets = self.analysis_data.get('token_buckets', {})
        if isinstance(buckets, dict):
            print(f"     - Small (0-10K): {buckets.get('small', 0)} messages")
            print(f"     - Medium (10-50K): {buckets.get('medium', 0)} messages")
            print(f"     - Large (50-200K): {buckets.get('large', 0)} messages")
            print(f"     - Xlarge (200K+): {buckets.get('xlarge', 0)} messages")
        else:
            print(f"     - Token distribution: Available")
    
    def _print_cache_metrics(self) -> None:
        """Print cache performance analysis."""
        print(f"\n💾 CACHE METRICS")
        print(f"   • Cache Hit Rate (%): {self.metrics.cache_hit_rate*100:.1f}%")
        print(f"   • Cache ROI (return on investment multiplier): {self.metrics.cache_roi:.1f}x")
        print(f"   • Cache Efficiency (%): {self.metrics.cache_efficiency:.1f}%")
        
        total_non_cached = self.metrics.input_tokens + self.metrics.cache_creation_tokens
        print(f"   • Input Tokens Cached vs Not Cached: {self.metrics.cache_read_tokens:,} vs {total_non_cached:,}")
        
        if self.metrics.cache_creation_tokens > 0:
            cache_ratio = self.metrics.cache_read_tokens / self.metrics.cache_creation_tokens
            print(f"   • Cache Creation to Cache Read Ratio: 1:{cache_ratio:.1f}")
        else:
            print(f"   • Cache Creation to Cache Read Ratio: N/A")
    
    def _print_timing_arbitrage_metrics(self) -> None:
        """Print timing-based cost optimization opportunities."""
        print(f"\n⏰ TIMING ARBITRAGE METRICS")
        
        hourly_patterns = self.analysis_data.get('hourly_patterns', {})
        if not hourly_patterns or not isinstance(hourly_patterns, dict):
            print(f"   • No hourly pattern data available")
            return
        
        hourly_efficiency = self._calculate_hourly_efficiency(hourly_patterns)
        if not hourly_efficiency:
            print(f"   • Insufficient data for hourly analysis")
            return
        
        best_hour = min(hourly_efficiency, key=hourly_efficiency.get)
        worst_hour = max(hourly_efficiency, key=hourly_efficiency.get)
        best_cost = hourly_efficiency[best_hour]
        worst_cost = hourly_efficiency[worst_hour]
        
        print(f"   • Cost per Token by Hour (timezone-aware):")
        print(f"     - Best Hour: {best_hour:02d}:00 (${best_cost:.6f}/token)")
        print(f"     - Worst Hour: {worst_hour:02d}:00 (${worst_cost:.6f}/token)")
        
        self._print_hourly_patterns(hourly_patterns, best_hour, worst_hour, best_cost, worst_cost)
    
    def _calculate_hourly_efficiency(self, hourly_patterns: Dict) -> Dict[int, float]:
        """Calculate cost efficiency by hour."""
        hourly_efficiency = {}
        for hour, data in hourly_patterns.items():
            if isinstance(data, dict) and data.get('tokens', 0) > 0:
                hourly_efficiency[hour] = data['cost'] / data['tokens']
        return hourly_efficiency
    
    def _print_hourly_patterns(self, hourly_patterns: Dict, best_hour: int, worst_hour: int, 
                              best_cost: float, worst_cost: float) -> None:
        """Print detailed hourly pattern analysis."""
        message_volumes = {
            hour: data.get('count', 0) 
            for hour, data in hourly_patterns.items() 
            if isinstance(data, dict)
        }
        
        if message_volumes:
            min_vol = min(message_volumes.values())
            max_vol = max(message_volumes.values())
            print(f"   • Message Volume by Hour: Varies from {min_vol} to {max_vol}")
        
        buckets = self.analysis_data.get('token_buckets', {})
        bucket_count = len(buckets) if isinstance(buckets, dict) else 0
        print(f"   • Token-Size-Controlled Cost Analysis: Available for {bucket_count} size categories")
        print(f"   • Best/Worst Hours for Efficiency: {best_hour:02d}:00 / {worst_hour:02d}:00")
        
        if worst_cost > 0 and best_cost > 0:
            arbitrage_ratio = worst_cost / best_cost
            print(f"   • Arbitrage Ratio (cost difference between hours): {arbitrage_ratio:.1f}x")
    
    def _print_model_efficiency_metrics(self) -> None:
        """Print model performance comparison."""
        print(f"\n🤖 MODEL EFFICIENCY METRICS")
        
        model_usage = self.analysis_data.get('model_usage', {})
        for model, data in model_usage.items():
            if isinstance(data, dict) and data.get('count', 0) > 0:
                model_cost_per_token = data['cost'] / data['tokens'] if data['tokens'] > 0 else 0
                model_tokens_per_dollar = data['tokens'] / data['cost'] if data['cost'] > 0 else 0
                
                print(f"   • {model}:")
                print(f"     - Cost per Token: ${model_cost_per_token:.6f}")
                print(f"     - Tokens per Dollar: {model_tokens_per_dollar:,.0f}")
                print(f"     - Usage Count: {data['count']} messages")
        
        print(f"   • Model Switching Opportunities: Use sonnet over opus")
    
    def _print_session_patterns(self) -> None:
        """Print session usage patterns."""
        print(f"\n📈 SESSION & USAGE PATTERNS")
        print(f"   • Session Count: {self.metrics.session_count}")
        print(f"   • Average Session Duration: {self.metrics.avg_session_duration:.1f} hours")
        print(f"   • Session Intensity (tokens/hour): {self.metrics.session_intensity:,.0f}")
        print(f"   • Message Frequency: {self.metrics.message_frequency:.1f} messages/session")
        
        self._print_productivity_hours()
    
    def _print_productivity_hours(self) -> None:
        """Print peak productivity hours."""
        hourly_patterns = self.analysis_data.get('hourly_patterns', {})
        if not hourly_patterns or not isinstance(hourly_patterns, dict):
            return
        
        valid_hours = {
            h: data for h, data in hourly_patterns.items() 
            if isinstance(data, dict) and data.get('count', 0) > 0
        }
        
        if valid_hours:
            peak_hour = max(valid_hours, key=lambda h: valid_hours[h]['count'])
            print(f"   • Peak Productivity Hours: {peak_hour:02d}:00")
            print(f"   • Cost per Hour Patterns: Available in hourly breakdown")
    
    def _print_optimization_opportunities(self) -> None:
        """Print actionable optimization recommendations."""
        print(f"\n🎯 OPTIMIZATION OPPORTUNITIES")
        
        # Get optional metrics with defaults
        expensive_ops_count = getattr(self.metrics, 'expensive_operations_count', 0)
        expensive_ops_cost = getattr(self.metrics, 'expensive_operations_cost', 0.0)
        inefficient_msgs = getattr(self.metrics, 'inefficient_messages', 0)
        
        print(f"   • Expensive Operations (>$5 messages): {expensive_ops_count} messages, ${expensive_ops_cost:.2f} total")
        print(f"   • Token Waste Patterns: {inefficient_msgs} inefficient messages detected")
        print(f"   • Model Switching Potential Savings: Available")
        
        self._print_timing_savings()
        print(f"   • Cache Optimization Opportunities: Current {self.metrics.cache_hit_rate*100:.1f}% hit rate")
    
    def _print_timing_savings(self) -> None:
        """Calculate and print potential timing arbitrage savings."""
        hourly_patterns = self.analysis_data.get('hourly_patterns', {})
        if not hourly_patterns:
            return
        
        hourly_efficiency = self._calculate_hourly_efficiency(hourly_patterns)
        if hourly_efficiency:
            best_cost = min(hourly_efficiency.values())
            worst_cost = max(hourly_efficiency.values())
            potential_savings = (worst_cost - best_cost) * self.metrics.total_tokens
            print(f"   • Timing Shift Potential Savings: ${potential_savings:.2f}")
    
    def _print_recent_activity(self) -> None:
        """Print last 5 hours activity analysis."""
        print(f"\n⏱️ LAST 5 HOURS METRICS")
        
        if self.metrics.last_5h_messages > 0:
            print(f"   • Cost (last 5 hours): ${self.metrics.last_5h_cost:.2f}")
            print(f"   • Tokens (last 5 hours): {self.metrics.last_5h_tokens:,}")
            print(f"   • Messages (last 5 hours): {self.metrics.last_5h_messages}")
            print(f"   • Cache Hit Rate (last 5 hours): {self.metrics.last_5h_cache_hit_rate*100:.1f}%")
            print(f"   • Average Cost per Token (last 5 hours): ${self.metrics.last_5h_avg_cost_per_token:.6f}")
            
            self._print_recent_comparisons()
        else:
            print(f"   • No activity in the last 5 hours")
    
    def _print_recent_comparisons(self) -> None:
        """Print recent vs overall performance comparisons."""
        # Compare to overall averages
        cost_ratio = (
            self.metrics.last_5h_avg_cost_per_token / self.metrics.cost_per_token 
            if self.metrics.cost_per_token > 0 else 1
        )
        cache_diff = (self.metrics.last_5h_cache_hit_rate - self.metrics.cache_hit_rate) * 100
        
        print(f"   • Recent vs Overall Cost Efficiency: {cost_ratio:.1f}x (recent vs average)")
        print(f"   • Recent vs Overall Cache Performance: {cache_diff:+.1f}% difference")


def print_metrics_only(metrics: ComprehensiveMetrics, analysis_data: Dict[str, Any], 
                      five_hour_patterns: Optional[Any] = None, 
                      avg_5h_tokens_before_limit: float = 0, 
                      avg_5h_messages_before_limit: float = 0, 
                      avg_tokens_per_minute_before_limit: float = 0, 
                      current_3h_tokens: int = 0, 
                      current_3h_count: int = 0, 
                      current_tokens_per_minute: float = 0, 
                      current_messages_per_minute: float = 0) -> None:
    """
    Print only cost and optimization metrics (no predictions).
    
    This is the main entry point for displaying comprehensive metrics analysis.
    Additional parameters are kept for backward compatibility but not used.
    """
    formatter = MetricsFormatter(metrics, analysis_data)
    formatter.print_all_metrics()