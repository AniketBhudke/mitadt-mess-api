from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from testapp.models import FeedbackPeriod

class Command(BaseCommand):
    help = 'Create sample feedback periods for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing periods before creating new ones',
        )

    def handle(self, *args, **options):
        try:
            # Clear existing periods if requested
            if options['clear']:
                deleted_count = FeedbackPeriod.objects.count()
                FeedbackPeriod.objects.all().delete()
                self.stdout.write(f"Deleted {deleted_count} existing periods.")
            
            # Get current date
            today = timezone.now().date()
            
            # Create current active period (this week)
            current_start = today - timedelta(days=today.weekday())  # Monday of this week
            current_end = current_start + timedelta(days=6)  # Sunday of this week
            current_deadline = current_end - timedelta(days=1)  # Saturday (one day before end)
            
            # Check if current period already exists
            if not FeedbackPeriod.objects.filter(start_date=current_start).exists():
                current_period = FeedbackPeriod.objects.create(
                    name=f"Week {current_start.strftime('%U')} - {current_start.strftime('%B %Y')}",
                    start_date=current_start,
                    end_date=current_end,
                    submission_deadline=current_deadline,
                    is_active=True
                )
                self.stdout.write(f"Created current period: {current_period.name}")
            else:
                self.stdout.write("Current period already exists.")
            
            # Create next week's period (inactive for now)
            next_start = current_end + timedelta(days=1)  # Next Monday
            next_end = next_start + timedelta(days=6)  # Next Sunday
            next_deadline = next_end - timedelta(days=1)  # Next Saturday
            
            if not FeedbackPeriod.objects.filter(start_date=next_start).exists():
                next_period = FeedbackPeriod.objects.create(
                    name=f"Week {next_start.strftime('%U')} - {next_start.strftime('%B %Y')}",
                    start_date=next_start,
                    end_date=next_end,
                    submission_deadline=next_deadline,
                    is_active=False
                )
                self.stdout.write(f"Created next period: {next_period.name}")
            else:
                self.stdout.write("Next period already exists.")
            
            # Create a past period (for testing)
            past_start = current_start - timedelta(days=7)  # Last Monday
            past_end = past_start + timedelta(days=6)  # Last Sunday
            past_deadline = past_end - timedelta(days=1)  # Last Saturday
            
            if not FeedbackPeriod.objects.filter(start_date=past_start).exists():
                past_period = FeedbackPeriod.objects.create(
                    name=f"Week {past_start.strftime('%U')} - {past_start.strftime('%B %Y')}",
                    start_date=past_start,
                    end_date=past_end,
                    submission_deadline=past_deadline,
                    is_active=False
                )
                self.stdout.write(f"Created past period: {past_period.name}")
            else:
                self.stdout.write("Past period already exists.")
            
            self.stdout.write(
                self.style.SUCCESS('Successfully processed feedback periods!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating feedback periods: {str(e)}')
            )