"""
Custom thumbnail namer for easy-thumbnails that includes the 'box' parameter in filenames.
This ensures that thumbnails with different crop boxes are treated as separate files.
"""
from easy_thumbnails import utils


def custom_namer(thumbnailer, prepared_options, source_filename, thumbnail_extension, **kwargs):
    """
    Custom namer that includes the 'box' parameter in the thumbnail filename.
    
    This is necessary when using image cropping with easy-thumbnails + GCS backend,
    as the default namer doesn't include the box parameter in the filename.
    
    Also handles simple size-only requests from admin widgets (e.g., 300x300).
    """
    # Get the thumbnail options - prepared_options might be a list
    thumbnail_options = kwargs.get('thumbnail_options', {})
    
    # If prepared_options is a list (as it can be), convert to dict-like access
    opts_dict = {}
    if isinstance(prepared_options, (list, tuple)):
        for item in prepared_options:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                opts_dict[item[0]] = item[1]
            elif isinstance(item, str) and 'x' in item:
                # This is likely the size string like '300x400'
                try:
                    w, h = map(int, item.split('x'))
                    opts_dict['size'] = (w, h)
                except ValueError:
                    pass
    
    # Also check thumbnail_options dict directly
    if isinstance(thumbnail_options, dict):
        opts_dict.update(thumbnail_options)
    
    # Start with the source filename - normalize to forward slashes for GCS/Linux
    path = source_filename.replace('\\', '/')
    
    # Build the options suffix
    opts = []
    
    # Add size (required)
    if 'size' in opts_dict:
        size = opts_dict['size']
        if isinstance(size, (list, tuple)):
            opts.append('%sx%s' % tuple(size))
        else:
            opts.append(str(size))
    elif 'width' in opts_dict and 'height' in opts_dict:
        opts.append('%sx%s' % (opts_dict['width'], opts_dict['height']))
    
    # Add quality (if specified)
    if 'quality' in opts_dict:
        opts.append('q%s' % opts_dict['quality'])
    
    # Add box parameter if present - check both places
    box = opts_dict.get('box') or thumbnail_options.get('box')
    
    if box:
        if isinstance(box, str):
            # If box is a string like "0,0,100,100", use it directly  
            opts.append('box-%s' % box.replace(',', '_')) # Use underscore to avoid URL enc issues
        else:
            # If box is a tuple/list, format it
            opts.append('box-%s' % ','.join(str(int(x)) for x in box).replace(',', '_'))
    
    # Add other boolean options (only if True)
    for key in ['crop', 'upscale', 'detail', 'sharpen', 'bw']:
        if opts_dict.get(key) is True:
            opts.append(key)
    
    # Join all options - if only size, use simple format for admin compatibility
    if len(opts) == 1 and 'x' in opts[0]:
        # Simple size-only request (e.g., from admin widget) - use simple format
        opts_str = opts[0]
    else:
        opts_str = '_'.join(opts)
    
    # Return the final filename
    import os
    base_path, _ = os.path.splitext(path)
    # Ensure extension starts with a dot
    ext = thumbnail_extension
    if ext and not ext.startswith('.'):
        ext = '.' + ext
    
    result = '%s.%s%s' % (base_path, opts_str, ext)
    return result
