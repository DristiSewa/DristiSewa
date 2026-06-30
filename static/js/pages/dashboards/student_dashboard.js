let currentStep = 1;

    document.addEventListener('DOMContentLoaded', function () {
        const savedTest = document.getElementById('testType').value;
        if (savedTest) { selectTest(savedTest); }

        const savedCountry = document.getElementById('preferredCountry').value;
        if (savedCountry) { selectCountry(savedCountry); }
    });

    function selectTest(type) {
        document.getElementById('testType').value = type;
        ['IELTS', 'PTE', 'TOEFL'].forEach(t => {
            document.getElementById(`card_${t}`).classList.remove('active');
        });
        document.getElementById(`card_${type}`).classList.add('active');

        const wrapper = document.getElementById('scoreFieldWrapper');
        const label = document.getElementById('scoreLabel');
        const scoreInput = document.getElementById('score');

        wrapper.classList.remove('hidden');
        if(type === 'IELTS') { label.innerText = "Obtained Band Score (0 - 9)"; scoreInput.placeholder = "e.g., 7.5"; }
        if(type === 'PTE') { label.innerText = "Obtained Overall Score (10 - 90)"; scoreInput.placeholder = "e.g., 68"; }
        if(type === 'TOEFL') { label.innerText = "Obtained Total Score (0 - 120)"; scoreInput.placeholder = "e.g., 102"; }
    }

    function selectCountry(country) {
        document.getElementById('preferredCountry').value = country;
        ['UK', 'USA', 'Canada', 'Australia'].forEach(c => {
            document.getElementById(`country_${c}`).classList.remove('active');
        });
        let elementId = country === "United Kingdom" ? 'UK' : country === "United States" ? 'USA' : country;
        const el = document.getElementById(`country_${elementId}`);
        if (el) { el.classList.add('active'); }
    }

    function processStep() {
        let error = document.getElementById("error");
        error.classList.add("hidden");
        error.classList.remove("shake-element");

        if (currentStep === 1) {
            let dob = document.getElementById("dob");
            if (!dob.value) { return triggerError(dob, "Please supply your valid Date of Birth parameter."); }

            currentStep = 2;
            document.getElementById("formSection1").classList.add("hidden");
            document.getElementById("formSection2").classList.remove("hidden");
            document.getElementById("prevBtn").classList.remove("opacity-0", "visibility-hidden");
            updateMeters();
        }
        else if (currentStep === 2) {
            let college = document.getElementById("college");
            let year = document.getElementById("year");
            let gpa = document.getElementById("gpa");

            if (!college.value.trim()) { return triggerError(college, "Institution workspace location name cannot remain empty."); }
            let y = parseInt(year.value);
            if (isNaN(y) || y < 1990 || y > 2027) { return triggerError(year, "Passed year must belong strictly between 1990 and 2027."); }
            let g = parseFloat(gpa.value);
            if (isNaN(g) || g < 0 || g > 4) { return triggerError(gpa, "Calculated score parameters must sit inside 0.0 and 4.0 GPA limits."); }

            currentStep = 3;
            document.getElementById("formSection2").classList.add("hidden");
            document.getElementById("formSection3").classList.remove("hidden");
            document.getElementById("btnText").innerText = "Submit Application";
            document.getElementById("btnIcon").className = "fa-solid fa-circle-check";
            updateMeters();
        }
        else if (currentStep === 3) {
            let testType = document.getElementById("testType").value;
            let score = document.getElementById("score");
            let s = parseFloat(score.value);

            if (!testType) { return triggerError(document.getElementById("card_IELTS"), "Please select one English Assessment matrix option."); }

            if (testType === "IELTS" && (isNaN(s) || s < 0 || s > 9)) { return triggerError(score, "IELTS score bands scale explicitly between 0 and 9."); }
            if (testType === "PTE" && (isNaN(s) || s < 10 || s > 90)) { return triggerError(score, "PTE scores dynamically operate solely between 10 and 90."); }
            if (testType === "TOEFL" && (isNaN(s) || s < 0 || s > 120)) { return triggerError(score, "TOEFL standard point thresholds range inside 0 - 120."); }

            document.getElementById('appForm').submit();
        }
    }

    function moveBack() {
        if (currentStep === 3) {
            currentStep = 2;
            document.getElementById("formSection3").classList.add("hidden");
            document.getElementById("formSection2").classList.remove("hidden");
            document.getElementById("btnText").innerText = "Continue";
            document.getElementById("btnIcon").className = "fa-solid fa-arrow-right";
        } else if (currentStep === 2) {
            currentStep = 1;
            document.getElementById("formSection2").classList.add("hidden");
            document.getElementById("formSection1").classList.remove("hidden");
            document.getElementById("prevBtn").classList.add("opacity-0", "visibility-hidden");
        }
        updateMeters();
    }

    function updateMeters() {
        for (let i = 1; i <= 3; i++) {
            let meter = document.getElementById(`stepMeter${i}`);
            let badge = meter.querySelector('span');
            let txt = meter.querySelector('p');

            if (i === currentStep) {
                meter.className = "flex items-center gap-3 border-b-4 border-blue-600 pb-3 transition-all";
                badge.className = "w-8 h-8 rounded-xl bg-blue-600 text-white flex items-center justify-center text-xs font-black";
                txt.className = "text-xs font-black uppercase tracking-wider text-slate-800";
            } else if (i < currentStep) {
                meter.className = "flex items-center gap-3 border-b-4 border-emerald-500 pb-3 transition-all";
                badge.className = "w-8 h-8 rounded-xl bg-emerald-500 text-white flex items-center justify-center text-xs font-black";
                txt.className = "text-xs font-black uppercase tracking-wider text-slate-500";
            } else {
                meter.className = "flex items-center gap-3 border-b-4 border-slate-200 pb-3 transition-all";
                badge.className = "w-8 h-8 rounded-xl bg-slate-200 text-slate-600 flex items-center justify-center text-xs font-black";
                txt.className = "text-xs font-black uppercase tracking-wider text-slate-400";
            }
        }
    }

    function triggerError(el, msg) {
        let error = document.getElementById("error");
        error.innerText = msg;
        error.classList.remove("hidden");

        setTimeout(() => { error.classList.add("shake-element"); }, 10);
        el.focus();
        return false;
    }
