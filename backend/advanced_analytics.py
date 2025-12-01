"""
Advanced Analytics Module
10 advanced metrics for comprehensive grade analysis
"""

import numpy as np
from typing import List, Dict, Any, Optional
from scipy import stats
from datetime import datetime, timedelta
from collections import defaultdict


class AdvancedAnalytics:
    """Advanced analytics for grade analysis"""
    
    def __init__(self, grades: List[Dict[str, Any]]):
        self.grades = grades
        self.subjects = self._group_by_subject()
    
    def _group_by_subject(self) -> Dict[str, List[Dict[str, Any]]]:
        """Group grades by subject"""
        subjects = {}
        for grade in self.grades:
            subject = grade['subject']
            if subject not in subjects:
                subjects[subject] = []
            subjects[subject].append(grade)
        return subjects
    
    def _parse_grade(self, grade_str: str) -> Optional[float]:
        """Parse grade string to float"""
        if not grade_str or grade_str in ['Absent', 'Dispensé', 'Non noté', 'N/A']:
            return None
        try:
            grade_str = str(grade_str).replace(',', '.')
            return float(grade_str)
        except (ValueError, TypeError):
            return None
    
    def calculate_consistency_index(self, subject: str) -> Dict[str, Any]:
        """
        1. Consistency Index (Academic Stability)
        Measure how stable a student's grades are over time
        """
        if subject not in self.subjects:
            return None
        
        grades = self.subjects[subject]
        data_points = []
        
        for grade in grades:
            grade_value = self._parse_grade(grade['grade'])
            if grade_value is None or not grade['date']:
                continue
            
            out_of = float(grade['out_of']) if grade['out_of'] else 20
            normalized_grade = (grade_value / out_of) * 20
            date_obj = datetime.strptime(grade['date'], '%Y-%m-%d')
            data_points.append((date_obj, normalized_grade))
        
        if len(data_points) < 2:
            return {'consistency_score': 0, 'stability': 'insufficient_data', 'reversals': 0, 'std_dev': 0}
        
        data_points.sort(key=lambda x: x[0])
        grades_array = np.array([p[1] for p in data_points])
        std_dev = np.std(grades_array)
        
        # Count trend reversals
        reversals = 0
        for i in range(1, len(grades_array) - 1):
            if (grades_array[i] > grades_array[i-1] and grades_array[i] > grades_array[i+1]) or \
               (grades_array[i] < grades_array[i-1] and grades_array[i] < grades_array[i+1]):
                reversals += 1
        
        # Calculate consistency score (0-100)
        max_std_dev = 10
        max_reversals = len(grades_array) / 2
        std_penalty = min(std_dev / max_std_dev, 1.0) * 50
        reversal_penalty = min(reversals / max_reversals, 1.0) * 50 if max_reversals > 0 else 0
        consistency_score = 100 - std_penalty - reversal_penalty
        
        stability = 'very_stable' if consistency_score >= 80 else \
                   'stable' if consistency_score >= 60 else \
                   'moderate' if consistency_score >= 40 else 'volatile'
        
        return {
            'consistency_score': round(consistency_score, 2),
            'stability': stability,
            'reversals': reversals,
            'std_dev': round(std_dev, 2),
            'grade_count': len(grades_array)
        }
    
    def calculate_improvement_rate(self, subject: str, window_days: int = 30) -> Dict[str, Any]:
        """
        2. Improvement Rate per Period
        Analyze grade progression per time window
        """
        if subject not in self.subjects:
            return None
        
        grades = self.subjects[subject]
        data_points = []
        
        for grade in grades:
            grade_value = self._parse_grade(grade['grade'])
            if grade_value is None or not grade['date']:
                continue
            
            out_of = float(grade['out_of']) if grade['out_of'] else 20
            normalized_grade = (grade_value / out_of) * 20
            date_obj = datetime.strptime(grade['date'], '%Y-%m-%d')
            data_points.append((date_obj, normalized_grade))
        
        if len(data_points) < 2:
            return {'improvement_rate': 0, 'rate_per_month': 0, 'trend': 'insufficient_data'}
        
        data_points.sort(key=lambda x: x[0])
        first_date, first_grade = data_points[0]
        last_date, last_grade = data_points[-1]
        
        days_elapsed = (last_date - first_date).days
        if days_elapsed == 0:
            return {'improvement_rate': 0, 'rate_per_month': 0, 'trend': 'insufficient_time'}
        
        total_improvement = last_grade - first_grade
        rate_per_month = (total_improvement / days_elapsed) * 30
        
        trend = 'strong_improvement' if rate_per_month > 0.5 else \
                'slight_improvement' if rate_per_month > 0 else \
                'slight_decline' if rate_per_month > -0.5 else 'strong_decline'
        
        return {
            'improvement_rate': round(total_improvement, 2),
            'rate_per_month': round(rate_per_month, 2),
            'days_elapsed': days_elapsed,
            'trend': trend,
            'start_grade': round(first_grade, 2),
            'current_grade': round(last_grade, 2)
        }
    
    def analyze_volatility_vs_difficulty(self, subject: str) -> Dict[str, Any]:
        """
        3. Grade Volatility vs. Difficulty Correlation
        Analyze if high coefficients cause more grade dispersion
        """
        if subject not in self.subjects:
            return None
        
        grades = self.subjects[subject]
        low_coef_grades = []
        medium_coef_grades = []
        high_coef_grades = []
        
        for grade in grades:
            grade_value = self._parse_grade(grade['grade'])
            if grade_value is None:
                continue
            
            out_of = float(grade['out_of']) if grade['out_of'] else 20
            normalized_grade = (grade_value / out_of) * 20
            coefficient = float(grade['coefficient']) if grade['coefficient'] else 1
            
            if coefficient < 1.5:
                low_coef_grades.append(normalized_grade)
            elif coefficient < 2.5:
                medium_coef_grades.append(normalized_grade)
            else:
                high_coef_grades.append(normalized_grade)
        
        return {
            'low_stakes': self._volatility_stats(low_coef_grades, 'Low (<1.5)'),
            'medium_stakes': self._volatility_stats(medium_coef_grades, 'Medium (1.5-2.5)'),
            'high_stakes': self._volatility_stats(high_coef_grades, 'High (≥2.5)')
        }
    
    def _volatility_stats(self, grades: List[float], label: str) -> Dict[str, Any]:
        """Helper for volatility statistics"""
        if not grades:
            return {'label': label, 'count': 0, 'std_dev': 0, 'average': 0}
        
        grades_array = np.array(grades)
        return {
            'label': label,
            'count': len(grades),
            'std_dev': round(np.std(grades_array), 2),
            'average': round(np.mean(grades_array), 2),
            'range': round(np.max(grades_array) - np.min(grades_array), 2)
        }
    
    def analyze_performance_by_context(self, subject: str) -> Dict[str, Any]:
        """
        4. Best & Worst Context Performance
        Analyze performance by assessment type
        """
        if subject not in self.subjects:
            return None
        
        grades = self.subjects[subject]
        context_grades = defaultdict(list)
        
        keywords = {
            'DS': ['ds', 'devoir surveillé', 'contrôle'],
            'DM': ['dm', 'devoir maison', 'homework'],
            'Oral': ['oral', 'exposé', 'présentation'],
            'TP': ['tp', 'travaux pratiques', 'practical'],
            'Quiz': ['quiz', 'qcm', 'test']
        }
        
        for grade in grades:
            grade_value = self._parse_grade(grade['grade'])
            if grade_value is None:
                continue
            
            out_of = float(grade['out_of']) if grade['out_of'] else 20
            normalized_grade = (grade_value / out_of) * 20
            comment = (grade.get('comment') or '').lower()
            
            classified = False
            for context_type, keywords_list in keywords.items():
                if any(kw in comment for kw in keywords_list):
                    context_grades[context_type].append(normalized_grade)
                    classified = True
                    break
            
            if not classified:
                context_grades['Other'].append(normalized_grade)
        
        result = {}
        for context_type, grades_list in context_grades.items():
            if grades_list:
                result[context_type] = {
                    'average': round(np.mean(grades_list), 2),
                    'count': len(grades_list),
                    'std_dev': round(np.std(grades_list), 2)
                }
        
        if len(result) > 1:
            sorted_contexts = sorted(result.items(), key=lambda x: x[1]['average'], reverse=True)
            result['best_context'] = sorted_contexts[0][0]
            result['worst_context'] = sorted_contexts[-1][0]
            result['difference'] = round(sorted_contexts[0][1]['average'] - sorted_contexts[-1][1]['average'], 2)
        
        return result
    
    def project_cumulative_gpa(self) -> Dict[str, Any]:
        """
        5. Cumulative GPA Projection
        Simulate year-end average based on current trends
        """
        from grade_analyzer import GradeAnalyzer
        analyzer = GradeAnalyzer(self.grades)
        
        current_averages = []
        projected_averages = []
        
        for subject in self.subjects.keys():
            current_avg = analyzer.calculate_subject_average(subject)
            trend = analyzer.predict_trend(subject)
            
            if current_avg is None:
                continue
            
            current_averages.append(current_avg)
            
            if trend and trend['trend'] != 'insufficient_data':
                projected_change = trend['slope'] * 3 * 30 * 1e-6
                projected_avg = max(0, min(20, current_avg + projected_change))
            else:
                projected_avg = current_avg
            
            projected_averages.append(projected_avg)
        
        if not current_averages:
            return {'current_gpa': 0, 'projected_gpa': 0, 'change': 0}
        
        current_gpa = np.mean(current_averages)
        projected_gpa = np.mean(projected_averages)
        
        return {
            'current_gpa': round(current_gpa, 2),
            'projected_gpa': round(projected_gpa, 2),
            'change': round(projected_gpa - current_gpa, 2),
            'subjects_analyzed': len(current_averages)
        }
    
    def analyze_subject_correlations(self) -> Dict[str, Any]:
        """
        6. Subject Correlation Analysis
        Check correlations between subjects' grades
        """
        all_dates = set()
        for subject_grades in self.subjects.values():
            for grade in subject_grades:
                if grade['date']:
                    all_dates.add(grade['date'])
        
        if len(self.subjects) < 2 or len(all_dates) < 3:
            return {'correlations': [], 'strongest_correlation': None}
        
        subject_vectors = {}
        for subject, grades in self.subjects.items():
            grade_dict = {}
            for grade in grades:
                if grade['date']:
                    grade_value = self._parse_grade(grade['grade'])
                    if grade_value is not None:
                        out_of = float(grade['out_of']) if grade['out_of'] else 20
                        normalized = (grade_value / out_of) * 20
                        grade_dict[grade['date']] = normalized
            
            if len(grade_dict) >= 3:
                subject_vectors[subject] = grade_dict
        
        correlations = []
        subject_names = list(subject_vectors.keys())
        
        for i in range(len(subject_names)):
            for j in range(i + 1, len(subject_names)):
                subj1, subj2 = subject_names[i], subject_names[j]
                common_dates = set(subject_vectors[subj1].keys()) & set(subject_vectors[subj2].keys())
                
                if len(common_dates) >= 3:
                    grades1 = [subject_vectors[subj1][d] for d in sorted(common_dates)]
                    grades2 = [subject_vectors[subj2][d] for d in sorted(common_dates)]
                    
                    if np.std(grades1) > 0 and np.std(grades2) > 0:
                        corr = np.corrcoef(grades1, grades2)[0, 1]
                        correlations.append({
                            'subject1': subj1,
                            'subject2': subj2,
                            'correlation': round(corr, 3),
                            'strength': self._correlation_strength(corr)
                        })
        
        correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
        
        return {
            'correlations': correlations[:10],
            'strongest_correlation': correlations[0] if correlations else None
        }
    
    def _correlation_strength(self, corr: float) -> str:
        """Classify correlation strength"""
        abs_corr = abs(corr)
        return 'very_strong' if abs_corr >= 0.8 else \
               'strong' if abs_corr >= 0.6 else \
               'moderate' if abs_corr >= 0.4 else \
               'weak' if abs_corr >= 0.2 else 'very_weak'
    
    def benchmark_vs_class(self, subject: str) -> Dict[str, Any]:
        """
        7. Performance vs. Class Average (Benchmarking)
        Compare performance to class average
        """
        if subject not in self.subjects:
            return None
        
        grades = self.subjects[subject]
        student_grades = []
        class_grades = []
        differences = []
        
        for grade in grades:
            grade_value = self._parse_grade(grade['grade'])
            class_avg = self._parse_grade(grade.get('class_average'))
            
            if grade_value is None:
                continue
            
            out_of = float(grade['out_of']) if grade['out_of'] else 20
            normalized_student = (grade_value / out_of) * 20
            student_grades.append(normalized_student)
            
            if class_avg is not None:
                normalized_class = (class_avg / out_of) * 20
                class_grades.append(normalized_class)
                differences.append(normalized_student - normalized_class)
        
        if not student_grades:
            return {'average_difference': 0, 'performance': 'no_data'}
        
        result = {'student_average': round(np.mean(student_grades), 2)}
        
        if class_grades:
            avg_diff = np.mean(differences)
            result.update({
                'class_average': round(np.mean(class_grades), 2),
                'average_difference': round(avg_diff, 2),
                'performance': 'above' if avg_diff > 0.5 else ('below' if avg_diff < -0.5 else 'average')
            })
        
        return result
    
    def analyze_temporal_decay(self, subject: str, window_days: int = 30) -> Dict[str, Any]:
        """
        8. Fatigue or Temporal Decay Analysis
        Detect burnout patterns over time
        """
        if subject not in self.subjects:
            return None
        
        grades = self.subjects[subject]
        data_points = []
        
        for grade in grades:
            grade_value = self._parse_grade(grade['grade'])
            if grade_value is None or not grade['date']:
                continue
            
            out_of = float(grade['out_of']) if grade['out_of'] else 20
            normalized_grade = (grade_value / out_of) * 20
            date_obj = datetime.strptime(grade['date'], '%Y-%m-%d')
            data_points.append((date_obj, normalized_grade))
        
        if len(data_points) < 4:
            return {'decay_detected': False, 'message': 'Insufficient data'}
        
        data_points.sort(key=lambda x: x[0])
        first_date = data_points[0][0]
        last_date = data_points[-1][0]
        total_days = (last_date - first_date).days
        
        if total_days < window_days:
            return {'decay_detected': False, 'message': 'Time period too short'}
        
        first_window_end = first_date + timedelta(days=window_days)
        last_window_start = last_date - timedelta(days=window_days)
        
        first_window_grades = [g for d, g in data_points if d <= first_window_end]
        last_window_grades = [g for d, g in data_points if d >= last_window_start]
        
        if not first_window_grades or not last_window_grades:
            return {'decay_detected': False, 'message': 'Insufficient data in windows'}
        
        first_avg = np.mean(first_window_grades)
        last_avg = np.mean(last_window_grades)
        decay_percent = ((last_avg - first_avg) / first_avg) * 100 if first_avg > 0 else 0
        
        return {
            'decay_detected': decay_percent < -10,
            'decay_percent': round(decay_percent, 2),
            'first_period_avg': round(first_avg, 2),
            'last_period_avg': round(last_avg, 2),
            'pattern': 'decline' if decay_percent < -5 else ('improvement' if decay_percent > 5 else 'stable')
        }
    
    def forecast_with_confidence(self, subject: str, confidence_level: float = 0.95) -> Dict[str, Any]:
        """
        9. Forecast Confidence Intervals
        Predict next grade with error margins
        """
        if subject not in self.subjects:
            return None
        
        grades = self.subjects[subject]
        data_points = []
        
        for grade in grades:
            grade_value = self._parse_grade(grade['grade'])
            if grade_value is None or not grade['date']:
                continue
            
            out_of = float(grade['out_of']) if grade['out_of'] else 20
            normalized_grade = (grade_value / out_of) * 20
            date_obj = datetime.strptime(grade['date'], '%Y-%m-%d')
            data_points.append((date_obj.timestamp(), normalized_grade))
        
        if len(data_points) < 3:
            return {'prediction': None, 'message': 'Insufficient data'}
        
        data_points.sort(key=lambda x: x[0])
        timestamps = np.array([p[0] for p in data_points])
        grades_array = np.array([p[1] for p in data_points])
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(timestamps, grades_array)
        
        avg_interval = (timestamps[-1] - timestamps[0]) / (len(timestamps) - 1)
        next_timestamp = timestamps[-1] + avg_interval
        predicted_grade = slope * next_timestamp + intercept
        
        predicted_values = slope * timestamps + intercept
        residuals = grades_array - predicted_values
        residual_std = np.std(residuals)
        
        from scipy.stats import t
        n = len(data_points)
        t_value = t.ppf((1 + confidence_level) / 2, n - 2)
        margin_of_error = t_value * residual_std
        
        return {
            'prediction': round(max(0, min(20, predicted_grade)), 2),
            'margin_of_error': round(margin_of_error, 2),
            'confidence_interval': {
                'lower': round(max(0, predicted_grade - margin_of_error), 2),
                'upper': round(min(20, predicted_grade + margin_of_error), 2)
            },
            'reliability': 'high' if r_value ** 2 > 0.7 else ('medium' if r_value ** 2 > 0.4 else 'low')
        }
    
    def calculate_learning_efficiency(self, subject: str) -> Dict[str, Any]:
        """
        10. Learning Efficiency Index
        Combine improvement slope with number of tests and weights
        """
        if subject not in self.subjects:
            return None
        
        improvement_rate = self.calculate_improvement_rate(subject)
        
        if not improvement_rate or improvement_rate['trend'] == 'insufficient_data':
            return {'efficiency_index': 0, 'rating': 'insufficient_data'}
        
        grades = self.subjects[subject]
        eval_count = 0
        total_weight = 0
        
        for grade in grades:
            grade_value = self._parse_grade(grade['grade'])
            if grade_value is not None:
                eval_count += 1
                coefficient = float(grade['coefficient']) if grade['coefficient'] else 1
                total_weight += coefficient
        
        if eval_count == 0:
            return {'efficiency_index': 0, 'rating': 'no_data'}
        
        monthly_improvement = improvement_rate['rate_per_month']
        avg_weight = total_weight / eval_count
        efficiency_index = (monthly_improvement * avg_weight) / max(eval_count / 3, 1)
        
        rating = 'excellent' if efficiency_index > 1.5 else \
                 'good' if efficiency_index > 0.8 else \
                 'moderate' if efficiency_index > 0.3 else \
                 'low' if efficiency_index > -0.3 else 'declining'
        
        return {
            'efficiency_index': round(efficiency_index, 2),
            'rating': rating,
            'evaluation_count': eval_count,
            'monthly_improvement': round(monthly_improvement, 2)
        }
