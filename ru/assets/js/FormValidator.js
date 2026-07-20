// FormValidator Class
/* exported FormValidator */
class FormValidator {
  constructor(formElement, validationRules) {
    this.form = formElement;
    this.rules = validationRules || {};
    this.errors = {};
  }

  validate() {
    this.errors = {};
    let isValid = true;
    this.clearErrors();

    for (const fieldName in this.rules) {
      const field = this.form.elements[fieldName];
      if (!field) continue;
      const fieldValid = this.validateField(fieldName, field.value);
      if (!fieldValid) isValid = false;
    }

    if (!isValid) this.showErrors();
    return isValid;
  }

  validateField(fieldName, value) {
    const rules = this.rules[fieldName];
    if (!rules) return true;

    if (rules.required && (!value || value.trim() === '')) {
      this.errors[fieldName] =
        rules.requiredMessage ||
        (typeof t === 'function' ? t('validation.required') : 'validation.required');
      return false;
    }

    if (!value || value.trim() === '') return true;

    if (rules.email) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(value)) {
        this.errors[fieldName] =
          rules.emailMessage ||
          (typeof t === 'function' ? t('validation.email') : 'validation.email');
        return false;
      }
    }

    if (rules.minLength && value.length < rules.minLength) {
      this.errors[fieldName] =
        rules.minLengthMessage ||
        (typeof t === 'function'
          ? t('validation.minLength', { min: rules.minLength })
          : 'validation.minLength');
      return false;
    }

    if (rules.maxLength && value.length > rules.maxLength) {
      this.errors[fieldName] =
        rules.maxLengthMessage ||
        (typeof t === 'function'
          ? t('validation.maxLength', { max: rules.maxLength })
          : 'validation.maxLength');
      return false;
    }

    if (rules.pattern && !rules.pattern.test(value)) {
      this.errors[fieldName] =
        rules.patternMessage ||
        (typeof t === 'function' ? t('validation.pattern') : 'validation.pattern');
      return false;
    }

    if (rules.custom && typeof rules.custom === 'function') {
      const customResult = rules.custom(value);
      if (customResult !== true) {
        this.errors[fieldName] =
          customResult ||
          (typeof t === 'function' ? t('validation.invalid') : 'validation.invalid');
        return false;
      }
    }

    return true;
  }

  showErrors() {
    for (const fieldName in this.errors) {
      const errorElement = document.getElementById(`${fieldName}-error`);
      const fieldElement = this.form.elements[fieldName];
      if (errorElement) {
        errorElement.textContent = this.errors[fieldName];
        errorElement.classList.add('show');
      }
      if (fieldElement) {
        fieldElement.classList.add('error');
        fieldElement.setAttribute('aria-invalid', 'true');
      }
    }
  }

  clearErrors() {
    this.errors = {};
    this.form.querySelectorAll('.form-error').forEach((el) => {
      el.textContent = '';
      el.classList.remove('show');
    });
    this.form.querySelectorAll('.form-input, .form-textarea').forEach((field) => {
      field.classList.remove('error');
      field.removeAttribute('aria-invalid');
    });
  }

  showSuccess(message) {
    const successElement = document.getElementById('form-success');
    if (successElement) {
      if (message) successElement.querySelector('p').textContent = message;
      successElement.classList.add('show');
      successElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }

  hideSuccess() {
    document.getElementById('form-success')?.classList.remove('show');
  }

  reset() {
    this.form.reset();
    this.clearErrors();
    this.hideSuccess();
  }

  getFormData() {
    const formData = {};
    for (let i = 0; i < this.form.elements.length; i++) {
      const element = this.form.elements[i];
      if (element.name && element.type !== 'submit') {
        formData[element.name] = element.value;
      }
    }
    return formData;
  }
}
