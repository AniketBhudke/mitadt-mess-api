from django.core.management.base import BaseCommand
from django.db import connection, transaction
from testapp.models import FeedbackPeriod, MessFeedback
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Fix feedback database tables and create initial periods'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                cursor = connection.cursor()
                
                # Create FeedbackPeriod table if it doesn't exist
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
                
                self.stdout.write(
                    self.style.SUCCESS('Created testapp_feedbackperiod table')
                )
                
                # Check if we have any feedback periods
                period_count = FeedbackPeriod.objects.count()
                
                if period_count == 0:
                    # Create initial feedback periods
                    today = date.today()
                    
                    # Current week
                    start_of_week = today - timedelta(days=today.weekday())
                    end_of_week = start_of_week + timedelta(days=6)
                    deadline = end_of_week + timedelta(days=1)  # Next day after week ends
                    
                    periods_to_create = [
                        {
                            'name': f'Week 1 - {start_of_week.strftime("%b %Y")}',
                            'start_date': start_of_week,
                            'end_date': end_of_week,
                            'submission_deadline': deadline,
                            'is_active': True
                        }
                    ]
                    
                    # Create next 3 weeks
                    for i in range(1, 4):
                        week_start = start_of_week + timedelta(weeks=i)
                        week_end = week_start + timedelta(days=6)
                        week_deadline = week_end + timedelta(days=1)
                        
                        periods_to_create.append({
                            'name': f'Week {i+1} - {week_start.strftime("%b %Y")}',
                            'start_date': week_start,
                            'end_date': week_end,
                            'submission_deadline': week_deadline,
                            'is_active': False
                        })
                    
                    # Create the periods
                    for period_data in periods_to_create:
                        period = FeedbackPeriod.objects.create(**period_data)
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Created feedback period: {period.name} '
                                f'({period.start_date} to {period.end_date})'
                            )
                        )
                
                # Update existing MessFeedback entries without period info
                feedback_without_period = MessFeedback.objects.filter(
                    feedback_period_start__isnull=True,
                    feedback_period_end__isnull=True
                )
                
                if feedback_without_period.exists():
                    # Get current active period
                    current_period = FeedbackPeriod.get_current_period()
                    
                    if current_period:
                        updated_count = feedback_without_period.update(
                            feedback_period_start=current_period.start_date,
                            feedback_period_end=current_period.end_date
                        )
                        
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Updated {updated_count} feedback entries with period information'
                            )
                        )
                
                # Show current status
                current_period = FeedbackPeriod.get_current_period()
                if current_period:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Current active feedback period: {current_period.name}'
                        )
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Submission deadline: {current_period.submission_deadline}'
                        )
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Submissions allowed: {current_period.is_submission_allowed()}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING('No active feedback period found')
                    )
                
                self.stdout.write(
                    self.style.SUCCESS('Feedback database fix completed successfully!')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error fixing feedback database: {str(e)}')
            )
            raise e