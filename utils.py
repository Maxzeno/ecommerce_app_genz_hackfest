from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django_user_agents.utils import get_user_agent
from core.models import Category, SubCategory

def popular_categories():
	categories = Category.objects.order_by('ordered')[:8]
	return {'categories': categories}


def popular_categories_and_sub():
	""" Returns list of categories and sub ordered by ordered """
	categories = Category.objects.order_by('ordered').values('id', 'name')
	result = []
	for category in categories:
		result.append([
			category['name'],
			[ data[0] for data in SubCategory.objects.filter(category=category['id']).values_list('name') ]
		])
	return {'categories_and_sub': result}


def paginate_page(products, request, error, obj, per_page=12, name='page', on_each_side=0, on_ends=1):
	paginator = Paginator(products, per_page)
	page_number = request.GET.get(name)

	try:
		page_obj = paginator.page(page_number)
	except PageNotAnInteger:
		page_obj = paginator.page(1)
	except EmptyPage:
		raise error("The resource you requested does not exist")

	page_list = page_obj.paginator.get_elided_page_range(page_obj.number, on_each_side=on_each_side, on_ends=on_ends)
	return {'page_list': page_list, obj: page_obj}


def is_mobile(request):
	user_agent = get_user_agent(request)
	return user_agent.is_mobile
