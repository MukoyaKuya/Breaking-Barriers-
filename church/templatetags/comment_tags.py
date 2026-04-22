from django import template
from django.contrib.contenttypes.models import ContentType
from ..models import ArticleComment
from ..forms import ArticleCommentForm

register = template.Library()

@register.inclusion_tag('church/partials/comments_section.html', takes_context=True)
def render_comments(context, obj):
    """
    Renders the comments section for any given model instance.
    Includes the list of approved comments and the submission form.
    """
    request = context['request']
    ct = ContentType.objects.get_for_model(obj)
    
    # Fetch approved comments for this object
    comments = ArticleComment.objects.filter(
        content_type=ct, 
        object_id=obj.id, 
        is_approved=True
    )
    
    # Instantiate an empty form for submission
    form = ArticleCommentForm()
    
    return {
        'request': request,
        'obj': obj,
        'content_type_id': ct.id,
        'comments': comments,
        'form': form,
    }
