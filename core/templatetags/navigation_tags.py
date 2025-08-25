from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
@register.filter
def active(context, *url_names):
    """
    Usage: {% active 'welcome-page' 'another-name' %}
    Returns 'font-bold aria-current="page"' if current url_name is one of url_names, otherwise ''.
    """
    try:
        current = context['request'].resolver_match.url_name
    except Exception:
        return ''
    if current in url_names:
        return 'font-bold text-green-200 aria-current="page"'
    return ''

"""
highlight selected nav item.
alternative to using templatetags, in html file:
<a href="{% url 'welcome-page' %}"
     class="hover:text-blue-200 {% if request.resolver_match.url_name == 'welcome-page' %}font-bold{% endif %}"
     {% if request.resolver_match.url_name == 'welcome-page' %}aria-current="page"{% endif %}>
    Home
</a>
"""