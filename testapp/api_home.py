from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import redirect

@api_view(['GET'])
def api_home(request):
    """
    API Home - Welcome endpoint
    """
    return Response({
        "message": "Welcome to MIT ADT Mess Management API",
        "version": "1.0.0",
        "documentation": request.build_absolute_uri('/api/docs/'),
        "endpoints": {
            "api_docs": "/api/docs/",
            "raj_mess": "/api/raj-mess/",
            "notices": "/api/notices/",
            "rate_dish": "/api/rate-dish/",
            "complaint": "/api/complaint/",
        }
    })
