from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from testapp.models import SuggestionPeriod

class Command(BaseCommand):
    help = 'Activate the current suggestion period based on today\'s date'

    def handle(self, *args, **options):
        # Use the actual current date (not timezone-dependent)
        today = date.today()
        self.stdout.write(f"Today's date: {today}")
        
        # Find the period that should be active for today
        current_period = SuggestionPeriod.objects.filter(
            start_date__lte=today,
            end_date__gte=today
        ).first()
        
        if current_period:
            # Deactivate all other periods
            SuggestionPeriod.objects.all().update(is_active=False)
            
            # Activate the current period
            current_period.is_active = True
            current_period.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Activated period: {current_period.name} '
                    f'({current_period.start_date} to {current_period.end_date})'
                )
            )
            
            # Verify submission is allowed
            if current_period.is_submission_allowed():
                self.stdout.write(self.style.SUCCESS('✅ Submissions are now allowed'))
            else:
                self.stdout.write(self.style.WARNING('⚠️ Submissions are not allowed (past deadline)'))
                
        else:
            self.stdout.write(self.style.WARNING(f'No period found for {today}'))
            
            # Create a new period for this week if none exists
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            
            period_name = f"Week {start_of_week.strftime('%b %d')} - {end_of_week.strftime('%b %d, %Y')}"
            
            # Deactivate all other periods
            SuggestionPeriod.objects.all().update(is_active=False)
            
            # Create new period
            new_period = SuggestionPeriod.objects.create(
                name=period_name,
                start_date=start_of_week,
                end_date=end_of_week,
                submission_deadline=end_of_week,
                is_active=True
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created new period: {new_period.name} '
                    f'({new_period.start_date} to {new_period.end_date})'
                )
            )