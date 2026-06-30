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

    function toggleQuickBranchForm() {
        const container = document.getElementById('quickBranchContainer');
        container.classList.toggle('hidden');
        if (!container.classList.contains('hidden')) {
            document.getElementById('quickBranchName').focus();
        }
    }

    function submitQuickBranch() {
        const nameInput = document.getElementById('quickBranchName');
        const locInput = document.getElementById('quickBranchLocation');
        const branchName = nameInput.value.trim();
        const location = locInput.value.trim();

        if (!branchName || !location) {
            alert('Please fill out both Branch Name and Location fields.');
            return;
        }

        fetch(CREATE_BRANCH_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({ 'branch_name': branchName, 'location': location })
        })
        .then(response => {
            if (!response.ok) throw new Error('Network error setup.');
            return response.json();
        })
        .then(data => {
            if (data.success) {
                const selectElement = document.querySelector('#branchSelectWrapper select');
                if (selectElement) {
                    const newOption = document.createElement('option');
                    newOption.value = data.branch_id;
                    newOption.text = `${branchName} (${location})`;
                    newOption.selected = true;
                    selectElement.add(newOption);
                }

                addBranchToPage(data.branch_id, data.name, data.address || location, data.code);

                nameInput.value = '';
                locInput.value = '';
                toggleQuickBranchForm();
            } else {
                alert('Error creating branch: ' + (data.error || 'Unknown event.'));
            }
        })
        .catch(err => {
            console.error(err);
            alert('Failed to save branch configuration record.');
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
                    <button type="button" onclick="openEditBranchModal(${branchId}, '${branchName.replace(/'/g, "\\'")}', '${(code || '').replace(/'/g, "\\'")}', '${(address || '').replace(/'/g, "\\'")}', '', '', true)" class="text-slate-400 hover:text-blue-600 transition shrink-0" title="Edit branch">
                        <i class="fa-solid fa-pen-to-square text-sm"></i>
                    </button>
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
                        <button type="button" onclick="openEditBranchModal(${branchId}, '${branchName.replace(/'/g, "\\'")}', '${(code || '').replace(/'/g, "\\'")}', '${(address || '').replace(/'/g, "\\'")}', '', '', true)" class="text-slate-400 hover:text-blue-600 transition shrink-0" title="Edit branch">
                            <i class="fa-solid fa-pen-to-square text-xs"></i>
                        </button>
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

    let currentEditBranchId = null;

    function openEditBranchModal(branchId, name, code, address, phone, email, isActive) {
        currentEditBranchId = branchId;
        document.getElementById('editBranchName').value = name || '';
        document.getElementById('editBranchCode').value = code || '';
        document.getElementById('editBranchAddress').value = address || '';
        document.getElementById('editBranchPhone').value = phone || '';
        document.getElementById('editBranchEmail').value = email || '';
        document.getElementById('editBranchActive').checked = !!isActive;

        const errorEl = document.getElementById('editBranchError');
        errorEl.classList.add('hidden');
        errorEl.textContent = '';

        const modal = document.getElementById('editBranchModalWrapper');
        modal.classList.remove('hidden');
        modal.classList.add('flex');
    }

    function closeEditBranchModal() {
        const modal = document.getElementById('editBranchModalWrapper');
        modal.classList.add('hidden');
        modal.classList.remove('flex');
        currentEditBranchId = null;
    }

    function submitEditBranch() {
        if (!currentEditBranchId) return;

        const name = document.getElementById('editBranchName').value.trim();
        let code = document.getElementById('editBranchCode').value.trim();
        const address = document.getElementById('editBranchAddress').value.trim();
        const phone = document.getElementById('editBranchPhone').value.trim();
        const email = document.getElementById('editBranchEmail').value.trim();
        const isActive = document.getElementById('editBranchActive').checked;
        const errorEl = document.getElementById('editBranchError');

        if (!name) {
            errorEl.textContent = 'Branch name is required.';
            errorEl.classList.remove('hidden');
            return;
        }

        // Auto-generate a code from the name if it's missing
        if (!code) {
            code = name.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 8) || 'BR';
        }

        const modal = document.getElementById('editBranchModalWrapper');
        const urlTemplate = modal.dataset.updateActionTemplate;
        const url = urlTemplate.replace(/0\/?$/, currentEditBranchId + '/');

        const saveBtn = document.getElementById('editBranchSaveBtn');
        saveBtn.disabled = true;
        saveBtn.textContent = 'Saving...';

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({ name, code, address, phone, email, is_active: isActive })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateBranchOnPage(data);
                closeEditBranchModal();
            } else {
                errorEl.textContent = data.error || 'Failed to update branch.';
                errorEl.classList.remove('hidden');
            }
        })
        .catch(err => {
            console.error(err);
            errorEl.textContent = 'Failed to save branch changes.';
            errorEl.classList.remove('hidden');
        })
        .finally(() => {
            saveBtn.disabled = false;
            saveBtn.textContent = 'Save Changes';
        });
    }

    function updateBranchOnPage(data) {
        const initials = data.name.slice(0, 2).toUpperCase();

        // Update card
        const card = document.querySelector(`[data-branch-card="${data.branch_id}"]`);
        if (card) {
            const nameEl = card.querySelector('.branch-card-name');
            const initialsEl = card.querySelector('.branch-card-initials');
            if (nameEl) nameEl.textContent = data.name;
            if (initialsEl) initialsEl.textContent = initials;
        }

        // Update filter dropdown option
        const filterSelect = document.getElementById('branchFilterSelect');
        if (filterSelect) {
            const opt = Array.from(filterSelect.options).find(o => o.value === String(data.branch_id));
            if (opt) opt.text = data.name;
        }

        // Update table row(s)
        document.querySelectorAll(`[data-branch-row="${data.branch_id}"]`).forEach(row => {
            const nameEl = row.querySelector('.branch-row-name');
            const initialsEl = row.querySelector('.branch-row-initials');
            const addressEl = row.querySelector('.branch-row-address');
            if (nameEl) nameEl.textContent = data.name;
            if (initialsEl) initialsEl.textContent = initials;
            if (addressEl) addressEl.innerHTML = data.address || '<span class="text-slate-300">—</span>';
        });

        // Sync card edit/delete buttons too
        if (card) {
            const editBtn = card.querySelector('button[onclick^="openEditBranchModal"]');
            if (editBtn) {
                editBtn.setAttribute('onclick', `openEditBranchModal(${data.branch_id}, '${data.name.replace(/'/g, "\\'")}', '${data.code.replace(/'/g, "\\'")}', '${(data.address || '').replace(/'/g, "\\'")}', '${(data.phone || '').replace(/'/g, "\\'")}', '${(data.email || '').replace(/'/g, "\\'")}', ${data.is_active})`);
            }
            const deleteBtn = card.querySelector('button[onclick^="openDeleteBranchModal"]');
            if (deleteBtn) {
                deleteBtn.setAttribute('onclick', `openDeleteBranchModal(${data.branch_id}, '${data.name.replace(/'/g, "\\'")}')`);
            }
        }

        // Sync table row delete buttons too
        document.querySelectorAll(`[data-branch-row="${data.branch_id}"]`).forEach(row => {
            const deleteBtn = row.querySelector('button[onclick^="openDeleteBranchModal"]');
            if (deleteBtn) {
                deleteBtn.setAttribute('onclick', `openDeleteBranchModal(${data.branch_id}, '${data.name.replace(/'/g, "\\'")}')`);
            }
        });
    }

    let currentDeleteBranchId = null;

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
        document.getElementById('drawerTitle').textContent = 'Create Staff Account';
        document.getElementById('drawerSubmitBtn').textContent = 'Save Account';
        document.getElementById('drawerHelpText').textContent = 'Configure access credentials to instantiate the branch manager profile layout.';

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

    window.addEventListener('DOMContentLoaded', () => {
        if (window.location.hash === "#create-branch") {
            toggleBranchDrawer();
            history.replaceState(null, null, ' ');
        }

        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('openDrawer') === 'true') { toggleBranchDrawer(); }
    });
