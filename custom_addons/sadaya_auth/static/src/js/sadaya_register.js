/** @odoo-module **/
/**
 * Sadaya Register - JavaScript spesifik halaman registrasi
 */

'use strict';

document.addEventListener('DOMContentLoaded', function () {

    // =====================
    // TABS: BADAN USAHA / PERORANGAN
    // =====================
    const tabBadanUsaha = document.querySelector('[data-tab="badan_usaha"]');
    const tabPerorangan = document.querySelector('[data-tab="perorangan"]');

    if (tabBadanUsaha && tabPerorangan) {
        tabBadanUsaha.addEventListener('click', (e) => {
            e.preventDefault();
            window.location.href = '/sadaya/register/badan-usaha';
        });

        tabPerorangan.addEventListener('click', (e) => {
            e.preventDefault();
            window.location.href = '/sadaya/register/perorangan';
        });
    }

    // =====================
    // EMAIL REAL-TIME CHECK
    // =====================
    const emailInput = document.getElementById('email');
    if (emailInput) {
        let emailTimer;
        emailInput.addEventListener('input', () => {
            clearTimeout(emailTimer);
            emailTimer = setTimeout(async () => {
                const email = emailInput.value.trim();
                const pattern = /^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$/;
                if (!pattern.test(email)) return;

                // Visual feedback while checking
                emailInput.style.borderColor = 'var(--sadaya-secondary)';
            }, 500);
        });
    }

    // =====================
    // NPWP FORMATTING
    // =====================
    const npwpInput = document.getElementById('npwp_perusahaan');
    if (npwpInput) {
        npwpInput.addEventListener('input', function () {
            this.value = this.value.replace(/\D/g, '').slice(0, 16);

            // Show formatted display
            const digits = this.value;
            const display = document.getElementById('npwp_display');
            if (display && digits) {
                // Format: XX.XXX.XXX.X-XXX.XXX
                let formatted = digits;
                if (digits.length > 2) formatted = digits.slice(0, 2) + '.' + digits.slice(2);
                if (digits.length > 5) formatted = formatted.slice(0, 6) + '.' + formatted.slice(6);
                if (digits.length > 8) formatted = formatted.slice(0, 10) + '.' + formatted.slice(10);
                if (digits.length > 9) formatted = formatted.slice(0, 12) + '-' + formatted.slice(12);
                if (digits.length > 12) formatted = formatted.slice(0, 16) + '.' + formatted.slice(16);
                display.textContent = formatted || '-';
            }
        });
    }

    // =====================
    // FILE SIZE VALIDATION
    // =====================
    function validateFile(input, maxSizeMB, allowedTypes, errorContainer) {
        if (!input.files || !input.files[0]) return false;

        const file = input.files[0];
        const ext = file.name.split('.').pop().toLowerCase();
        const sizeMB = file.size / (1024 * 1024);

        if (allowedTypes && !allowedTypes.includes(ext)) {
            if (errorContainer) errorContainer.textContent = `Format tidak didukung. Gunakan: ${allowedTypes.join(', ').toUpperCase()}`;
            input.value = '';
            return false;
        }

        if (sizeMB > maxSizeMB) {
            if (errorContainer) errorContainer.textContent = `Ukuran file maksimal ${maxSizeMB} MB`;
            input.value = '';
            return false;
        }

        if (errorContainer) errorContainer.textContent = '';
        return true;
    }

    // Swafoto KTP
    const swafotoInput = document.getElementById('swafoto_ktp');
    if (swafotoInput) {
        swafotoInput.addEventListener('change', function () {
            const errorEl = document.getElementById('swafoto_error');
            validateFile(this, 10, ['jpg', 'jpeg', 'png'], errorEl);
        });
    }

    // Bukti NPWP
    const npwpBuktiInput = document.getElementById('bukti_npwp');
    if (npwpBuktiInput) {
        npwpBuktiInput.addEventListener('change', function () {
            const errorEl = document.getElementById('bukti_npwp_error');
            validateFile(this, 10, ['pdf'], errorEl);
        });
    }

    // =====================
    // MULTI-STEP REGISTER FORM WIZARD
    // =====================
    const registerForm = document.getElementById('sadaya-register-form');
    if (registerForm) {
        let activeStep = 1;

        // Custom field error helpers to avoid scope issues
        function showFieldErrorLocal(fieldEl, message) {
            fieldEl.classList.add('is-invalid');
            
            let errorParent = fieldEl.parentElement;
            if (errorParent.classList.contains('input-group')) {
                errorParent = errorParent.parentElement;
            }

            let errorEl = errorParent.querySelector('.sadaya-field-error');
            if (!errorEl) {
                errorEl = document.createElement('div');
                errorEl.className = 'sadaya-field-error text-danger small mt-1';
                errorParent.appendChild(errorEl);
            }
            errorEl.textContent = '⚠ ' + message;

            const backendError = errorParent.querySelector('.text-danger:not(.sadaya-field-error)');
            if (backendError) {
                backendError.style.display = 'none';
            }
        }

        function clearFieldErrorLocal(fieldEl) {
            fieldEl.classList.remove('is-invalid');
            
            let errorParent = fieldEl.parentElement;
            if (errorParent.classList.contains('input-group')) {
                errorParent = errorParent.parentElement;
            }

            const errorEl = errorParent.querySelector('.sadaya-field-error');
            if (errorEl) errorEl.textContent = '';

            const backendError = errorParent.querySelector('.text-danger:not(.sadaya-field-error)');
            if (backendError) {
                backendError.textContent = '';
            }

            const btn = fieldEl.parentElement.querySelector('button');
            if (btn) btn.classList.remove('is-invalid');
        }

        // Check password strength locally
        function checkPasswordStrength(password) {
            let score = 0;
            if (password.length >= 8) score++;
            if (/[0-9]/.test(password)) score++;
            if (/[A-Z]/.test(password)) score++;
            if (/[a-z]/.test(password)) score++;
            return score;
        }

        // Validate fields within a single step
        function validateStep(stepNum) {
            const stepEl = registerForm.querySelector(`.register-step[data-step="${stepNum}"]`);
            if (!stepEl) return true;

            let isValid = true;
            const inputs = stepEl.querySelectorAll('input, select, textarea');

            inputs.forEach(input => {
                clearFieldErrorLocal(input);

                if (input.disabled || input.type === 'hidden') return;

                const val = input.value.trim();

                // Required check
                if (input.hasAttribute('required')) {
                    if (input.type === 'file') {
                        if (!input.files || input.files.length === 0) {
                            showFieldErrorLocal(input, 'File wajib diunggah');
                            const btn = input.parentElement.querySelector('button');
                            if (btn) btn.classList.add('is-invalid');
                            isValid = false;
                            return;
                        }
                    } else if (!val) {
                        showFieldErrorLocal(input, 'Wajib diisi');
                        isValid = false;
                        return;
                    }
                }

                // If optional and empty, skip further check
                if (!val) return;

                // Email validation
                if (input.type === 'email') {
                    const emailPattern = /^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$/;
                    if (!emailPattern.test(val)) {
                        showFieldErrorLocal(input, 'Format email tidak valid');
                        isValid = false;
                        return;
                    }
                }

                // WhatsApp/Phone validation
                if (input.hasAttribute('data-sadaya-phone')) {
                    const digits = val.replace(/\D/g, '');
                    if (digits.length < 12 || !(val.startsWith('+62') || digits.startsWith('62') || digits.startsWith('08'))) {
                        showFieldErrorLocal(input, 'Format: +628123456789 (minimal 12 digit)');
                        isValid = false;
                        return;
                    }
                }

                // NIK validation
                if (input.hasAttribute('data-sadaya-nik')) {
                    const digits = val.replace(/\D/g, '');
                    if (digits.length !== 16) {
                        showFieldErrorLocal(input, 'NIK harus terdiri dari 16 digit');
                        isValid = false;
                        return;
                    }
                }

                // NPWP validation
                if (input.hasAttribute('data-sadaya-npwp')) {
                    const digits = val.replace(/\D/g, '');
                    if (digits.length !== 16) {
                        showFieldErrorLocal(input, 'NPWP harus terdiri dari 16 digit');
                        isValid = false;
                        return;
                    }
                }

                // Password match check
                if (input.id === 'password_confirm') {
                    const pwd = document.getElementById('password');
                    if (pwd && val !== pwd.value) {
                        showFieldErrorLocal(input, 'Kata sandi tidak sesuai');
                        isValid = false;
                        return;
                    }
                }

                // Password strength validation
                if (input.id === 'password') {
                    const errors = [];
                    if (val.length < 8) errors.push('minimal 8 karakter');
                    if (!/[0-9]/.test(val)) errors.push('satu angka');
                    if (!/[A-Z]/.test(val)) errors.push('satu huruf besar');
                    if (!/[a-z]/.test(val)) errors.push('satu huruf kecil');

                    if (errors.length > 0) {
                        showFieldErrorLocal(input, 'Sandi kurang kuat: ' + errors.join(', '));
                        isValid = false;
                        return;
                    }
                }
            });

            return isValid;
        }

        // Navigate to target step
        function goToStep(stepNum) {
            activeStep = stepNum;

            // Show/hide step panels
            registerForm.querySelectorAll('.register-step').forEach(stepEl => {
                const step = parseInt(stepEl.getAttribute('data-step'));
                if (step === activeStep) {
                    stepEl.classList.remove('d-none');
                } else {
                    stepEl.classList.add('d-none');
                }
            });

            // Update progress bar segments
            document.querySelectorAll('.progress-bar-segment').forEach(seg => {
                const step = parseInt(seg.getAttribute('data-step'));
                seg.classList.remove('active', 'completed');
                if (step === activeStep) {
                    seg.classList.add('active'); // active/current step is red
                } else if (step < activeStep) {
                    seg.classList.add('completed'); // completed steps are green
                }
            });

            // Update title
            const activeStepEl = registerForm.querySelector(`.register-step[data-step="${activeStep}"]`);
            const stepTitleEl = document.querySelector('.sadaya-step-title');
            if (activeStepEl && stepTitleEl) {
                stepTitleEl.innerHTML = activeStepEl.getAttribute('data-title');
            }

            // Scroll to the top of form card smoothly
            const brandPanel = document.querySelector('.sadaya-auth-panel-right');
            if (brandPanel) {
                brandPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }

        // Autodetect backend validation errors on page load and jump to that step
        const firstErrorField = registerForm.querySelector('.is-invalid, .text-danger:not(:empty)');
        if (firstErrorField) {
            const errorStepEl = firstErrorField.closest('.register-step');
            if (errorStepEl) {
                const errorStep = parseInt(errorStepEl.getAttribute('data-step')) || 1;
                goToStep(errorStep);
            }
        } else {
            // Default step 1 initialization
            goToStep(1);
        }

        // Bind next buttons
        registerForm.querySelectorAll('.next-step').forEach(btn => {
            btn.addEventListener('click', function () {
                if (validateStep(activeStep)) {
                    goToStep(activeStep + 1);
                } else {
                    const firstErr = registerForm.querySelector(`.register-step[data-step="${activeStep}"] .is-invalid`);
                    if (firstErr) {
                        firstErr.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                }
            });
        });

        // Bind back buttons
        registerForm.querySelectorAll('.prev-step').forEach(btn => {
            btn.addEventListener('click', function () {
                goToStep(activeStep - 1);
            });
        });

        // Form Submission validation check
        registerForm.addEventListener('submit', function (e) {
            let isAllValid = true;
            for (let s = 1; s <= 3; s++) {
                if (!validateStep(s)) {
                    isAllValid = false;
                    goToStep(s);
                    break;
                }
            }

            if (!isAllValid) {
                e.preventDefault();
                const submitBtn = registerForm.querySelector('.sadaya-form-submit');
                if (submitBtn) {
                    submitBtn.classList.remove('loading');
                    submitBtn.innerHTML = 'Daftar';
                }
            }
        });
    }

});
