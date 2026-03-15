from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from testapp.models import SuggestionPeriod

class Command(BaseCommand):
    help = 'Create initial suggestion periods for weekly suggestions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--weeks',
            type=int,
            default=4,
            help='Number of weeks to create periods for (default: 4)'
        )

    def handle(self, *args, **options):
        weeks = options['weeks']
        today = timezone.now().date()
        
        # Start from the beginning of current week (Monday)
        start_of_week = today - timedelta(days=today.weekday())
        
        created_count = 0
        
        for i in range(weeks):
            week_start = start_of_week + timedelta(weeks=i)
            week_end = week_start + timedelta(days=6)  # Sunday
            # Submission deadline is the Sunday of the week
            submission_deadline = week_end
            
            period_name = f"Week {i+1} - {week_start.strftime('%b %Y')}"
            
            # Check if period already exists
            existing = SuggestionPeriod.objects.filter(
                start_date=week_start,
                end_date=week_end
            ).first()
            
            if not existing:
                # Only mark the current week as active
                is_active = (i == 0)
                
                period = SuggestionPeriod.objects.create(
                    name=period_name,
                    start_date=week_start,
                    end_date=week_end,
                    submission_deadline=submission_deadline,
                    is_active=is_active
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created suggestion period: {period.name} '
                        f'({period.start_date} to {period.end_date}) '
                        f'- Active: {period.is_active}'
                    )
                )
                created_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'Period already exists: {existing.name}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nCreated {created_count} new suggestion periods.'
            )
        )
        
        # Show current active period
        current_period = SuggestionPeriod.get_current_period()
        if current_period:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Current active period: {current_period.name} '
                    f'(Deadline: {current_period.submission_deadline})'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    'No active suggestion period found. You may need to activate one manually.'
                )
            )