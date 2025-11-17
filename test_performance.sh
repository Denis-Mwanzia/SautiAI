#!/bin/bash
# Performance Testing Script for SautiAI

echo "=========================================="
echo "SautiAI Performance Test Suite"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if backend is running
echo "1. Checking Backend Status..."
if curl -sS http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is running${NC}"
else
    echo -e "${RED}❌ Backend is not running. Please start it first.${NC}"
    exit 1
fi

echo ""
echo "2. Testing API Endpoints Performance..."
echo "----------------------------------------"

# Test dashboard insights
echo -n "  Dashboard Insights: "
INSIGHTS_TIME=$(curl -w "%{time_total}" -sS -o /dev/null http://localhost:8000/api/v1/dashboard/insights?days=7)
INSIGHTS_SIZE=$(curl -sS http://localhost:8000/api/v1/dashboard/insights?days=7 | wc -c)
echo -e "${GREEN}${INSIGHTS_TIME}s${NC} (${INSIGHTS_SIZE} bytes)"

# Test sentiment trends
echo -n "  Sentiment Trends: "
TRENDS_TIME=$(curl -w "%{time_total}" -sS -o /dev/null http://localhost:8000/api/v1/dashboard/sentiment-trends?days=30)
TRENDS_SIZE=$(curl -sS http://localhost:8000/api/v1/dashboard/sentiment-trends?days=30 | wc -c)
echo -e "${GREEN}${TRENDS_TIME}s${NC} (${TRENDS_SIZE} bytes)"

# Test with compression
echo -n "  Dashboard Insights (GZip): "
GZIP_TIME=$(curl -H "Accept-Encoding: gzip" -w "%{time_total}" -sS -o /dev/null http://localhost:8000/api/v1/dashboard/insights?days=7)
GZIP_SIZE=$(curl -H "Accept-Encoding: gzip" -sS http://localhost:8000/api/v1/dashboard/insights?days=7 | wc -c)
echo -e "${GREEN}${GZIP_TIME}s${NC} (${GZIP_SIZE} bytes, ${YELLOW}$(( (INSIGHTS_SIZE - GZIP_SIZE) * 100 / INSIGHTS_SIZE ))% smaller${NC})"

# Test cache headers
echo ""
echo "3. Checking Cache Headers..."
echo "----------------------------------------"
CACHE_HEADER=$(curl -I -sS http://localhost:8000/api/v1/dashboard/insights?days=7 | grep -i "cache-control" | cut -d: -f2 | xargs)
if [ -n "$CACHE_HEADER" ]; then
    echo -e "  Cache-Control: ${GREEN}${CACHE_HEADER}${NC}"
else
    echo -e "  Cache-Control: ${RED}Not found${NC}"
fi

ETAG_HEADER=$(curl -I -sS http://localhost:8000/api/v1/dashboard/insights?days=7 | grep -i "etag" | cut -d: -f2 | xargs)
if [ -n "$ETAG_HEADER" ]; then
    echo -e "  ETag: ${GREEN}Present${NC}"
else
    echo -e "  ETag: ${YELLOW}Not present${NC}"
fi

PROCESS_TIME=$(curl -I -sS http://localhost:8000/api/v1/dashboard/insights?days=7 | grep -i "x-process-time" | cut -d: -f2 | xargs)
if [ -n "$PROCESS_TIME" ]; then
    echo -e "  X-Process-Time: ${GREEN}${PROCESS_TIME}s${NC}"
else
    echo -e "  X-Process-Time: ${YELLOW}Not found${NC}"
fi

# Test parallel requests
echo ""
echo "4. Testing Parallel Request Performance..."
echo "----------------------------------------"
echo -n "  Sequential requests (2x): "
START=$(date +%s.%N)
curl -sS -o /dev/null http://localhost:8000/api/v1/dashboard/insights?days=7
curl -sS -o /dev/null http://localhost:8000/api/v1/dashboard/sentiment-trends?days=30
END=$(date +%s.%N)
SEQUENTIAL_TIME=$(echo "$END - $START" | bc)
echo -e "${YELLOW}${SEQUENTIAL_TIME}s${NC}"

echo -n "  Parallel requests (2x): "
START=$(date +%s.%N)
curl -sS -o /dev/null http://localhost:8000/api/v1/dashboard/insights?days=7 &
curl -sS -o /dev/null http://localhost:8000/api/v1/dashboard/sentiment-trends?days=30 &
wait
END=$(date +%s.%N)
PARALLEL_TIME=$(echo "$END - $START" | bc)
echo -e "${GREEN}${PARALLEL_TIME}s${NC}"
IMPROVEMENT=$(echo "scale=1; ($SEQUENTIAL_TIME - $PARALLEL_TIME) * 100 / $SEQUENTIAL_TIME" | bc)
echo -e "  ${GREEN}Improvement: ${IMPROVEMENT}%${NC}"

# Test cache hit
echo ""
echo "5. Testing Cache Performance..."
echo "----------------------------------------"
echo -n "  First request (cache miss): "
CACHE_MISS=$(curl -w "%{time_total}" -sS -o /dev/null http://localhost:8000/api/v1/dashboard/insights?days=7)
echo -e "${YELLOW}${CACHE_MISS}s${NC}"

echo -n "  Second request (cache hit): "
sleep 1
CACHE_HIT=$(curl -w "%{time_total}" -sS -o /dev/null http://localhost:8000/api/v1/dashboard/insights?days=7)
echo -e "${GREEN}${CACHE_HIT}s${NC}"
CACHE_SPEEDUP=$(echo "scale=1; ($CACHE_MISS - $CACHE_HIT) * 100 / $CACHE_MISS" | bc)
echo -e "  ${GREEN}Cache speedup: ${CACHE_SPEEDUP}%${NC}"

# Frontend bundle test
echo ""
echo "6. Checking Frontend Bundle..."
echo "----------------------------------------"
if [ -d "frontend/dist" ]; then
    echo "  Building frontend..."
    cd frontend
    npm run build > /dev/null 2>&1
    if [ -d "dist/assets" ]; then
        echo "  Bundle sizes:"
        for file in dist/assets/*.js; do
            if [ -f "$file" ]; then
                SIZE=$(du -h "$file" | cut -f1)
                FILENAME=$(basename "$file")
                echo -e "    ${GREEN}${FILENAME}: ${SIZE}${NC}"
            fi
        done
        TOTAL_SIZE=$(du -sh dist/assets 2>/dev/null | cut -f1)
        echo -e "  ${GREEN}Total assets: ${TOTAL_SIZE}${NC}"
    fi
    cd ..
else
    echo -e "  ${YELLOW}Frontend not built. Run 'npm run build' in frontend/ directory${NC}"
fi

# Performance summary
echo ""
echo "=========================================="
echo "Performance Summary"
echo "=========================================="
echo ""
echo "API Response Times:"
echo "  - Dashboard Insights: ${INSIGHTS_TIME}s"
echo "  - Sentiment Trends: ${TRENDS_TIME}s"
echo ""
echo "Optimizations:"
echo "  - GZip Compression: $(( (INSIGHTS_SIZE - GZIP_SIZE) * 100 / INSIGHTS_SIZE ))% size reduction"
echo "  - Parallel Requests: ${IMPROVEMENT}% faster"
echo "  - Cache Hit: ${CACHE_SPEEDUP}% faster"
echo ""
echo -e "${GREEN}✅ Performance test complete!${NC}"

