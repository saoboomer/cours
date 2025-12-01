"""
Flask Backend API for PRONOTE Grade Analysis Application
Provides REST endpoints for authentication, grade fetching, and analysis
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from pronote_client import PronoteClient
from grade_analyzer import GradeAnalyzer
from advanced_analytics import AdvancedAnalytics
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Allow all origins for development

# Store active sessions (in production, use proper session management)
sessions = {}


def validate_session():
    """Validate session and return client if valid"""
    token = request.headers.get('Authorization')
    if not token or token not in sessions:
        return None, jsonify({'error': 'Unauthorized - invalid or missing token'}), 401
    
    client = sessions[token]
    if not client or not hasattr(client, 'client') or not client.client:
        # Clean up invalid session
        del sessions[token]
        return None, jsonify({'error': 'Session expired - please login again'}), 401
    
    return client, None, None


def handle_api_error(func):
    """Decorator for consistent error handling"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"API Error in {func.__name__}: {e}")
            return jsonify({'error': f'Internal server error: {str(e)}'}), 500
    wrapper.__name__ = func.__name__
    return wrapper


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'PRONOTE Analysis API is running'})


@app.route('/api/schools/regions', methods=['GET'])
def get_regions_route():
    """Get all available regions"""
    from schools_database import get_regions
    regions = get_regions()
    print(f"Returning {len(regions)} regions")  # Debug
    return jsonify(regions)


@app.route('/api/schools/cities', methods=['GET'])
def get_cities_route():
    """Get cities in a region"""
    from schools_database import get_cities
    region = request.args.get('region')
    if not region:
        return jsonify({'error': 'Region parameter required'}), 400
    cities = get_cities(region)
    print(f"Returning {len(cities)} cities for region: {region}")  # Debug
    return jsonify(cities)


@app.route('/api/schools/list', methods=['GET'])
def get_schools_route():
    """Get schools in a city"""
    from schools_database import get_schools
    region = request.args.get('region')
    city = request.args.get('city')
    if not region or not city:
        return jsonify({'error': 'Region and city parameters required'}), 400
    schools = get_schools(region, city)
    print(f"Returning {len(schools)} schools for {city}, {region}")  # Debug
    return jsonify(schools)


@app.route('/api/schools/search', methods=['GET'])
def search_schools_route():
    """Search schools by name"""
    from schools_database import search_schools
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
    results = search_schools(query)
    print(f"Search for '{query}' returned {len(results)} results")  # Debug
    return jsonify(results)


@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    Authenticate with PRONOTE
    
    Request body:
        {
            "url": "PRONOTE instance URL",
            "username": "username",
            "password": "password",
            "ent": "ENT identifier (optional)"
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        url = data.get('url', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        ent = data.get('ent', '').strip() if data.get('ent') else None
        
        if not all([url, username, password]):
            return jsonify({'error': 'Missing required fields: url, username, and password are required'}), 400
        
        # Validate URL format
        if not url.startswith('http'):
            return jsonify({'error': 'URL must start with http:// or https://'}), 400
        
        print(f"Attempting login for user: {username} at {url}")
        
        client = PronoteClient(url, username, password, ent)
        
        if not client.login():
            return jsonify({'error': 'Authentication failed. Please check your credentials and URL.'}), 401
        
        # Generate session token (simplified - use proper JWT in production)
        session_token = f"{username}_{hash(password)}_{hash(url)}"
        sessions[session_token] = client
        
        try:
            student_info = client.get_student_info()
        except Exception as e:
            print(f"Warning: Could not fetch student info: {e}")
            student_info = {'name': username, 'class': 'Unknown', 'establishment': 'Unknown'}
        
        print(f"Login successful for {student_info.get('name', username)}")
        
        return jsonify({
            'success': True,
            'token': session_token,
            'student': student_info
        })
    
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': f'Login failed: {str(e)}'}), 500


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout and clear session"""
    try:
        token = request.headers.get('Authorization')
        
        if token and token in sessions:
            sessions[token].logout()
            del sessions[token]
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/student/info', methods=['GET'])
@handle_api_error
def get_student_info():
    """Get student information"""
    client, error_response, status_code = validate_session()
    if error_response:
        return error_response, status_code
    
    try:
        info = client.get_student_info()
        return jsonify(info)
    except Exception as e:
        print(f"Error fetching student info: {e}")
        return jsonify({'error': 'Failed to fetch student information'}), 500


@app.route('/api/periods', methods=['GET'])
@handle_api_error
def get_periods():
    """Get all available periods"""
    client, error_response, status_code = validate_session()
    if error_response:
        return error_response, status_code
    
    try:
        periods = client.get_periods()
        return jsonify(periods)
    except Exception as e:
        print(f"Error fetching periods: {e}")
        return jsonify({'error': 'Failed to fetch periods'}), 500


@app.route('/api/grades', methods=['GET'])
@handle_api_error
def get_grades():
    """
    Get grades for a period
    
    Query params:
        period: Period name (optional)
    """
    client, error_response, status_code = validate_session()
    if error_response:
        return error_response, status_code
    
    try:
        period = request.args.get('period')
        grades = client.get_grades(period)
        return jsonify(grades)
    except Exception as e:
        print(f"Error fetching grades: {e}")
        return jsonify({'error': 'Failed to fetch grades'}), 500


@app.route('/api/averages', methods=['GET'])
@handle_api_error
def get_averages():
    """
    Get averages for all subjects
    
    Query params:
        period: Period name (optional)
    """
    client, error_response, status_code = validate_session()
    if error_response:
        return error_response, status_code
    
    try:
        period = request.args.get('period')
        averages = client.get_averages(period)
        return jsonify(averages)
    except Exception as e:
        print(f"Error fetching averages: {e}")
        return jsonify({'error': 'Failed to fetch averages'}), 500


@app.route('/api/analysis/statistics', methods=['GET'])
def get_statistics():
    """
    Get statistical analysis
    
    Query params:
        period: Period name (optional)
        subject: Subject name (optional)
    """
    try:
        token = request.headers.get('Authorization')
        
        if not token or token not in sessions:
            return jsonify({'error': 'Unauthorized'}), 401
        
        client = sessions[token]
        period = request.args.get('period')
        subject = request.args.get('subject')
        
        grades = client.get_grades(period)
        analyzer = GradeAnalyzer(grades)
        
        stats = analyzer.get_statistics(subject)
        
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analysis/trends', methods=['GET'])
def get_trends():
    """
    Get trend analysis for a subject
    
    Query params:
        period: Period name (optional)
        subject: Subject name (required)
    """
    try:
        token = request.headers.get('Authorization')
        
        if not token or token not in sessions:
            return jsonify({'error': 'Unauthorized'}), 401
        
        subject = request.args.get('subject')
        if not subject:
            return jsonify({'error': 'Subject parameter required'}), 400
        
        client = sessions[token]
        period = request.args.get('period')
        
        grades = client.get_grades(period)
        analyzer = GradeAnalyzer(grades)
        
        trend = analyzer.predict_trend(subject)
        
        return jsonify(trend)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analysis/needed-grade', methods=['POST'])
def calculate_needed_grade():
    """
    Calculate what grade is needed to reach target average
    
    Request body:
        {
            "subject": "Subject name",
            "target_average": 15.0,
            "coefficient": 1.0,
            "out_of": 20.0,
            "period": "Period name (optional)"
        }
    """
    try:
        token = request.headers.get('Authorization')
        
        if not token or token not in sessions:
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        subject = data.get('subject')
        target_average = data.get('target_average')
        
        if not subject or target_average is None:
            return jsonify({'error': 'Missing required fields'}), 400
        
        coefficient = data.get('coefficient', 1.0)
        out_of = data.get('out_of', 20.0)
        period = data.get('period')
        
        client = sessions[token]
        grades = client.get_grades(period)
        analyzer = GradeAnalyzer(grades)
        
        result = analyzer.calculate_needed_grade(
            subject, 
            float(target_average),
            float(coefficient),
            float(out_of)
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analysis/simulate-grades', methods=['POST'])
def simulate_grades():
    """
    Simulate multiple future grades
    
    Request body:
        {
            "subject": "Subject name",
            "target_average": 15.0,
            "num_grades": 3,
            "coefficient": 1.0,
            "out_of": 20.0,
            "period": "Period name (optional)"
        }
    """
    try:
        token = request.headers.get('Authorization')
        
        if not token or token not in sessions:
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        subject = data.get('subject')
        target_average = data.get('target_average')
        num_grades = data.get('num_grades')
        
        if not all([subject, target_average is not None, num_grades]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        coefficient = data.get('coefficient', 1.0)
        out_of = data.get('out_of', 20.0)
        period = data.get('period')
        
        client = sessions[token]
        grades = client.get_grades(period)
        analyzer = GradeAnalyzer(grades)
        
        result = analyzer.simulate_multiple_grades(
            subject,
            float(target_average),
            int(num_grades),
            float(coefficient),
            float(out_of)
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analysis/comparison', methods=['GET'])
def get_subject_comparison():
    """
    Compare performance across all subjects
    
    Query params:
        period: Period name (optional)
    """
    try:
        token = request.headers.get('Authorization')
        
        if not token or token not in sessions:
            return jsonify({'error': 'Unauthorized'}), 401
        
        client = sessions[token]
        period = request.args.get('period')
        
        grades = client.get_grades(period)
        analyzer = GradeAnalyzer(grades)
        
        comparison = analyzer.get_subject_comparison()
        
        return jsonify(comparison)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/advanced/consistency', methods=['GET'])
def get_consistency():
    """Get consistency index for a subject"""
    try:
        token = request.headers.get('Authorization')
        if not token or token not in sessions:
            return jsonify({'error': 'Unauthorized'}), 401
        
        subject = request.args.get('subject')
        if not subject:
            return jsonify({'error': 'Subject parameter required'}), 400
        
        client = sessions[token]
        grades = client.get_grades()
        analytics = AdvancedAnalytics(grades)
        result = analytics.calculate_consistency_index(subject)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/advanced/improvement-rate', methods=['GET'])
def get_improvement_rate():
    """Get improvement rate for a subject"""
    try:
        token = request.headers.get('Authorization')
        if not token or token not in sessions:
            return jsonify({'error': 'Unauthorized'}), 401
        
        subject = request.args.get('subject')
        if not subject:
            return jsonify({'error': 'Subject parameter required'}), 400
        
        client = sessions[token]
        grades = client.get_grades()
        analytics = AdvancedAnalytics(grades)
        result = analytics.calculate_improvement_rate(subject)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/advanced/volatility', methods=['GET'])
def get_volatility():
    """Get volatility vs difficulty analysis"""
    try:
        token = request.headers.get('Authorization')
        if not token or token not in sessions:
            return jsonify({'error': 'Unauthorized'}), 401
        
        subject = request.args.get('subject')
        if not subject:
            return jsonify({'error': 'Subject parameter required'}), 400
        
        client = sessions[token]
        grades = client.get_grades()
        analytics = AdvancedAnalytics(grades)
        result = analytics.analyze_volatility_vs_difficulty(subject)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/advanced/context-performance', methods=['GET'])
def get_context_performance():
    """Get performance by context/assessment type"""
    try:
        token = request.headers.get('Authorization')
        if not token or token not in sessions:
            return jsonify({'error': 'Unauthorized'}), 401
        
        subject = request.args.get('subject')
        if not subject:
            return jsonify({'error': 'Subject parameter required'}), 400
        
        client = sessions[token]
        grades = client.get_grades()
        analytics = AdvancedAnalytics(grades)
        result = analytics.analyze_performance_by_context(subject)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/advanced/gpa-projection', methods=['GET'])
def get_gpa_projection():
    """Get cumulative GPA projection"""
    try:
        token = request.headers.get('Authorization')
        if not token or token not in sessions:
            return jsonify({'error': 'Unauthorized'}), 401
        
        client = sessions[token]
        grades = client.get_grades()
        analytics = AdvancedAnalytics(grades)
        result = analytics.project_cumulative_gpa()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/advanced/correlations', methods=['GET'])
def get_correlations():
    """Get subject correlations"""
    try:
        token = request.headers.get('Authorization')
        if not token or token not in sessions:
            return jsonify({'error': 'Unauthorized'}), 401
        
        client = sessions[token]
        grades = client.get_grades()
        analytics = AdvancedAnalytics(grades)
        result = analytics.analyze_subject_correlations()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/advanced/benchmark', methods=['GET'])
def get_benchmark():
    """Get benchmark vs class average"""
    try:
        token = request.headers.get('Authorization')
        if not token or token not in sessions:
            return jsonify({'error': 'Unauthorized'}), 401
        
        subject = request.args.get('subject')
        if not subject:
            return jsonify({'error': 'Subject parameter required'}), 400
        
        client = sessions[token]
        grades = client.get_grades()
        analytics = AdvancedAnalytics(grades)
        result = analytics.benchmark_vs_class(subject)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/advanced/temporal-decay', methods=['GET'])
def get_temporal_decay():
    """Get temporal decay/fatigue analysis"""
    try:
        token = request.headers.get('Authorization')
        if not token or token not in sessions:
            return jsonify({'error': 'Unauthorized'}), 401
        
        subject = request.args.get('subject')
        if not subject:
            return jsonify({'error': 'Subject parameter required'}), 400
        
        client = sessions[token]
        grades = client.get_grades()
        analytics = AdvancedAnalytics(grades)
        result = analytics.analyze_temporal_decay(subject)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/advanced/forecast', methods=['GET'])
def get_forecast():
    """Get forecast with confidence intervals"""
    try:
        token = request.headers.get('Authorization')
        if not token or token not in sessions:
            return jsonify({'error': 'Unauthorized'}), 401
        
        subject = request.args.get('subject')
        if not subject:
            return jsonify({'error': 'Subject parameter required'}), 400
        
        client = sessions[token]
        grades = client.get_grades()
        analytics = AdvancedAnalytics(grades)
        result = analytics.forecast_with_confidence(subject)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/advanced/learning-efficiency', methods=['GET'])
def get_learning_efficiency():
    """Get learning efficiency index"""
    try:
        token = request.headers.get('Authorization')
        if not token or token not in sessions:
            return jsonify({'error': 'Unauthorized'}), 401
        
        subject = request.args.get('subject')
        if not subject:
            return jsonify({'error': 'Subject parameter required'}), 400
        
        client = sessions[token]
        grades = client.get_grades()
        analytics = AdvancedAnalytics(grades)
        result = analytics.calculate_learning_efficiency(subject)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    app.run(host='0.0.0.0', port=port, debug=debug)
