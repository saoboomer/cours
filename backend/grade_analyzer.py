"""
Grade Analysis Module
Provides advanced analysis tools for PRONOTE grades including predictions,
tendencies, what-if scenarios, and 10 advanced analytics metrics
"""

import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from scipy import stats
from datetime import datetime, timedelta
from collections import defaultdict
import re


class GradeAnalyzer:
    """Analyzer for grade predictions and statistics"""
    
    def __init__(self, grades: List[Dict[str, Any]]):
        """
        Initialize analyzer with grades data
        
        Args:
            grades: List of grade dictionaries from PRONOTE
        """
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
        """
        Parse grade string to float with improved validation
        
        Args:
            grade_str: Grade as string (e.g., "15.5", "Absent", "15,5")
            
        Returns:
            float: Numeric grade or None if not parseable
        """
        if not grade_str:
            return None
        
        # Convert to string and normalize
        grade_str = str(grade_str).strip()
        
        # Handle various non-numeric cases
        non_numeric_values = [
            'absent', 'abs', 'dispensé', 'disp', 'non noté', 'non note', 
            'n/a', 'na', 'null', 'undefined', '-', '--', '???', '?'
        ]
        
        if grade_str.lower() in non_numeric_values:
            return None
        
        try:
            # Handle comma decimal separator (French format)
            grade_str = grade_str.replace(',', '.')
            
            # Remove any extra characters
            import re
            grade_str = re.sub(r'[^\d.-]', '', grade_str)
            
            if not grade_str:
                return None
            
            grade_value = float(grade_str)
            
            # Validate reasonable grade range (0-20 for French system)
            if 0 <= grade_value <= 20:
                return grade_value
            elif 0 <= grade_value <= 100:
                # Convert from percentage to /20 scale
                return (grade_value / 100) * 20
            else:
                print(f"Warning: Grade value {grade_value} is outside expected range (0-20)")
                return None
                
        except (ValueError, TypeError) as e:
            print(f"Warning: Could not parse grade '{grade_str}': {e}")
            return None
    
    def calculate_subject_average(self, subject: str, include_coefficients: bool = True) -> Optional[float]:
        """
        Calculate average for a specific subject with improved validation
        
        Args:
            subject: Subject name
            include_coefficients: Whether to weight by coefficients
            
        Returns:
            float: Subject average or None if insufficient data
        """
        if not subject or subject not in self.subjects:
            return None
        
        grades = self.subjects[subject]
        if not grades:
            return None
        
        total_points = 0
        total_weight = 0
        valid_grades_count = 0
        
        for grade in grades:
            if not isinstance(grade, dict):
                continue
                
            grade_value = self._parse_grade(grade.get('grade'))
            if grade_value is None:
                continue
            
            try:
                # Validate and parse out_of value
                out_of_raw = grade.get('out_of')
                if out_of_raw is None:
                    out_of = 20  # Default French scale
                else:
                    out_of = float(out_of_raw)
                    if out_of <= 0:
                        out_of = 20  # Fallback for invalid values
                
                # Validate and parse coefficient
                coefficient_raw = grade.get('coefficient')
                if coefficient_raw is None or not include_coefficients:
                    coefficient = 1
                else:
                    coefficient = float(coefficient_raw)
                    if coefficient <= 0:
                        coefficient = 1  # Fallback for invalid values
                
                # Normalize to /20 scale
                normalized_grade = (grade_value / out_of) * 20
                
                # Additional validation for normalized grade
                if 0 <= normalized_grade <= 20:
                    total_points += normalized_grade * coefficient
                    total_weight += coefficient
                    valid_grades_count += 1
                else:
                    print(f"Warning: Normalized grade {normalized_grade} is outside valid range (0-20)")
                    
            except (ValueError, TypeError) as e:
                print(f"Warning: Error processing grade data: {e}")
                continue
        
        if total_weight == 0 or valid_grades_count == 0:
            return None
        
        average = total_points / total_weight
        return round(average, 2)
    
    def predict_trend(self, subject: str) -> Dict[str, Any]:
        """
        Predict grade trend using linear regression with improved validation
        
        Args:
            subject: Subject name
            
        Returns:
            dict: Trend analysis with slope, prediction, and confidence
        """
        if not subject or subject not in self.subjects:
            return {
                'trend': 'insufficient_data',
                'slope': 0,
                'prediction': None,
                'confidence': 0,
                'error': 'Subject not found'
            }
        
        grades = self.subjects[subject]
        if not grades:
            return {
                'trend': 'insufficient_data',
                'slope': 0,
                'prediction': None,
                'confidence': 0,
                'error': 'No grades found for subject'
            }
        
        # Extract valid grades with dates
        data_points = []
        for grade in grades:
            if not isinstance(grade, dict):
                continue
                
            grade_value = self._parse_grade(grade.get('grade'))
            if grade_value is None:
                continue
            
            date_str = grade.get('date')
            if not date_str:
                continue
            
            try:
                # Validate and parse out_of value
                out_of_raw = grade.get('out_of')
                if out_of_raw is None:
                    out_of = 20
                else:
                    out_of = float(out_of_raw)
                    if out_of <= 0:
                        out_of = 20
                
                # Normalize to /20 scale
                normalized_grade = (grade_value / out_of) * 20
                
                # Validate normalized grade
                if not (0 <= normalized_grade <= 20):
                    continue
                
                # Parse date
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                timestamp = date_obj.timestamp()
                
                data_points.append((timestamp, normalized_grade))
                
            except (ValueError, TypeError) as e:
                print(f"Warning: Error processing grade data for trend: {e}")
                continue
        
        if len(data_points) < 2:
            return {
                'trend': 'insufficient_data',
                'slope': 0,
                'prediction': None,
                'confidence': 0,
                'error': f'Need at least 2 valid grades with dates (found {len(data_points)})'
            }
        
        # Sort by date
        data_points.sort(key=lambda x: x[0])
        
        try:
            # Perform linear regression
            timestamps = np.array([p[0] for p in data_points])
            grades_array = np.array([p[1] for p in data_points])
            
            # Check for sufficient variance
            if np.std(timestamps) == 0 or np.std(grades_array) == 0:
                return {
                    'trend': 'stable',
                    'slope': 0,
                    'prediction': round(np.mean(grades_array), 2),
                    'confidence': 0,
                    'error': 'Insufficient variance in data'
                }
            
            slope, intercept, r_value, p_value, std_err = stats.linregress(timestamps, grades_array)
            
            # Predict next grade
            last_timestamp = timestamps[-1]
            avg_interval = (timestamps[-1] - timestamps[0]) / (len(timestamps) - 1)
            next_timestamp = last_timestamp + avg_interval
            predicted_grade = slope * next_timestamp + intercept
            
            # Clamp prediction to valid range
            predicted_grade = max(0, min(20, predicted_grade))
            
            # Determine trend
            if abs(slope) < 1e-8:
                trend = 'stable'
            elif slope > 0:
                trend = 'improving'
            else:
                trend = 'declining'
            
            return {
                'trend': trend,
                'slope': round(slope * 1e6, 4),  # Scale for readability
                'prediction': round(predicted_grade, 2),
                'confidence': round(abs(r_value) * 100, 2),
                'r_squared': round(r_value ** 2, 4),
                'data_points': len(data_points)
            }
            
        except Exception as e:
            print(f"Error in trend prediction: {e}")
            return {
                'trend': 'error',
                'slope': 0,
                'prediction': None,
                'confidence': 0,
                'error': f'Prediction failed: {str(e)}'
            }
    
    def calculate_needed_grade(self, subject: str, target_average: float, 
                              next_grade_coefficient: float = 1.0,
                              next_grade_out_of: float = 20.0) -> Dict[str, Any]:
        """
        Calculate what grade is needed to reach a target average
        
        Args:
            subject: Subject name
            target_average: Desired average (out of 20)
            next_grade_coefficient: Coefficient of the next grade
            next_grade_out_of: Maximum points for next grade
            
        Returns:
            dict: Required grade and feasibility analysis
        """
        if subject not in self.subjects:
            return None
        
        grades = self.subjects[subject]
        current_points = 0
        current_weight = 0
        
        for grade in grades:
            grade_value = self._parse_grade(grade['grade'])
            if grade_value is None:
                continue
            
            out_of = float(grade['out_of']) if grade['out_of'] else 20
            coefficient = float(grade['coefficient']) if grade['coefficient'] else 1
            
            normalized_grade = (grade_value / out_of) * 20
            current_points += normalized_grade * coefficient
            current_weight += coefficient
        
        # Calculate needed points
        total_weight = current_weight + next_grade_coefficient
        needed_total_points = target_average * total_weight
        needed_points = needed_total_points - current_points
        needed_grade_normalized = needed_points / next_grade_coefficient
        
        # Convert to the actual scale
        needed_grade = (needed_grade_normalized / 20) * next_grade_out_of
        
        # Determine feasibility
        is_possible = 0 <= needed_grade <= next_grade_out_of
        difficulty = 'impossible' if not is_possible else (
            'easy' if needed_grade <= next_grade_out_of * 0.5 else
            'moderate' if needed_grade <= next_grade_out_of * 0.75 else
            'difficult'
        )
        
        return {
            'needed_grade': round(needed_grade, 2),
            'out_of': next_grade_out_of,
            'normalized_needed': round(needed_grade_normalized, 2),
            'is_possible': is_possible,
            'difficulty': difficulty,
            'current_average': round(current_points / current_weight, 2) if current_weight > 0 else 0,
            'target_average': target_average
        }
    
    def simulate_multiple_grades(self, subject: str, target_average: float,
                                num_grades: int, coefficient: float = 1.0,
                                out_of: float = 20.0) -> Dict[str, Any]:
        """
        Calculate average grade needed over multiple future assessments
        
        Args:
            subject: Subject name
            target_average: Desired average
            num_grades: Number of future grades to consider
            coefficient: Coefficient for each grade
            out_of: Maximum points for each grade
            
        Returns:
            dict: Average needed per grade
        """
        if subject not in self.subjects:
            return None
        
        grades = self.subjects[subject]
        current_points = 0
        current_weight = 0
        
        for grade in grades:
            grade_value = self._parse_grade(grade['grade'])
            if grade_value is None:
                continue
            
            grade_out_of = float(grade['out_of']) if grade['out_of'] else 20
            grade_coefficient = float(grade['coefficient']) if grade['coefficient'] else 1
            
            normalized_grade = (grade_value / grade_out_of) * 20
            current_points += normalized_grade * grade_coefficient
            current_weight += grade_coefficient
        
        # Calculate needed average grade
        total_weight = current_weight + (num_grades * coefficient)
        needed_total_points = target_average * total_weight
        needed_points = needed_total_points - current_points
        needed_avg_normalized = needed_points / (num_grades * coefficient)
        needed_avg = (needed_avg_normalized / 20) * out_of
        
        is_possible = 0 <= needed_avg <= out_of
        
        return {
            'average_needed_per_grade': round(needed_avg, 2),
            'out_of': out_of,
            'normalized_average': round(needed_avg_normalized, 2),
            'num_grades': num_grades,
            'is_possible': is_possible,
            'current_average': round(current_points / current_weight, 2) if current_weight > 0 else 0
        }
    
    def get_statistics(self, subject: str = None) -> Dict[str, Any]:
        """
        Get comprehensive statistics for a subject or all subjects
        
        Args:
            subject: Subject name (optional, None for all subjects)
            
        Returns:
            dict: Statistical analysis
        """
        if subject:
            if subject not in self.subjects:
                return None
            subjects_to_analyze = {subject: self.subjects[subject]}
        else:
            subjects_to_analyze = self.subjects
        
        stats_data = {}
        
        for subj_name, subj_grades in subjects_to_analyze.items():
            valid_grades = []
            
            for grade in subj_grades:
                grade_value = self._parse_grade(grade['grade'])
                if grade_value is None:
                    continue
                
                out_of = float(grade['out_of']) if grade['out_of'] else 20
                normalized_grade = (grade_value / out_of) * 20
                valid_grades.append(normalized_grade)
            
            if not valid_grades:
                continue
            
            grades_array = np.array(valid_grades)
            
            stats_data[subj_name] = {
                'count': len(valid_grades),
                'average': round(np.mean(grades_array), 2),
                'median': round(np.median(grades_array), 2),
                'std_dev': round(np.std(grades_array), 2),
                'min': round(np.min(grades_array), 2),
                'max': round(np.max(grades_array), 2),
                'range': round(np.max(grades_array) - np.min(grades_array), 2),
                'variance': round(np.var(grades_array), 2)
            }
        
        return stats_data
    
    def get_subject_comparison(self) -> List[Dict[str, Any]]:
        """
        Compare performance across all subjects
        
        Returns:
            list: Subjects ranked by performance
        """
        comparison = []
        
        for subject in self.subjects:
            avg = self.calculate_subject_average(subject)
            if avg is None:
                continue
            
            stats = self.get_statistics(subject)
            trend = self.predict_trend(subject)
            
            comparison.append({
                'subject': subject,
                'average': avg,
                'grade_count': stats[subject]['count'],
                'std_dev': stats[subject]['std_dev'],
                'trend': trend['trend'],
                'trend_confidence': trend['confidence']
            })
        
        # Sort by average (descending)
        comparison.sort(key=lambda x: x['average'], reverse=True)
        
        return comparison
