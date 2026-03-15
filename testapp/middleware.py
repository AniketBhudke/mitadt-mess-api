"""
Middleware to ensure database tables exist before processing requests
"""
from django.db import connection
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

class DatabaseTableMiddleware:
    """
    Middleware to ensure critical database tables exist before processing requests.
    This prevents crashes when tables are missing in production.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.tables_checked = False
        
    def __call__(self, request):
        # Only check tables once per server startup
        if not self.tables_checked:
            self.ensure_tables_exist()
            self.tables_checked = True
            
        response = self.get_response(request)
        return response
    
    def ensure_tables_exist(self):
        """Ensure critical tables exist and periods are properly set up"""
        try:
            with connection.cursor() as cursor:
                # Check and create SuggestionPeriod table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS testapp_suggestionperiod (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name VARCHAR(100) NOT NULL,
                        start_date DATE NOT NULL,
                        end_date DATE NOT NULL,
                        submission_deadline DATE NOT NULL,
                        is_active BOOLEAN NOT NULL DEFAULT 1,
                        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Check and create FeedbackPeriod table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS testapp_feedbackperiod (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name VARCHAR(100) NOT NULL,
                        start_date DATE NOT NULL,
                        end_date DATE NOT NULL,
                        submission_deadline DATE NOT NULL,
                        is_active BOOLEAN NOT NULL DEFAULT 1,
                        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Check and create Complaint table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS testapp_complaint (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_name VARCHAR(100) NOT NULL,
                        email VARCHAR(254) NOT NULL,
                        mess_name VARCHAR(100),
                        message TEXT NOT NULL,
                        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Ensure period tracking fields exist in weekly_suggestion table
                try:
                    cursor.execute("""
                        ALTER TABLE testapp_weekly_suggestion 
                        ADD COLUMN suggestion_period_start DATE;
                    """)
                except:
                    pass  # Column might already exist
                    
                try:
                    cursor.execute("""
                        ALTER TABLE testapp_weekly_suggestion 
                        ADD COLUMN suggestion_period_end DATE;
                    """)
                except:
                    pass  # Column might already exist
                
                # Ensure unique constraint for email + mess_name + period
                try:
                    cursor.execute("""
                        CREATE UNIQUE INDEX IF NOT EXISTS 
                        testapp_weekly_suggestion_unique_email_mess_period 
                        ON testapp_weekly_suggestion(email, mess_name, suggestion_period_start, suggestion_period_end);
                    """)
                except:
                    pass  # Index might already exist
                
                logger.info("Database tables ensured by middleware")
                
                # Auto-fix suggestion periods
                self.ensure_active_suggestion_period()
                
        except Exception as e:
            logger.error(f"Database table middleware error: {str(e)}")
            # Don't crash the application, just log the error
    
    def ensure_active_suggestion_period(self):
        """Ensure there's always an active suggestion period"""
        try:
            from datetime import date, timedelta
            
            # Import inside method to avoid import-time errors
            try:
                from testapp.models import SuggestionPeriod
            except:
                return  # Models not ready yet
            
            today = date.today()
            
            # Check if there's a current active period
            current_period = SuggestionPeriod.objects.filter(
                is_active=True,
                start_date__lte=today,
                submission_deadline__gte=today
            ).first()
            
            if current_period:
                return  # Already have active period
            
            # Find period that should be active for today
            should_be_active = SuggestionPeriod.objects.filter(
                start_date__lte=today,
                end_date__gte=today
            ).first()
            
            if should_be_active:
                # Deactivate all others and activate this one
                SuggestionPeriod.objects.all().update(is_active=False)
                should_be_active.is_active = True
                should_be_active.save()
                logger.info(f"Auto-activated period: {should_be_active.name}")
            else:
                # Create new period for current week
                start_of_week = today - timedelta(days=today.weekday())
                end_of_week = start_of_week + timedelta(days=6)
                
                # Deactivate all existing periods
                SuggestionPeriod.objects.all().update(is_active=False)
                
                # Create new active period
                period_name = f"Week {start_of_week.strftime('%b %d')} - {end_of_week.strftime('%b %d, %Y')}"
                new_period = SuggestionPeriod.objects.create(
                    name=period_name,
                    start_date=start_of_week,
                    end_date=end_of_week,
                    submission_deadline=end_of_week + timedelta(days=1),
                    is_active=True
                )
                logger.info(f"Auto-created period: {new_period.name}")
                
        except Exception as e:
            logger.error(f"Auto-period creation error: {str(e)}")
            # Don't crash the application