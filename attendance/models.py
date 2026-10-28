"""
Models for the Student Attendance Management System.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Student(models.Model):
    """Represents a registered student in the system."""

    DEPARTMENT_CHOICES = [
        ('CSE', 'Computer Science & Engineering'),
        ('ECE', 'Electronics & Communication Engineering'),
        ('EEE', 'Electrical & Electronics Engineering'),
        ('MECH', 'Mechanical Engineering'),
        ('CIVIL', 'Civil Engineering'),
        ('IT', 'Information Technology'),
    ]

    YEAR_CHOICES = [
        (1, 'First Year'),
        (2, 'Second Year'),
        (3, 'Third Year'),
        (4, 'Fourth Year'),
    ]

    roll_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Roll Number',
        help_text='Unique roll number for the student'
    )
    full_name = models.CharField(
        max_length=100,
        verbose_name='Full Name'
    )
    department = models.CharField(
        max_length=10,
        choices=DEPARTMENT_CHOICES,
        verbose_name='Department'
    )
    year_of_study = models.PositiveSmallIntegerField(
        choices=YEAR_CHOICES,
        verbose_name='Year of Study'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Last Updated')

    class Meta:
        ordering = ['department', 'year_of_study', 'roll_number']
        verbose_name = 'Student'
        verbose_name_plural = 'Students'

    def __str__(self):
        return f"{self.roll_number} - {self.full_name}"

    def get_department_display_full(self):
        return dict(self.DEPARTMENT_CHOICES).get(self.department, self.department)

    def get_year_display_text(self):
        return dict(self.YEAR_CHOICES).get(self.year_of_study, str(self.year_of_study))

    def attendance_stats(self, start_date=None, end_date=None):
        """Calculate attendance statistics for this student."""
        qs = self.attendance_set.all()
        if start_date:
            qs = qs.filter(date__gte=start_date)
        if end_date:
            qs = qs.filter(date__lte=end_date)

        total = qs.count()
        present = qs.filter(status='P').count()
        absent = total - present

        if total > 0:
            percentage = round((present / total) * 100, 1)
        else:
            percentage = 0

        return {
            'total': total,
            'present': present,
            'absent': absent,
            'percentage': percentage,
        }


class Attendance(models.Model):
    """Records a single attendance event for a student on a given date."""

    STATUS_CHOICES = [
        ('P', 'Present'),
        ('A', 'Absent'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,   # Protect historical data
        verbose_name='Student'
    )
    date = models.DateField(verbose_name='Attendance Date')
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        verbose_name='Status'
    )
    marked_at = models.DateTimeField(auto_now_add=True, verbose_name='Marked At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Last Updated')

    class Meta:
        unique_together = ('student', 'date')   # DB-level constraint
        ordering = ['-date', 'student__roll_number']
        verbose_name = 'Attendance Record'
        verbose_name_plural = 'Attendance Records'

    def __str__(self):
        return f"{self.student.roll_number} | {self.date} | {self.get_status_display()}"
