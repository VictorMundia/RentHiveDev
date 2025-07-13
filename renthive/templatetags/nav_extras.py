defaultregister = template.Library()
from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def is_minimal_nav(context):
    request = context.get('request')
    # Minimal nav for login, registration, and password reset pages
    if request and request.path in [
        '/accounts/login/', '/users/register/', '/users/password_reset/', '/users/reset/', '/users/reset/done/'
    ]:
        return True
    return False
