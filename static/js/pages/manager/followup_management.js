(function () {
    const searchInput = document.getElementById('studentSearch');
    const sortFilter  = document.getElementById('sortFilter');
    const tbody       = document.getElementById('tableBody');
    const rows        = Array.from(tbody.querySelectorAll('tr'));
    const counter     = document.getElementById('counter');
    const total       = rows.length;

    function applyFilters() {
        const q      = searchInput.value.toLowerCase().trim();
        const filter = sortFilter.value;

        // Split query into words for multi-word matching
        const words = q ? q.split(/\s+/) : [];

        // Partition rows into: starts-with matches, contains matches, hidden
        const startsWith = [];
        const contains   = [];

        rows.forEach(row => {
            const name  = row.dataset.name  || '';
            const phone = row.dataset.phone || '';
            const label = row.dataset.label || '';

            // Date filter
            let filterMatch = true;
            if (filter === 'today')    filterMatch = label === 'today';
            if (filter === 'upcoming') filterMatch = label === 'upcoming';
            if (filter === 'overdue')  filterMatch = label === 'overdue';

            if (!filterMatch) {
                row.style.display = 'none';
                return;
            }

            if (!q) {
                row.style.display = '';
                startsWith.push(row);
                return;
            }

            // Every word must match name or phone
            const textMatch = words.every(w => name.includes(w) || phone.includes(w));

            if (!textMatch) {
                row.style.display = 'none';
                return;
            }

            row.style.display = '';

            // Typeahead: name starts with first word → higher priority
            if (name.startsWith(words[0])) {
                startsWith.push(row);
            } else {
                contains.push(row);
            }
        });

        // Re-order DOM: starts-with first, then contains
        [...startsWith, ...contains].forEach(row => tbody.appendChild(row));

        const shown = startsWith.length + contains.length;
        counter.textContent = `Showing ${shown} of ${total} entries`;
    }

    searchInput.addEventListener('input', applyFilters);
    sortFilter.addEventListener('change', applyFilters);
})();
