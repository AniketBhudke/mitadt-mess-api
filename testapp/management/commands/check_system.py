from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.db import connection
from testapp.models import FeedbackPeriod, MessFeedback
from django.contrib.auth.models import User
import sys

class Command(BaseCommand):
    help = 'Check system for potential errors and issues'

    def handle(self, *args, **options):
        self.stdout.write("🔍 Starting system check...")
        
        errors = []
        warnings = []
        
        # Check 1: Database connectivity
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.stdout.write("✅ Database connection: OK")
        except Exception as e:
            errors.append(f"❌ Database connection failed: {e}")
        
        # Check 2: Model validation
        try:
            # Check FeedbackPeriod model
            periods = FeedbackPeriod.objects.all()
            for period in periods:
                try:
                    period.full_clean()
                except ValidationError as e:
                    errors.append(f"❌ FeedbackPeriod validation error: {e}")
            
            self.stdout.write(f"✅ FeedbackPeriod model validation: OK ({periods.count()} periods)")
        except Exception as e:
            errors.append(f"❌ FeedbackPeriod model error: {e}")
        
        # Check 3: Current period logic
        try:
            current_period = FeedbackPeriod.get_current_period()
            if current_period:
                self.stdout.write(f"✅ Current period found: {current_period.name}")
                if current_period.is_submission_allowed():
                    self.stdout.write("✅ Submissions are currently allowed")
                else:
                    warnings.append("⚠️ Submissions are currently not allowed")
            else:
                warnings.append("⚠️ No current active period found")
        except Exception as e:
            errors.append(f"❌ Current period logic error: {e}")
        
        # Check 4: Feedback model integrity
        try:
            feedback_count = MessFeedback.objects.count()
            self.stdout.write(f"✅ MessFeedback model: OK ({feedback_count} feedback entries)")
            
            # Check for orphaned feedback (without period info)
            orphaned = MessFeedback.objects.filter(
                feedback_period_start__isnull=True
            ).count()
            if orphaned > 0:
                warnings.append(f"⚠️ Found {orphaned} feedback entries without period information")
        except Exception as e:
            errors.append(f"❌ MessFeedback model error: {e}")
        
        # Check 5: Admin user exists
        try:
            admin_users = User.objects.filter(is_superuser=True).count()
            if admin_users > 0:
                self.stdout.write(f"✅ Admin users: {admin_users} found")
            else:
                warnings.append("⚠️ No admin users found")
        except Exception as e:
            errors.append(f"❌ User model error: {e}")
        
        # Check 6: Template files exist
        import os
        from django.conf import settings
        
        template_files = [
            'testapp/feedback.html',
            'testapp/feedback_success.html',
            'testapp/working_login.html',
            'testapp/working_signup.html',
            'testapp/index.html'
        ]
        
        for template in template_files:
            template_path = None
            for template_dir in settings.TEMPLATES[0]['DIRS']:
                full_path = os.path.join(template_dir, template)
                if os.path.exists(full_path):
                    template_path = full_path
                    break
            
            if template_path:
                self.stdout.write(f"✅ Template found: {template}")
            else:
                errors.append(f"❌ Template missing: {template}")
        
        # Check 7: Static files
        static_files = [
            'testapp/css/styles.css',
            'testapp/css/login.css',
            'testapp/css/sign_up.css'
        ]
        
        for static_file in static_files:
            static_path = None
            for static_dir in settings.STATICFILES_DIRS:
                full_path = os.path.join(static_dir, static_file)
                if os.path.exists(full_path):
                    static_path = full_path
                    break
            
            if static_path:
                self.stdout.write(f"✅ Static file found: {static_file}")
            else:
                warnings.append(f"⚠️ Static file missing: {static_file}")
        
        # Summary
        self.stdout.write("\n" + "="*50)
        self.stdout.write("📊 SYSTEM CHECK SUMMARY")
        self.stdout.write("="*50)
        
        if not errors and not warnings:
            self.stdout.write(self.style.SUCCESS("🎉 All checks passed! System is healthy."))
        else:
            if errors:
                self.stdout.write(self.style.ERROR(f"❌ {len(errors)} ERRORS found:"))
                for error in errors:
                    self.stdout.write(f"  {error}")
            
            if warnings:
                self.stdout.write(self.style.WARNING(f"⚠️ {len(warnings)} WARNINGS found:"))
                for warning in warnings:
                    self.stdout.write(f"  {warning}")
        
        # Return appropriate exit code
        if errors:
            sys.exit(1)
        elif warnings:
            sys.exit(2)
        else:
            sys.exit(0)