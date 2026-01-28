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
    
    # Start with the source filename
    path = source_filename
    
    # Build the options suffix
    opts = []
    
    # Add size
    if 'size' in opts_dict:
        opts.append('%sx%s' % tuple(opts_dict['size']))
    
    # Add quality
    if 'quality' in opts_dict:
        opts.append('q%s' % opts_dict['quality'])
    
    # Add box parameter if present - check both places
    box = opts_dict.get('box') or thumbnail_options.get('box')
    
    if box:
        if isinstance(box, str):
            # If box is a string like "0,0,100,100", use it directly  
            opts.append('box-%s' % box)
        else:
            # If box is a tuple/list, format it
            opts.append('box-%s' % ','.join(str(int(x)) for x in box))
    
    # Add other boolean options
    for key in ['crop', 'upscale', 'detail', 'sharpen', 'bw']:
        if opts_dict.get(key):
            opts.append(key)
    
    # Join all options
    opts_str = '_'.join(opts)
    
    # Return the final filename
    result = '%s.%s%s' % (path, opts_str, thumbnail_extension)
    return result
