from django.core.management.base import BaseCommand
from django.utils import timezone
from analytics.views import generate_daily_analytics


class Command(BaseCommand):
    help = 'Generate aggregated daily analytics for the superadmin database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Number of past days to generate analytics for (default: 1)'
        )

    def handle(self, *args, **options):
        days = options['days']

        self.stdout.write(
            self.style.SUCCESS(f'Starting analytics generation for the last {days} day(s)...')
        )

        try:
            generate_daily_analytics()
            self.stdout.write(
                self.style.SUCCESS('✓ Analytics generated successfully!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error generating analytics: {str(e)}')
            )
