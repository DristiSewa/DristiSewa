document.getElementById("{{ form.profile_pic.id_for_label }}").addEventListener("change", function (e) {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = function (ev) {
            const img = document.getElementById("profile-pic-preview");
            const placeholder = document.getElementById("profile-pic-placeholder");
            img.src = ev.target.result;
            img.classList.remove("hidden");
            if (placeholder) {
                placeholder.classList.add("hidden");
                placeholder.classList.remove("flex");
            }
        };
        reader.readAsDataURL(file);
    });
