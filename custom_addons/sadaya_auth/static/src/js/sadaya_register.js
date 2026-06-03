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
    // FORM SUBMIT VALIDATION
    // =====================
    const registerForm = document.getElementById('sadaya-register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', function (e) {
            let hasError = false;

            // Check swafoto required
            const swafotoFile = document.getElementById('swafoto_ktp');
            if (swafotoFile && !swafotoFile.files.length) {
                const errEl = document.getElementById('swafoto_error');
                if (errEl) errEl.textContent = 'Swafoto memegang KTP wajib diunggah';
                hasError = true;
            }

            if (hasError) {
                e.preventDefault();
                // Scroll to first error
                const firstError = registerForm.querySelector('.sadaya-field-error:not(:empty), [id$="_error"]:not(:empty)');
                if (firstError) {
                    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
        });
    }

});
