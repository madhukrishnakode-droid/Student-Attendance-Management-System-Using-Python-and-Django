"""
Management command to load demo student data.
Run: python manage.py load_demo_students
"""
from django.core.management.base import BaseCommand
from attendance.models import Student


DEMO_STUDENTS = [
    {'roll_number': '23CS101', 'full_name': 'Ravi Kumar',   'department': 'CSE',  'year_of_study': 2},
    {'roll_number': '23CS102', 'full_name': 'Priya Sharma', 'department': 'CSE',  'year_of_study': 2},
    {'roll_number': '23EC101', 'full_name': 'Arjun Kumar',  'department': 'ECE',  'year_of_study': 2},
    {'roll_number': '24CS101', 'full_name': 'Sneha Reddy',  'department': 'CSE',  'year_of_study': 1},
    {'roll_number': '24IT101', 'full_name': 'Kiran Kumar',  'department': 'IT',   'year_of_study': 1},
]


class Command(BaseCommand):
    help = 'Load demo student data for testing purposes.'

    def handle(self, *args, **options):
        created = 0
        skipped = 0

        for data in DEMO_STUDENTS:
            obj, was_created = Student.objects.get_or_create(
                roll_number=data['roll_number'],
                defaults={
                    'full_name': data['full_name'],
                    'department': data['department'],
                    'year_of_study': data['year_of_study'],
                }
            )
            if was_created:
                self.stdout.write(self.style.SUCCESS(f"  Created: {obj}"))
                created += 1
            else:
                self.stdout.write(f"  Skipped (already exists): {obj}")
                skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nDone! Created {created} student(s), skipped {skipped} existing."
        ))
