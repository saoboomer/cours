"""
PRONOTE API Client Module
Handles authentication and data fetching from PRONOTE using pronotepy
Following official documentation: https://pronotepy.readthedocs.io/
"""

import pronotepy
from typing import Optional, Dict, List, Any
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


class PronoteClient:
    """Client for interacting with PRONOTE API following pronotepy best practices"""
    
    def __init__(self, url: str = None, username: str = None, password: str = None, ent: str = None):
        """
        Initialize PRONOTE client
        
        Args:
            url: PRONOTE instance URL (must end with eleve.html as per pronotepy docs)
            username: Student username
            password: Student password
            ent: ENT identifier (optional, for regional accounts)
        """
        self.url = url or os.getenv('PRONOTE_URL')
        self.username = username or os.getenv('PRONOTE_USERNAME')
        self.password = password or os.getenv('PRONOTE_PASSWORD')
        self.ent = ent or os.getenv('PRONOTE_ENT')
        self.client: Optional[pronotepy.Client] = None
        
        # Ensure URL ends with eleve.html (as per pronotepy documentation)
        if self.url and not self.url.endswith('eleve.html'):
            if '?' in self.url:
                self.url = self.url.split('?')[0]
            if not self.url.endswith('.html'):
                self.url = self.url.rstrip('/') + '/eleve.html'
        
    def login(self) -> bool:
        """
        Authenticate with PRONOTE following pronotepy best practices
        Documentation: https://pronotepy.readthedocs.io/en/stable/quickstart.html#client-initialisation
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            # Get ENT function if specified
            ent_func = None
            if self.ent:
                try:
                    import pronotepy.ent as ent_module
                    ent_func = getattr(ent_module, self.ent, None)
                    if not ent_func:
                        print(f"Warning: ENT '{self.ent}' not found, trying without ENT")
                except (ImportError, AttributeError) as e:
                    print(f"Warning: Could not load ENT '{self.ent}': {e}")
            
            # Create client (as per pronotepy docs)
            if ent_func:
                self.client = pronotepy.Client(
                    self.url,
                    username=self.username,
                    password=self.password,
                    ent=ent_func
                )
            else:
                self.client = pronotepy.Client(
                    self.url,
                    username=self.username,
                    password=self.password
                )
            
            # Check if login was successful (as per docs: client.logged_in)
            if not self.client.logged_in:
                print("Login failed: client.logged_in is False")
                return False
            
            print(f"✅ Successfully logged in as: {self.client.info.name}")
            return True
            
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    def get_student_info(self) -> Dict[str, Any]:
        """Get student information"""
        if not self.client or not self.client.logged_in:
            raise Exception("Not logged in")
        
        info = self.client.info
        return {
            'name': info.name,
            'class': info.class_name,
            'establishment': info.establishment
        }
    
    def get_grades(self, period: str = None) -> List[Dict[str, Any]]:
        """
        Fetch all grades for a specific period
        Following pronotepy docs: period.grades returns list of Grade objects
        Documentation: https://pronotepy.readthedocs.io/en/stable/quickstart.html#grades
        
        Args:
            period: Period name (optional)
            
        Returns:
            list: List of grades with details
        """
        if not self.client or not self.client.logged_in:
            raise Exception("Not logged in")
        
        # Get target period (as per pronotepy docs)
        target_period = None
        
        if period:
            # Find specific period by name
            for p in self.client.periods:
                if p.name == period:
                    target_period = p
                    break
            if not target_period:
                raise Exception(f"Period '{period}' not found")
        else:
            # Use current period (as per docs: client.current_period)
            target_period = self.client.current_period
        
        if not target_period:
            raise Exception("No period available")
        
        grades_data = []
        
        # Iterate over grades (as per pronotepy documentation)
        for grade in target_period.grades:
            try:
                grade_info = {
                    'id': grade.id,
                    'subject': grade.subject.name,
                    'grade': str(grade.grade),  # Always a string as per docs (could be "Absent", etc.)
                    'out_of': grade.out_of,
                    'coefficient': grade.coefficient,
                    'date': grade.date.strftime('%Y-%m-%d') if grade.date else None,
                    'comment': grade.comment if hasattr(grade, 'comment') else '',
                    'is_bonus': grade.is_bonus if hasattr(grade, 'is_bonus') else False,
                    'is_optionnal': grade.is_optionnal if hasattr(grade, 'is_optionnal') else False,
                    'average': grade.average if hasattr(grade, 'average') else None,
                    'max': grade.max if hasattr(grade, 'max') else None,
                    'min': grade.min if hasattr(grade, 'min') else None,
                    'class_average': grade.class_average if hasattr(grade, 'class_average') else None
                }
                grades_data.append(grade_info)
            except Exception as e:
                print(f"Warning: Could not parse grade: {e}")
                continue
        
        return grades_data
    
    def get_averages(self, period: str = None) -> Dict[str, Any]:
        """Get averages for all subjects"""
        if not self.client or not self.client.logged_in:
            raise Exception("Not logged in")
        
        # Get target period
        target_period = None
        
        if period:
            for p in self.client.periods:
                if p.name == period:
                    target_period = p
                    break
        else:
            target_period = self.client.current_period
        
        if not target_period:
            raise Exception("No period available")
        
        averages_data = {
            'overall_average': target_period.overall_average,
            'class_overall_average': target_period.class_overall_average,
            'subjects': []
        }
        
        for average in target_period.averages:
            subject_avg = {
                'subject': average.subject.name,
                'student_average': average.student,
                'class_average': average.class_average,
                'max': average.max,
                'min': average.min,
                'out_of': average.out_of,
                'background_color': average.background_color if hasattr(average, 'background_color') else None
            }
            averages_data['subjects'].append(subject_avg)
        
        return averages_data
    
    def get_periods(self) -> List[Dict[str, Any]]:
        """Get all available periods"""
        if not self.client or not self.client.logged_in:
            raise Exception("Not logged in")
        
        periods_data = []
        for period in self.client.periods:
            period_info = {
                'id': period.id,
                'name': period.name,
                'start': period.start.strftime('%Y-%m-%d') if period.start else None,
                'end': period.end.strftime('%Y-%m-%d') if period.end else None
            }
            periods_data.append(period_info)
        
        return periods_data
    
    def logout(self):
        """Close the PRONOTE session"""
        if self.client:
            self.client = None
