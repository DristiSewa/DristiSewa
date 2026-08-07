function openDeletePrompt(deleteUrl, targetName) {
        const modal = document.getElementById('deleteModalWrapper');
        document.getElementById('deleteModalTargetName').textContent = `'${targetName}'`;
        document.getElementById('deleteModalConfirmButton').setAttribute('href', deleteUrl);
        modal.classList.remove('hidden');
        modal.classList.add('flex');
    }

    function closeDeletePrompt() {
        const modal = document.getElementById('deleteModalWrapper');
        modal.classList.remove('flex');
        modal.classList.add('hidden');
    }

    function toggleBranchDrawer() {
        const drawer = document.getElementById('branchDrawer');
        const overlay = document.getElementById('drawerOverlay');
        
        if (drawer.classList.contains('translate-x-full')) {
            overlay.classList.remove('hidden');
            setTimeout(() => { overlay.classList.remove('opacity-0'); }, 10);
            drawer.classList.remove('translate-x-full');
        } else {
            drawer.classList.add('translate-x-full');
            overlay.classList.add('opacity-0');
            setTimeout(() => { overlay.classList.add('hidden'); }, 300);
        }
    }

    function togglePasswordVisibility() {
        const passwordInput = document.querySelector('#branchDrawer input[type="password"]');
        const eyeIcon = document.getElementById('passwordEyeIcon');
        
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            eyeIcon.classList.replace('fa-regular', 'fa-solid');
        } else {
            passwordInput.type = 'password';
            eyeIcon.classList.replace('fa-solid', 'fa-regular');
        }
    }

    function openCreateBranchDrawer() {
        const drawer = document.getElementById('branchDrawer');
        const form = document.getElementById('staffDrawerForm');
        const submitBtn = document.getElementById('drawerSubmitBtn');

        form.reset();
        form.action = CREATE_BRANCH_URL;
        drawer.classList.remove('h-full', 'bg-slate-50');
        drawer.classList.add('h-auto', 'rounded-bl-3xl', 'bg-white');
        form.classList.remove('h-full');
        form.classList.add('h-auto');
        document.getElementById('staffDrawerFields').classList.add('hidden');
        document.getElementById('branchCreateFields').classList.remove('hidden');
        document.getElementById('branchCreateFields').classList.add('flex');
        document.getElementById('drawerTitle').textContent = 'Create New Branch';
        document.getElementById('drawerHelpText').textContent = '';
        document.getElementById('drawerHelpText').classList.add('hidden');
        document.getElementById('createBranchError').classList.add('hidden');
        submitBtn.type = 'button';
        submitBtn.onclick = submitNewBranch;
        if (!form.dataset.branchCreateListenerAttached) {
            form.addEventListener('submit', event => {
                if (!document.getElementById('branchCreateFields').classList.contains('hidden')) {
                    submitNewBranch(event);
                }
            });
            form.dataset.branchCreateListenerAttached = '1';
        }
        submitBtn.textContent = 'Save Branch';

        if (drawer.classList.contains('translate-x-full')) {
            toggleBranchDrawer();
        }
        document.getElementById('createBranchName').focus();
    }

    function submitNewBranch(event) {
        if (event && typeof event.preventDefault === 'function') {
            event.preventDefault();
        }

        const nameInput = document.getElementById('createBranchName');
        const locationInput = document.getElementById('createBranchLocation');
        const errorEl = document.getElementById('createBranchError');
        const submitBtn = document.getElementById('drawerSubmitBtn');
        const branchName = nameInput.value.trim();

        if (!branchName) {
            errorEl.textContent = 'Branch name is required.';
            errorEl.classList.remove('hidden');
            nameInput.focus();
            return;
        }

        errorEl.classList.add('hidden');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Saving...';

        const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        if (!csrfTokenElement) {
            errorEl.textContent = 'CSRF token missing. Please refresh the page and try again.';
            errorEl.classList.remove('hidden');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Save Branch';
            return;
        }

        fetch(CREATE_BRANCH_URL, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfTokenElement.value,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                branch_name: branchName,
                location: locationInput.value.trim(),
                is_active: document.getElementById('createBranchIsActive').checked
            })
        })
        .then(async response => {
            const text = await response.text();
            let data;
            try {
                data = JSON.parse(text);
            } catch {
                throw new Error(text || `Server error: ${response.status}`);
            }
            if (!response.ok) {
                throw new Error(data.error || `Request failed with status ${response.status}`);
            }
            if (!data.success) {
                throw new Error(data.error || 'Could not create branch.');
            }
            window.location.href = window.location.pathname;
        })
        .catch(error => {
            errorEl.textContent = error.message || 'Could not create branch.';
            errorEl.classList.remove('hidden');
        })
        .finally(() => {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Save Branch';
        });
    }

    function addBranchToPage(branchId, branchName, address, code) {
        const initials = branchName.slice(0, 2).toUpperCase();

        // 1. Branch overview card
        const cardsGrid = document.getElementById('branchCardsGrid');
        const cardsEmpty = document.getElementById('branchCardsEmpty');
        if (cardsEmpty) cardsEmpty.remove();
        if (cardsGrid) {
            const card = document.createElement('div');
            card.className = 'bg-white p-5 rounded-2xl border border-slate-200 shadow-sm';
            card.setAttribute('data-branch-card', branchId);
            card.innerHTML = `
                <div class="flex items-center gap-3 mb-3.5">
                    <div class="w-9 h-9 bg-blue-50 text-blue-700 rounded-xl flex items-center justify-center font-bold text-xs uppercase shrink-0 branch-card-initials">${initials}</div>
                    <p class="text-base font-bold text-slate-800 truncate flex-1 branch-card-name">${branchName}</p>
                    <button type="button" onclick="openDeleteBranchModal(${branchId}, '${branchName.replace(/'/g, "\\'")}')" class="text-slate-400 hover:text-red-600 transition shrink-0" title="Delete branch">
                        <i class="fa-solid fa-trash-can text-sm"></i>
                    </button>
                </div>
                <div class="flex items-center justify-between gap-3">
                    <div class="flex items-center gap-2.5">
                        <div class="bg-indigo-50 text-indigo-600 p-2.5 rounded-xl"><i class="fa-solid fa-id-badge text-sm"></i></div>
                        <div>
                            <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">Managers</p>
                            <div class="text-xl font-bold text-slate-800">0</div>
                        </div>
                    </div>
                    <div class="flex items-center gap-2.5">
                        <div class="bg-teal-50 text-teal-600 p-2.5 rounded-xl"><i class="fa-solid fa-headset text-sm"></i></div>
                        <div>
                            <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">Front Desk</p>
                            <div class="text-xl font-bold text-slate-800">0</div>
                        </div>
                    </div>
                    <div class="flex items-center gap-2.5">
                        <div class="bg-blue-50 text-blue-600 p-2.5 rounded-xl"><i class="fa-solid fa-graduation-cap text-sm"></i></div>
                        <div>
                            <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">Students</p>
                            <div class="text-xl font-bold text-slate-800">0</div>
                        </div>
                    </div>
                </div>`;
            cardsGrid.appendChild(card);
        }

        // 2. "All Branches" filter dropdown
        const filterSelect = document.getElementById('branchFilterSelect');
        if (filterSelect) {
            const opt = document.createElement('option');
            opt.value = branchId;
            opt.text = branchName;
            filterSelect.add(opt);
        }

        // 3. Branch managers table row
        const tableEmpty = document.getElementById('branchTableEmpty');
        if (tableEmpty) tableEmpty.remove();
        const tbody = document.querySelector('#branchStaffTable tbody');
        if (tbody) {
            const row = document.createElement('tr');
            row.className = 'hover:bg-slate-50/80 transition-colors main-data-row';
            row.setAttribute('data-branch-row', branchId);
            row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center gap-3">
                        <div class="w-9 h-9 bg-blue-50 text-blue-700 rounded-xl flex items-center justify-center font-bold text-xs uppercase branch-row-initials">${initials}</div>
                        <div class="font-semibold text-slate-900 text-base branch-row-name">${branchName}</div>
                        <button type="button" onclick="openDeleteBranchModal(${branchId}, '${branchName.replace(/'/g, "\\'")}')" class="text-slate-400 hover:text-red-600 transition shrink-0" title="Delete branch">
                            <i class="fa-solid fa-trash-can text-xs"></i>
                        </button>
                    </div>
                </td>
                <td class="px-6 py-4 text-base text-slate-600 branch-row-address">${address || '<span class="text-slate-300">—</span>'}</td>
                <td class="px-6 py-4 text-sm text-slate-400 italic" colspan="4">No staff assigned</td>`;
            tbody.appendChild(row);
        }

        // Keep the "Showing X of Y" counter in sync
        const countEl = document.querySelector('#branchStaffTable').closest('.bg-white').querySelector('.px-6.py-4.flex.items-center.justify-between span');
        if (countEl) {
            const match = countEl.textContent.match(/Showing (\d+) of (\d+)/);
            if (match) {
                const shown = parseInt(match[1], 10) + 1;
                const total = parseInt(match[2], 10) + 1;
                countEl.textContent = `Showing ${shown} of ${total} registered branches.`;
            }
        }
    }

    let currentDeleteBranchId = null;
    let currentEditBranchId = null;
    let currentEditBranchIsActive = null;

    function openEditBranchModal(branchId, name, address, isActive) {
        currentEditBranchId = branchId;
        currentEditBranchIsActive = Boolean(isActive);
        document.getElementById('editBranchName').value = name;
        document.getElementById('editBranchLocation').value = address || '';
        document.getElementById('editBranchIsActive').checked = Boolean(isActive);
        const errorEl = document.getElementById('editBranchError');
        errorEl.classList.add('hidden');
        errorEl.textContent = '';
        const modal = document.getElementById('editBranchModalWrapper');
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        document.getElementById('editBranchName').focus();
    }

    function closeEditBranchModal() {
        const modal = document.getElementById('editBranchModalWrapper');
        modal.classList.add('hidden');
        modal.classList.remove('flex');
        currentEditBranchId = null;
        currentEditBranchIsActive = null;
    }

    function submitEditBranch() {
        if (!currentEditBranchId) return;
        const name = document.getElementById('editBranchName').value.trim();
        const location = document.getElementById('editBranchLocation').value.trim();
        const isActive = document.getElementById('editBranchIsActive').checked;
        const errorEl = document.getElementById('editBranchError');
        const saveBtn = document.getElementById('editBranchSaveBtn');
        if (!name) {
            errorEl.textContent = 'Branch name is required.';
            errorEl.classList.remove('hidden');
            return;
        }

        const template = document.getElementById('editBranchModalWrapper').dataset.updateActionTemplate;
        const url = template.replace(/0\/?$/, currentEditBranchId + '/');
        saveBtn.disabled = true;
        saveBtn.textContent = 'Saving...';
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({branch_name: name, location, is_active: isActive})
        })
        .then(response => response.json())
        .then(data => {
            if (!data.success) throw new Error(data.error || 'Failed to update branch.');
            if (data.is_active !== isActive) throw new Error('The branch status could not be updated.');
            // A status change moves the card between active/inactive sections.
            // Reload so counts, filters, and both card collections stay correct.
            if (data.is_active !== currentEditBranchIsActive) {
                window.location.reload();
                return;
            }
            updateBranchOnPage(data.branch_id, data.name, data.address);
            closeEditBranchModal();
        })
        .catch(error => {
            errorEl.textContent = error.message;
            errorEl.classList.remove('hidden');
        })
        .finally(() => {
            saveBtn.disabled = false;
            saveBtn.textContent = 'Save changes';
        });
    }

    function updateBranchOnPage(branchId, name, address) {
        const initials = name.slice(0, 2).toUpperCase();
        document.querySelectorAll(`[data-branch-card="${branchId}"] .branch-card-name`).forEach(el => el.textContent = name);
        document.querySelectorAll(`[data-branch-card="${branchId}"] .branch-card-initials`).forEach(el => el.textContent = initials);
        document.querySelectorAll(`[data-branch-row="${branchId}"] .branch-row-name`).forEach(el => el.textContent = name);
        document.querySelectorAll(`[data-branch-row="${branchId}"] .branch-row-initials`).forEach(el => el.textContent = initials);
        document.querySelectorAll(`[data-branch-row="${branchId}"] .branch-row-address`).forEach(el => el.textContent = address || '—');
        const option = Array.from(document.getElementById('branchFilterSelect').options).find(item => item.value === String(branchId));
        if (option) option.textContent = name;
    }

    function openDeleteBranchModal(branchId, name) {
        currentDeleteBranchId = branchId;
        document.getElementById('deleteBranchModalTargetName').textContent = `'${name}'`;

        const errorEl = document.getElementById('deleteBranchError');
        errorEl.classList.add('hidden');
        errorEl.textContent = '';

        const modal = document.getElementById('deleteBranchModalWrapper');
        modal.classList.remove('hidden');
        modal.classList.add('flex');
    }

    function closeDeleteBranchModal() {
        const modal = document.getElementById('deleteBranchModalWrapper');
        modal.classList.add('hidden');
        modal.classList.remove('flex');
        currentDeleteBranchId = null;
    }

    function submitDeleteBranch() {
        if (!currentDeleteBranchId) return;

        const modal = document.getElementById('deleteBranchModalWrapper');
        const urlTemplate = modal.dataset.deleteActionTemplate;
        const url = urlTemplate.replace(/0\/?$/, currentDeleteBranchId + '/');
        const errorEl = document.getElementById('deleteBranchError');
        const confirmBtn = document.getElementById('deleteBranchConfirmBtn');

        confirmBtn.disabled = true;
        confirmBtn.textContent = 'Deleting...';

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                removeBranchFromPage(data.branch_id);
                closeDeleteBranchModal();
            } else {
                errorEl.textContent = data.error || 'Failed to delete branch.';
                errorEl.classList.remove('hidden');
            }
        })
        .catch(err => {
            console.error(err);
            errorEl.textContent = 'Failed to delete branch.';
            errorEl.classList.remove('hidden');
        })
        .finally(() => {
            confirmBtn.disabled = false;
            confirmBtn.textContent = 'Delete';
        });
    }

    function removeBranchFromPage(branchId) {
        // Remove card
        const card = document.querySelector(`[data-branch-card="${branchId}"]`);
        if (card) card.remove();

        // Remove filter dropdown option
        const filterSelect = document.getElementById('branchFilterSelect');
        if (filterSelect) {
            const opt = Array.from(filterSelect.options).find(o => o.value === String(branchId));
            if (opt) opt.remove();
        }

        // Remove table row(s)
        document.querySelectorAll(`[data-branch-row="${branchId}"]`).forEach(row => row.remove());

        // Keep the "Showing X of Y" counter in sync
        const countEl = document.querySelector('#branchStaffTable')?.closest('.bg-white').querySelector('.px-6.py-4.flex.items-center.justify-between span');
        if (countEl) {
            const match = countEl.textContent.match(/Showing (\d+) of (\d+)/);
            if (match) {
                const shown = Math.max(0, parseInt(match[1], 10) - 1);
                const total = Math.max(0, parseInt(match[2], 10) - 1);
                countEl.textContent = `Showing ${shown} of ${total} registered branches.`;
            }
        }

        // Show empty states if nothing left
        const cardsGrid = document.getElementById('branchCardsGrid');
        if (cardsGrid && !cardsGrid.querySelector('[data-branch-card]')) {
            const emptyCard = document.createElement('div');
            emptyCard.id = 'branchCardsEmpty';
            emptyCard.className = 'col-span-full text-center text-sm text-slate-400 py-10';
            emptyCard.textContent = 'No active branches found.';
            cardsGrid.appendChild(emptyCard);
        }

        const tbody = document.querySelector('#branchStaffTable tbody');
        if (tbody && !tbody.querySelector('[data-branch-row]')) {
            const emptyRow = document.createElement('tr');
            emptyRow.id = 'branchTableEmpty';
            emptyRow.innerHTML = `<td colspan="5" class="px-6 py-10 text-center text-sm text-slate-500">No active branches found.</td>`;
            tbody.appendChild(emptyRow);
        }
    }

    function resetDrawerToCreateMode() {
        const drawer = document.getElementById('branchDrawer');
        const form = document.getElementById('staffDrawerForm');

        form.action = drawer.dataset.createAction;
        drawer.classList.remove('h-auto', 'rounded-bl-3xl', 'bg-slate-50');
        drawer.classList.add('h-full', 'bg-white');
        form.classList.remove('h-auto');
        form.classList.add('h-full');
        document.getElementById('drawerTitle').textContent = 'Create Staff Account';
        document.getElementById('drawerSubmitBtn').textContent = 'Save Account';
        document.getElementById('drawerHelpText').textContent = 'Configure access credentials to instantiate the branch manager profile layout.';
        document.getElementById('drawerHelpText').classList.remove('hidden');
        document.getElementById('branchCreateFields').classList.add('hidden');
        document.getElementById('branchCreateFields').classList.remove('flex');
        document.getElementById('staffDrawerFields').classList.remove('hidden');
        document.getElementById('drawerSubmitBtn').type = 'submit';
        document.getElementById('drawerSubmitBtn').onclick = null;

        form.reset();

        const passwordField = document.getElementById('id_password');
        if (passwordField) {
            passwordField.required = true;
            passwordField.placeholder = '';
        }
    }

    function filterManagerTable() {
        const filter = document.getElementById('managerSearchInput').value.trim().toUpperCase();
        const rows = document.querySelectorAll('#branchStaffTable tbody tr.main-data-row');

        rows.forEach(row => {
            const text = row.textContent.toUpperCase();
            row.style.display = text.includes(filter) ? '' : 'none';
        });
    }

    function sortManagerTable(colIndex, header) {
        const table = document.getElementById('branchStaffTable');
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr.main-data-row'));
        if (!rows.length) return;

        const currentDir = header.getAttribute('data-sort-dir') === 'asc' ? 'desc' : 'asc';

        table.querySelectorAll('thead th[data-sort-dir]').forEach(th => {
            th.removeAttribute('data-sort-dir');
            const icon = th.querySelector('i');
            if (icon) icon.className = 'fa-solid fa-sort text-[10px] text-slate-300 ml-1';
        });
        header.setAttribute('data-sort-dir', currentDir);
        const headerIcon = header.querySelector('i');
        if (headerIcon) {
            headerIcon.className = currentDir === 'asc'
                ? 'fa-solid fa-sort-up text-[10px] text-blue-600 ml-1'
                : 'fa-solid fa-sort-down text-[10px] text-blue-600 ml-1';
        }

        rows.sort((a, b) => {
            const aText = a.cells[colIndex].textContent.trim().toUpperCase();
            const bText = b.cells[colIndex].textContent.trim().toUpperCase();
            if (aText < bText) return currentDir === 'asc' ? -1 : 1;
            if (aText > bText) return currentDir === 'asc' ? 1 : -1;
            return 0;
        });

        rows.forEach(row => tbody.appendChild(row));
    }

    function openAddManagerDrawer(branchId) {
        resetDrawerToCreateMode();

        const branchSelect = document.querySelector('#branchSelectWrapper select');
        const roleSelect = document.getElementById('id_role');

        if (branchSelect) branchSelect.value = String(branchId);
        if (roleSelect) roleSelect.value = 'MANAGER';

        const drawer = document.getElementById('branchDrawer');
        if (drawer.classList.contains('translate-x-full')) {
            toggleBranchDrawer();
        }
    }

    function openEditManagerDrawer(userId, firstName, lastName, email, branchId, experienceDetails) {
        const drawer = document.getElementById('branchDrawer');
        const form = document.getElementById('staffDrawerForm');

        form.reset();
        drawer.classList.remove('h-auto', 'rounded-bl-3xl', 'bg-slate-50');
        drawer.classList.add('h-full', 'bg-white');
        form.classList.remove('h-auto');
        form.classList.add('h-full');
        document.getElementById('branchCreateFields').classList.add('hidden');
        document.getElementById('branchCreateFields').classList.remove('flex');
        document.getElementById('staffDrawerFields').classList.remove('hidden');
        document.getElementById('drawerHelpText').classList.remove('hidden');
        document.getElementById('drawerSubmitBtn').type = 'submit';
        document.getElementById('drawerSubmitBtn').onclick = null;
        form.action = drawer.dataset.updateActionTemplate.replace(/0\/update\/?$/, userId + '/update/');

        document.getElementById('drawerTitle').textContent = 'Edit Manager Account';
        document.getElementById('drawerSubmitBtn').textContent = 'Update Account';
        document.getElementById('drawerHelpText').textContent = 'Update this manager\'s profile, branch assignment, and access details.';

        const firstNameField = document.getElementById('id_first_name');
        const lastNameField = document.getElementById('id_last_name');
        const emailField = document.getElementById('id_email');
        const roleSelect = document.getElementById('id_role');
        const branchSelect = document.querySelector('#branchSelectWrapper select');
        const experienceField = document.getElementById('id_experience_details');
        const passwordField = document.getElementById('id_password');

        if (firstNameField) firstNameField.value = firstName;
        if (lastNameField) lastNameField.value = lastName;
        if (emailField) emailField.value = email;
        if (roleSelect) roleSelect.value = 'MANAGER';
        if (branchSelect) branchSelect.value = String(branchId);
        if (experienceField) experienceField.value = experienceDetails;
        if (passwordField) {
            passwordField.value = '';
            passwordField.required = false;
            passwordField.placeholder = 'Leave blank to keep current password';
        }

        if (drawer.classList.contains('translate-x-full')) {
            toggleBranchDrawer();
        }
    }

    function reactivateBranch(btn) {
        const url     = btn.dataset.reactivateUrl;
        const name    = btn.dataset.branchName;
        let   code    = btn.dataset.branchCode;
        const address = btn.dataset.branchAddress;
        const phone   = btn.dataset.branchPhone;
        const email   = btn.dataset.branchEmail;

        if (!code) {
            code = name.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 8) || 'BR';
        }

        btn.disabled = true;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Reactivating…';

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({ name, code, address, phone, email, is_active: true })
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                btn.disabled = false;
                btn.innerHTML = '<i class="fa-solid fa-rotate-right"></i> Reactivate';
                alert(data.error || 'Failed to reactivate branch.');
            }
        })
        .catch(() => {
            btn.disabled = false;
            btn.innerHTML = '<i class="fa-solid fa-rotate-right"></i> Reactivate';
            alert('Network error — could not reactivate branch.');
        });
    }

    window.addEventListener('DOMContentLoaded', () => {
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('openDrawer') === 'true') { toggleBranchDrawer(); }
    });
