# api/app/services/train.py
"""
TRAIN API integration service.
Currently simulated - will be replaced with real TRAIN API in Phase 2.
"""
from typing import List, Dict, Any
from datetime import datetime, date, timedelta
import random

from config import get_settings

settings = get_settings()


class TRAINService:
    """
    Service for integrating with TRAIN Learning Network API.
    This is a SIMULATED implementation for Phase 1.
    """
    
    def __init__(self):
        self.base_url = settings.TRAIN_API_URL
        self.api_key = settings.TRAIN_API_KEY
    
    async def sync_volunteer_training(self, volunteer_email: str) -> List[Dict[str, Any]]:
        """
        Sync training records for a volunteer from TRAIN.
        
        SIMULATED: Returns mock data for demonstration.
        
        Args:
            volunteer_email: Volunteer's email (used for TRAIN lookup)
            
        Returns:
            List of training record dictionaries
        """
        # Simulate API delay
        import asyncio
        await asyncio.sleep(0.5)
        
        # Return simulated training data
        return [
            {
                "train_course_id": "TRAIN-ICS100",
                "train_completion_id": f"COMP-{random.randint(10000, 99999)}",
                "course_name": "ICS 100: Introduction to Incident Command System",
                "course_code": "ICS-100",
                "course_category": "Emergency Management",
                "course_provider": "FEMA",
                "completion_date": date.today() - timedelta(days=random.randint(30, 365)),
                "expiration_date": date.today() + timedelta(days=random.randint(365, 1460)),
                "score": round(random.uniform(85, 100), 2),
                "certificate_url": f"https://train.org/certificates/COMP-{random.randint(10000, 99999)}.pdf"
            },
            {
                "train_course_id": "TRAIN-NIMS700",
                "train_completion_id": f"COMP-{random.randint(10000, 99999)}",
                "course_name": "IS-700: National Incident Management System",
                "course_code": "IS-700",
                "course_category": "Emergency Management",
                "course_provider": "FEMA",
                "completion_date": date.today() - timedelta(days=random.randint(30, 365)),
                "expiration_date": None,  # No expiration
                "score": round(random.uniform(85, 100), 2),
                "certificate_url": f"https://train.org/certificates/COMP-{random.randint(10000, 99999)}.pdf"
            },
            {
                "train_course_id": "TRAIN-CPR",
                "train_completion_id": f"COMP-{random.randint(10000, 99999)}",
                "course_name": "CPR/AED for Healthcare Providers",
                "course_code": "CPR-HEALTH",
                "course_category": "Medical",
                "course_provider": "American Heart Association",
                "completion_date": date.today() - timedelta(days=random.randint(30, 365)),
                "expiration_date": date.today() + timedelta(days=random.randint(365, 730)),
                "score": round(random.uniform(85, 100), 2),
                "certificate_url": f"https://train.org/certificates/COMP-{random.randint(10000, 99999)}.pdf"
            }
        ]
    
    async def get_course_details(self, course_id: str) -> Dict[str, Any]:
        """
        Get details about a TRAIN course.
        
        SIMULATED: Returns mock course data.
        
        Args:
            course_id: TRAIN course identifier
            
        Returns:
            Course details dictionary
        """
        import asyncio
        await asyncio.sleep(0.2)
        
        # Simulated course catalog
        courses = {
            "TRAIN-ICS100": {
                "course_id": "TRAIN-ICS100",
                "name": "ICS 100: Introduction to Incident Command System",
                "description": "This course introduces the Incident Command System (ICS) and provides the foundation for higher level ICS training.",
                "duration_hours": 3,
                "provider": "FEMA",
                "category": "Emergency Management",
                "is_required": True,
                "validity_period_days": 1460  # 4 years
            },
            "TRAIN-CPR": {
                "course_id": "TRAIN-CPR",
                "name": "CPR/AED for Healthcare Providers",
                "description": "Learn to recognize cardiac arrest, provide high-quality chest compressions, deliver appropriate ventilations and use an AED.",
                "duration_hours": 4,
                "provider": "American Heart Association",
                "category": "Medical",
                "is_required": True,
                "validity_period_days": 730  # 2 years
            }
        }
        
        return courses.get(course_id, {
            "course_id": course_id,
            "name": "Unknown Course",
            "description": "Course details not found",
            "duration_hours": 0,
            "provider": "Unknown"
        })
    
    async def check_training_requirements(
        self,
        volunteer_trainings: List[Dict[str, Any]],
        required_courses: List[str]
    ) -> Dict[str, bool]:
        """
        Check if volunteer meets training requirements.
        
        Args:
            volunteer_trainings: List of volunteer's completed trainings
            required_courses: List of required TRAIN course IDs
            
        Returns:
            Dictionary mapping course IDs to completion status
        """
        completed_courses = {
            t["train_course_id"] 
            for t in volunteer_trainings 
            if t.get("train_course_id")
        }
        
        return {
            course_id: course_id in completed_courses
            for course_id in required_courses
        }


# Singleton instance
train_service = TRAINService()