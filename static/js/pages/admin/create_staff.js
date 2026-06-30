function generatePassword(fieldId) {
        const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789!@#$%';
        let password = '';
        for (let i = 0; i < 10; i++) {
            password += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        const field = document.getElementById(fieldId);
        if (field) {
            field.value = password;
            field.type = 'text';
        }
    }
