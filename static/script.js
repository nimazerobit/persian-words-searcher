document.addEventListener("DOMContentLoaded", () => {
    const lettersInput   = document.getElementById("lettersInput");
    const lengthInput    = document.getElementById("lengthInput");
    const categorySelect = document.getElementById("categorySelect");
    const resultsList    = document.getElementById("results");
    const timingEl       = document.getElementById("timing");
    const langWarning    = document.getElementById("lang-warning");
    const errBox         = document.getElementById("error-box");
    const loadingEl      = document.getElementById("loading");

    if (!lettersInput || !lengthInput || !categorySelect || !resultsList) {
        return;
    }

    let debounceTimer = null;
    let activeController = null;
    let searchVersion = 0;

    // filter characters
    const allowOnlyPersian = (el) => {
        if (/[^آ-یٔ‌ء‍#@]/.test(el.value)) {
            langWarning.hidden = false;
        } else {
            langWarning.hidden = true;
        }
        el.value = el.value.replace(/[^آ-یٔ‌ء‍#@]/g, "");
    };

    const setLoading = (isLoading) => {
        loadingEl.hidden = !isLoading;
        resultsList.setAttribute("aria-busy", String(isLoading));
    };

    const renderTiming = (data, responseMs) => {
        const parts = [`زمان پاسخ: ${responseMs} میلی ثانیه`];

        if (data.server_ms !== undefined) {
            parts.push(`پردازش سرور: ${data.server_ms} میلی ثانیه`);
        }
        if (data.count !== undefined) {
            parts.push(`تعداد نتایج: ${data.count}`);
        }

        timingEl.textContent = parts.join(" • ");
    };

    // executes the search request
    const runSearch = async (version) => {
        // remove pulse effect from all fields
        document.querySelectorAll(".pulse-effect").forEach(el => {
            el.classList.remove("pulse-effect");
        });

        const queryParams = {
            letters:  lettersInput.value.trim(),
            length:   lengthInput.value.trim(),
            category: categorySelect.value.trim()
        };

        activeController = new AbortController();
        const startedAt = performance.now();

        errBox.textContent = "";
        timingEl.textContent = "";
        setLoading(true);

        try {
            const response = await fetch(`/search?${new URLSearchParams(queryParams)}`, {
                signal: activeController.signal
            });

            if (!response.ok) {
                throw new Error(`Search request failed with status ${response.status}`);
            }

            const data = await response.json();
            const responseMs = Math.round(performance.now() - startedAt);

            if (version !== searchVersion) {
                return;
            }

            resultsList.innerHTML = "";
            renderTiming(data, responseMs);

            // handle errors
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

            if (!data.results.length) {
                const emptyItem = document.createElement("li");
                emptyItem.className = "empty-result";
                emptyItem.textContent = "نتیجه‌ای پیدا نشد.";
                resultsList.appendChild(emptyItem);
                return;
            }

            // append results
            const fragment = document.createDocumentFragment();
            data.results.forEach((word, index) => {
                const li = document.createElement("li");
                li.textContent = word;
                if (data.results.length <= 200) {
                    li.style.setProperty("--delay", index);
                }
                fragment.appendChild(li);
            });
            resultsList.appendChild(fragment);
        } catch (err) {
            if (err.name !== "AbortError" && version === searchVersion) {
                errBox.textContent = "خطا در دریافت پاسخ از سرور";
                timingEl.textContent = "";
                console.error(err);
            }
        } finally {
            if (version === searchVersion) {
                setLoading(false);
                activeController = null;
            }
        }
    };

    // debounces the search trigger
    const scheduleSearch = () => {
        clearTimeout(debounceTimer);
        activeController?.abort();
        activeController = null;
        setLoading(false);

        searchVersion += 1;
        const version = searchVersion;
        debounceTimer = setTimeout(() => runSearch(version), 300);
    };

    lettersInput.addEventListener("input", () => {
        allowOnlyPersian(lettersInput);
        if (langWarning.hidden) {
            scheduleSearch();
        }
    });
    lengthInput.addEventListener("input", () => {
        langWarning.hidden = true;
        scheduleSearch();
    });
    categorySelect.addEventListener("change", () => {
        langWarning.hidden = true;
        scheduleSearch();
    });
});
