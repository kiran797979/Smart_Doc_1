# 🐛 File Upload Troubleshooting Guide

## Issue: "Upload failed. Please try again."

### 🔍 Diagnosed Problems & Solutions

#### 1. ✅ **CORS Configuration Issue (FIXED)**

**Problem**: Backend CORS configuration didn't include specific Vercel deployment URLs

**Solution Applied**: Updated `backend/api/api_server.py` CORS settings to include:
- `https://frontend-amber-alpha-10.vercel.app`
- `https://frontend-22at20ato-kirans-projects-abcb66a1.vercel.app`
- All previous deployment URLs

```python
allow_origins=[
    # ... existing origins ...
    "https://frontend-amber-alpha-10.vercel.app",  # Current frontend URL
    "https://frontend-22at20ato-kirans-projects-abcb66a1.vercel.app",  # Alternative frontend URL
    # ... additional URLs ...
]
```

#### 2. 🕐 **Timeout Issues**

**Current Configuration**: 
- Frontend timeout: 60 seconds for uploads
- Backend timeout: Default (should be sufficient)

**Files affected**: `frontend/src/services/api.ts`

#### 3. 📁 **File Size & Type Limits**

**Supported formats**: `.pdf`, `.docx`, `.doc`, `.txt`
**Current limits**: No explicit size limit (uses default FastAPI limits)

### 🧪 **Quick Tests to Run**

#### Test 1: Backend Health Check
```bash
curl https://smart-doc-1-3.onrender.com/health
# Should return: {"status":"healthy","timestamp":"..."}
```

#### Test 2: CORS Preflight Test
```bash
curl -X OPTIONS https://smart-doc-1-3.onrender.com/upload \
  -H "Origin: https://frontend-amber-alpha-10.vercel.app" \
  -H "Access-Control-Request-Method: POST"
# Should return CORS headers
```

#### Test 3: Simple Upload Test
1. Go to https://frontend-amber-alpha-10.vercel.app
2. Open browser Developer Tools (F12) → Network tab
3. Try uploading a small text file
4. Check for CORS errors or network failures

### 🚀 **Immediate Fix Required**

**The CORS update needs to be deployed to the backend on Render.**

Since the backend is deployed on Render, the changes to `api_server.py` need to be:
1. Committed to GitHub
2. Deployed to Render (auto-deployment should trigger)

### 📋 **Common Upload Issues & Solutions**

| Issue | Symptoms | Solution |
|-------|----------|----------|
| CORS Error | "Access to fetch blocked by CORS policy" | ✅ Fixed - backend CORS updated |
| Network Timeout | "Upload timed out" | Use smaller files or check network |
| File Type Error | "Unsupported file type" | Use .pdf, .docx, .doc, .txt files |
| File Size Error | "Request entity too large" | Use files smaller than 16MB |

### 🎯 **Next Steps**

1. **Deploy Backend Changes**: Commit and push CORS updates to trigger Render deployment
2. **Test Upload**: Try uploading after backend deployment completes
3. **Monitor Logs**: Check Render logs for any runtime errors
4. **Frontend Debugging**: Use browser developer tools to inspect failed requests

### 🔧 **Emergency Workaround**

If the issue persists, you can test locally:
1. Run backend locally: `cd backend && python api/api_server.py`
2. Update frontend API URL temporarily to `http://localhost:8000`
3. Test upload functionality locally

---

**Status**: CORS issue identified and fixed. Awaiting backend deployment to resolve upload failures.