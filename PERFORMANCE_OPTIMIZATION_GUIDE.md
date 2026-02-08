# Performance Optimization Guide

## Issues Found and Solutions

### 1. Cache TTL Optimization
**Problem**: Very short cache TTLs (10-30 seconds) cause frequent API calls.

**Solution**: Increase cache TTLs based on data volatility:
- Projects list: 300s → 600s (10 minutes)
- User data: 30s → 180s (3 minutes)
- Metrics: 10s → 60s (1 minute)
- Role counts: 10s → 60s (1 minute)

### 2. N+1 Query Problem
**Problem**: Looping through projects and making individual API calls.

**Current Code** (lines 1145-1151):
```python
for project_id in project_ids:
    metrics = get_project_metrics_cached(project_id, date_str, date_str)
```

**Solution**: Create batch endpoints in the API to fetch data for multiple projects at once.

### 3. Connection Pool Tuning
**Problem**: Small connection pool (10) may be insufficient for concurrent requests.

**Solution**: Increase pool size for hosted environments:
```python
pool_connections=20,
pool_maxsize=50,
```

### 4. Request Timeout Optimization
**Problem**: Long read timeout (30s) can cause slow responses to block the UI.

**Solution**: Reduce timeouts for hosted environments:
```python
timeout=(5, 15)  # connect: 5s, read: 15s
```

### 5. Lazy Loading with Tabs/Expanders
**Problem**: All sections load simultaneously on page load.

**Solution**: Use st.tabs() to defer loading of heavy sections until viewed.

### 6. Database Query Optimization
**Recommendations**:
- Add database indexes on frequently queried columns
- Use eager loading for relationships in SQLAlchemy
- Consider database connection pooling

### 7. API Response Compression
**Add to FastAPI main.py**:
```python
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### 8. Reduce API Call Frequency
- Implement "Load More" buttons instead of loading all data
- Add manual refresh buttons with longer auto-refresh intervals
- Show loading indicators for better UX

## Priority Implementation Order

1. **High Priority** (Immediate 2-3x improvement):
   - Increase cache TTLs
   - Add batch API endpoints
   - Optimize connection pool

2. **Medium Priority** (Additional 1.5-2x improvement):
   - Add lazy loading with tabs
   - Reduce timeouts
   - Add response compression

3. **Low Priority** (Long-term improvements):
   - Database indexing
   - Pagination
   - WebSocket for real-time updates
