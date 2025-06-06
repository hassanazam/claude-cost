"""
Advanced probabilistic usage limit prediction system.

This module implements a sophisticated prediction algorithm that:
1. Classifies session contexts (exploration, coding, debugging, optimization)
2. Uses probabilistic models with uncertainty quantification
3. Provides multi-horizon predictions with confidence intervals
4. Calculates dynamic risk scores based on behavioral patterns
"""

import numpy as np
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict, deque
import math


class SessionContext(Enum):
    """Different types of user sessions with distinct usage patterns"""
    EXPLORATION = "exploration"    # High variance, unpredictable bursts
    CODING = "coding"             # Steady rate, predictable patterns  
    DEBUGGING = "debugging"       # Irregular bursts, high intensity
    OPTIMIZATION = "optimization" # Declining rate, refinement focused
    UNKNOWN = "unknown"           # Insufficient data


@dataclass
class PredictionResult:
    """Container for prediction results with uncertainty"""
    mean_minutes: float
    confidence_interval: Tuple[float, float]  # (5th, 95th percentile)
    probability_within_hour: float
    risk_score: float
    context: SessionContext
    horizon_minutes: int


@dataclass
class BehavioralFeatures:
    """Extracted behavioral features for prediction"""
    # Rate-based features
    tokens_per_minute: float
    messages_per_minute: float
    cost_per_minute: float
    
    # Variance features
    token_rate_variance: float
    message_gap_variance: float
    
    # Trend features  
    rate_acceleration: float
    complexity_trend: float
    
    # Context features
    avg_message_size: float
    cache_hit_rate: float
    model_diversity: float
    
    # Temporal features
    session_duration_minutes: float
    time_since_last_message: float
    hour_of_day: int


class SessionContextClassifier:
    """Classifies current session type based on behavioral patterns"""
    
    def __init__(self):
        # Define context signatures based on typical patterns
        self.context_signatures = {
            SessionContext.EXPLORATION: {
                'token_variance_threshold': 0.8,      # High variance
                'message_gap_threshold': 300,         # Long gaps between messages
                'complexity_increasing': True,        # Messages getting more complex
                'cache_hit_rate': 0.2                # Low cache efficiency
            },
            SessionContext.CODING: {
                'token_variance_threshold': 0.3,      # Low variance
                'message_gap_threshold': 120,         # Consistent gaps
                'complexity_increasing': False,       # Stable complexity
                'cache_hit_rate': 0.6                # Good cache efficiency
            },
            SessionContext.DEBUGGING: {
                'token_variance_threshold': 1.2,      # Very high variance
                'message_gap_threshold': 60,          # Quick back-and-forth
                'complexity_increasing': False,       # Focused on specific issues
                'cache_hit_rate': 0.4                # Medium cache efficiency
            },
            SessionContext.OPTIMIZATION: {
                'token_variance_threshold': 0.4,      # Medium variance
                'message_gap_threshold': 180,         # Medium gaps
                'complexity_increasing': False,       # Decreasing complexity
                'cache_hit_rate': 0.7                # High cache efficiency
            }
        }
    
    def classify(self, features: BehavioralFeatures, recent_messages: List[Dict]) -> SessionContext:
        """Classify session context based on behavioral features"""
        if len(recent_messages) < 3:
            return SessionContext.UNKNOWN
            
        scores = {}
        
        for context, signature in self.context_signatures.items():
            score = 0
            
            # Variance score
            if features.token_rate_variance <= signature['token_variance_threshold']:
                score += 1
            
            # Message gap pattern
            gaps = self._calculate_message_gaps(recent_messages)
            avg_gap = statistics.mean(gaps) if gaps else 0
            if abs(avg_gap - signature['message_gap_threshold']) < 60:
                score += 1
                
            # Cache efficiency
            if abs(features.cache_hit_rate - signature['cache_hit_rate']) < 0.2:
                score += 1
                
            # Complexity trend
            complexity_trend = self._calculate_complexity_trend(recent_messages)
            if (complexity_trend > 0) == signature['complexity_increasing']:
                score += 1
                
            scores[context] = score
        
        # Return context with highest score
        best_context = max(scores.keys(), key=lambda k: scores[k])
        return best_context if scores[best_context] > 1 else SessionContext.UNKNOWN
    
    def _calculate_message_gaps(self, messages: List[Dict]) -> List[float]:
        """Calculate gaps between messages in seconds"""
        gaps = []
        for i in range(1, len(messages)):
            if messages[i]['timestamp'] and messages[i-1]['timestamp']:
                gap = (messages[i]['timestamp'] - messages[i-1]['timestamp']).total_seconds()
                gaps.append(gap)
        return gaps
    
    def _calculate_complexity_trend(self, messages: List[Dict]) -> float:
        """Calculate trend in message complexity (positive = increasing)"""
        if len(messages) < 3:
            return 0
            
        complexities = [msg['tokens'] for msg in messages[-5:]]
        
        # Simple linear regression slope
        n = len(complexities)
        x = list(range(n))
        y = complexities
        
        slope = (n * sum(x[i] * y[i] for i in range(n)) - sum(x) * sum(y)) / \
                (n * sum(x[i]**2 for i in range(n)) - sum(x)**2)
        
        return slope


class ProbabilisticPredictor:
    """Core probabilistic prediction engine"""
    
    def __init__(self):
        self.context_models = self._initialize_context_models()
        
    def _initialize_context_models(self) -> Dict[SessionContext, Dict]:
        """Initialize context-specific prediction models"""
        return {
            SessionContext.EXPLORATION: {
                'base_multiplier': 1.5,     # Higher uncertainty
                'variance_penalty': 2.0,    # Penalize high variance more
                'rate_sensitivity': 0.8     # Less sensitive to current rate
            },
            SessionContext.CODING: {
                'base_multiplier': 1.0,     # Standard uncertainty
                'variance_penalty': 1.0,    # Standard variance penalty
                'rate_sensitivity': 1.2     # More sensitive to current rate
            },
            SessionContext.DEBUGGING: {
                'base_multiplier': 1.3,     # Higher uncertainty
                'variance_penalty': 1.5,    # Medium variance penalty
                'rate_sensitivity': 1.5     # Very sensitive to current rate
            },
            SessionContext.OPTIMIZATION: {
                'base_multiplier': 0.8,     # Lower uncertainty
                'variance_penalty': 0.8,    # Less variance penalty
                'rate_sensitivity': 0.9     # Less sensitive to current rate
            },
            SessionContext.UNKNOWN: {
                'base_multiplier': 1.8,     # High uncertainty
                'variance_penalty': 2.5,    # High variance penalty
                'rate_sensitivity': 1.0     # Standard sensitivity
            }
        }
    
    def predict_time_to_limit(
        self, 
        features: BehavioralFeatures,
        context: SessionContext,
        historical_patterns: List[Dict],
        horizon_minutes: int = 60
    ) -> PredictionResult:
        """Generate probabilistic prediction for time to usage limit"""
        
        if not historical_patterns:
            return self._fallback_prediction(horizon_minutes, context)
        
        # Calculate base prediction from historical patterns
        base_prediction = self._calculate_base_prediction(historical_patterns, features)
        
        # Apply context-specific adjustments
        model_params = self.context_models[context]
        adjusted_prediction = base_prediction * model_params['base_multiplier']
        
        # Calculate uncertainty based on variance and context
        uncertainty = self._calculate_uncertainty(features, model_params, historical_patterns)
        
        # Generate confidence interval
        lower_bound = max(5, adjusted_prediction - uncertainty)
        upper_bound = adjusted_prediction + uncertainty
        
        # Calculate probability of hitting limit within horizon
        prob_within_horizon = self._calculate_probability_within_horizon(
            adjusted_prediction, uncertainty, horizon_minutes
        )
        
        # Calculate dynamic risk score
        risk_score = self._calculate_risk_score(
            adjusted_prediction, uncertainty, features, context, horizon_minutes
        )
        
        return PredictionResult(
            mean_minutes=adjusted_prediction,
            confidence_interval=(lower_bound, upper_bound),
            probability_within_hour=prob_within_horizon,
            risk_score=risk_score,
            context=context,
            horizon_minutes=horizon_minutes
        )
    
    def _calculate_base_prediction(self, historical_patterns: List[Dict], features: BehavioralFeatures) -> float:
        """Calculate base prediction from historical data"""
        if not historical_patterns:
            return 180  # Default 3 hours
            
        # Weight recent patterns more heavily
        weights = [1.0 / (i + 1) for i in range(len(historical_patterns))]
        total_weight = sum(weights)
        
        weighted_times = []
        for i, pattern in enumerate(historical_patterns):
            time_to_limit = pattern.get('time_to_limit_minutes', 180)
            weighted_times.append(time_to_limit * weights[i] / total_weight)
        
        base_time = sum(weighted_times)
        
        # Adjust based on current rate vs historical rate
        if features.tokens_per_minute > 0:
            historical_rates = [p.get('avg_tokens_per_minute', 0) for p in historical_patterns]
            avg_historical_rate = statistics.mean([r for r in historical_rates if r > 0])
            
            if avg_historical_rate > 0:
                rate_ratio = features.tokens_per_minute / avg_historical_rate
                # Inverse relationship: higher rate = less time to limit
                base_time = base_time / rate_ratio
        
        return max(5, base_time)  # Minimum 5 minutes
    
    def _calculate_uncertainty(
        self, 
        features: BehavioralFeatures, 
        model_params: Dict, 
        historical_patterns: List[Dict]
    ) -> float:
        """Calculate prediction uncertainty"""
        
        # Base uncertainty from historical variance
        if len(historical_patterns) > 1:
            times = [p.get('time_to_limit_minutes', 180) for p in historical_patterns]
            historical_std = statistics.stdev(times)
        else:
            historical_std = 60  # Default uncertainty
        
        # Adjust for current variance
        variance_adjustment = 1 + (features.token_rate_variance * model_params['variance_penalty'])
        
        # Adjust for sample size (less data = more uncertainty)
        sample_size_adjustment = max(1.0, 3.0 / len(historical_patterns))
        
        total_uncertainty = historical_std * variance_adjustment * sample_size_adjustment
        
        return min(total_uncertainty, 300)  # Cap at 5 hours
    
    def _calculate_probability_within_horizon(
        self, 
        mean_prediction: float, 
        uncertainty: float, 
        horizon: int
    ) -> float:
        """Calculate probability of hitting limit within time horizon"""
        
        # Assume log-normal distribution (usage patterns are typically right-skewed)
        if uncertainty <= 0:
            return 1.0 if mean_prediction <= horizon else 0.0
        
        # Convert to log-normal parameters
        variance = uncertainty ** 2
        mu = math.log(mean_prediction ** 2 / math.sqrt(variance + mean_prediction ** 2))
        sigma = math.sqrt(math.log(variance / mean_prediction ** 2 + 1))
        
        # Calculate CDF at horizon point
        # Approximation of log-normal CDF
        normalized = (math.log(horizon) - mu) / sigma
        
        # Error function approximation
        def erf_approx(x):
            # Abramowitz and Stegun approximation
            a1 =  0.254829592
            a2 = -0.284496736
            a3 =  1.421413741
            a4 = -1.453152027
            a5 =  1.061405429
            p  =  0.3275911
            
            sign = 1 if x >= 0 else -1
            x = abs(x)
            
            t = 1.0 / (1.0 + p * x)
            y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x * x)
            
            return sign * y
        
        cdf = 0.5 * (1 + erf_approx(normalized / math.sqrt(2)))
        return min(1.0, max(0.0, cdf))
    
    def _calculate_risk_score(
        self,
        mean_prediction: float,
        uncertainty: float,
        features: BehavioralFeatures,
        context: SessionContext,
        horizon: int
    ) -> float:
        """Calculate dynamic risk score (0-100)"""
        
        # Base risk from time to limit
        time_risk = max(0, (horizon - mean_prediction) / horizon * 100)
        
        # Uncertainty penalty (higher uncertainty = higher risk)
        uncertainty_risk = min(30, uncertainty / 10)
        
        # Context-specific risk adjustments
        context_multipliers = {
            SessionContext.EXPLORATION: 1.2,   # Unpredictable
            SessionContext.CODING: 1.0,        # Standard
            SessionContext.DEBUGGING: 1.5,     # High intensity bursts
            SessionContext.OPTIMIZATION: 0.8,  # Typically declining
            SessionContext.UNKNOWN: 1.3        # Unknown is risky
        }
        
        context_multiplier = context_multipliers.get(context, 1.0)
        
        # Rate acceleration penalty
        if features.rate_acceleration > 0:
            acceleration_risk = min(20, features.rate_acceleration * 10)
        else:
            acceleration_risk = 0
        
        total_risk = (time_risk + uncertainty_risk + acceleration_risk) * context_multiplier
        
        return min(100, max(0, total_risk))
    
    def _fallback_prediction(self, horizon: int, context: SessionContext) -> PredictionResult:
        """Fallback prediction when no historical data available"""
        return PredictionResult(
            mean_minutes=horizon * 2,  # Conservative estimate
            confidence_interval=(horizon * 0.5, horizon * 4),
            probability_within_hour=0.1,
            risk_score=20.0,
            context=context,
            horizon_minutes=horizon
        )


class AdvancedPredictionEngine:
    """Main engine that orchestrates the advanced prediction system"""
    
    def __init__(self):
        self.context_classifier = SessionContextClassifier()
        self.predictor = ProbabilisticPredictor()
        self.feature_extractor = BehavioralFeatureExtractor()
    
    def generate_predictions(
        self, 
        recent_messages: List[Dict], 
        historical_patterns: List[Dict],
        horizons: List[int] = [15, 30, 60, 120]
    ) -> Dict[int, PredictionResult]:
        """Generate multi-horizon predictions with uncertainty"""
        
        if len(recent_messages) < 2:
            return self._generate_fallback_predictions(horizons)
        
        # Extract behavioral features
        features = self.feature_extractor.extract_features(recent_messages)
        
        # Classify session context
        context = self.context_classifier.classify(features, recent_messages)
        
        # Generate predictions for each horizon
        predictions = {}
        for horizon in horizons:
            prediction = self.predictor.predict_time_to_limit(
                features, context, historical_patterns, horizon
            )
            predictions[horizon] = prediction
        
        return predictions
    
    def _generate_fallback_predictions(self, horizons: List[int]) -> Dict[int, PredictionResult]:
        """Generate fallback predictions when insufficient data"""
        predictions = {}
        for horizon in horizons:
            predictions[horizon] = PredictionResult(
                mean_minutes=horizon * 3,
                confidence_interval=(horizon, horizon * 6),
                probability_within_hour=0.05,
                risk_score=10.0,
                context=SessionContext.UNKNOWN,
                horizon_minutes=horizon
            )
        return predictions


class BehavioralFeatureExtractor:
    """Extracts behavioral features from message history"""
    
    def extract_features(self, messages: List[Dict]) -> BehavioralFeatures:
        """Extract comprehensive behavioral features"""
        
        if len(messages) < 2:
            return self._default_features()
        
        # Sort messages by timestamp
        sorted_messages = sorted(messages, key=lambda m: m['timestamp'] or datetime.min)
        
        # Calculate time-based features
        duration = self._calculate_duration(sorted_messages)
        tokens_per_minute = self._calculate_tokens_per_minute(sorted_messages, duration)
        messages_per_minute = len(sorted_messages) / max(1, duration)
        cost_per_minute = sum(m['cost'] for m in sorted_messages) / max(1, duration)
        
        # Calculate variance features
        token_rates = self._calculate_windowed_rates(sorted_messages)
        token_rate_variance = statistics.stdev(token_rates) if len(token_rates) > 1 else 0
        
        message_gaps = self._calculate_message_gaps(sorted_messages)
        message_gap_variance = statistics.stdev(message_gaps) if len(message_gaps) > 1 else 0
        
        # Calculate trend features
        rate_acceleration = self._calculate_rate_acceleration(token_rates)
        complexity_trend = self._calculate_complexity_trend(sorted_messages)
        
        # Calculate context features
        avg_message_size = statistics.mean([m['tokens'] for m in sorted_messages])
        cache_hit_rate = self._calculate_cache_hit_rate(sorted_messages)
        model_diversity = len(set(m['model'] for m in sorted_messages))
        
        # Temporal features
        time_since_last = self._time_since_last_message(sorted_messages)
        hour_of_day = sorted_messages[-1]['timestamp'].hour if sorted_messages[-1]['timestamp'] else 12
        
        return BehavioralFeatures(
            tokens_per_minute=tokens_per_minute,
            messages_per_minute=messages_per_minute,
            cost_per_minute=cost_per_minute,
            token_rate_variance=token_rate_variance,
            message_gap_variance=message_gap_variance,
            rate_acceleration=rate_acceleration,
            complexity_trend=complexity_trend,
            avg_message_size=avg_message_size,
            cache_hit_rate=cache_hit_rate,
            model_diversity=model_diversity,
            session_duration_minutes=duration,
            time_since_last_message=time_since_last,
            hour_of_day=hour_of_day
        )
    
    def _calculate_duration(self, messages: List[Dict]) -> float:
        """Calculate session duration in minutes"""
        if len(messages) < 2:
            return 1.0
        
        start = messages[0]['timestamp']
        end = messages[-1]['timestamp']
        
        if not start or not end:
            return 1.0
        
        duration_seconds = (end - start).total_seconds()
        return max(1.0, duration_seconds / 60.0)
    
    def _calculate_tokens_per_minute(self, messages: List[Dict], duration: float) -> float:
        """Calculate average tokens per minute"""
        total_tokens = sum(m['tokens'] for m in messages)
        return total_tokens / max(1, duration)
    
    def _calculate_windowed_rates(self, messages: List[Dict], window_minutes: int = 10) -> List[float]:
        """Calculate token rates in sliding windows"""
        if len(messages) < 2:
            return [0]
        
        rates = []
        window_size = timedelta(minutes=window_minutes)
        
        for i in range(len(messages)):
            window_start = messages[i]['timestamp']
            if not window_start:
                continue
                
            window_end = window_start + window_size
            
            # Find messages in window
            window_messages = [
                m for m in messages[i:] 
                if m['timestamp'] and window_start <= m['timestamp'] <= window_end
            ]
            
            if len(window_messages) > 0:
                total_tokens = sum(m['tokens'] for m in window_messages)
                rate = total_tokens / window_minutes
                rates.append(rate)
        
        return rates if rates else [0]
    
    def _calculate_message_gaps(self, messages: List[Dict]) -> List[float]:
        """Calculate gaps between messages in minutes"""
        gaps = []
        for i in range(1, len(messages)):
            if messages[i]['timestamp'] and messages[i-1]['timestamp']:
                gap_seconds = (messages[i]['timestamp'] - messages[i-1]['timestamp']).total_seconds()
                gaps.append(gap_seconds / 60.0)
        return gaps if gaps else [0]
    
    def _calculate_rate_acceleration(self, rates: List[float]) -> float:
        """Calculate acceleration in token rate"""
        if len(rates) < 3:
            return 0
        
        # Simple second derivative approximation
        accelerations = []
        for i in range(1, len(rates) - 1):
            accel = rates[i+1] - 2*rates[i] + rates[i-1]
            accelerations.append(accel)
        
        return statistics.mean(accelerations) if accelerations else 0
    
    def _calculate_complexity_trend(self, messages: List[Dict]) -> float:
        """Calculate trend in message complexity"""
        if len(messages) < 3:
            return 0
        
        complexities = [m['tokens'] for m in messages[-5:]]
        
        # Linear regression slope
        n = len(complexities)
        x = list(range(n))
        y = complexities
        
        if n < 2:
            return 0
        
        slope = (n * sum(x[i] * y[i] for i in range(n)) - sum(x) * sum(y)) / \
                (n * sum(x[i]**2 for i in range(n)) - sum(x)**2)
        
        return slope
    
    def _calculate_cache_hit_rate(self, messages: List[Dict]) -> float:
        """Calculate cache hit rate"""
        total_input_like = sum(
            m.get('input_tokens', 0) + 
            m.get('cache_creation_tokens', 0) + 
            m.get('cache_read_tokens', 0) 
            for m in messages
        )
        
        total_cache_reads = sum(m.get('cache_read_tokens', 0) for m in messages)
        
        return total_cache_reads / max(1, total_input_like)
    
    def _time_since_last_message(self, messages: List[Dict]) -> float:
        """Calculate minutes since last message"""
        if not messages or not messages[-1]['timestamp']:
            return 0
        
        now = datetime.now(messages[-1]['timestamp'].tzinfo)
        last_time = messages[-1]['timestamp']
        
        return (now - last_time).total_seconds() / 60.0
    
    def _default_features(self) -> BehavioralFeatures:
        """Return default features when insufficient data"""
        return BehavioralFeatures(
            tokens_per_minute=0,
            messages_per_minute=0,
            cost_per_minute=0,
            token_rate_variance=0,
            message_gap_variance=0,
            rate_acceleration=0,
            complexity_trend=0,
            avg_message_size=0,
            cache_hit_rate=0,
            model_diversity=0,
            session_duration_minutes=0,
            time_since_last_message=0,
            hour_of_day=12
        )