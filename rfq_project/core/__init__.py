from rest_framework.response import Response

def get(self, request, *args, **kwargs):
    if request.user and request.user.is_authenticated:
        # ... your redirect logic ...
        pass
    # If not authenticated, show a message or render a template
    return Response({"detail": "Please POST your credentials to this endpoint to obtain a token."}, status=405)



