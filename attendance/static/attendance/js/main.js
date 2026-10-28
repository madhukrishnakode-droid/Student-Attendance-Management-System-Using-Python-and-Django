/**
 * Student Attendance Management System - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function () {

    // ── Sidebar toggle (mobile) ───────────────────────
    const toggleBtn = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.getElementById('sidebarOverlay');

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', function () {
            sidebar.classList.toggle('mobile-open');
            if (overlay) overlay.style.display = sidebar.classList.contains('mobile-open') ? 'block' : 'none';
        });
    }
    if (overlay) {
        overlay.addEventListener('click', function () {
            sidebar.classList.remove('mobile-open');
            overlay.style.display = 'none';
        });
    }

    // ── Highlight active nav link ─────────────────────
    const currentPath = window.location.pathname;
    document.querySelectorAll('.sidebar-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // ── Password show/hide ────────────────────────────
    const togglePasswordBtn = document.getElementById('togglePassword');
    const passwordField = document.getElementById('id_password');
    if (togglePasswordBtn && passwordField) {
        togglePasswordBtn.addEventListener('click', function () {
            const isText = passwordField.type === 'text';
            passwordField.type = isText ? 'password' : 'text';
            this.querySelector('i').classList.toggle('bi-eye', isText);
            this.querySelector('i').classList.toggle('bi-eye-slash', !isText);
        });
    }

    // ── Confirm delete ────────────────────────────────
    document.querySelectorAll('[data-confirm]').forEach(function (el) {
        el.addEventListener('click', function (e) {
            const msg = this.getAttribute('data-confirm') || 'Are you sure?';
            if (!confirm(msg)) {
                e.preventDefault();
            }
        });
    });

    // ── Auto-dismiss alerts ───────────────────────────
    setTimeout(function () {
        document.querySelectorAll('.alert.auto-dismiss').forEach(function (alert) {
            if (typeof bootstrap !== 'undefined') {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        });
    }, 4000);

    // ── Attendance row highlight on radio change ──────
    document.querySelectorAll('.att-radio-group input[type=radio]').forEach(function (radio) {
        radio.addEventListener('change', function () {
            const row = this.closest('tr');
            if (!row) return;
            row.classList.remove('att-row-present', 'att-row-absent');
            if (this.value === 'P') {
                row.classList.add('att-row-present');
            } else if (this.value === 'A') {
                row.classList.add('att-row-absent');
            }
        });
        // Colour existing status on page load
        if (radio.checked) radio.dispatchEvent(new Event('change'));
    });

    // ── Attendance - Mark all present / absent ────────
    const markAllPresent = document.getElementById('markAllPresent');
    const markAllAbsent  = document.getElementById('markAllAbsent');

    if (markAllPresent) {
        markAllPresent.addEventListener('click', function () {
            document.querySelectorAll('input.present-radio').forEach(r => { r.checked = true; r.dispatchEvent(new Event('change')); });
        });
    }
    if (markAllAbsent) {
        markAllAbsent.addEventListener('click', function () {
            document.querySelectorAll('input.absent-radio').forEach(r => { r.checked = true; r.dispatchEvent(new Event('change')); });
        });
    }

    // ── Update summary counter on attendance page ─────
    function updateAttendanceSummary() {
        const total = document.querySelectorAll('input.present-radio').length;
        const present = document.querySelectorAll('input.present-radio:checked').length;
        const absent  = document.querySelectorAll('input.absent-radio:checked').length;
        const unmarked = total - present - absent;

        const el = document.getElementById('att-live-summary');
        if (el) {
            el.innerHTML = `<span class="text-success fw-600">${present} Present</span> &nbsp;|&nbsp; ` +
                           `<span class="text-danger fw-600">${absent} Absent</span> &nbsp;|&nbsp; ` +
                           `<span class="text-muted">${unmarked} Unmarked</span>`;
        }
    }
    document.querySelectorAll('.att-radio-group input[type=radio]').forEach(r => {
        r.addEventListener('change', updateAttendanceSummary);
    });
    updateAttendanceSummary();

    // ── Search filter table (client side quick filter) ──
    const tableSearch = document.getElementById('tableSearch');
    if (tableSearch) {
        tableSearch.addEventListener('input', function () {
            const q = this.value.toLowerCase();
            document.querySelectorAll('.filterable-row').forEach(function (row) {
                row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
            });
        });
    }

});
