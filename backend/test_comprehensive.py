#!/usr/bin/env python3
"""
Comprehensive Feature Testing Suite
Tests all endpoints and functionality of Sauti AI platform
"""

import asyncio
import httpx
import json
import sys
from typing import Dict, Any, List
from datetime import datetime

API_BASE = "http://localhost:8000/api/v1"
FRONTEND_URL = "http://localhost:5173"

# Test results
results = {
    "passed": [],
    "failed": [],
    "warnings": []
}


def log_test(name: str, passed: bool, message: str = "", warning: bool = False):
    """Log test result"""
    status = "✅ PASSED" if passed else "❌ FAILED"
    if warning:
        status = "⚠️  WARNING"
    
    print(f"{status}: {name}")
    if message:
        print(f"  → {message}")
    
    if passed:
        results["passed"].append(name)
    elif warning:
        results["warnings"].append(name)
    else:
        results["failed"].append(name)


async def test_endpoint(
    client: httpx.AsyncClient,
    method: str,
    endpoint: str,
    name: str,
    expected_status: int = 200,
    json_data: Dict = None,
    params: Dict = None,
    timeout: float = 30.0
) -> bool:
    """Test an API endpoint"""
    try:
        url = f"{API_BASE}{endpoint}"
        
        if method == "GET":
            response = await client.get(url, params=params, timeout=timeout)
        elif method == "POST":
            response = await client.post(url, json=json_data, params=params, timeout=timeout)
        else:
            log_test(name, False, f"Unsupported method: {method}")
            return False
        
        if response.status_code == expected_status:
            log_test(name, True, f"Status: {response.status_code}")
            return True
        else:
            try:
                error_detail = response.json().get("detail", "Unknown error")
            except:
                error_detail = response.text[:100]
            log_test(name, False, f"Expected {expected_status}, got {response.status_code}: {error_detail}")
            return False
    except httpx.TimeoutException:
        log_test(name, False, "Request timeout")
        return False
    except Exception as e:
        log_test(name, False, f"Exception: {str(e)}")
        return False


async def test_health(client: httpx.AsyncClient):
    """Test system health"""
    print("\n" + "="*60)
    print("1. SYSTEM HEALTH")
    print("="*60)
    
    # Health check is at root level, not under /api/v1
    try:
        response = await client.get("http://localhost:8000/health", timeout=10.0)
        if response.status_code == 200:
            log_test("Health check endpoint", True, f"Status: {response.status_code}")
        else:
            log_test("Health check endpoint", False, f"Expected 200, got {response.status_code}")
    except Exception as e:
        log_test("Health check endpoint", False, f"Exception: {str(e)}")
    
    try:
        response = await client.get("http://localhost:8000/", timeout=10.0)
        if response.status_code == 200:
            log_test("Root endpoint", True, f"Status: {response.status_code}")
        else:
            log_test("Root endpoint", False, f"Expected 200, got {response.status_code}")
    except Exception as e:
        log_test("Root endpoint", False, f"Exception: {str(e)}")


async def test_data_sources(client: httpx.AsyncClient):
    """Test data sources endpoints"""
    print("\n" + "="*60)
    print("2. DATA SOURCES")
    print("="*60)
    
    await test_endpoint(client, "GET", "/ingest/sources", "List all data sources")
    await test_endpoint(client, "GET", "/ingest/sources", "List enabled sources", params={"enabled_only": True})
    await test_endpoint(client, "GET", "/ingest/sources", "Filter by RSS type", params={"source_type": "rss_feed"})
    await test_endpoint(client, "GET", "/ingest/sources", "Filter by governance", params={"category": "governance"})
    await test_endpoint(client, "GET", "/ingest/status", "Get ingestion status")


async def test_data_ingestion(client: httpx.AsyncClient):
    """Test data ingestion endpoints"""
    print("\n" + "="*60)
    print("3. DATA INGESTION")
    print("="*60)
    
    # RSS ingestion
    await test_endpoint(
        client, "POST", "/ingest/rss",
        "RSS feed ingestion",
        json_data=["https://www.bbc.com/news/world/africa/rss.xml"]
    )
    
    # Open Data ingestion
    await test_endpoint(
        client, "POST", "/ingest/open-data",
        "Open Data Portal ingestion"
    )
    
    # Government complaints
    await test_endpoint(
        client, "POST", "/ingest/government-complaints",
        "Government complaints ingestion",
        params={"limit": 10}
    )


async def test_ai_analysis(client: httpx.AsyncClient):
    """Test AI analysis endpoints"""
    print("\n" + "="*60)
    print("4. AI ANALYSIS")
    print("="*60)
    
    # First, create sample feedback to test with
    try:
        sample_response = await client.post(
            f"{API_BASE}/sample/sample",
            json={"count": 1, "sectors": ["health"]},
            timeout=30.0
        )
        if sample_response.status_code == 200:
            sample_data = sample_response.json()
            feedback_id = sample_data.get("data", {}).get("feedback_ids", [None])[0]
            
            if feedback_id:
                # Sentiment analysis (increased timeout for AI calls)
                await test_endpoint(
                    client, "POST", "/ai/analyze-sentiment",
                    "Sentiment analysis",
                    json_data={
                        "feedback_id": feedback_id,
                        "text": "The hospital has poor service and long waiting times",
                        "language": "en"
                    },
                    timeout=60.0
                )
                
                # Sector classification (increased timeout for AI calls)
                await test_endpoint(
                    client, "POST", "/ai/classify-sector",
                    "Sector classification",
                    json_data={
                        "feedback_id": feedback_id,
                        "text": "The hospital has poor service",
                        "language": "en"
                    },
                    timeout=60.0
                )
            else:
                log_test("Sentiment analysis", False, "Could not create sample feedback")
                log_test("Sector classification", False, "Could not create sample feedback")
        else:
            log_test("Sentiment analysis", False, "Could not create sample feedback")
            log_test("Sector classification", False, "Could not create sample feedback")
    except Exception as e:
        log_test("Sentiment analysis", False, f"Error setting up test: {str(e)}")
        log_test("Sector classification", False, f"Error setting up test: {str(e)}")
    
    # Get summaries
    await test_endpoint(client, "GET", "/ai/summaries", "Get AI summaries", timeout=60.0)
    
    # Get recommendations
    await test_endpoint(client, "GET", "/ai/recommendations", "Get policy recommendations")


async def test_dashboard(client: httpx.AsyncClient):
    """Test dashboard endpoints"""
    print("\n" + "="*60)
    print("5. DASHBOARD")
    print("="*60)
    
    await test_endpoint(client, "GET", "/dashboard/insights", "Get dashboard insights", params={"days": 7})
    await test_endpoint(client, "GET", "/dashboard/sentiment-trends", "Get sentiment trends", params={"days": 30})
    await test_endpoint(client, "GET", "/dashboard/top-issues", "Get top issues", params={"limit": 10})
    await test_endpoint(client, "GET", "/dashboard/county-heatmap", "Get county heatmap", params={"days": 7})


async def test_jaseci_agents(client: httpx.AsyncClient):
    """Test Jaseci agents endpoints"""
    print("\n" + "="*60)
    print("6. JASECI AGENTS")
    print("="*60)
    
    await test_endpoint(client, "GET", "/agents/types", "Get available agent types")
    await test_endpoint(client, "GET", "/agents/status", "Get agent status")
    
    await test_endpoint(
        client, "POST", "/agents/run",
        "Run data ingestion agent",
        json_data={
            "agent_type": "data_ingestion",
            "parameters": {"source_type": "rss_feed"}
        }
    )


async def test_reports(client: httpx.AsyncClient):
    """Test reports endpoints"""
    print("\n" + "="*60)
    print("7. REPORTS")
    print("="*60)
    
    await test_endpoint(
        client, "POST", "/reports/pulse",
        "Generate pulse report",
        params={"period": "weekly"},
        timeout=60.0
    )
    
    await test_endpoint(
        client, "GET", "/reports/pulse",
        "Get pulse reports",
        params={"limit": 10},
        timeout=60.0
    )


async def test_alerts(client: httpx.AsyncClient):
    """Test alerts endpoints"""
    print("\n" + "="*60)
    print("8. ALERTS")
    print("="*60)
    
    await test_endpoint(
        client, "POST", "/alerts/check-trending",
        "Check trending complaints",
        params={"hours": 24, "threshold": 5}
    )
    
    await test_endpoint(
        client, "GET", "/alerts/red-flags",
        "Get red flag alerts",
        params={"limit": 20}
    )


async def test_chat(client: httpx.AsyncClient):
    """Test chat functionality"""
    print("\n" + "="*60)
    print("9. CHAT")
    print("="*60)
    
    await test_endpoint(
        client, "POST", "/chat/message",
        "Send chat message",
        json_data={
            "message": "What is the overall sentiment of citizen feedback?",
            "conversation_history": []
        },
        timeout=60.0
    )
    
    await test_endpoint(
        client, "POST", "/chat/message",
        "Chat with context",
        json_data={
            "message": "Show me top issues in healthcare sector",
            "conversation_history": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hello! How can I help?"}
            ]
        },
        timeout=60.0
    )


async def test_sample_data(client: httpx.AsyncClient):
    """Test sample data generation"""
    print("\n" + "="*60)
    print("10. SAMPLE DATA")
    print("="*60)
    
    # Sample data endpoint now accepts JSON body
    await test_endpoint(
        client, "POST", "/sample/sample",
        "Generate sample data",
        json_data={"count": 10, "sectors": ["health", "education"]},
        timeout=30.0
    )


async def test_frontend(client: httpx.AsyncClient):
    """Test frontend accessibility"""
    print("\n" + "="*60)
    print("11. FRONTEND")
    print("="*60)
    
    try:
        response = await client.get(FRONTEND_URL, timeout=10.0, follow_redirects=True)
        if response.status_code == 200:
            log_test("Frontend accessible", True, f"Status: {response.status_code}")
        else:
            log_test("Frontend accessible", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Frontend accessible", False, f"Exception: {str(e)}")


async def main():
    """Run all tests"""
    print("="*60)
    print("SAUTI AI - COMPREHENSIVE FEATURE TESTING")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API Base URL: {API_BASE}")
    print(f"Frontend URL: {FRONTEND_URL}")
    
    async with httpx.AsyncClient() as client:
        # Test all features
        await test_health(client)
        await test_data_sources(client)
        await test_data_ingestion(client)
        await test_ai_analysis(client)
        await test_dashboard(client)
        await test_jaseci_agents(client)
        await test_reports(client)
        await test_alerts(client)
        await test_chat(client)
        await test_sample_data(client)
        await test_frontend(client)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"✅ Passed: {len(results['passed'])}")
    print(f"❌ Failed: {len(results['failed'])}")
    print(f"⚠️  Warnings: {len(results['warnings'])}")
    print(f"\nTotal Tests: {len(results['passed']) + len(results['failed']) + len(results['warnings'])}")
    
    if results['failed']:
        print("\nFailed Tests:")
        for test in results['failed']:
            print(f"  - {test}")
    
    if results['warnings']:
        print("\nWarnings:")
        for test in results['warnings']:
            print(f"  - {test}")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Exit with error code if any tests failed
    sys.exit(1 if results['failed'] else 0)


if __name__ == "__main__":
    asyncio.run(main())

