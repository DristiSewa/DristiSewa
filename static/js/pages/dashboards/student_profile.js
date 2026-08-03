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

        const pageParams = new URLSearchParams(window.location.search);

        if (pageParams.get('tab') === 'remarks') {
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

        const scoreCriteria = {
            IELTS: { min: 0, max: 9, step: 0.5, label: 'IELTS', help: 'IELTS score range: 0 to 9, in 0.5 bands.' },
            PTE: { min: 10, max: 90, step: 1, label: 'PTE', help: 'PTE score range: 10 to 90.' },
            TOEFL: { min: 0, max: 120, step: 1, label: 'TOEFL', help: 'TOEFL score range: 0 to 120.' },
        };

        function validateScoreInput() {
            const testTypeInput = document.getElementById('inputTestType');
            const scoreInput = document.getElementById('inputScore');
            const scoreHelp = document.getElementById('scoreHelp');
            if (!testTypeInput || !scoreInput || !scoreHelp) return true;

            const rule = scoreCriteria[testTypeInput.value];
            scoreInput.setCustomValidity('');

            if (!rule) {
                if (scoreInput.value) {
                    scoreInput.setCustomValidity('Please choose a test type first.');
                    scoreHelp.textContent = 'Choose a test type before entering a score.';
                    scoreHelp.classList.remove('text-slate-400');
                    scoreHelp.classList.add('text-red-500');
                    return false;
                }
                return true;
            }

            if (!scoreInput.value) {
                scoreHelp.textContent = rule.help;
                scoreHelp.classList.remove('text-red-500');
                scoreHelp.classList.add('text-slate-400');
                return true;
            }

            const score = Number(scoreInput.value);
            const isOutOfRange = Number.isNaN(score) || score < rule.min || score > rule.max;

            if (isOutOfRange) {
                scoreInput.setCustomValidity(`${rule.label} score must be between ${rule.min} and ${rule.max}.`);
                scoreHelp.textContent = `${rule.label} score must be between ${rule.min} and ${rule.max}.`;
                scoreHelp.classList.remove('text-slate-400');
                scoreHelp.classList.add('text-red-500');
                return false;
            }

            scoreHelp.textContent = rule.help;
            scoreHelp.classList.remove('text-red-500');
            scoreHelp.classList.add('text-slate-400');
            return true;
        }

        function updateScoreCriteria() {
            const testTypeInput = document.getElementById('inputTestType');
            const scoreInput = document.getElementById('inputScore');
            const scoreHelp = document.getElementById('scoreHelp');
            if (!testTypeInput || !scoreInput || !scoreHelp) return;

            const rule = scoreCriteria[testTypeInput.value];
            if (!rule) {
                scoreInput.min = 0;
                scoreInput.max = 120;
                scoreInput.step = 0.01;
                scoreInput.placeholder = '';
                scoreInput.setCustomValidity('');
                scoreHelp.textContent = 'Choose a test type to see score range.';
                scoreHelp.classList.remove('text-red-500');
                scoreHelp.classList.add('text-slate-400');
                return;
            }

            scoreInput.min = rule.min;
            scoreInput.max = rule.max;
            scoreInput.step = rule.step;
            scoreInput.placeholder = `${rule.min} - ${rule.max}`;
            scoreHelp.textContent = rule.help;

            const currentScore = parseFloat(scoreInput.value);
            if (scoreInput.value && (Number.isNaN(currentScore) || currentScore < rule.min || currentScore > rule.max)) {
                scoreInput.value = '';
            }
            validateScoreInput();
        }

        window.validateScoreInput = validateScoreInput;
        window.updateScoreCriteria = updateScoreCriteria;

        function initScoreCriteria() {
            const testTypeInput = document.getElementById('inputTestType');
            const scoreInput = document.getElementById('inputScore');

            if (testTypeInput) {
                testTypeInput.addEventListener('change', updateScoreCriteria);
                updateScoreCriteria();
            }

            if (scoreInput) {
                scoreInput.addEventListener('input', validateScoreInput);
            }

            if (scoreInput) {
                const editProfileForm = scoreInput.closest('form');
                if (editProfileForm) {
                    editProfileForm.addEventListener('submit', (event) => {
                        if (!validateScoreInput()) {
                            event.preventDefault();
                            scoreInput.reportValidity();
                        }
                    });
                }
            }
        }

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initScoreCriteria);
        } else {
            initScoreCriteria();
        }

        if (pageParams.get('edit') === '1') {
            toggleEditProfileModal(true);
        }
