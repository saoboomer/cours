# PRONOTE Grade Analyzer 📊

A comprehensive web application for analyzing PRONOTE grades with advanced prediction tools, trend analysis, and statistical insights.

## Features ✨

### 🔐 Authentication
- Secure login to PRONOTE via pronotepy
- Support for ENT (regional accounts)
- Session management

### 📈 Grade Analysis
- **Overview Dashboard**: View overall averages, class comparisons, and subject statistics
- **Detailed Grades View**: Browse all your grades with filtering options
- **Statistical Analysis**: Mean, median, standard deviation, min/max for each subject
- **Trend Prediction**: Linear regression-based trend analysis with confidence scores
- **Subject Comparison**: Visual comparison of performance across all subjects

### 🎯 Prediction Tools
1. **Calculate Needed Grade**: Find out what grade you need on your next test to reach a target average
   - Customizable coefficient and grade scale
   - Feasibility analysis (easy/moderate/difficult/impossible)
   
2. **Simulate Multiple Grades**: Calculate the average grade needed over several future assessments
   - Plan ahead for multiple upcoming tests
   - Realistic goal setting

### 📊 Visualizations
- Interactive bar charts for subject comparison
- Color-coded trend indicators (improving/stable/declining)
- Beautiful, modern UI with responsive design

## Installation 🚀

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- A modern web browser

### Setup

1. **Clone or navigate to the project directory**
   ```bash
   cd windsurf-project
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your PRONOTE credentials:
   ```env
   PRONOTE_URL=https://your-pronote-instance.com/pronote/eleve.html
   PRONOTE_USERNAME=your_username
   PRONOTE_PASSWORD=your_password
   PRONOTE_ENT=  # Optional: e.g., ac_rennes, ac_paris, etc.
   
   FLASK_PORT=5000
   FLASK_DEBUG=True
   ```

4. **Start the backend server**
   ```bash
   cd backend
   python app.py
   ```
   
   The API will be available at `http://localhost:5000`

5. **Open the frontend**
   
   Open `frontend/index.html` in your web browser, or serve it with a local server:
   ```bash
   cd frontend
   python -m http.server 8000
   ```
   
   Then navigate to `http://localhost:8000`

## Usage 📖

### Login
1. Enter your PRONOTE instance URL
2. Provide your username and password
3. (Optional) Specify your ENT if you use regional authentication
4. Click "Se connecter"

### Navigate the Dashboard
- **Vue d'ensemble**: See your overall statistics and subject comparison
- **Notes détaillées**: Browse all your grades with filters
- **Analyse avancée**: View detailed statistics and trends for each subject
- **Prédictions**: Use prediction tools to plan your academic goals

### Using Prediction Tools

#### Calculate Needed Grade
1. Select a subject
2. Enter your target average (out of 20)
3. Specify the coefficient and scale of the next grade
4. Click "Calculer" to see what grade you need

#### Simulate Multiple Grades
1. Select a subject
2. Enter your target average
3. Specify how many future grades to consider
4. Click "Simuler" to see the average needed per grade

## Project Structure 📁

```
windsurf-project/
├── backend/
│   ├── app.py                 # Flask REST API
│   ├── pronote_client.py      # PRONOTE API integration
│   └── grade_analyzer.py      # Analysis algorithms
├── frontend/
│   ├── index.html             # Main HTML structure
│   ├── styles.css             # Styling and design
│   └── app.js                 # Frontend logic and API calls
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## API Endpoints 🔌

### Authentication
- `POST /api/auth/login` - Login to PRONOTE
- `POST /api/auth/logout` - Logout and clear session

### Data Retrieval
- `GET /api/student/info` - Get student information
- `GET /api/periods` - Get all available periods
- `GET /api/grades` - Get grades (optional: ?period=name)
- `GET /api/averages` - Get averages (optional: ?period=name)

### Analysis
- `GET /api/analysis/statistics` - Get statistical analysis
- `GET /api/analysis/trends` - Get trend analysis for a subject
- `GET /api/analysis/comparison` - Compare performance across subjects
- `POST /api/analysis/needed-grade` - Calculate needed grade
- `POST /api/analysis/simulate-grades` - Simulate multiple grades

## Technologies Used 💻

### Backend
- **Flask**: Web framework for REST API
- **pronotepy**: Python library for PRONOTE API integration
- **NumPy**: Numerical computing for statistics
- **Pandas**: Data manipulation and analysis
- **SciPy**: Scientific computing for linear regression

### Frontend
- **Vanilla JavaScript**: No framework dependencies
- **Chart.js**: Interactive charts and visualizations
- **Modern CSS**: Responsive design with CSS Grid and Flexbox

## Analysis Algorithms 🧮

### Statistical Analysis
- Mean, median, mode
- Standard deviation and variance
- Min/max values and range

### Trend Prediction
- Linear regression using SciPy
- Confidence scoring based on R-squared values
- Prediction of next grade based on historical trends

### Grade Calculations
- Weighted averages with coefficients
- Normalization to /20 scale
- What-if scenario simulations

## Security Notes 🔒

- **Never commit your `.env` file** to version control
- Use environment variables for sensitive credentials
- In production, implement proper JWT-based authentication
- Use HTTPS for all API communications
- Consider implementing rate limiting and CORS policies

## Troubleshooting 🔧

### Login Issues
- Verify your PRONOTE URL is correct (should end with `/eleve.html`)
- Check your username and password
- If using ENT, ensure the ENT identifier is correct (see [pronotepy ENT list](https://github.com/bain3/pronotepy/blob/master/pronotepy/ent/ent.py))

### API Connection Issues
- Ensure the backend server is running on port 5000
- Check that CORS is properly configured
- Verify the API_BASE_URL in `frontend/app.js` matches your backend URL

### No Grades Showing
- Ensure you're logged in successfully
- Check that the current period has grades
- Try selecting a different period from the filter

## Contributing 🤝

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## License 📄

This project is open source and available for educational purposes.

## Acknowledgments 🙏

- [pronotepy](https://github.com/bain3/pronotepy) - Python API for PRONOTE
- [PapillonApp](https://github.com/PapillonApp) - Inspiration for PRONOTE integration
- Chart.js - Beautiful charts and visualizations

## Support 💬

For issues or questions, please open an issue on the project repository.

---

**Made with ❤️ for students using PRONOTE**
