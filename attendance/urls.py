"""
URL configuration for the attendance app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Student Management
    path('students/', views.student_list, name='student_list'),
    path('students/add/', views.student_add, name='student_add'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('students/<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),
    path('students/<int:pk>/attendance/', views.student_attendance_history, name='student_attendance_history'),

    # Attendance
    path('attendance/mark/', views.mark_attendance, name='mark_attendance'),

    # Reports
    path('reports/', views.attendance_reports, name='attendance_reports'),
    path('reports/export/', views.export_attendance_csv, name='export_csv'),
]
