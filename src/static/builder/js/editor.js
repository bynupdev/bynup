class WebsiteBuilder {
    constructor(templateName) {
        this.templateName = templateName;
        this.textContents = {};
        this.styleCustomizations = {};
        this.init();
    }

    init() {
        this.loadTemplate();
        this.setupEventListeners();
        this.loadExistingData();
    }

    loadTemplate() {
        const previewContainer = document.getElementById('template-preview');
        if (!previewContainer) return;

        fetch(`/builder/template/${this.templateName}/`)
            .then(response => {
                if (!response.ok) throw new Error('Template not found');
                return response.text();
            })
            .then(html => {
                previewContainer.innerHTML = html;
                this.setupEditableElements();
            })
            .catch(error => {
                previewContainer.innerHTML = `
                    <div class="alert alert-danger text-center">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Failed to load template: ${error.message}
                    </div>
                `;
            });
    }

    setupEditableElements() {
        // Make text elements editable
        document.querySelectorAll('.editable-text').forEach(element => {
            element.addEventListener('click', (e) => {
                this.editText(element);
            });
            
            // Add hover effects
            element.addEventListener('mouseenter', (e) => {
                element.style.outline = '2px dashed #4361ee';
                element.style.cursor = 'text';
            });
            
            element.addEventListener('mouseleave', (e) => {
                if (!element.hasAttribute('data-editing')) {
                    element.style.outline = '';
                }
            });
        });

        // Make sections styleable
        document.querySelectorAll('.editable-section').forEach(element => {
            element.addEventListener('mouseenter', (e) => {
                element.style.outline = '2px dashed #f72585';
                element.style.cursor = 'pointer';
            });
            
            element.addEventListener('mouseleave', (e) => {
                if (!element.hasAttribute('data-editing')) {
                    element.style.outline = '';
                }
            });
        });
    }

    editText(element) {
        const elementId = element.getAttribute('data-text');
        const currentText = element.textContent;
        
        // Create textarea for editing
        const input = document.createElement('textarea');
        input.value = currentText;
        input.style.width = '100%';
        input.style.height = '100px';
        input.style.padding = '8px';
        input.style.border = '2px solid #4361ee';
        input.style.borderRadius = '4px';
        
        element.innerHTML = '';
        element.appendChild(input);
        element.setAttribute('data-editing', 'true');
        input.focus();
        
        const saveText = () => {
            const newText = input.value;
            element.textContent = newText;
            element.removeAttribute('data-editing');
            this.textContents[elementId] = newText;
            this.updateHiddenFields();
        };
        
        input.addEventListener('blur', saveText);
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                saveText();
            }
        });
    }

    updateStyle(elementId, property, value) {
        if (!this.styleCustomizations[elementId]) {
            this.styleCustomizations[elementId] = {};
        }
        this.styleCustomizations[elementId][property] = value;
        this.updateHiddenFields();
    }

    updateHiddenFields() {
        const textContentsField = document.getElementById('text-contents');
        const styleCustomizationsField = document.getElementById('style-customizations');
        
        if (textContentsField) {
            textContentsField.value = JSON.stringify(this.textContents);
        }
        
        if (styleCustomizationsField) {
            styleCustomizationsField.value = JSON.stringify(this.styleCustomizations);
        }
    }

    loadExistingData() {
        // Load existing text contents
        const existingTexts = document.getElementById('existing-text-contents');
        if (existingTexts && existingTexts.value) {
            try {
                this.textContents = JSON.parse(existingTexts.value);
            } catch (e) {
                console.error('Error parsing existing text contents:', e);
            }
        }
        
        // Load existing style customizations
        const existingStyles = document.getElementById('existing-style-customizations');
        if (existingStyles && existingStyles.value) {
            try {
                this.styleCustomizations = JSON.parse(existingStyles.value);
            } catch (e) {
                console.error('Error parsing existing style customizations:', e);
            }
        }
    }

    setupEventListeners() {
        // Color pickers
        document.querySelectorAll('.color-picker').forEach(picker => {
            picker.addEventListener('input', (e) => {
                const elementId = e.target.getAttribute('data-element');
                const property = e.target.getAttribute('data-property');
                this.updateStyle(elementId, property, e.target.value);
                
                // Update preview
                document.querySelectorAll(`[data-section="${elementId}"]`).forEach(el => {
                    el.style[property] = e.target.value;
                });
            });
        });

        // Font size
        const fontSizeSelect = document.getElementById('font-size');
        if (fontSizeSelect) {
            fontSizeSelect.addEventListener('change', (e) => {
                this.updateStyle('global', 'font_size', e.target.value);
                document.body.style.fontSize = e.target.value;
            });
        }
    }
}

// Initialize builder when page loads
document.addEventListener('DOMContentLoaded', function() {
    const templateNameElement = document.getElementById('template-name');
    if (templateNameElement) {
        const templateName = templateNameElement.value;
        window.websiteBuilder = new WebsiteBuilder(templateName);
    }
});
 













