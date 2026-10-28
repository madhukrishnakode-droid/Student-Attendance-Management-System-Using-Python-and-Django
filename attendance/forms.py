"""
Forms for Student Attendance Management System.
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Student, Attendance
import datetime


class LoginForm(AuthenticationForm):
    """Custom login form with Bootstrap styling."""

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username',
            'autofocus': True,
            'id': 'id_username',
        }),
        label='Username'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'id': 'id_password',
        }),
        label='Password'
    )


class StudentForm(forms.ModelForm):
    """Form for creating and editing students."""

    class Meta:
        model = Student
        fields = ['roll_number', 'full_name', 'department', 'year_of_study']
        widgets = {
            'roll_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 23CS101',
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full name of the student',
            }),
            'department': forms.Select(attrs={
                'class': 'form-select',
            }),
            'year_of_study': forms.Select(attrs={
                'class': 'form-select',
            }),
        }
        labels = {
            'roll_number': 'Roll Number',
            'full_name': 'Full Name',
            'department': 'Department',
            'year_of_study': 'Year of Study',
        }

    def clean_roll_number(self):
        roll = self.cleaned_data.get('roll_number', '').strip().upper()
        if not roll:
            raise forms.ValidationError("Roll number is required.")
        # Check uniqueness (exclude self for edit)
        qs = Student.objects.filter(roll_number=roll)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                f"A student with roll number '{roll}' already exists."
            )
        return roll

    def clean_full_name(self):
        name = self.cleaned_data.get('full_name', '').strip()
        if not name:
            raise forms.ValidationError("Full name is required.")
        return name


class AttendanceDateForm(forms.Form):
    """Simple form to select a date for marking attendance."""

    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'attendance_date',
        }),
        label='Attendance Date',
        initial=datetime.date.today,
    )


class AttendanceReportFilterForm(forms.Form):
    """Filter form for attendance reports."""

    DEPARTMENT_CHOICES = [('', 'All Departments')] + list(Student.DEPARTMENT_CHOICES)

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name or roll number',
        }),
        label='Search'
    )
    department = forms.ChoiceField(
        required=False,
        choices=DEPARTMENT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Department'
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        }),
        label='Start Date'
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        }),
        label='End Date'
    )
