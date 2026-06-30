const chartFont = { family: 'ui-sans-serif, system-ui, sans-serif' };
Chart.defaults.font.family = chartFont.family;
Chart.defaults.color = '#64748b';

// Student Growth Trend
new Chart(document.getElementById('studentTrendChart').getContext('2d'), {
    type: 'line',
    data: {
        labels: {{ trend_labels|safe }},
        datasets: [{
            label: 'Student Count',
            data: {{ student_trend|safe }},
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
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, grid: { color: '#f1f5f9' } }, x: { grid: { display: false } } }
    }
});

// Application Status Distribution
new Chart(document.getElementById('applicationStatusChart').getContext('2d'), {
    type: 'doughnut',
    data: {
        labels: Object.keys({{ application_status|safe }}),
        datasets: [{
            data: Object.values({{ application_status|safe }}),
            backgroundColor: ['#2563eb', '#38bdf8', '#f59e0b', '#10b981', '#f43f5e', '#94a3b8'],
            borderWidth: 0,
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom', labels: { boxWidth: 12, padding: 16 } } }
    }
});

// Document Status Distribution
new Chart(document.getElementById('documentStatusChart').getContext('2d'), {
    type: 'bar',
    data: {
        labels: Object.keys({{ document_status|safe }}),
        datasets: [{
            label: 'Document Count',
            data: Object.values({{ document_status|safe }}),
            backgroundColor: ['#f59e0b', '#10b981', '#f43f5e'],
            borderRadius: 6,
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: 'y',
        plugins: { legend: { display: false } },
        scales: { x: { beginAtZero: true, grid: { color: '#f1f5f9' } }, y: { grid: { display: false } } }
    }
});

// Visa Grant Trend
new Chart(document.getElementById('visaTrendChart').getContext('2d'), {
    type: 'line',
    data: {
        labels: {{ trend_labels|safe }},
        datasets: [{
            label: 'Visas Granted',
            data: {{ visa_trend|safe }},
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
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, grid: { color: '#f1f5f9' } }, x: { grid: { display: false } } }
    }
});
