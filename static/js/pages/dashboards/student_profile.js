function switchTab(tabName) {
            const docContent = document.getElementById('documentContent');
            const remContent = document.getElementById('remarksContent');
            const docTab = document.getElementById('docTab');
            const remTab = document.getElementById('remTab');
            const uploadBtn = document.getElementById('uploadActionSection');

            docContent.classList.add('hidden');
            remContent.classList.add('hidden');
            uploadBtn.classList.add('hidden');
            docTab.classList.remove('active-tab');
            remTab.classList.remove('active-tab');

            if (tabName === 'document') {
                docContent.classList.remove('hidden');
                uploadBtn.classList.remove('hidden');
                docTab.classList.add('active-tab');
            } else {
                remContent.classList.remove('hidden');
                remTab.classList.add('active-tab');
            }
        }

        if (new URLSearchParams(window.location.search).get('tab') === 'remarks') {
            switchTab('remarks');
        }

        function toggleRemarkBox() {
            const box = document.getElementById('remarkInputBox');
            box.classList.toggle('hidden');
            if (!box.classList.contains('hidden')) {
                box.querySelector('textarea').focus();
            }
        }

        function toggleUploadModal(show) {
            const modal = document.getElementById('uploadDocumentModal');
            if (show) {
                modal.classList.remove('hidden');
            } else {
                modal.classList.add('hidden');
            }
        }

        function toggleEditProfileModal(show) {
            const modal = document.getElementById('editProfileModal');
            if (show) {
                modal.classList.remove('hidden');
            } else {
                modal.classList.add('hidden');
            }
        }
