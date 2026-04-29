# middleware.py — COMPLETE FIXED VERSION

from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
import logging
import re
import os

logger = logging.getLogger(__name__)


class RegistrationStatusMiddleware:
    """
    Enforce profile → payment → access flow.
    Production-safe with no redirect loops.
    """

    # ✅ Paths that are ALWAYS accessible (no auth checks)
    PUBLIC_PATHS = [
        '/',
        '/admin/',
        '/auth/',
        '/static/',
        '/media/',  # ✅ ADDED BACK - media files should be publicly accessible
    ]

    # ✅ These named URLs are exempt from profile/payment checks
    EXEMPT_NAMED_URLS = [
        'mck_auth:website_signin',
        'mck_auth:website_signup',
        'mck_auth:verify_otp',
        'mck_auth:resend_otp',
        'mck_website:profile_completion',
        'mck_website:payment_gateway',
        'mck_website:payment_success',
        'mck_website:payment_success_page',
        'mck_website:payment_failure',
        'mck_website:payment_callback',
        'mck_website:home_page',
        'mck_website:about_page',
        'mck_website:privacy_policy_page',
        'mck_website:terms_page',
        'mck_website:contact-us',
    ]

    # ✅ URL path prefixes always exempt (AJAX, static, etc.)
    EXEMPT_PATH_PREFIXES = [
        '/ajax/',
        '/static/',
        '/admin/',
        '/auth/',
        '/media/',  # ✅ ADDED BACK - ensure media is always accessible
    ]

    # 🔒 Pages that require payment (block if user hasn't paid)
    PAYMENT_REQUIRED_PATTERNS = [
        r'^/profile/\d+/$',           # Profile detail: /profile/123/
        r'^/Profile-detail/$',          # Profile listing page
        r'^/Profile-detail$',            # Without trailing slash
        r'^/community-match/$',          # Community match page
        r'^/community-match$',            # Without trailing slash
    ]

    # ❌ REMOVED MEDIA_PROTECTED_PATTERNS entirely since we want media accessible

    def __init__(self, get_response):
        self.get_response = get_response
        self._exempt_paths = None  # Lazy-resolved
        self._payment_required_patterns = [re.compile(pattern) for pattern in self.PAYMENT_REQUIRED_PATTERNS]
        # ❌ Removed media protected patterns initialization

    def _get_exempt_paths(self):
        """Resolve named URLs once and cache them."""
        if self._exempt_paths is None:
            paths = set()
            for name in self.EXEMPT_NAMED_URLS:
                try:
                    paths.add(reverse(name))
                except Exception:
                    pass
            self._exempt_paths = paths
        return self._exempt_paths

    def _requires_payment(self, path):
        """Check if the current path requires payment."""
        for pattern in self._payment_required_patterns:
            if pattern.match(path):
                return True
        return False

    # ❌ Removed _is_protected_media method

    def _serve_forbidden_image(self):
        """Return a forbidden response or a placeholder image."""
        return HttpResponseForbidden("Access denied")

    def __call__(self, request):
        # ─── 1. First check if path is media - ALWAYS allow access ───
        if request.path.startswith('/media/'):
            return self.get_response(request)

        if not request.user.is_authenticated:
            # For unauthenticated users, still allow access to media
            return self.get_response(request)

        path = request.path
        is_ajax = (
            request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            or request.content_type == 'application/json'
        )

        # ─── 2. Always-exempt prefixes (includes media now) ───
        if any(path.startswith(p) for p in self.EXEMPT_PATH_PREFIXES):
            return self.get_response(request)

        # ─── 3. Named-URL exemptions ───
        exempt_paths = self._get_exempt_paths()
        if path in exempt_paths:
            return self.get_response(request)

        # ─── 4. Public path prefixes ───
        if any(path.startswith(p) for p in self.PUBLIC_PATHS):
            return self.get_response(request)

        # ─── 5. Check profile completion ───
        if not getattr(request.user, 'is_profile_completed', False):
            logger.debug(f"User {request.user.email} needs to complete profile, path={path}")
            if is_ajax:
                return JsonResponse({
                    "success": False,
                    "message": "Please complete your profile first.",
                    "redirect": reverse('mck_website:profile_completion')
                }, status=403)
            messages.warning(request, "Please complete your profile first.")
            return redirect('mck_website:profile_completion')

        # ─── 6. Check payment for protected pages ───
        if self._requires_payment(path):
            # Check if user has paid
            has_paid = getattr(request.user, 'has_paid', False)
            if not has_paid:
                # Re-query DB to avoid stale cache
                has_paid = request.user.payments.filter(status='COMPLETED').exists()
            
            if not has_paid:
                logger.debug(f"User {request.user.email} needs to pay to access protected page: {path}")
                if is_ajax:
                    return JsonResponse({
                        "success": False,
                        "message": "Please complete payment to access profiles and community features.",
                        "redirect": reverse('mck_website:payment_gateway')
                    }, status=403)
                messages.warning(request, "Please complete your payment to access profiles and community features.")
                return redirect('mck_website:payment_gateway')
        
        # ─── 7. Original payment check for all other pages ───
        elif not request.user.has_paid:
            # Re-query DB to avoid stale cache
            has_paid = request.user.payments.filter(status='COMPLETED').exists()
            if not has_paid:
                logger.debug(f"User {request.user.email} needs to pay, path={path}")
                if is_ajax:
                    return JsonResponse({
                        "success": False,
                        "message": "Please complete payment to access all features.",
                        "redirect": reverse('mck_website:payment_gateway')
                    }, status=403)
                messages.warning(request, "Please complete your payment to continue.")
                return redirect('mck_website:payment_gateway')

        return self.get_response(request)