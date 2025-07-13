from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css):
    # Only add class, do not override input type
    return field.as_widget(attrs={"class": css})
