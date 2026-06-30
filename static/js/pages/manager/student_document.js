const tabDocBtn     = document.getElementById('tabDocBtn');
    const tabRemarksBtn = document.getElementById('tabRemarksBtn');
    const paneDocuments = document.getElementById('paneDocuments');
    const paneRemarks   = document.getElementById('paneRemarks');

    tabDocBtn.addEventListener('click', () => {
        tabDocBtn.classList.add('tab-active');
        tabRemarksBtn.classList.remove('tab-active');
        paneDocuments.classList.add('pane-active');
        paneRemarks.classList.remove('pane-active');
    });

    tabRemarksBtn.addEventListener('click', () => {
        tabRemarksBtn.classList.add('tab-active');
        tabDocBtn.classList.remove('tab-active');
        paneRemarks.classList.add('pane-active');
        paneDocuments.classList.remove('pane-active');
    });

    // Auto-open Remarks tab if there's a URL hash
    if (window.location.hash === '#remarks') {
        tabRemarksBtn.click();
    }
