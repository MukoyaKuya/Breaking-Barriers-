/**
 * Refresh image preview in admin when a new image is uploaded
 * This fixes the issue where uploaded images don't display immediately
 */
(function($) {
    'use strict';
    if (!$) return;
    
    function refreshImagePreview(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            var $input = $(input);
            var $field = $input.closest('.form-row, .field-image, .field-photo, .field-logo, .aligned');
            
            reader.onload = function(e) {
                // Update any existing preview images in the field
                $field.find('img.image-preview, img[src*="/media/"]').attr('src', e.target.result);
                
                // Find the image cropping widget if it exists
                var $croppingWidget = $input.closest('.form-row').next('.form-row').find('.image-cropping-widget, .image-cropping-container');
                if ($croppingWidget.length) {
                    // Update the cropping widget preview
                    $croppingWidget.find('img').attr('src', e.target.result);
                }
                
                // Create or update a preview image after the file input
                var $preview = $field.find('.upload-preview');
                if ($preview.length === 0) {
                    $preview = $('<div>', {
                        class: 'upload-preview',
                        style: 'margin-top: 10px;'
                    });
                    $input.after($preview);
                }
                
                $preview.html(
                    $('<img>', {
                        src: e.target.result,
                        style: 'max-width: 300px; max-height: 300px; border: 1px solid #ddd; padding: 5px; background: #fff;',
                        class: 'preview-image'
                    })
                );
            };
            
            reader.readAsDataURL(input.files[0]);
        }
    }
    
    $(document).ready(function() {
        // Handle file input changes for image fields
        $(document).on('change', 'input[type="file"][accept*="image"], input[type="file"][name*="image"], input[type="file"][name*="photo"], input[type="file"][name*="logo"]', function() {
            refreshImagePreview(this);
        });
        
        // Also handle dynamically added file inputs (for inlines)
        $(document).on('formset:added', function(event, $row) {
            $row.find('input[type="file"][accept*="image"]').on('change', function() {
                refreshImagePreview(this);
            });
        });
    });
})(typeof django !== 'undefined' ? django.jQuery : (typeof jQuery !== 'undefined' ? jQuery : null));
