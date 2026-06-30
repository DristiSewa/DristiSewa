function openProfile(name, email, phone, country) {
    document.getElementById('modalName').innerText = name;
    document.getElementById('modalEmail').innerText = email;
    document.getElementById('modalPhone').innerText = phone;
    document.getElementById('modalCountry').innerText = country;

    const initials = name.split(' ').map(n => n[0]).join('').toUpperCase();
    document.getElementById('modalInitials').innerText = initials;

    const modal = document.getElementById('profileModal');
    modal.classList.remove('hidden');
}

function closeProfile() {
    document.getElementById('profileModal').classList.add('hidden');
}

window.onclick = function(event) {
    const modal = document.getElementById('profileModal');
    if (event.target === modal) {
        closeProfile();
    }
};
