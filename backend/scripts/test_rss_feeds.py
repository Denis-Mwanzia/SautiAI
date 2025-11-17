#!/usr/bin/env python3
"""
Test RSS Feed URLs
Validates and tests RSS feed URLs to find working feeds
"""

import feedparser
import sys
from typing import List, Dict

# Test RSS feeds
TEST_FEEDS = [
    # International news (Kenya coverage)
    "https://www.bbc.com/news/world/africa/rss.xml",
    "https://feeds.bbci.co.uk/news/world/africa/rss.xml",
    "https://www.theguardian.com/world/africa/rss",
    
    # Kenyan news (to test)
    "https://www.nation.co.ke/kenya/rss",
    "https://www.standardmedia.co.ke/rss",
    "https://www.businessdailyafrica.com/rss",
    "https://citizentv.co.ke/rss",
    
    # Alternative formats
    "https://www.nation.co.ke/rss",
    "https://feeds.feedburner.com/nation-kenya",
]

def test_feed(feed_url: str) -> Dict:
    """Test a single RSS feed"""
    result = {
        "url": feed_url,
        "status": "unknown",
        "entries": 0,
        "error": None,
        "sample_title": None
    }
    
    try:
        feed = feedparser.parse(feed_url)
        
        if feed.bozo and feed.bozo_exception:
            result["status"] = "parse_error"
            result["error"] = str(feed.bozo_exception)
        elif feed.entries:
            result["status"] = "working"
            result["entries"] = len(feed.entries)
            if feed.entries:
                result["sample_title"] = feed.entries[0].get("title", "")[:60]
        else:
            result["status"] = "no_entries"
            result["error"] = "Feed parsed but no entries found"
            
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    
    return result

def main():
    print("Testing RSS Feeds...")
    print("=" * 80)
    
    working_feeds = []
    failed_feeds = []
    
    for feed_url in TEST_FEEDS:
        result = test_feed(feed_url)
        
        status_icon = "✓" if result["status"] == "working" else "✗"
        print(f"{status_icon} {feed_url}")
        print(f"   Status: {result['status']}")
        
        if result["status"] == "working":
            print(f"   Entries: {result['entries']}")
            if result["sample_title"]:
                print(f"   Sample: {result['sample_title']}...")
            working_feeds.append(feed_url)
        else:
            print(f"   Error: {result['error']}")
            failed_feeds.append(feed_url)
        
        print()
    
    print("=" * 80)
    print(f"Summary: {len(working_feeds)} working, {len(failed_feeds)} failed")
    print()
    
    if working_feeds:
        print("Working feeds:")
        for feed in working_feeds:
            print(f"  - {feed}")
    
    return len(working_feeds) > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

