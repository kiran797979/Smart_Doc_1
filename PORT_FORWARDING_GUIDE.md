# Smart Doc Checker - Port Forwarding Quick Guide

## 🎯 Current Status
- **Frontend**: Running on `http://localhost:3000`
- **Backend**: Running on `http://localhost:8000` 
- **Local IP**: `10.25.6.23`

## 🌐 Access Options

### 1. Local Network Access (LAN) - **READY NOW**
Your Smart Doc Checker is accessible on your local network:

**Frontend**: `http://10.25.6.23:3000`
**Backend**: `http://10.25.6.23:8000`

Anyone on the same WiFi/network can access these URLs!

### 2. Internet Access (WAN) - **Requires Setup**

#### Option A: Router Port Forwarding
1. Access router admin (usually `192.168.1.1`)
2. Find "Port Forwarding" section
3. Add rules:
   - **Port 3000** → **10.25.6.23:3000** (Frontend)
   - **Port 8000** → **10.25.6.23:8000** (Backend)
4. Find your public IP at [whatismyip.com](https://whatismyip.com)
5. Access via: `http://[PUBLIC_IP]:3000`

#### Option B: ngrok Tunnels (Recommended for Testing)
```bash
# Install ngrok from: https://ngrok.com/download
# Then run in separate terminals:
ngrok http 3000  # Frontend tunnel
ngrok http 8000  # Backend tunnel
```
- Provides HTTPS URLs like: `https://abc123.ngrok.io`
- No router configuration needed
- Secure and temporary

#### Option C: Cloud Deployment (Production)
Use the cloud deployment files we created:
```bash
# Deploy to Render (Backend) + Vercel (Frontend)
deploy_cloud.bat
```

### 3. Windows Firewall (Run as Administrator)
```cmd
# Run PowerShell as Administrator, then:
netsh advfirewall firewall add rule name="Smart Doc Frontend" dir=in action=allow protocol=TCP localport=3000
netsh advfirewall firewall add rule name="Smart Doc Backend" dir=in action=allow protocol=TCP localport=8000
```

## 🚀 Quick Test Steps

1. **Local Test**: Open `http://localhost:3000`
2. **LAN Test**: From another device, open `http://10.25.6.23:3000`
3. **Upload a document** and verify the full workflow works
4. **API Test**: Check `http://10.25.6.23:8000/docs` for API docs

## 📱 Mobile Access
From phones/tablets on same WiFi:
- Open browser → `http://10.25.6.23:3000`
- Should work perfectly for document uploads and analysis!

## 🔒 Security Notes
- Local network access is generally safe
- For internet access, consider authentication
- Use HTTPS in production (ngrok provides this automatically)
- Monitor access logs for unusual activity