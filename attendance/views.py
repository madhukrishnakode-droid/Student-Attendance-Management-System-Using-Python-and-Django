"""
Views for Student Attendance Management System.
All views require authentication via @login_required.
"""
import csv
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.db.models import Q, Count
from django.http import HttpResponse

from .models import Student, Attendance
from .forms import LoginForm, StudentForm, AttendanceDateForm, AttendanceReportFilterForm


# ─────────────────────────── Authentication ──────────────────────────────────

def login_view(request):
    """Login page. Redirects to dashboard if already authenticated."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = LoginForm(request)

    return render(request, 'attendance/login.html', {'form': form})


def logout_view(request):
    """Logout and redirect to login page."""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')


# ─────────────────────────── Dashboard ───────────────────────────────────────

@login_required
def dashboard(request):
    """Main dashboard with summary statistics for a selected date."""
    today = datetime.date.today()
    selected_date_str = request.GET.get('date', today.isoformat())

    try:
        selected_date = datetime.date.fromisoformat(selected_date_str)
    except ValueError:
        selected_date = today

    total_students = Student.objects.count()

    # Attendance for selected date
    day_records = Attendance.objects.filter(date=selected_date)
    day_total = day_records.count()
    day_present = day_records.filter(status='P').count()
    day_absent = day_records.filter(status='A').count()
    day_percentage = round((day_present / day_total * 100), 1) if day_total > 0 else 0

    # Recent attendance activity (last 5 records)
    recent_attendance = Attendance.objects.select_related('student').order_by('-marked_at')[:5]

    # Recently added students
    recent_students = Student.objects.order_by('-created_at')[:5]

    # Low attendance students (below 75% overall)
    low_attendance_students = []
    for student in Student.objects.all():
        stats = student.attendance_stats()
        if stats['total'] > 0 and stats['percentage'] < 75:
            low_attendance_students.append({
                'student': student,
                'percentage': stats['percentage'],
            })

    context = {
        'selected_date': selected_date,
        'total_students': total_students,
        'day_total': day_total,
        'day_present': day_present,
        'day_absent': day_absent,
        'day_percentage': day_percentage,
        'recent_attendance': recent_attendance,
        'recent_students': recent_students,
        'low_attendance_students': low_attendance_students[:5],
        'low_count': len(low_attendance_students),
    }
    return render(request, 'attendance/dashboard.html', context)


# ─────────────────────────── Student Management ───────────────────────────────

@login_required
def student_list(request):
    """List all students with search and department filter."""
    students = Student.objects.all()
    search = request.GET.get('search', '').strip()
    dept_filter = request.GET.get('department', '')

    if search:
        students = students.filter(
            Q(full_name__icontains=search) | Q(roll_number__icontains=search)
        )
    if dept_filter:
        students = students.filter(department=dept_filter)

    context = {
        'students': students,
        'search': search,
        'dept_filter': dept_filter,
        'department_choices': Student.DEPARTMENT_CHOICES,
        'total_count': students.count(),
    }
    return render(request, 'attendance/student_list.html', context)


@login_required
def student_add(request):
    """Add a new student."""
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            messages.success(request, f"Student '{student.full_name}' added successfully.")
            return redirect('student_detail', pk=student.pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = StudentForm()

    return render(request, 'attendance/student_form.html', {
        'form': form,
        'action': 'Add',
        'title': 'Add New Student',
    })


@login_required
def student_edit(request, pk):
    """Edit an existing student."""
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f"Student '{student.full_name}' updated successfully.")
            return redirect('student_detail', pk=student.pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = StudentForm(instance=student)

    return render(request, 'attendance/student_form.html', {
        'form': form,
        'student': student,
        'action': 'Edit',
        'title': f'Edit Student — {student.full_name}',
    })


@login_required
def student_detail(request, pk):
    """Display student details and attendance statistics."""
    student = get_object_or_404(Student, pk=pk)
    stats = student.attendance_stats()
    recent_records = student.attendance_set.order_by('-date')[:10]

    context = {
        'student': student,
        'stats': stats,
        'recent_records': recent_records,
    }
    return render(request, 'attendance/student_detail.html', context)


@login_required
def student_delete(request, pk):
    """Delete student with attendance protection."""
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        att_count = student.attendance_set.count()
        if att_count > 0:
            messages.error(
                request,
                f"Cannot delete '{student.full_name}' — they have {att_count} attendance "
                f"record(s). Historical records must be preserved."
            )
            return redirect('student_detail', pk=student.pk)
        else:
            name = student.full_name
            student.delete()
            messages.success(request, f"Student '{name}' deleted successfully.")
            return redirect('student_list')

    return render(request, 'attendance/confirm_delete.html', {
        'student': student,
        'att_count': student.attendance_set.count(),
    })


# ─────────────────────────── Attendance Marking ──────────────────────────────

@login_required
def mark_attendance(request):
    """Mark/update attendance for all students for a selected date."""
    date_form = AttendanceDateForm(request.GET or None)
    selected_date = datetime.date.today()

    if date_form.is_valid():
        selected_date = date_form.cleaned_data['date']

    students = Student.objects.all().order_by('department', 'roll_number')
    total_students = students.count()

    # Pre-load existing attendance records for this date
    existing = {
        att.student_id: att.status
        for att in Attendance.objects.filter(date=selected_date)
    }

    if request.method == 'POST':
        date_str = request.POST.get('attendance_date', '')
        try:
            selected_date = datetime.date.fromisoformat(date_str)
        except ValueError:
            messages.error(request, "Invalid date. Please select a valid date.")
            return redirect('mark_attendance')

        errors = []
        records_to_save = []

        for student in students:
            key = f'status_{student.pk}'
            status = request.POST.get(key, '').strip()
            if status not in ('P', 'A'):
                errors.append(f"Missing or invalid status for {student.roll_number} — {student.full_name}.")
            else:
                records_to_save.append((student, status))

        if errors:
            messages.error(
                request,
                f"Please mark attendance for all students. "
                f"{len(errors)} student(s) are unmarked."
            )
            # Reload with submitted values
            submitted = {
                s.pk: request.POST.get(f'status_{s.pk}', '')
                for s in students
            }
            return render(request, 'attendance/mark_attendance.html', {
                'date_form': AttendanceDateForm(initial={'date': selected_date}),
                'selected_date': selected_date,
                'students': students,
                'existing': submitted,
                'total_students': total_students,
                'errors': errors,
            })

        # Save all records in a transaction
        try:
            with transaction.atomic():
                for student, status in records_to_save:
                    Attendance.objects.update_or_create(
                        student=student,
                        date=selected_date,
                        defaults={'status': status}
                    )
            messages.success(
                request,
                f"Attendance for {selected_date} saved successfully for {len(records_to_save)} student(s)."
            )
        except Exception as e:
            messages.error(request, f"An error occurred while saving attendance: {e}")

        return redirect('mark_attendance')

    # Build student list with existing or empty status
    student_data = [
        {'student': s, 'status': existing.get(s.pk, '')}
        for s in students
    ]

    context = {
        'date_form': date_form,
        'selected_date': selected_date,
        'student_data': student_data,
        'total_students': total_students,
        'existing_count': len(existing),
        'already_marked': len(existing) > 0,
    }
    return render(request, 'attendance/mark_attendance.html', context)


# ─────────────────────────── Attendance Reports ──────────────────────────────

@login_required
def attendance_reports(request):
    """Attendance reports with filters and statistics."""
    form = AttendanceReportFilterForm(request.GET or None)
    students = Student.objects.all()

    search = request.GET.get('search', '').strip()
    dept_filter = request.GET.get('department', '')
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')

    start_date = None
    end_date = None

    if start_date_str:
        try:
            start_date = datetime.date.fromisoformat(start_date_str)
        except ValueError:
            pass
    if end_date_str:
        try:
            end_date = datetime.date.fromisoformat(end_date_str)
        except ValueError:
            pass

    if search:
        students = students.filter(
            Q(full_name__icontains=search) | Q(roll_number__icontains=search)
        )
    if dept_filter:
        students = students.filter(department=dept_filter)

    report_data = []
    for student in students:
        stats = student.attendance_stats(start_date=start_date, end_date=end_date)
        pct = stats['percentage']
        if stats['total'] == 0:
            status_label = 'no-records'
        elif pct >= 75:
            status_label = 'normal'
        else:
            status_label = 'low'

        report_data.append({
            'student': student,
            'total': stats['total'],
            'present': stats['present'],
            'absent': stats['absent'],
            'percentage': pct,
            'status_label': status_label,
        })

    # Summary counts
    normal_count = sum(1 for r in report_data if r['status_label'] == 'normal')
    low_count = sum(1 for r in report_data if r['status_label'] == 'low')
    no_records_count = sum(1 for r in report_data if r['status_label'] == 'no-records')

    context = {
        'form': form,
        'report_data': report_data,
        'search': search,
        'dept_filter': dept_filter,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'normal_count': normal_count,
        'low_count': low_count,
        'no_records_count': no_records_count,
        'department_choices': Student.DEPARTMENT_CHOICES,
    }
    return render(request, 'attendance/attendance_reports.html', context)


@login_required
def student_attendance_history(request, pk):
    """Show full attendance history for a specific student."""
    student = get_object_or_404(Student, pk=pk)

    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')
    start_date = None
    end_date = None

    if start_date_str:
        try:
            start_date = datetime.date.fromisoformat(start_date_str)
        except ValueError:
            pass
    if end_date_str:
        try:
            end_date = datetime.date.fromisoformat(end_date_str)
        except ValueError:
            pass

    records = student.attendance_set.all().order_by('-date')
    if start_date:
        records = records.filter(date__gte=start_date)
    if end_date:
        records = records.filter(date__lte=end_date)

    stats = student.attendance_stats(start_date=start_date, end_date=end_date)

    context = {
        'student': student,
        'records': records,
        'stats': stats,
        'start_date': start_date_str,
        'end_date': end_date_str,
    }
    return render(request, 'attendance/student_attendance_history.html', context)


@login_required
def export_attendance_csv(request):
    """Export attendance report as CSV."""
    search = request.GET.get('search', '').strip()
    dept_filter = request.GET.get('department', '')
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')

    start_date = None
    end_date = None
    if start_date_str:
        try:
            start_date = datetime.date.fromisoformat(start_date_str)
        except ValueError:
            pass
    if end_date_str:
        try:
            end_date = datetime.date.fromisoformat(end_date_str)
        except ValueError:
            pass

    students = Student.objects.all()
    if search:
        students = students.filter(
            Q(full_name__icontains=search) | Q(roll_number__icontains=search)
        )
    if dept_filter:
        students = students.filter(department=dept_filter)

    response = HttpResponse(content_type='text/csv')
    filename = f"attendance_report_{datetime.date.today()}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow([
        'Roll Number', 'Full Name', 'Department', 'Year',
        'Total Sessions', 'Present', 'Absent', 'Percentage (%)', 'Status'
    ])

    for student in students:
        stats = student.attendance_stats(start_date=start_date, end_date=end_date)
        if stats['total'] == 0:
            status = 'No Records'
        elif stats['percentage'] >= 75:
            status = 'Normal'
        else:
            status = 'Low Attendance'

        writer.writerow([
            student.roll_number,
            student.full_name,
            student.get_department_display(),
            student.get_year_of_study_display(),
            stats['total'],
            stats['present'],
            stats['absent'],
            stats['percentage'],
            status,
        ])

    return response
