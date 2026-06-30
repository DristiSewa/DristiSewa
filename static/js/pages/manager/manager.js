document.addEventListener('DOMContentLoaded', () => {
    initFrontDeskStaffModal();
});

/* ==========================================================================
   FRONT DESK STAFF MODALS
   ========================================================================== */
function initFrontDeskStaffModal() {
    const staffModal  = document.getElementById('staffFormModal');
    const deleteModal = document.getElementById('deleteConfirmModal');

    if (!staffModal || !deleteModal) return;

    const modalTitle        = document.getElementById('modalTitle');
    const modalSubmitBtn    = document.getElementById('modalSubmitBtn');
    const passwordLabel     = document.getElementById('passwordLabel');
    const nameInput         = document.getElementById('staff_name');
    const emailInput        = document.getElementById('staff_email');
    const passwordInput     = document.getElementById('staff_password');
    const deleteTargetName  = document.getElementById('deleteTargetName');
    const formActionInput   = document.getElementById('form_action');
    const staffIdInput      = document.getElementById('staff_id');
    const deleteStaffIdInput = document.getElementById('delete_staff_id');

    if (!modalTitle || !modalSubmitBtn || !passwordLabel ||
        !nameInput || !emailInput || !passwordInput || !deleteTargetName) return;

    function openCreateModal() {
        modalTitle.innerText     = "Create Front Desk Staff";
        modalSubmitBtn.innerText = "Create Staff Account";
        passwordLabel.innerText  = "Account Password";
        nameInput.value     = "";
        emailInput.value    = "";
        passwordInput.value = "";
        passwordInput.required = true;
        if (formActionInput) formActionInput.value = "create";
        if (staffIdInput) staffIdInput.value = "";
        staffModal.style.display = 'flex';
    }

    function openEditModal(name, email, staffId) {
        modalTitle.innerText     = `Edit Front Desk: ${name}`;
        modalSubmitBtn.innerText = "Update Account Details";
        passwordLabel.innerText  = "New Password (leave blank to keep current)";
        nameInput.value     = name;
        emailInput.value    = email || "";
        passwordInput.value = "";
        passwordInput.required = false;
        if (formActionInput) formActionInput.value = "edit";
        if (staffIdInput) staffIdInput.value = staffId || "";
        staffModal.style.display = 'flex';
    }

    function openDeleteModal(name, staffId) {
        deleteTargetName.innerText = `"${name}"`;
        if (deleteStaffIdInput) deleteStaffIdInput.value = staffId || "";
        deleteModal.style.display  = 'flex';
    }

    function closeAllModals() {
        staffModal.style.display  = 'none';
        deleteModal.style.display = 'none';
    }

    document.getElementById('openCreateStaffModalBtn')?.addEventListener('click', openCreateModal);

    document.querySelectorAll('.btn-action-edit').forEach(btn => {
        btn.addEventListener('click', () => openEditModal(btn.dataset.staffName, btn.dataset.staffEmail, btn.dataset.staffId));
    });

    document.querySelectorAll('.btn-action-delete').forEach(btn => {
        btn.addEventListener('click', () => openDeleteModal(btn.dataset.staffName, btn.dataset.staffId));
    });

    document.getElementById('closeStaffModalBtn')?.addEventListener('click', closeAllModals);
    document.getElementById('cancelStaffModalBtn')?.addEventListener('click', closeAllModals);
    document.getElementById('closeDeleteModalBtn')?.addEventListener('click', closeAllModals);
    document.getElementById('cancelDeleteModalBtn')?.addEventListener('click', closeAllModals);

    window.addEventListener('click', e => {
        if (e.target === staffModal || e.target === deleteModal) closeAllModals();
    });

    window.openCreateModal = openCreateModal;
    window.openEditModal   = openEditModal;
    window.openDeleteModal = openDeleteModal;
    window.closeAllModals  = closeAllModals;
}
