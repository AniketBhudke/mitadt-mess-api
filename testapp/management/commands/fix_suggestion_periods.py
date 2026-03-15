from django.core.management.base import BaseCommand
from django.db import transaction
from testapp.models import Weekly_suggestion, SuggestionPeriod
from datetime import timedelta

class Command(BaseCommand):
    help = 'Fix existing weekly suggestions by adding period information'

    def add_arguments(self, parser):
        parser.add_argument(
            '--remove-duplicates',
            action='store_true',
            help='Remove duplicate suggestions (keep the first one)',
        )

    def handle(self, *args, **options):
        # Get all suggestions without period information
        suggestions_without_period = Weekly_suggestion.objects.filter(
            suggestion_period_start__isnull=True,
            suggestion_period_end__isnull=True
        )
        
        total_suggestions = suggestions_without_period.count()
        
        if total_suggestions == 0:
            self.stdout.write(
                self.style.SUCCESS('All weekly suggestions already have period information.')
            )
            return
        
        self.stdout.write(f'Found {total_suggestions} suggestions without period information.')
        
        fixed_count = 0
        duplicate_count = 0
        
        # Group suggestions by email and submission week to handle duplicates
        processed_combinations = set()
        
        with transaction.atomic():
            for suggestion in suggestions_without_period.order_by('submitted_at'):
                # Use the submission date to determine the period
                submission_date = suggestion.submitted_at.date()
                
                # Calculate the week start (Monday) and end (Sunday) for this submission
                week_start = submission_date - timedelta(days=submission_date.weekday())
                week_end = week_start + timedelta(days=6)
                
                # Create a unique key for this email + period combination
                combination_key = (suggestion.email, week_start, week_end)
                
                if combination_key in processed_combinations:
                    # This is a duplicate
                    if options['remove_duplicates']:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Removing duplicate suggestion {suggestion.id}: {suggestion.student_name} '
                                f'({suggestion.email}) for period {week_start} to {week_end}'
                            )
                        )
                        suggestion.delete()
                        duplicate_count += 1
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Skipping duplicate suggestion {suggestion.id}: {suggestion.student_name} '
                                f'({suggestion.email}) for period {week_start} to {week_end}. '
                                f'Use --remove-duplicates to remove it.'
                            )
                        )
                    continue
                
                # Mark this combination as processed
                processed_combinations.add(combination_key)
                
                # Try to find an existing period that matches
                matching_period = SuggestionPeriod.objects.filter(
                    start_date=week_start,
                    end_date=week_end
                ).first()
                
                if matching_period:
                    # Use existing period
                    suggestion.suggestion_period_start = matching_period.start_date
                    suggestion.suggestion_period_end = matching_period.end_date
                else:
                    # Create period information based on submission date
                    suggestion.suggestion_period_start = week_start
                    suggestion.suggestion_period_end = week_end
                
                try:
                    suggestion.save()
                    fixed_count += 1
                    
                    self.stdout.write(
                        f'Fixed suggestion {suggestion.id}: {suggestion.student_name} '
                        f'({suggestion.suggestion_period_start} to {suggestion.suggestion_period_end})'
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Error fixing suggestion {suggestion.id}: {str(e)}'
                        )
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully fixed {fixed_count} weekly suggestions with period information.'
            )
        )
        
        if duplicate_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Removed {duplicate_count} duplicate suggestions.'
                )
            )
        
        # Check for remaining potential duplicates
        self.stdout.write('\nChecking for remaining potential duplicate submissions...')
        
        # Group by email and period to find duplicates
        from django.db.models import Count
        duplicates = Weekly_suggestion.objects.values(
            'email', 'suggestion_period_start', 'suggestion_period_end'
        ).annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        if duplicates:
            self.stdout.write(
                self.style.WARNING(
                    f'Found {len(duplicates)} remaining duplicate groups:'
                )
            )
            for dup in duplicates:
                self.stdout.write(
                    f"  Email: {dup['email']}, Period: {dup['suggestion_period_start']} to {dup['suggestion_period_end']}, Count: {dup['count']}"
                )
            self.stdout.write(
                self.style.WARNING(
                    'Run this command with --remove-duplicates to clean them up.'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('No duplicate submissions found.')
            )