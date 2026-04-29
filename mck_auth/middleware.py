# mck_auth/middleware.py
from django.http import HttpResponseForbidden
from django.urls import reverse
from django.shortcuts import redirect

class AdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Prevent website users from accessing admin routes
        if request.path.startswith('/admin/') or request.path.startswith('/console/'):
            if request.user.is_authenticated and not request.user.is_staff:
                return HttpResponseForbidden("Website users cannot access the admin panel.")
        
        # Prevent admin users from accessing website user areas if needed
        if request.path.startswith('/website/') and request.user.is_authenticated and request.user.is_staff:
            # Allow admin to access website if you want, or redirect:
            # return redirect('mck_admin_console:mck_dashboard')
            pass
            
        return None