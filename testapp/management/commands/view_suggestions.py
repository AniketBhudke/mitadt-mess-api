from django.core.management.base import BaseCommand
from testapp.models import Weekly_suggestion, SuggestionPeriod
from collections import defaultdict

class Command(BaseCommand):
    help = 'View weekly suggestions summary by period and mess'

    def add_arguments(self, parser):
        parser.add_argument(
            '--period',
            type=str,
            help='Show suggestions for specific period (e.g., "Week 2 - Mar 2026")',
        )
        parser.add_argument(
            '--mess',
            type=str,
            help='Filter by specific mess name',
        )

    def handle(self, *args, **options):
        # Get current period if no specific period requested
        if options['period']:
            try:
                period = SuggestionPeriod.objects.get(name__icontains=options['period'])
            except SuggestionPeriod.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Period '{options['period']}' not found"))
                return
        else:
            period = SuggestionPeriod.get_current_period()
            if not period:
                self.stdout.write(self.style.ERROR("No current active period found"))
                return

        self.stdout.write(f"📊 Weekly Suggestions for: {period.name}")
        self.stdout.write(f"Period: {period.start_date} to {period.end_date}")
        self.stdout.write(f"Deadline: {period.submission_deadline}")
        self.stdout.write("-" * 60)

        # Get suggestions for this period
        suggestions = Weekly_suggestion.objects.filter(
            suggestion_period_start=period.start_date,
            suggestion_period_end=period.end_date
        )

        if options['mess']:
            suggestions = suggestions.filter(mess_name__icontains=options['mess'])

        if not suggestions.exists():
            self.stdout.write(self.style.WARNING("No suggestions found for this period"))
            return

        # Group by mess
        by_mess = defaultdict(list)
        for suggestion in suggestions:
            by_mess[suggestion.mess_name].append(suggestion)

        # Display summary
        total_suggestions = suggestions.count()
        unique_emails = suggestions.values('email').distinct().count()
        
        self.stdout.write(f"📈 Summary:")
        self.stdout.write(f"  Total Suggestions: {total_suggestions}")
        self.stdout.write(f"  Unique Users: {unique_emails}")
        self.stdout.write(f"  Messes with Suggestions: {len(by_mess)}")
        self.stdout.write("")

        # Display by mess
        for mess_name, mess_suggestions in by_mess.items():
            self.stdout.write(f"🍽️  {mess_name}: {len(mess_suggestions)} suggestions")
            for suggestion in mess_suggestions:
                self.stdout.write(f"   • {suggestion.student_name} ({suggestion.email}) - {suggestion.submitted_at.strftime('%Y-%m-%d %H:%M')}")
            self.stdout.write("")

        # Show duplicate prevention stats
        all_emails = [s.email for s in suggestions]
        email_counts = defaultdict(int)
        for email in all_emails:
            email_counts[email] += 1
        
        users_with_multiple = {email: count for email, count in email_counts.items() if count > 1}
        if users_with_multiple:
            self.stdout.write("👥 Users with multiple submissions (different messes):")
            for email, count in users_with_multiple.items():
                user_suggestions = suggestions.filter(email=email)
                messes = [s.mess_name for s in user_suggestions]
                self.stdout.write(f"   • {email}: {count} submissions ({', '.join(messes)})")
        else:
            self.stdout.write("✅ No users have submitted for multiple messes in this period")