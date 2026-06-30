const today = new Date().toISOString().split('T')[0];
const tomorrowDate = new Date();
tomorrowDate.setDate(tomorrowDate.getDate() + 1);
const tomorrow = tomorrowDate.toISOString().split('T')[0];

function filterData() {
    const query = document.getElementById('studentSearch').value.toLowerCase();
    const filter = document.getElementById('sortFilter').value;
    const rows = document.querySelectorAll('#tableBody tr[data-name]');
    let visible = 0;

    rows.forEach(row => {
        const name = row.getAttribute('data-name') || '';
        const phone = row.getAttribute('data-phone') || '';
        const followup = row.getAttribute('data-followup') || '';

        const searchMatch = name.includes(query) || phone.includes(query);
        let filterMatch = true;
        if (filter === 'today') filterMatch = (followup === today);
        if (filter === 'upcoming') filterMatch = (followup === tomorrow);
        if (filter === 'overdue') filterMatch = (followup !== '' && followup < today);

        const show = searchMatch && filterMatch;
        row.style.display = show ? '' : 'none';
        if (show) visible++;
    });

    document.getElementById('counter').innerText = `Showing ${visible} of ${rows.length} entries`;
}

window.onload = filterData;
