"""
Tests for Student Attendance Management System.
Run: python manage.py test attendance
"""
import datetime
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Student, Attendance


# ────────────────────────── Helpers ──────────────────────────────────────────

def make_student(roll='TEST001', name='Test Student', dept='CSE', year=1):
    return Student.objects.create(
        roll_number=roll, full_name=name, department=dept, year_of_study=year
    )


def make_user(username='faculty', password='testpass123'):
    return User.objects.create_user(username=username, password=password)


# ────────────────────────── Model Tests ──────────────────────────────────────

class StudentModelTest(TestCase):

    def test_student_creation(self):
        """Test 1: Student can be created with required fields."""
        student = make_student()
        self.assertEqual(student.roll_number, 'TEST001')
        self.assertEqual(student.full_name, 'Test Student')
        self.assertEqual(student.department, 'CSE')
        self.assertEqual(student.year_of_study, 1)

    def test_duplicate_roll_number_rejected(self):
        """Test 2: Duplicate roll number must raise an IntegrityError."""
        from django.db import IntegrityError
        make_student(roll='DUP001')
        with self.assertRaises(IntegrityError):
            make_student(roll='DUP001', name='Another Student')

    def test_attendance_creation(self):
        """Test 3: Attendance record can be created for a student."""
        student = make_student()
        today = datetime.date.today()
        att = Attendance.objects.create(student=student, date=today, status='P')
        self.assertEqual(att.student, student)
        self.assertEqual(att.date, today)
        self.assertEqual(att.status, 'P')

    def test_duplicate_attendance_rejected(self):
        """Test 4: Same student cannot have two records on the same date."""
        from django.db import IntegrityError
        student = make_student()
        today = datetime.date.today()
        Attendance.objects.create(student=student, date=today, status='P')
        with self.assertRaises(IntegrityError):
            Attendance.objects.create(student=student, date=today, status='A')

    def test_update_existing_attendance_no_duplicate(self):
        """Test 5: update_or_create does not produce duplicate records."""
        student = make_student()
        today = datetime.date.today()
        Attendance.objects.update_or_create(student=student, date=today, defaults={'status': 'P'})
        Attendance.objects.update_or_create(student=student, date=today, defaults={'status': 'A'})
        count = Attendance.objects.filter(student=student, date=today).count()
        self.assertEqual(count, 1)
        att = Attendance.objects.get(student=student, date=today)
        self.assertEqual(att.status, 'A')

    def test_attendance_percentage_calculation(self):
        """Test 6: Attendance percentage is calculated correctly."""
        student = make_student()
        base = datetime.date(2024, 1, 1)
        for i in range(4):
            Attendance.objects.create(student=student, date=base + datetime.timedelta(days=i), status='P')
        Attendance.objects.create(student=student, date=base + datetime.timedelta(days=4), status='A')
        stats = student.attendance_stats()
        self.assertEqual(stats['total'], 5)
        self.assertEqual(stats['present'], 4)
        self.assertEqual(stats['absent'], 1)
        self.assertEqual(stats['percentage'], 80.0)

    def test_zero_attendance_records(self):
        """Test 7: Student with no records returns 0% without error."""
        student = make_student()
        stats = student.attendance_stats()
        self.assertEqual(stats['total'], 0)
        self.assertEqual(stats['percentage'], 0)

    def test_invalid_attendance_status_rejected(self):
        """Test 10: Only P or A are valid status values (via full_clean)."""
        from django.core.exceptions import ValidationError
        student = make_student()
        att = Attendance(student=student, date=datetime.date.today(), status='X')
        with self.assertRaises(ValidationError):
            att.full_clean()

    def test_filter_attendance_by_date_range(self):
        """Test 12: attendance_stats respects start and end date filters."""
        student = make_student()
        base = datetime.date(2024, 3, 1)
        # 5 days in March
        for i in range(5):
            Attendance.objects.create(student=student,
                                      date=base + datetime.timedelta(days=i),
                                      status='P')
        # 3 days in April
        april_base = datetime.date(2024, 4, 1)
        for i in range(3):
            Attendance.objects.create(student=student,
                                      date=april_base + datetime.timedelta(days=i),
                                      status='A')
        # Filter only March
        stats = student.attendance_stats(
            start_date=datetime.date(2024, 3, 1),
            end_date=datetime.date(2024, 3, 31)
        )
        self.assertEqual(stats['total'], 5)
        self.assertEqual(stats['present'], 5)


# ────────────────────────── View / Auth Tests ─────────────────────────────────

class AuthTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = make_user()

    def test_login_success(self):
        """Test 8: Faculty can log in successfully."""
        response = self.client.post(reverse('login'), {
            'username': 'faculty',
            'password': 'testpass123',
        })
        self.assertRedirects(response, reverse('dashboard'))

    def test_logout(self):
        """Test 8b: Faculty can log out."""
        self.client.login(username='faculty', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

    def test_redirect_unauthenticated_from_dashboard(self):
        """Test 9: Unauthenticated users are redirected from protected pages."""
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, '/login/?next=/')

    def test_redirect_unauthenticated_from_student_list(self):
        """Test 9b: Unauthenticated users cannot access student list."""
        response = self.client.get(reverse('student_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response['Location'])

    def test_authenticated_user_can_access_dashboard(self):
        """Authenticated users can access the dashboard."""
        self.client.login(username='faculty', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)


class AttendanceMarkingTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = make_user()
        self.client.login(username='faculty', password='testpass123')
        self.s1 = make_student(roll='S001', name='Alice')
        self.s2 = make_student(roll='S002', name='Bob')

    def test_bulk_attendance_rollback_on_partial_data(self):
        """Test 11: If any student has invalid status, nothing is saved."""
        today = datetime.date.today().isoformat()
        response = self.client.post(reverse('mark_attendance'), {
            'attendance_date': today,
            f'status_{self.s1.pk}': 'P',
            # s2 is missing → should fail validation
        })
        # No attendance should be saved
        self.assertEqual(Attendance.objects.count(), 0)
        self.assertEqual(response.status_code, 200)  # re-renders form

    def test_attendance_saved_successfully(self):
        """All students marked → attendance is saved."""
        today = datetime.date.today().isoformat()
        self.client.post(reverse('mark_attendance'), {
            'attendance_date': today,
            f'status_{self.s1.pk}': 'P',
            f'status_{self.s2.pk}': 'A',
        })
        self.assertEqual(Attendance.objects.count(), 2)
        self.assertEqual(Attendance.objects.get(student=self.s1).status, 'P')
        self.assertEqual(Attendance.objects.get(student=self.s2).status, 'A')
