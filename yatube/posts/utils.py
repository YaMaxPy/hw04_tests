from django.core.paginator import Paginator

POSTS_ON_PAGE: int = 10


def paginator(request, object):
    paginator = Paginator(object, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'paginator': paginator,
        'page_number': page_number,
        'page_obj': page_obj,
    }
