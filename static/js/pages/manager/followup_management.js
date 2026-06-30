(function () {
    const searchInput = document.getElementById('studentSearch');
    const sortFilter  = document.getElementById('sortFilter');
    const rows        = Array.from(document.querySelectorAll('#tableBody tr'));
    const counter     = document.getElementById('counter');
    const total       = {{ total }};

    function applyFilters() {
        const q      = searchInput.value.toLowerCase().trim();
        const filter = sortFilter.value;
        let shown = 0;

        rows.forEach(row => {
            const nameMatch  = row.dataset.name.includes(q);
            const phoneMatch = row.dataset.phone.includes(q);
            const label      = row.dataset.label;

            let filterMatch = true;
            if (filter === 'today')    filterMatch = label === 'today';
            if (filter === 'upcoming') filterMatch = label === 'upcoming';
            if (filter === 'overdue')  filterMatch = label === 'overdue';

            const visible = (nameMatch || phoneMatch) && filterMatch;
            row.style.display = visible ? '' : 'none';
            if (visible) shown++;
        });

        counter.textContent = `Showing ${shown} of ${total} entries`;
    }

    searchInput.addEventListener('keyup', applyFilters);
    sortFilter.addEventListener('change', applyFilters);
})();
