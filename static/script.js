document.addEventListener("DOMContentLoaded", () => {
    const lettersInput   = document.getElementById("lettersInput");
    const lengthInput    = document.getElementById("lengthInput");
    const categorySelect = document.getElementById("categorySelect");
    const resultsList    = document.getElementById("results");
    const timingEl       = document.getElementById("timing");
    const langWarning    = document.getElementById("lang-warning");
    const errBox         = document.getElementById("error-box");

    let debounceTimer = null;

    // filter characters
    const allowOnlyPersian = (el) => {
        if (/[^آ-یٔ‌ء‍#@]/.test(el.value)) {
            langWarning.style.display = "block";
        } else {
            langWarning.style.display = "none";
        }
        el.value = el.value.replace(/[^آ-یٔ‌ء‍#@]/g, ""); 
    };

    // executes the search request
    const runSearch = () => {
        // remove pulse effect from all fields
        document.querySelectorAll(".pulse-effect").forEach(el => {
            el.classList.remove("pulse-effect");
        });

        const queryParams = {
            letters:  lettersInput.value.trim(),
            length:   lengthInput.value.trim(),
            category: categorySelect.value.trim()
        };

        fetch(`/search?${new URLSearchParams(queryParams)}`)
            .then(res => res.json())
            .then(data => {
                // Reset UI
                errBox.textContent = "";
                resultsList.innerHTML = "";
                timingEl.textContent = "";

                // Handle errors
                if (data.error) {
                    errBox.textContent = data.error;

                    if (Array.isArray(data.fields)) {
                        data.fields.forEach(id => {
                            const el = document.getElementById(id);
                            if (el) el.classList.add("pulse-effect");
                        });

                        if (data.fields[0]) {
                            const firstEl = document.getElementById(data.fields[0]);
                            if (firstEl) firstEl.focus();
                        }
                    }
                    return;
                }

                // Append results
                data.results.forEach((word, index) => {
                    const li = document.createElement("li");
                    li.textContent = word;
                    if (data.results.length <= 200) {
                        li.style.setProperty("--delay", index);
                    }
                    resultsList.appendChild(li);
                });

                if (data.server_ms !== undefined) {
                    let text = `زمان جستجو : ${data.server_ms} میلی‌ثانیه`;
                    if (data.count !== undefined) {
                        text += ` - تعداد نتایج: ${data.count}`;
                    }
                    timingEl.textContent = text;
                }
            })
            .catch(err => {
                errBox.textContent = "خطا در دریافت پاسخ از سرور";
                console.error(err);
            });
    };

    // debounces the search trigger
    const scheduleSearch = () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(runSearch, 300);
    };

    // --- Event listeners ---
    lettersInput.addEventListener("input", () => {
        allowOnlyPersian(lettersInput);
        // only schedule search if the warning is not visible
        if (langWarning.style.display === "none") {
            scheduleSearch();
        }
    });
    lengthInput.addEventListener("input", () => {
        // hide warning if user starts interacting with length
        langWarning.style.display = "none"; 
        scheduleSearch();
    });
    categorySelect.addEventListener("change", () => {
        // hide warning if user changes category
        langWarning.style.display = "none";
        scheduleSearch();
    });
});
