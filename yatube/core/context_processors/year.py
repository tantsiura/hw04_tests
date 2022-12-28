from django.utils import timezone


def year(request):
    today = timezone.localtime(timezone.now())
    year = str(today.year)
    return {
        'year': year,
    }
