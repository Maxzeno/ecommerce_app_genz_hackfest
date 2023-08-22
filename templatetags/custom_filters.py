from django import template

register = template.Library()

@register.filter(name='subtract')
def subtract(value, arg):
	return int(value) - int(arg)


@register.filter(name='format_price')
def format_number(value):
    if value is None:
        return ''
    return '{:,.2f}'.format(value)


def image_url_path(value, path='/static/img/NA-removebg.png'):
	if value and hasattr(value, 'url') and value.url:
		return value.url
	return path

@register.filter(name='image_url')
def image_url(value):
	return image_url_path(value)


@register.filter(name='image_user_url')
def image_user_url(value):
    return image_url_path(value, '/static/img/person.png')
   
