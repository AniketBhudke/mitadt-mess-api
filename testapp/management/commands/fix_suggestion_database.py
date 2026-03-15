from django.core.management.base import BaseCommand
from django.db import connection
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Fix missing SuggestionPeriod table and create initial periods'

    def handle(self, *args, **options):
        try:
            with connection.cursor() as cursor:
                # Check if SuggestionPeriod table exists
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='testapp_suggestionperiod';
                """)
                
                if not cursor.fetchone():
                    self.stdout.write("Creating SuggestionPeriod table...")
                    
                    # Create SuggestionPeriod table
                    cursor.execute("""
                        CREATE TABLE testapp_suggestionperiod (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name VARCHAR(100) NOT NULL,
                            start_date DATE NOT NULL,
                            end_date DATE NOT NULL,
                            submission_deadline DATETIME NOT NULL,
                            is_active BOOLEAN NOT NULL DEFAULT 1,
                            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                        );
                    """)
                    
                    self.stdout.write("SuggestionPeriod table created successfully!")
                    
                    # Create initial suggestion periods
                    today = date.today()
                    
                    # Current week period
                    start_of_week = today - timedelta(days=today.weekday())
                    end_of_week = start_of_week + timedelta(days=6)
                    deadline = end_of_week.replace(hour=23, minute=59, second=59) if hasattr(end_of_week, 'replace') else f"{end_of_week} 23:59:59"
                    
                    cursor.execute("""
                        INSERT INTO testapp_suggestionperiod 
                        (name, start_date, end_date, submission_deadline, is_active, created_at)
                        VALUES (?, ?, ?, ?, ?, datetime('now'))
                    """, [
                        f"Week {start_of_week.strftime('%b %d')} - {end_of_week.strftime('%b %d, %Y')}",
                        start_of_week,
                        end_of_week,
                        f"{end_of_week} 23:59:59",
                        True
                    ])
                    
                    # Next week period
                    next_start = start_of_week + timedelta(days=7)
                    next_end = next_start + timedelta(days=6)
                    next_deadline = f"{next_end} 23:59:59"
                    
                    cursor.execute("""
                        INSERT INTO testapp_suggestionperiod 
                        (name, start_date, end_date, submission_deadline, is_active, created_at)
                        VALUES (?, ?, ?, ?, ?, datetime('now'))
                    """, [
                        f"Week {next_start.strftime('%b %d')} - {next_end.strftime('%b %d, %Y')}",
                        next_start,
                        next_end,
                        next_deadline,
                        True
                    ])
                    
                    self.stdout.write("Initial suggestion periods created!")
                    
                else:
                    self.stdout.write("SuggestionPeriod table already exists.")
                
                # Verify the table and show contents
                cursor.execute("SELECT COUNT(*) FROM testapp_suggestionperiod")
                count = cursor.fetchone()[0]
                self.stdout.write(f"SuggestionPeriod table has {count} records.")
                
                if count > 0:
                    cursor.execute("SELECT name, start_date, end_date FROM testapp_suggestionperiod ORDER BY start_date")
                    periods = cursor.fetchall()
                    self.stdout.write("Available periods:")
                    for period in periods:
                        self.stdout.write(f"  - {period[0]} ({period[1]} to {period[2]})")
                
                self.stdout.write(self.style.SUCCESS("SuggestionPeriod database fix completed!"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error fixing suggestion database: {str(e)}"))
            raise