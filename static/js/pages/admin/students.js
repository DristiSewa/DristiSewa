document.querySelectorAll('.tab-btn').forEach(button => {
        button.addEventListener('click', function() {
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.style.background = 'transparent';
                btn.style.color = '#64748b';
                btn.style.fontWeight = '500';
            });
            this.style.background = 'white';
            this.style.color = '#1e40af';
            this.style.fontWeight = '600';
        });
    });
