/** @odoo-module **/
/**
 * Sadaya Auth - Main JavaScript
 * Utility functions untuk autentikasi Sadaya
 */

'use strict';

// =====================
// PASSWORD STRENGTH
// =====================
function checkPasswordStrength(password) {
    let score = 0;
    if (password.length >= 8) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[a-z]/.test(password)) score++;
    if (password.length >= 12) score++;
    return score;
}

function updatePasswordStrength(password, barsEl, labelEl) {
    const score = checkPasswordStrength(password);
    const bars = barsEl.querySelectorAll('.sadaya-pwd-bar');

    bars.forEach((bar, i) => {
        bar.classList.remove('weak', 'medium', 'strong');
    });

    let label = '';
    let className = '';

    if (score <= 2) {
        className = 'weak';
        label = 'Lemah';
        bars[0] && bars[0].classList.add('weak');
    } else if (score <= 3) {
        className = 'medium';
        label = 'Sedang';
        bars[0] && bars[0].classList.add('medium');
        bars[1] && bars[1].classList.add('medium');
    } else {
        className = 'strong';
        label = 'Kuat';
        bars.forEach(b => b.classList.add('strong'));
    }

    if (labelEl) labelEl.textContent = `Kekuatan: ${label}`;
}

// =====================
// NPWP FORMAT
// =====================
function formatNPWP(value) {
    const digits = value.replace(/\D/g, '').slice(0, 16);
    return digits;
}

// =====================
// PHONE FORMAT VALIDATION
// =====================
function validatePhoneID(phone) {
    const digits = phone.replace(/\D/g, '');
    return digits.length >= 12 && (phone.startsWith('+62') || digits.startsWith('62') || digits.startsWith('08'));
}

// =====================
// FILE UPLOAD HANDLING
// =====================
function initFileUpload(container) {
    const input = container.querySelector('input[type="file"]');
    if (!input) return;

    const normalState = container.querySelector('.upload-state-normal');
    const uploadedState = container.querySelector('.upload-state-uploaded');
    const nameLabel = container.querySelector('.file-name-label');
    const clearBtn = container.querySelector('.clear-file-btn');

    ['dragenter', 'dragover'].forEach(evt => {
        if (normalState) {
            normalState.addEventListener(evt, (e) => {
                e.preventDefault();
                normalState.classList.add('bg-light');
            });
        }
    });

    ['dragleave', 'drop'].forEach(evt => {
        if (normalState) {
            normalState.addEventListener(evt, (e) => {
                e.preventDefault();
                normalState.classList.remove('bg-light');
            });
        }
    });

    if (normalState) {
        normalState.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length && input) {
                const dt = new DataTransfer();
                dt.items.add(files[0]);
                input.files = dt.files;
                input.dispatchEvent(new Event('change'));
            }
        });
    }

    input.addEventListener('change', () => {
        const preview = input.id ? document.getElementById(input.id + '_preview') : null;

        if (input.files && input.files[0]) {
            const file = input.files[0];
            const sizeMB = (file.size / (1024 * 1024)).toFixed(2);

            if (preview) {
                preview.textContent = `✓ ${file.name} (${sizeMB} MB)`;
                preview.style.color = 'var(--sadaya-success)';
            }

            if (normalState) {
                normalState.classList.add('d-none');
            }
            if (uploadedState) {
                uploadedState.classList.remove('d-none');
            }
            if (nameLabel) {
                nameLabel.textContent = file.name;
                nameLabel.title = file.name; // Show full file name on hover
            }
        } else {
            if (preview) {
                preview.textContent = '';
            }
            if (normalState) {
                normalState.classList.remove('d-none');
            }
            if (uploadedState) {
                uploadedState.classList.add('d-none');
            }
        }
    });

    if (clearBtn) {
        clearBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            input.value = ''; // Clear file input
            input.dispatchEvent(new Event('change')); // Trigger change state
        });
    }
}

// =====================
// TOGGLE PASSWORD VISIBILITY
// =====================
function initPasswordToggle(inputEl, toggleBtn) {
    if (!inputEl || !toggleBtn) return;
    toggleBtn.addEventListener('click', () => {
        const isPassword = inputEl.type === 'password';
        inputEl.type = isPassword ? 'text' : 'password';
        const icon = toggleBtn.querySelector('i');
        if (icon) {
            if (isPassword) {
                icon.className = 'fa fa-eye-slash';
            } else {
                icon.className = 'fa fa-eye';
            }
        }
    });
}

// =====================
// FORM VALIDATION UI
// =====================
function showFieldError(fieldEl, message) {
    fieldEl.classList.add('is-invalid');
    let errorEl = fieldEl.parentElement.querySelector('.sadaya-field-error');
    if (!errorEl) {
        errorEl = document.createElement('div');
        errorEl.className = 'sadaya-field-error';
        fieldEl.parentElement.appendChild(errorEl);
    }
    errorEl.textContent = '⚠ ' + message;
}

function clearFieldError(fieldEl) {
    fieldEl.classList.remove('is-invalid');
    const errorEl = fieldEl.parentElement.querySelector('.sadaya-field-error');
    if (errorEl) errorEl.textContent = '';
}

// =====================
// INIT ON DOM READY
// =====================
document.addEventListener('DOMContentLoaded', function () {

    // Init all file uploads
    document.querySelectorAll('.sadaya-file-upload, .sadaya-file-container').forEach(initFileUpload);

    // Password strength meter
    const pwdInput = document.getElementById('password');
    const pwdBars = document.querySelector('.sadaya-pwd-bars');
    const pwdLabel = document.querySelector('.sadaya-pwd-label');

    if (pwdInput && pwdBars) {
        pwdInput.addEventListener('input', () => {
            updatePasswordStrength(pwdInput.value, pwdBars, pwdLabel);
        });
    }

    // Password toggle buttons
    document.querySelectorAll('[data-sadaya-toggle-pwd]').forEach(btn => {
        const targetId = btn.getAttribute('data-sadaya-toggle-pwd');
        const target = document.getElementById(targetId);
        initPasswordToggle(target, btn);
    });

    // NIK: digits only
    document.querySelectorAll('[data-sadaya-nik]').forEach(input => {
        input.addEventListener('input', () => {
            input.value = input.value.replace(/\D/g, '').slice(0, 16);
        });
    });

    // Phone validation feedback
    document.querySelectorAll('[data-sadaya-phone]').forEach(input => {
        input.addEventListener('blur', () => {
            const val = input.value.trim();
            if (val && !validatePhoneID(val)) {
                showFieldError(input, 'Format: +628123456789 (minimal 12 digit)');
            } else {
                clearFieldError(input);
            }
        });
    });

    // NPWP digits only
    document.querySelectorAll('[data-sadaya-npwp]').forEach(input => {
        input.addEventListener('input', () => {
            input.value = input.value.replace(/\D/g, '').slice(0, 16);
        });
    });

    // Confirm password match check
    const pwdConfirm = document.getElementById('password_confirm');
    if (pwdInput && pwdConfirm) {
        pwdConfirm.addEventListener('blur', () => {
            if (pwdInput.value && pwdConfirm.value !== pwdInput.value) {
                showFieldError(pwdConfirm, 'Kata sandi tidak sesuai');
            } else {
                clearFieldError(pwdConfirm);
            }
        });
    }

    // Submit button loading state
    document.querySelectorAll('.sadaya-form-submit').forEach(btn => {
        const form = btn.closest('form');
        if (form) {
            form.addEventListener('submit', () => {
                btn.classList.add('loading');
                btn.innerHTML = '<span class="sadaya-spinner"></span> Memproses...';
            });
        }
    });

    // Navbar mobile toggle (simple)
    const navToggle = document.querySelector('.sadaya-nav-toggle');
    const sidebar = document.querySelector('.sadaya-sidebar');
    if (navToggle && sidebar) {
        navToggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
    }

});
