from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from testapp.models import SuggestionPeriod

class Command(BaseCommand):
    help = 'Fix and ensure suggestion periods are always available'

    def handle(self, *args, **options):
        self.stdout.write("🔧 Fixing suggestion periods...")
        
        # Get today's date
        today = date.today()
        self.stdout.write(f"Today's date: {today}")
        
        # Deactivate all periods first
        SuggestionPeriod.objects.all().update(is_active=False)
        self.stdout.write("Deactivated all existing periods")
        
        # Find or create current week period
        start_of_week = today - timedelta(days=today.weekday())  # Monday
        end_of_week = start_of_week + timedelta(days=6)  # Sunday
        
        # Try to find existing period for this week
        current_period = SuggestionPeriod.objects.filter(
            start_date=start_of_week,
            end_date=end_of_week
        ).first()
        
        if current_period:
            # Activate existing period
            current_period.is_active = True
            current_period.save()
            self.stdout.write(f"✅ Activated existing period: {current_period.name}")
        else:
            # Create new period for current week
            period_name = f"Week {start_of_week.strftime('%b %d')} - {end_of_week.strftime('%b %d, %Y')}"
            current_period = SuggestionPeriod.objects.create(
                name=period_name,
                start_date=start_of_week,
                end_date=end_of_week,
                submission_deadline=end_of_week + timedelta(days=1),  # Next Monday
                is_active=True
            )
            self.stdout.write(f"✅ Created new period: {current_period.name}")
        
        # Create next 4 weeks if they don't exist
        for i in range(1, 5):
            future_start = start_of_week + timedelta(weeks=i)
            future_end = future_start + timedelta(days=6)
            
            existing = SuggestionPeriod.objects.filter(
                start_date=future_start,
                end_date=future_end
            ).exists()
            
            if not existing:
                future_name = f"Week {future_start.strftime('%b %d')} - {future_end.strftime('%b %d, %Y')}"
                SuggestionPeriod.objects.create(
                    name=future_name,
                    start_date=future_start,
                    end_date=future_end,
                    submission_deadline=future_end + timedelta(days=1),
                    is_active=False
                )
                self.stdout.write(f"Created future period: {future_name}")
        
        # Verify current period
        active_period = SuggestionPeriod.get_current_period()
        if active_period and active_period.is_submission_allowed():
            self.stdout.write(self.style.SUCCESS(f"✅ SUCCESS: Current period is active and accepting submissions"))
            self.stdout.write(f"   Period: {active_period.name}")
            self.stdout.write(f"   Dates: {active_period.start_date} to {active_period.end_date}")
            self.stdout.write(f"   Deadline: {active_period.submission_deadline}")
        else:
            self.stdout.write(self.style.ERROR("❌ ERROR: No active period found or submissions not allowed"))
            
        # Show all periods
        all_periods = SuggestionPeriod.objects.all().order_by('start_date')
        self.stdout.write(f"\n📋 All periods ({all_periods.count()} total):")
        for period in all_periods:
            status = "🟢 ACTIVE" if period.is_active else "⚪ INACTIVE"
            self.stdout.write(f"   {status} {period.name} ({period.start_date} to {period.end_date})")