(function () {
  'use strict';

  let formValidator;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  function init() {
    const form = document.getElementById('contact-form');
    if (!form) return;

    formValidator = new FormValidator(form, {
      name: {
        required: true,
        minLength: 2,
        maxLength: 100,
        requiredMessage: 'Lütfen adınızı ve soyadınızı girin',
        minLengthMessage: 'Ad soyad en az 2 karakter olmalıdır',
      },
      email: {
        required: true,
        email: true,
        requiredMessage: 'Lütfen e-posta adresinizi girin',
        emailMessage: 'Geçerli bir e-posta adresi girin',
      },
      phone: {
        required: false,
        pattern: /^[\d\s+\-()]+$/,
        patternMessage: 'Geçerli bir telefon numarası girin',
      },
      subject: {
        required: true,
        minLength: 3,
        maxLength: 200,
        requiredMessage: 'Lütfen mesajınızın konusunu girin',
        minLengthMessage: 'Konu en az 3 karakter olmalıdır',
      },
      message: {
        required: true,
        minLength: 10,
        maxLength: 1000,
        requiredMessage: 'Lütfen mesajınızı girin',
        minLengthMessage: 'Mesaj en az 10 karakter olmalıdır',
        maxLengthMessage: 'Mesaj en fazla 1000 karakter olmalıdır',
      },
    });

    prefillFromUrl(form);
    form.addEventListener('submit', handleSubmit);

    form.querySelectorAll('.form-input, .form-textarea').forEach((field) => {
      field.addEventListener('blur', () => {
        if (field.value) {
          formValidator.validateField(field.name, field.value);
          formValidator.showErrors();
        }
      });
      field.addEventListener('input', () => {
        const errorElement = document.getElementById(`${field.name}-error`);
        if (errorElement?.classList.contains('show')) {
          errorElement.classList.remove('show');
          field.classList.remove('error');
          field.removeAttribute('aria-invalid');
        }
      });
    });
  }

  function prefillFromUrl(form) {
    const params = new URLSearchParams(window.location.search);
    const konu = params.get('konu');
    const subjectField = form.elements.subject;
    if (!konu || !subjectField) return;

    const productName = decodeURIComponent(konu.replace(/\+/g, ' ')).trim();
    if (productName) {
      subjectField.value = `Fiyat Teklifi - ${productName}`;
    }
  }

  function handleSubmit(e) {
    e.preventDefault();
    formValidator.hideSuccess();

    if (!formValidator.validate()) {
      document.querySelector('.form-input.error, .form-textarea.error')?.focus();
      return;
    }

    const form = document.getElementById('contact-form');
    const submitBtn = form?.querySelector('[type="submit"]');
    const payload = {
      type: 'contact',
      name: form.elements.name?.value?.trim() || '',
      email: form.elements.email?.value?.trim() || '',
      phone: form.elements.phone?.value?.trim() || '',
      subject: form.elements.subject?.value?.trim() || '',
      message: form.elements.message?.value?.trim() || '',
      website: document.getElementById('contact-website')?.value || '',
    };

    if (submitBtn) {
      submitBtn.disabled = true;
    }

    sendFormMail(payload)
      .then(() => {
        formValidator.showSuccess(
          '✓ Mesajınız başarıyla gönderildi! En kısa sürede size dönüş yapacağız.'
        );
        setTimeout(() => formValidator.reset(), 3000);
      })
      .catch((err) => {
        const messageEl = document.getElementById('message-error');
        if (messageEl) {
          messageEl.textContent = err.message || 'Gönderim başarısız.';
          messageEl.classList.add('show');
          document.getElementById('message')?.classList.add('error');
        }
      })
      .finally(() => {
        if (submitBtn) submitBtn.disabled = false;
      });
  }
})();
