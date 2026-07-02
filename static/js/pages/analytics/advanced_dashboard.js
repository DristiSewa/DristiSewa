Chart.defaults.font.family = 'ui-sans-serif, system-ui, sans-serif';
Chart.defaults.color = '#64748b';

// Student Growth Trend
new Chart(document.getElementById('studentTrendChart').getContext('2d'), {
    type: 'line',
    data: {
        labels: TREND_LABELS,
        datasets: [{
            label: 'New Students',
            data: STUDENT_TREND,
            borderColor: '#2563eb',
            backgroundColor: 'rgba(37, 99, 235, 0.08)',
            tension: 0.4,
            fill: true,
            pointRadius: 3,
            pointBackgroundColor: '#2563eb',
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: { callbacks: { label: ctx => ` ${ctx.parsed.y} students` } }
        },
        scales: {
            y: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: '#f1f5f9' } },
            x: { grid: { display: false } }
        }
    }
});

// Application Status Distribution
new Chart(document.getElementById('applicationStatusChart').getContext('2d'), {
    type: 'doughnut',
    data: {
        labels: Object.keys(APP_STATUS),
        datasets: [{
            data: Object.values(APP_STATUS),
            backgroundColor: ['#2563eb', '#38bdf8', '#f59e0b', '#10b981', '#f43f5e', '#94a3b8'],
            borderWidth: 2,
            borderColor: '#fff',
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { position: 'bottom', labels: { boxWidth: 12, padding: 16 } },
            tooltip: { callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed}` } }
        }
    }
});

// Document Status Overview
new Chart(document.getElementById('documentStatusChart').getContext('2d'), {
    type: 'bar',
    data: {
        labels: Object.keys(DOC_STATUS),
        datasets: [{
            label: 'Documents',
            data: Object.values(DOC_STATUS),
            backgroundColor: ['#f59e0b', '#10b981', '#f43f5e'],
            borderRadius: 8,
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: 'y',
        plugins: {
            legend: { display: false },
            tooltip: { callbacks: { label: ctx => ` ${ctx.parsed.x} documents` } }
        },
        scales: {
            x: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: '#f1f5f9' } },
            y: { grid: { display: false } }
        }
    }
});

// Visa Grants Trend
new Chart(document.getElementById('visaTrendChart').getContext('2d'), {
    type: 'line',
    data: {
        labels: TREND_LABELS,
        datasets: [{
            label: 'Visas Granted',
            data: VISA_TREND,
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.12)',
            tension: 0.4,
            fill: true,
            pointRadius: 3,
            pointBackgroundColor: '#10b981',
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: { callbacks: { label: ctx => ` ${ctx.parsed.y} visas granted` } }
        },
        scales: {
            y: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: '#f1f5f9' } },
            x: { grid: { display: false } }
        }
    }
});
