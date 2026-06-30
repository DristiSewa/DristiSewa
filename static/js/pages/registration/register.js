// When a branch is picked, check if it has more than one Front Desk
    // officer; if so, let the student choose who handles their application.
    document.getElementById("branchSelect").addEventListener("change", function(){
        const branchId = this.value;
        const wrapper = document.getElementById("frontDeskFieldWrapper");
        const select = document.getElementById("frontDeskSelect");

        select.innerHTML = '<option value="">Auto-assign</option>';
        wrapper.classList.add("hidden");

        if (!branchId) return;

        fetch(`/register/branches/${branchId}/frontdesk/`)
            .then(res => res.json())
            .then(data => {
                const staff = data.front_desk_staff || [];
                if (staff.length > 1) {
                    staff.forEach(fd => {
                        const opt = document.createElement("option");
                        opt.value = fd.id;
                        opt.textContent = fd.name;
                        select.appendChild(opt);
                    });
                    wrapper.classList.remove("hidden");
                }
            })
            .catch(() => {});
    });

    document.getElementById("registerForm").addEventListener("submit", function(e){

        let password = document.getElementById("password");
        let confirm = document.getElementById("confirm_password");

        password.classList.remove("error-field");
        confirm.classList.remove("error-field");

        if(password.value !== confirm.value){
            e.preventDefault();

            password.classList.add("error-field");
            confirm.classList.add("error-field");

            // Custom elegant validation alert logic trigger
            alert("Oops! Passwords do not match. Please verify again.");
        }
    });
