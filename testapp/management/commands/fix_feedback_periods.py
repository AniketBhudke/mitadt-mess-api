from django.core.management.base import BaseCommand
from testapp.models import FeedbackPeriod, MessFeedback
from django.utils import timezone
from datetime import timedelta
from django.db import transaction

class Command(BaseCommand):
    help = 'Fix feedback entries without period information'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write("🔍 DRY RUN MODE - No changes will be made")
        
        # Find feedback without period information
        orphaned_feedback = MessFeedback.objects.filter(
            feedback_period_start__isnull=True
        )
        
        if not orphaned_feedback.exists():
            self.stdout.write("✅ No orphaned feedback found!")
            return
        
        self.stdout.write(f"Found {orphaned_feedback.count()} feedback entries without period information")
        
        # Temporarily remove the unique constraint by updating each feedback with unique periods
        try:
            updated_count = 0
            skipped_count = 0
            
            for i, feedback in enumerate(orphaned_feedback):
                # Create a unique period for each orphaned feedback to avoid constraint issues
                feedback_date = feedback.submitted_at.date() if feedback.submitted_at else timezone.now().date()
                
                # Create period based on submission date
                start_date = feedback_date - timedelta(days=feedback_date.weekday())  # Monday of that week
                end_date = start_date + timedelta(days=6)  # Sunday of that week
                
                if not dry_run:
                    try:
                        with transaction.atomic():
                            feedback.feedback_period_start = start_date
                            feedback.feedback_period_end = end_date
                            feedback.save()
                        updated_count += 1
                        self.stdout.write(f"Updated feedback {feedback.id} ({feedback.email}) with period {start_date} to {end_date}")
                    except Exception as e:
                        # If there's still a constraint violation, create a unique period
                        unique_start = start_date - timedelta(days=i)  # Make it unique by shifting days
                        unique_end = unique_start + timedelta(days=6)
                        
                        try:
                            feedback.feedback_period_start = unique_start
                            feedback.feedback_period_end = unique_end
                            feedback.save()
                            updated_count += 1
                            self.stdout.write(f"Updated feedback {feedback.id} with unique period {unique_start} to {unique_end}")
                        except Exception as e2:
                            self.stdout.write(f"⚠️ Skipped feedback {feedback.id}: {e2}")
                            skipped_count += 1
                else:
                    self.stdout.write(f"Would update feedback {feedback.id} ({feedback.email}) with period {start_date} to {end_date}")
                    updated_count += 1
            
            if dry_run:
                self.stdout.write(f"Would update {updated_count} feedback entries")
            else:
                self.stdout.write(f"✅ Updated {updated_count} feedback entries")
                if skipped_count > 0:
                    self.stdout.write(f"⚠️ Skipped {skipped_count} feedback entries due to constraints")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error fixing feedback periods: {e}"))