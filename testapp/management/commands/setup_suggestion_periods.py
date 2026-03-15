from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from testapp.models import SuggestionPeriod

class Command(BaseCommand):
    help = 'Setup suggestion periods for production deployment'

    def handle(self, *args, **options):
        today = timezone.now().date()
        
        # Ensure current week has an active period with extended deadline
        current_week_start = today - timedelta(days=today.weekday())
        current_week_end = current_week_start + timedelta(days=6)
        
        # Check if current week period exists
        current_period = SuggestionPeriod.objects.filter(
            start_date=current_week_start,
            end_date=current_week_end
        ).first()
        
        if current_period:
            # Extend deadline if it's today or in the past
            if current_period.submission_deadline <= today:
                current_period.submission_deadline = today + timedelta(days=1)
                current_period.is_active = True
                current_period.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Extended deadline for {current_period.name} to {current_period.submission_deadline}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Current period {current_period.name} is already active with deadline {current_period.submission_deadline}'
                    )
                )
        else:
            # Create current week period
            period_name = f"Week - {current_week_start.strftime('%b %Y')}"
            current_period = SuggestionPeriod.objects.create(
                name=period_name,
                start_date=current_week_start,
                end_date=current_week_end,
                submission_deadline=today + timedelta(days=1),
                is_active=True
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created current week period: {current_period.name}'
                )
            )
        
        # Ensure we have at least 8 weeks of periods
        weeks_to_create = 8
        created_count = 0
        
        for i in range(weeks_to_create):
            week_start = current_week_start + timedelta(weeks=i)
            week_end = week_start + timedelta(days=6)
            submission_deadline = week_end
            
            # For current week, use extended deadline
            if i == 0:
                submission_deadline = max(submission_deadline, today + timedelta(days=1))
            
            period_name = f"Week {i+1} - {week_start.strftime('%b %Y')}"
            
            existing = SuggestionPeriod.objects.filter(
                start_date=week_start,
                end_date=week_end
            ).first()
            
            if not existing:
                is_active = (i == 0)  # Only current week is active
                
                period = SuggestionPeriod.objects.create(
                    name=period_name,
                    start_date=week_start,
                    end_date=week_end,
                    submission_deadline=submission_deadline,
                    is_active=is_active
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created period: {period.name} (Deadline: {period.submission_deadline})'
                    )
                )
                created_count += 1
        
        # Deactivate old periods
        old_periods = SuggestionPeriod.objects.filter(
            end_date__lt=current_week_start,
            is_active=True
        )
        
        for period in old_periods:
            period.is_active = False
            period.save()
            self.stdout.write(
                self.style.WARNING(
                    f'Deactivated old period: {period.name}'
                )
            )
        
        # Show current status
        active_period = SuggestionPeriod.get_current_period()
        if active_period:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nCurrent active period: {active_period.name}'
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Submission deadline: {active_period.submission_deadline}'
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Submissions allowed: {active_period.is_submission_allowed()}'
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    'No active period found! Please check the configuration.'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSetup complete. Created {created_count} new periods.'
            )
        )