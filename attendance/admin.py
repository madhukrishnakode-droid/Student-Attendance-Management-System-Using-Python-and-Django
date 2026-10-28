"""
Admin configuration for Student Attendance Management System.
"""
from django.contrib import admin
from .models import Student, Attendance


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'full_name', 'department', 'get_year_of_study_display', 'created_at')
    list_filter = ('department', 'year_of_study')
    search_fields = ('roll_number', 'full_name')
    ordering = ('department', 'year_of_study', 'roll_number')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Student Information', {
            'fields': ('roll_number', 'full_name', 'department', 'year_of_study')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status', 'marked_at')
    list_filter = ('status', 'date', 'student__department')
    search_fields = ('student__roll_number', 'student__full_name')
    date_hierarchy = 'date'
    ordering = ('-date', 'student__roll_number')
    readonly_fields = ('marked_at', 'updated_at')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student')
