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
        """Ensure critical tables exist"""
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
                
                logger.info("Database tables ensured by middleware")
                
        except Exception as e:
            logger.error(f"Database table middleware error: {str(e)}")
            # Don't crash the application, just log the error