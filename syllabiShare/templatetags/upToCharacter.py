from django import template

register = template.Library()

@register.filter(needs_autoescape=True)
def upToCharacter(text, char, autoescape=True):
    index = text.index(char)
    if index > 0:
        return text[0:index]
    return text