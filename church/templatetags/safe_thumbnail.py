"""
Custom template tag for safe thumbnail generation that handles errors gracefully.
"""
from django import template
from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.exceptions import InvalidImageFormatError
from django.core.files.storage import default_storage
from PIL import Image as PILImage
import logging

register = template.Library()
logger = logging.getLogger(__name__)


class SafeThumbnailNode(template.Node):
    def __init__(self, image_field, size, box_var, crop, detail, var_name):
        self.image_field = template.Variable(image_field)
        self.size = size
        self.box_var = template.Variable(box_var) if box_var else None
        self.crop = crop
        self.detail = detail
        self.var_name = var_name
    
    def render(self, context):
        try:
            image_field = self.image_field.resolve(context)
            
            if not image_field or not image_field.name:
                context[self.var_name] = None
                return ''
            
            # Check if file exists
            if not default_storage.exists(image_field.name):
                context[self.var_name] = None
                return ''
            
            # Try to validate the image file
            try:
                with default_storage.open(image_field.name, 'rb') as f:
                    PILImage.open(f).verify()
            except Exception:
                # Image is corrupted or invalid
                logger.warning(f"Invalid image file: {image_field.name}")
                context[self.var_name] = None
                return ''
            
            # Generate thumbnail
            thumbnailer = get_thumbnailer(image_field)
            
            options = {
                'size': self.size,
                'crop': self.crop,
                'detail': self.detail,
            }
            
            if self.box_var:
                try:
                    box = self.box_var.resolve(context)
                    if box:
                        options['box'] = box
                except template.VariableDoesNotExist:
                    pass
            
            thumbnail = thumbnailer.get_thumbnail(options)
            context[self.var_name] = thumbnail
            return ''
            
        except (InvalidImageFormatError, IOError, OSError, Exception) as e:
            logger.warning(f"Failed to generate thumbnail for {image_field.name if 'image_field' in locals() else 'unknown'}: {e}")
            context[self.var_name] = None
            return ''


@register.tag(name='safe_thumbnail')
def safe_thumbnail_tag(parser, token):
    """
    Safely generate a thumbnail, setting the variable to None if the image is invalid.
    
    Usage:
        {% safe_thumbnail article.image "800x600" box=article.image_cropping crop=True detail=True as thumb %}
        {% if thumb %}
            <img src="{{ thumb.url }}" alt="...">
        {% else %}
            <!-- fallback -->
        {% endif %}
    """
    bits = token.split_contents()
    if len(bits) < 4:
        raise template.TemplateSyntaxError(
            "'safe_thumbnail' tag requires at least image field and size"
        )
    
    image_field = bits[1]
    size_str = bits[2].strip('"\'')
    
    # Parse size
    try:
        width, height = map(int, size_str.split('x'))
        size = (width, height)
    except ValueError:
        raise template.TemplateSyntaxError(
            f"Invalid size format: {size_str}. Expected format: '800x600'"
        )
    
    box_var = None
    crop = True
    detail = False
    var_name = None
    
    i = 3
    while i < len(bits):
        bit = bits[i]
        if bit == 'box':
            if i + 1 >= len(bits):
                raise template.TemplateSyntaxError("'box' requires a value")
            box_var = bits[i + 1]
            i += 2
        elif bit == 'crop':
            if i + 1 >= len(bits):
                raise template.TemplateSyntaxError("'crop' requires a value")
            crop = bits[i + 1].lower() == 'true'
            i += 2
        elif bit == 'detail':
            if i + 1 >= len(bits):
                raise template.TemplateSyntaxError("'detail' requires a value")
            detail = bits[i + 1].lower() == 'true'
            i += 2
        elif bit == 'as':
            if i + 1 >= len(bits):
                raise template.TemplateSyntaxError("'as' requires a variable name")
            var_name = bits[i + 1]
            i += 2
        else:
            i += 1
    
    if not var_name:
        raise template.TemplateSyntaxError("'safe_thumbnail' tag requires 'as variable_name'")
    
    return SafeThumbnailNode(image_field, size, box_var, crop, detail, var_name)
