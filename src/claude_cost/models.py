"""
Data models and pricing configuration for Claude Cost analysis.
"""

from dataclasses import dataclass

# Claude pricing (per million tokens) - June 2025
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