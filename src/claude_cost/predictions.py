"""
Prediction and backtesting functions for Claude Cost analysis.

This module contains functions for usage limit predictions and algorithm validation.
"""

import statistics
from datetime import timedelta
from typing import Dict, List

from .models import ComprehensiveMetrics


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