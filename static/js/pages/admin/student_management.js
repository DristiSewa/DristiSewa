function filterStatus(element, status) {
        // Clear active classes from sibling tab filters
        const buttons = document.querySelectorAll('.tab-btn');
        buttons.forEach(btn => {
            btn.classList.remove('bg-white', 'text-blue-700', 'shadow-sm');
            btn.classList.add('text-slate-500', 'hover:text-slate-800');
        });

        // Add active classes to selected tab element
        element.classList.remove('text-slate-500', 'hover:text-slate-800');
        element.classList.add('bg-white', 'text-blue-700', 'shadow-sm');

        // Filter table rows by follow-up status
        document.querySelectorAll('tbody tr[data-status]').forEach(row => {
            row.style.display = (status === 'all' || row.getAttribute('data-status') === status) ? '' : 'none';
        });
    }
