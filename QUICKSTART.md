# Quick Start Guide 🚀

## Installation (First Time Only)

1. **Install Python dependencies:**
   ```bash
   pip install pronotepy flask flask-cors numpy pandas scipy python-dotenv
   ```

## Running the Application

### Option 1: Using the Startup Script (Windows)
Simply double-click `start.bat` in the project folder.

### Option 2: Manual Start

1. **Start the backend server:**
   ```bash
   cd backend
   python app.py
   ```
   Keep this terminal window open.

2. **Open the frontend:**
   - Open `frontend/index.html` in your web browser
   - Or serve it with: `python -m http.server 8000` from the frontend folder

## First Login

Use the demo credentials (already configured in `.env`):
- **URL**: `https://demo.index-education.net/pronote/eleve.html`
- **Username**: `demonstration`
- **Password**: `pronotevs`
- **ENT**: Leave empty

## Using Your Own PRONOTE Account

Edit the `.env` file with your credentials:
```env
PRONOTE_URL=https://your-school.index-education.net/pronote/eleve.html
PRONOTE_USERNAME=your_username
PRONOTE_PASSWORD=your_password
PRONOTE_ENT=  # Only if you use ENT (e.g., ac_rennes)
```

## Features Overview

### 📊 Vue d'ensemble (Overview)
- See your overall average and class average
- Compare all subjects with a bar chart
- View trend indicators for each subject

### 📝 Notes détaillées (Detailed Grades)
- Browse all your grades
- Filter by period or subject
- See grade details, coefficients, and class statistics

### 📈 Analyse avancée (Advanced Analysis)
- Statistical analysis: mean, median, standard deviation
- Trend predictions with confidence scores
- Subject-by-subject breakdown

### 🎯 Prédictions (Predictions)
1. **Calculate Needed Grade**: "What grade do I need to get a 15/20 average?"
2. **Simulate Multiple Grades**: "What average do I need on my next 3 tests?"

## Example Use Cases

### Scenario 1: Target a Specific Average
You have a 13/20 average in Math and want to reach 15/20:
1. Go to **Prédictions** tab
2. Select "Mathématiques"
3. Enter target: `15`
4. Set coefficient and grade scale
5. Click **Calculer**
→ See exactly what grade you need!

### Scenario 2: Plan Ahead
You have 3 tests coming up and want to maintain a 16/20 average:
1. Go to **Prédictions** tab
2. Use "Simuler plusieurs notes"
3. Select subject and enter target: `16`
4. Set number of grades: `3`
5. Click **Simuler**
→ See the average you need per test!

## Troubleshooting

**Backend won't start?**
- Make sure Python is installed: `python --version`
- Install dependencies: `pip install -r requirements.txt`

**Can't login?**
- Check your PRONOTE URL (must end with `/eleve.html`)
- Verify username and password
- For ENT users, check the correct ENT code

**No data showing?**
- Ensure backend is running on port 5000
- Check browser console for errors (F12)
- Verify you're logged in successfully

## Need Help?

Check the full `README.md` for detailed documentation!
