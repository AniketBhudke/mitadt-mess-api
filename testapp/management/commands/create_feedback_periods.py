from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from testapp.models import FeedbackPeriod

class Command(BaseCommand):
    help = 'Create sample feedback periods for testing'

    def handle(self, *args, **options):
        # Clear existing periods
        FeedbackPeriod.objects.all().delete()
        
        # Get current date
        today = timezone.now().date()
        
        # Create current active period (this week)
        current_start = today - timedelta(days=today.weekday())  # Monday of this week
        current_end = current_start + timedelta(days=6)  # Sunday of this week
        current_deadline = current_end - timedelta(days=1)  # Saturday (one day before end)
        
        current_period = FeedbackPeriod.objects.create(
            name=f"Week {current_start.strftime('%U')} - {current_start.strftime('%B %Y')}",
            start_date=current_start,
            end_date=current_end,
            submission_deadline=current_deadline,
            is_active=True
        )
        
        # Create next week's period (inactive for now)
        next_start = current_end + timedelta(days=1)  # Next Monday
        next_end = next_start + timedelta(days=6)  # Next Sunday
        next_deadline = next_end - timedelta(days=1)  # Next Saturday
        
        next_period = FeedbackPeriod.objects.create(
            name=f"Week {next_start.strftime('%U')} - {next_start.strftime('%B %Y')}",
            start_date=next_start,
            end_date=next_end,
            submission_deadline=next_deadline,
            is_active=False
        )
        
        # Create a past period (for testing)
        past_start = current_start - timedelta(days=7)  # Last Monday
        past_end = past_start + timedelta(days=6)  # Last Sunday
        past_deadline = past_end - timedelta(days=1)  # Last Saturday
        
        past_period = FeedbackPeriod.objects.create(
            name=f"Week {past_start.strftime('%U')} - {past_start.strftime('%B %Y')}",
            start_date=past_start,
            end_date=past_end,
            submission_deadline=past_deadline,
            is_active=False
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created feedback periods:\n'
                f'- Current: {current_period.name} (Active)\n'
                f'- Next: {next_period.name} (Inactive)\n'
                f'- Past: {past_period.name} (Inactive)'
            )
        )