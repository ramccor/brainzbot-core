from django.utils import timezone

class TimezoneMiddleware:
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        tz = request.session.get('django_timezone', "UTC") or "UTC"
        timezone.activate(tz)

        response = self.get_response(request)
        
        # Code to be executed for each response after the view is called
        return response

    # For backwards compatibility with old-style middleware
    def process_request(self, request):
        tz = request.session.get('django_timezone', "UTC") or "UTC"
        timezone.activate(tz)
