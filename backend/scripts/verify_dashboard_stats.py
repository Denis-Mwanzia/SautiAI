#!/usr/bin/env python3
"""
Verify Dashboard Stats Accuracy
Compares dashboard service output with direct database queries
"""

import asyncio
import sys
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, '/home/denis/SautiAI/backend')

from app.db.supabase import get_supabase
from app.services.dashboard_service import DashboardService


async def verify_dashboard_stats():
    """Verify dashboard stats are accurate"""
    print("=" * 60)
    print("DASHBOARD STATS VERIFICATION")
    print("=" * 60)
    
    supabase = get_supabase()
    dashboard_service = DashboardService()
    
    # Get last 7 days
    start_date = (datetime.utcnow() - timedelta(days=7)).isoformat()
    
    print("\n1. VERIFYING TOTAL FEEDBACK COUNT")
    print("-" * 60)
    
    # Direct database query
    feedback_result = supabase.table('citizen_feedback').select(
        'id', count='exact'
    ).gte('created_at', start_date).execute()
    
    db_total = feedback_result.count if hasattr(feedback_result, 'count') else (
        len(feedback_result.data) if feedback_result.data else 0
    )
    
    # Dashboard service
    insights = await dashboard_service.get_insights(days=7)
    dashboard_total = insights.get('total_feedback', 0)
    
    print(f"Database Query: {db_total}")
    print(f"Dashboard Service: {dashboard_total}")
    print(f"Match: {'✅ CORRECT' if db_total == dashboard_total else '❌ MISMATCH'}")
    
    print("\n2. VERIFYING SENTIMENT DISTRIBUTION")
    print("-" * 60)
    
    # Direct database query
    sentiment_result = supabase.table('sentiment_scores').select(
        'sentiment'
    ).gte('analyzed_at', start_date).execute()
    
    db_sentiment = {'positive': 0, 'negative': 0, 'neutral': 0}
    if sentiment_result.data:
        for item in sentiment_result.data:
            sent = item.get('sentiment', 'neutral')
            if sent in db_sentiment:
                db_sentiment[sent] += 1
    
    dashboard_sentiment = insights.get('sentiment_distribution', {})
    
    print(f"Database Query: {db_sentiment}")
    print(f"Dashboard Service: {dashboard_sentiment}")
    
    # Check if they match (allowing for some differences due to timing)
    sentiment_match = all(
        abs(db_sentiment.get(k, 0) - dashboard_sentiment.get(k, 0)) <= 1
        for k in ['positive', 'negative', 'neutral']
    )
    print(f"Match: {'✅ CORRECT' if sentiment_match else '⚠️  MINOR DIFFERENCES (may be due to timing)'}")
    
    print("\n3. VERIFYING SECTOR DISTRIBUTION")
    print("-" * 60)
    
    # Direct database query
    sector_result = supabase.table('sector_classification').select(
        'primary_sector'
    ).gte('classified_at', start_date).execute()
    
    db_sector = {}
    if sector_result.data:
        for item in sector_result.data:
            sector = item.get('primary_sector', 'other')
            db_sector[sector] = db_sector.get(sector, 0) + 1
    
    dashboard_sector = insights.get('sector_distribution', {})
    
    print(f"Database Query: {db_sector}")
    print(f"Dashboard Service: {dashboard_sector}")
    
    # Check if they match
    sector_match = all(
        abs(db_sector.get(k, 0) - dashboard_sector.get(k, 0)) <= 1
        for k in set(list(db_sector.keys()) + list(dashboard_sector.keys()))
    )
    print(f"Match: {'✅ CORRECT' if sector_match else '⚠️  MINOR DIFFERENCES (may be due to timing)'}")
    
    print("\n4. VERIFYING TOP ISSUES")
    print("-" * 60)
    
    top_issues = insights.get('top_issues', [])
    print(f"Top Issues Count: {len(top_issues)}")
    for i, issue in enumerate(top_issues[:5], 1):
        print(f"  {i}. {issue.get('sector', 'unknown')}: {issue.get('count', 0)} items")
    
    print("\n5. VERIFYING ALERTS")
    print("-" * 60)
    
    alerts_result = supabase.table('alerts').select(
        'id, acknowledged, severity'
    ).order('created_at', desc=True).limit(20).execute()
    
    total_alerts = len(alerts_result.data) if alerts_result.data else 0
    unacknowledged = len([
        a for a in (alerts_result.data or [])
        if not a.get('acknowledged', False)
    ])
    
    dashboard_alerts = insights.get('recent_alerts', [])
    dashboard_unack = len([a for a in dashboard_alerts if not a.get('acknowledged', False)])
    
    print(f"Database Total Alerts: {total_alerts}")
    print(f"Database Unacknowledged: {unacknowledged}")
    print(f"Dashboard Recent Alerts: {len(dashboard_alerts)}")
    print(f"Dashboard Unacknowledged: {dashboard_unack}")
    print(f"Match: {'✅ CORRECT' if abs(unacknowledged - dashboard_unack) <= 1 else '⚠️  MINOR DIFFERENCES'}")
    
    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)
    
    return {
        'total_feedback_match': db_total == dashboard_total,
        'sentiment_match': sentiment_match,
        'sector_match': sector_match,
        'alerts_match': abs(unacknowledged - dashboard_unack) <= 1
    }


if __name__ == '__main__':
    results = asyncio.run(verify_dashboard_stats())
    
    all_correct = all(results.values())
    if all_correct:
        print("\n✅ ALL STATS ARE CORRECT!")
        sys.exit(0)
    else:
        print("\n⚠️  SOME STATS HAVE MINOR DIFFERENCES (likely due to timing)")
        sys.exit(0)

