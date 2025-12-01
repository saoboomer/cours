"""
PRONOTE API Client Module
Handles authentication and data fetching from PRONOTE using pronotepy
"""

import pronotepy
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()


class PronoteClient:
    """Client for interacting with PRONOTE API"""
    
    def __init__(self, url: str = None, username: str = None, password: str = None, ent: str = None):
        """
        Initialize PRONOTE client
        
        Args:
            url: PRONOTE instance URL (must end with eleve.html)
            username: Student username
            password: Student password
            ent: ENT identifier (optional, for regional accounts)
        """
        self.url = url or os.getenv('PRONOTE_URL')
        self.username = username or os.getenv('PRONOTE_USERNAME')
        self.password = password or os.getenv('PRONOTE_PASSWORD')
        self.ent = ent or os.getenv('PRONOTE_ENT')
        self.client: Optional[pronotepy.Client] = None
        
        # Ensure URL ends with eleve.html (as per pronotepy docs)
        if self.url and not self.url.endswith('eleve.html'):
            if '?' in self.url:
                self.url = self.url.split('?')[0]
            if not self.url.endswith('.html'):
                self.url = self.url.rstrip('/') + '/eleve.html'
        
    def login(self) -> bool:
        """
        Authenticate with PRONOTE following pronotepy best practices
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            # Get ENT function if specified
            ent_func = None
            if self.ent:
                try:
                    # Import ENT module dynamically
                    import pronotepy.ent as ent_module
                    ent_func = getattr(ent_module, self.ent, None)
                    if not ent_func:
                        print(f"Warning: ENT '{self.ent}' not found, trying without ENT")
                except (ImportError, AttributeError) as e:
                    print(f"Warning: Could not load ENT '{self.ent}': {e}")
            
            # Create client with or without ENT
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
            
            # Verify login was successful
            if not self.client.logged_in:
                raise Exception("Authentication failed - invalid credentials or URL")
            
            # Test if we can access basic info
            try:
                student_info = self.client.info
                if student_info and hasattr(student_info, 'name'):
                    print(f"Successfully logged in as {student_info.name}")
                else:
                    print("Successfully logged in (info not available)")
                return True
            except Exception as e:
                print(f"Login successful but info access failed: {e}")
                return True  # Still consider login successful if we can authenticate
            
        except Exception as e:
            error_msg = str(e)
            print(f"Login error: {error_msg}")
            
            # Provide more specific error messages
            if "Authentication failed" in error_msg or "Invalid credentials" in error_msg:
                print("💡 Tip: Check your username, password, and URL format")
                print("   URL should end with '/pronote/eleve.html'")
            elif "ENT" in error_msg:
                print("💡 Tip: Check your ENT identifier")
                if ent is not None:
                    available_ents = [attr for attr in dir(ent) if not attr.startswith('_')][:10]
                    print(f"   Available ENTs (first 10): {available_ents}")
                else:
                    print("   ENT module not available in this pronotepy version")
            elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                print("💡 Tip: Check your internet connection and PRONOTE server availability")
            
            self.client = None
            return False
    
    def get_student_info(self) -> Dict[str, Any]:
        """
        Get student information
        
        Returns:
            dict: Student information including name, class, etc.
        """
        if not self.client or not self.client.logged_in:
            raise Exception("Not logged in")
        
        try:
            info = self.client.info
            if not info:
                raise Exception("No student information available")
            
            student_info = {
                'name': getattr(info, 'name', 'Unknown Student'),
                'class': getattr(info, 'class_name', 'Unknown Class'),
                'establishment': getattr(info, 'establishment', 'Unknown Establishment')
            }
            
            print(f"Successfully fetched student info for: {student_info['name']}")
            return student_info
            
        except Exception as e:
            print(f"Error fetching student info: {e}")
            # Return fallback info
            return {
                'name': 'Unknown Student',
                'class': 'Unknown Class', 
            }
    
    def get_grades(self, period: str = None) -> List[Dict[str, Any]]:
        """
        Fetch all grades for a specific period or all periods
        Following pronotepy documentation: period.grades returns list of Grade objects
        
        Args:
            period: Period name (optional)
            
        Returns:
            list: List of grades with details
        """
        if not self.client or not self.client.logged_in:
            raise Exception("Not logged in")
        
        # Get periods (as per pronotepy docs: client.periods or client.current_period)
        target_period = None
                    grade_info = {
                        'id': getattr(grade, 'id', None),
                        'subject': getattr(grade.subject, 'name', 'Unknown Subject'),
                        'grade': grade.grade,
                        'out_of': grade.out_of,
                        'coefficient': getattr(grade, 'coefficient', 1),
                        'date': grade.date.strftime('%Y-%m-%d') if grade.date else None,
                        'comment': getattr(grade, 'comment', ''),
                        'is_bonus': getattr(grade, 'is_bonus', False),
                        'is_optionnal': getattr(grade, 'is_optionnal', False),
                        'average': getattr(grade, 'average', None),
                        'max': getattr(grade, 'max', None),
                        'min': getattr(grade, 'min', None),
                        'class_average': getattr(grade, 'class_average', None)
                    }
                    grades_data.append(grade_info)
                except Exception as e:
                    print(f"Error processing grade: {e}")
                    continue
            
            print(f"Successfully fetched {len(grades_data)} grades from period '{target_period.name}'")
            return grades_data
            
        except Exception as e:
            print(f"Error fetching grades: {e}")
            raise Exception(f"Failed to fetch grades: {str(e)}")
    
    def get_averages(self, period: str = None) -> Dict[str, Any]:
        """
        Get averages for all subjects
        
        Args:
            period: Period name (optional)
            
        Returns:
            dict: Averages by subject and overall
        """
        if not self.client or not self.client.logged_in:
            raise Exception("Not logged in")
        
        try:
            periods = self.client.periods
            if not periods:
                print("Warning: No periods found for averages")
                return {'overall_average': None, 'class_overall_average': None, 'subjects': []}
            
            target_period = None
            
            if period:
                for p in periods:
                    if p.name == period:
                        target_period = p
                        break
                if not target_period:
                    print(f"Period '{period}' not found for averages. Using first available period.")
                    target_period = periods[0]
            else:
                target_period = self.client.current_period
                if not target_period:
                    print("No current period found for averages, using first available period")
                    target_period = periods[0]
            
            if not target_period:
                raise Exception("No valid period found for averages")
            
            averages_data = {
                'overall_average': getattr(target_period, 'overall_average', None),
                'class_overall_average': getattr(target_period, 'class_overall_average', None),
                'subjects': []
            }
            
            averages = getattr(target_period, 'averages', [])
            if not averages:
                print(f"Warning: No averages found for period '{target_period.name}'")
                return averages_data
            
            for average in averages:
                try:
                    subject_avg = {
                        'subject': getattr(average.subject, 'name', 'Unknown Subject'),
                        'student_average': getattr(average, 'student', None),
                        'class_average': getattr(average, 'class_average', None),
                        'max': getattr(average, 'max', None),
                        'min': getattr(average, 'min', None),
                        'out_of': getattr(average, 'out_of', 20),
                        'background_color': getattr(average, 'background_color', None)
                    }
                    averages_data['subjects'].append(subject_avg)
                except Exception as e:
                    print(f"Error processing average: {e}")
                    continue
            
            print(f"Successfully fetched {len(averages_data['subjects'])} subject averages from period '{target_period.name}'")
            return averages_data
            
        except Exception as e:
            print(f"Error fetching averages: {e}")
            raise Exception(f"Failed to fetch averages: {str(e)}")
    
    def get_periods(self) -> List[Dict[str, Any]]:
        """
        Get all available periods
        
        Returns:
            list: List of periods with their details
        """
        if not self.client or not self.client.logged_in:
            raise Exception("Not logged in")
        
        try:
            periods = self.client.periods
            if not periods:
                print("Warning: No periods found")
                return []
            
            periods_data = []
            for period in periods:
                try:
                    period_info = {
                        'id': getattr(period, 'id', None),
                        'name': getattr(period, 'name', 'Unknown Period'),
                        'start': period.start.strftime('%Y-%m-%d') if getattr(period, 'start', None) else None,
                        'end': period.end.strftime('%Y-%m-%d') if getattr(period, 'end', None) else None
                    }
                    periods_data.append(period_info)
                except Exception as e:
                    print(f"Error processing period: {e}")
                    continue
            
            print(f"Successfully fetched {len(periods_data)} periods")
            return periods_data
            
        except Exception as e:
            print(f"Error fetching periods: {e}")
            raise Exception(f"Failed to fetch periods: {str(e)}")
    
    def logout(self):
        """Close the PRONOTE session"""
        if self.client:
            self.client = None
