# PRONOTE Grade Analyzer - Troubleshooting Guide

## 🔧 Common Issues and Solutions

### 1. Authentication Failed

**Error**: "Authentication failed. Please check your credentials and URL."

**Possible Causes & Solutions**:

#### A. URL Format Issues
- ✅ **Correct**: `https://your-school.index-education.net/pronote/eleve.html`
- ❌ **Wrong**: `https://your-school.index-education.net/pronote/`
- ❌ **Wrong**: `https://your-school.index-education.net/`

**Solution**: Make sure your URL ends with `/pronote/eleve.html`

#### B. Credentials Issues
- Check your username and password
- Make sure there are no extra spaces
- Try logging into PRONOTE web interface first to verify credentials

#### C. ENT (Regional Authentication) Issues
If your school uses regional authentication (ENT), you need to specify the correct ENT identifier:

**Common ENT identifiers**:
- `ac_rennes` - Académie de Rennes
- `ac_paris` - Académie de Paris  
- `ac_lyon` - Académie de Lyon
- `ac_bordeaux` - Académie de Bordeaux
- `ac_toulouse` - Académie de Toulouse
- `ac_montpellier` - Académie de Montpellier

**How to find your ENT**:
1. Check your school's PRONOTE login page
2. Look for regional authentication options
3. Contact your school's IT department

#### D. Network/Server Issues
- Check your internet connection
- Verify the PRONOTE server is accessible
- Try accessing PRONOTE in your browser first

### 2. Schools Database Issues

**Issue**: Not all schools are showing up in the search.

**Solution**: The database has been expanded and now includes:
- ✅ All schools are now returned (removed 20-result limit)
- ✅ Added more schools across all regions
- ✅ Improved search functionality

**Total schools in database**: 50+ schools across 14 regions

### 3. Backend Connection Issues

**Error**: "Backend not responding"

**Solutions**:
1. Make sure the backend is running:
   ```bash
   cd backend
   python app.py
   ```

2. Check if port 5000 is available:
   ```bash
   # Windows
   netstat -an | findstr :5000
   
   # Linux/Mac
   lsof -i :5000
   ```

3. Try restarting the backend server

### 4. Data Loading Issues

**Issue**: Grades or periods not loading

**Possible Causes**:
- Network timeout during data fetch
- PRONOTE server temporarily unavailable
- Session expired

**Solutions**:
1. Try refreshing the page
2. Log out and log back in
3. Check your internet connection
4. Wait a few minutes and try again

## 🛠️ Debugging Steps

### Step 1: Test Backend Connection
```bash
curl http://localhost:5000/api/health
```

### Step 2: Test Schools Database
```bash
curl http://localhost:5000/api/schools/regions
```

### Step 3: Test Authentication
Use the test script:
```bash
python test_auth.py
```

### Step 4: Check Browser Console
1. Open browser developer tools (F12)
2. Go to Console tab
3. Look for error messages
4. Check Network tab for failed requests

## 📞 Getting Help

If you're still having issues:

1. **Check the logs**: Look at the backend console output for error messages
2. **Try the demo**: Use the demo credentials to test if the system works
3. **Contact support**: Provide the following information:
   - Your school's PRONOTE URL
   - Error messages from the console
   - Browser and operating system information

## 🔍 Advanced Troubleshooting

### Manual PRONOTE Test
Test your credentials directly with pronotepy:
```python
import pronotepy

client = pronotepy.Client(
    "YOUR_PRONOTE_URL",
    "YOUR_USERNAME", 
    "YOUR_PASSWORD"
)

print(f"Logged in: {client.logged_in}")
```

### Check ENT Availability
```python
from pronotepy.ent import ent
print("Available ENTs:", [attr for attr in dir(ent) if not attr.startswith('_')])
```

## 📋 System Requirements

- **Python**: 3.8 or higher
- **Browser**: Modern browser with JavaScript enabled
- **Network**: Internet connection to access PRONOTE servers
- **Dependencies**: All required packages are in `requirements.txt`

## 🚀 Performance Tips

1. **Use specific periods**: Select a specific period instead of "All periods"
2. **Clear browser cache**: If experiencing slow loading
3. **Close other tabs**: Free up memory for better performance
4. **Use wired connection**: For more stable data loading
