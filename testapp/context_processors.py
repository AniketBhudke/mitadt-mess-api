"""
Context processors for safe user authentication handling
"""

def safe_auth(request):
    """
    Safely provide user authentication status even when session tables are missing
    """
    try:
        is_authenticated = request.user.is_authenticated
        user = request.user if is_authenticated else None
        return {
            'safe_user_authenticated': is_authenticated,
            'safe_user': user,
            'auth_error': False
        }
    except Exception as e:
        # If session/auth tables are missing, provide safe defaults
        return {
            'safe_user_authenticated': False,
            'safe_user': None,
            'auth_error': True,
            'auth_error_message': str(e)
        }