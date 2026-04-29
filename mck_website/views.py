# mck_website/views.py - Cleaned Version
# ============================================================================
# views_payment_plans.py
# Drop this content into mck_website/views.py (replace the relevant sections)
# ============================================================================

# ─────────────────────────────────────────────────────────────────────────────
# DECORATORS  (replace existing payment_required decorator)
# ─────────────────────────────────────────────────────────────────────────────
import os
import json
import logging
import random
import uuid
from datetime import date, timedelta
from decimal import Decimal, DecimalException

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Prefetch, Q
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, DetailView, ListView
from django.views.decorators.csrf import csrf_protect

import razorpay

from config import app_logger, app_seo as seo
from mck_website.api import *
from mck_website.models import *
from mck_auth import build_table as bt, role_validations as rv

from mck_master.models import Profile, Notification, Wishlist
from mck_admin_console.models import Gallery, Contact

LOG_NAME = "app"
logger = app_logger.createLogger(LOG_NAME)


# decorators.py
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from functools import wraps
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

# ============================================================================
# STEP 1 — Run migrations to add the new fields
# ============================================================================

# In your terminal:
# python manage.py makemigrations mck_master
# python manage.py migrate


# ============================================================================
# STEP 2 — Backfill valid_until for existing COMPLETED payments
# Save this as: mck_master/management/commands/backfill_plan_validity.py
# Then run: python manage.py backfill_plan_validity
# ============================================================================

from django.core.management.base import BaseCommand
from django.utils import timezone
from dateutil.relativedelta import relativedelta


class Command(BaseCommand):
    help = "Backfill valid_from / valid_until for existing COMPLETED payments"

    def handle(self, *args, **options):
        from mck_master.models import Payment

        payments = Payment.objects.filter(
            status='COMPLETED',
            valid_until__isnull=True
        )
        count = payments.count()
        self.stdout.write(f"Found {count} payments to backfill...")

        updated = 0
        for p in payments:
            # Use payment_date if available, else created_on
            start = p.payment_date or p.created_on or timezone.now()
            p.valid_from  = start
            p.valid_until = start + relativedelta(months=Payment.VALIDITY_MONTHS)
            p.save(update_fields=['valid_from', 'valid_until'])
            updated += 1
            self.stdout.write(
                f"  ✓ {p.user.email} | {p.plan} | expires {p.valid_until.strftime('%d %b %Y')}"
            )

        self.stdout.write(self.style.SUCCESS(f"\nDone. {updated} payments updated."))


# ============================================================================
# STEP 3 — Update payment_required decorator in views.py
# Replace the existing decorator with this version that checks expiry too
# ============================================================================

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def payment_required(view_func):
    """Require an active (non-expired) payment to access a view."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('mck_auth:website_signin')

        if not getattr(request.user, 'is_profile_completed', False):
            messages.warning(request, "Please complete your profile first.")
            return redirect('mck_website:profile_page')

        active = request.user.active_plan   # uses the updated property (checks valid_until)
        if not active:
            # Check if they ever paid — if yes, plan expired
            ever_paid = request.user.payments.filter(status='COMPLETED').exists()
            if ever_paid:
                messages.warning(
                    request,
                    "Your plan has expired. Please renew to continue accessing profiles."
                )
            else:
                messages.warning(request, "Please choose a plan to continue.")
            return redirect('mck_website:payment_gateway')

        return view_func(request, *args, **kwargs)
    return wrapper


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def get_opposite_gender(profile):
    """Return 'F' for Male profiles, 'M' for Female profiles."""
    if not profile:
        return None
    return 'F' if profile.gender == 'M' else 'M'


def check_view_limit(request, profile_obj):
    """
    Returns (can_view: bool, reason: str)
    - Checks gender filter
    - Checks plan view limit
    - Records view if allowed and new
    """
    from mck_master.models import ProfileView

    user = request.user
    limit = user.profile_view_limit          # 5 / 10 / 15
    already_viewed = ProfileView.has_viewed(user, profile_obj)
    views_used = ProfileView.count_for_user(user)

    # Gender check: only show opposite gender
    my_profile = user.profiles.filter(datamode='A').order_by('-updated_on').first()
    if my_profile:
        allowed_gender = get_opposite_gender(my_profile)
        if allowed_gender and profile_obj.gender != allowed_gender:
            return False, "gender_mismatch"

    if already_viewed:
        return True, "already_counted"          # doesn't consume a new slot

    if views_used >= limit:
        return False, "limit_reached"

    # Record the view
    ProfileView.record(user, profile_obj)
    return True, "new_view"


# ─────────────────────────────────────────────────────────────────────────────
# PAYMENT GATEWAY VIEW  (replaces existing PaymentGatewayView)
# ─────────────────────────────────────────────────────────────────────────────

from decimal import Decimal
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.utils import timezone
import razorpay
import logging

logger = logging.getLogger(__name__)


class PaymentGatewayView(LoginRequiredMixin, TemplateView):
    template_name = "website/payment_gateway.html"
    login_url = '/auth/website/login/'

    PLANS = {
        'THREE_MONTH': {'amount_paise': 299900,  'amount_inr': 2999,  'validity_months': 3,  'profile_limit': 40,  'label': '3 Month'},
        'SIX_MONTH':   {'amount_paise': 599900,  'amount_inr': 5999,  'validity_months': 6,  'profile_limit': 80,  'label': '6 Month'},
        'ONE_YEAR':    {'amount_paise': 1199900, 'amount_inr': 11999, 'validity_months': 12, 'profile_limit': 120, 'label': '1 Year'},
    }

    def get(self, request, *args, **kwargs):
        if not request.user.is_profile_completed:
            messages.warning(request, "Please complete your profile first.")
            return redirect('mck_website:profile_page')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plans']              = self.PLANS
        context['active_plan']        = self.request.user.active_plan
        context['profile_view_limit'] = self.request.user.profile_view_limit
        context['can_upgrade']        = self.request.user.can_upgrade
        return context

    def post(self, request, *args, **kwargs):
        try:
            data     = json.loads(request.body) if request.body else request.POST
            plan_key = data.get('plan', '').upper()

            if plan_key not in self.PLANS:
                return JsonResponse({'success': False, 'message': 'Invalid plan selected.'}, status=400)

            plan_cfg     = self.PLANS[plan_key]
            amount_paise = plan_cfg['amount_paise']

            # Upgrade check: new plan must cost more than current active plan
            active = request.user.active_plan
            if active:
                current_amount = self.PLANS.get(active.plan, {}).get('amount_inr', 0)
                if plan_cfg['amount_inr'] <= current_amount:
                    return JsonResponse({
                        'success': False,
                        'message': f"You already have the {active.plan_label} plan. Choose a higher plan to upgrade."
                    }, status=400)

            profile = request.user.profiles.first()

            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            razorpay_order = client.order.create({
                'amount':          amount_paise,
                'currency':        'INR',
                'receipt':         f"rcpt_{plan_key}_{request.user.id}_{int(timezone.now().timestamp())}",
                'payment_capture': 1,
                'notes': {
                    'user_id': str(request.user.id),
                    'email':   request.user.email,
                    'plan':    plan_key,
                }
            })

            Payment.objects.create(
                user          = request.user,
                profile       = profile,
                plan          = plan_key,
                order_id      = razorpay_order['id'],
                payment_id    = f"PENDING_{razorpay_order['id']}",
                amount        = Decimal(amount_paise) / 100,
                currency      = 'INR',
                status        = 'PENDING',
                response_data = razorpay_order
            )

            return JsonResponse({
                'success':       True,
                'order_id':      razorpay_order['id'],
                'amount_paise':  amount_paise,
                'plan':          plan_key,
                'plan_label':    plan_cfg['label'],
                'profile_limit': plan_cfg['profile_limit'],   # ← sent to frontend
                'razorpay_key':  settings.RAZORPAY_KEY_ID,
                'user_name':     profile.full_name if profile else request.user.get_full_name(),
                'user_email':    request.user.email,
                'user_phone':    profile.phone if profile else '',
            })

        except Exception as e:
            logger.exception(f"PaymentGatewayView POST error: {e}")
            return JsonResponse({'success': False, 'message': 'Could not create order. Try again.'}, status=500)

# ─────────────────────────────────────────────────────────────────────────────
# PROFILE DETAIL VIEW  (replaces existing ProfileDetailPage)
# ─────────────────────────────────────────────────────────────────────────────

from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin


@method_decorator(login_required(login_url=settings.LOGIN_WEB_REDIRECT_URL), name='dispatch')
@method_decorator(payment_required, name='dispatch')
class ProfileDetailPage(DetailView):
    """
    Profile detail — enforces:
      1. Opposite-gender-only filter
      2. Per-plan view limit (5 / 10 / 15)
    """
    model = Profile
    template_name = "profile_detail.html"
    context_object_name = "profile"

    def get_queryset(self):
        return Profile.objects.exclude(datamode='D')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        can_view, reason = check_view_limit(request, self.object)

        if not can_view:
            if reason == "gender_mismatch":
                messages.info(request, "This profile is not available for your search criteria.")
                return redirect('mck_website:community_match')
            elif reason == "limit_reached":
                limit = request.user.profile_view_limit
                plan  = request.user.active_plan
                messages.warning(
                    request,
                    f"You have reached your {plan.plan_label} plan limit of {limit} profile views. "
                    f"Upgrade your plan to view more profiles."
                )
                return redirect('mck_website:payment_gateway')

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        from mck_master.models import ProfileView
        context = super().get_context_data(**kwargs)
        profile = self.object
        user    = self.request.user

        context['age']             = calculate_age(profile.dob)
        context['formatted_income'] = f"₹{profile.annual_income:,.0f}" if profile.annual_income else None

        photos = []
        for i in range(1, 6):
            photo = getattr(profile, f'photo{i}', None)
            if photo and photo.url:
                photos.append({'url': photo.url, 'number': i})
        context['photos'] = photos
        context['profile_photo'] = profile.photo1.url if profile.photo1 else None

        context['marital_status_display'] = dict(Profile.MARITAL_STATUS_CHOICES).get(profile.marital_status, 'Not Specified')
        context['gender_display']         = dict(Profile.GENDER_CHOICES).get(profile.gender, 'Not Specified')
        context['dosham_display']         = profile.dosham or 'Not Specified'
        context['is_verified']            = bool(profile.phone and profile.email and profile.photo1)
        context['profile_completeness']   = self._calculate_completeness(profile)

        # Plan info for the upgrade nudge in template
        context['views_used']       = ProfileView.count_for_user(user)
        context['view_limit']       = user.profile_view_limit
        context['active_plan']      = user.active_plan
        context['can_upgrade']      = user.can_upgrade

        return context

    def _calculate_completeness(self, profile):
        fields = ['full_name','gender','dob','marital_status','religion','caste',
                  'education','occupation','annual_income','phone','email','city','bio','photo1']
        filled = sum(1 for f in fields if getattr(profile, f, None))
        return int((filled / len(fields)) * 100)


# ─────────────────────────────────────────────────────────────────────────────
# COMMUNITY SEARCH / PROFILE LISTING  — gender filter helper
# Apply this inside CommunitySearchPage.get() and ProfilePage.get_context_data()
# ─────────────────────────────────────────────────────────────────────────────

def apply_gender_filter(queryset, request_user):
    """
    Always show only opposite-gender profiles to a logged-in paid user.
    Returns the filtered queryset.
    """
    my_profile = request_user.profiles.filter(datamode='A').order_by('-updated_on').first()
    if my_profile:
        opposite = get_opposite_gender(my_profile)
        if opposite:
            queryset = queryset.filter(gender=opposite)
    return queryset


# ─────────────────────────────────────────────────────────────────────────────
# WISHLIST  — gender-aware toggle (replace existing toggle_wishlist)
# ─────────────────────────────────────────────────────────────────────────────

@login_required
@require_POST
@csrf_protect
def toggle_wishlist(request):
    """Add or remove profile from wishlist (only opposite gender allowed)."""
    import json
    try:
        data = json.loads(request.body) if request.body else request.POST
        profile_id = data.get('profile_id')
        action     = data.get('action', 'add')

        to_profile = get_object_or_404(Profile.objects.exclude(datamode='D'), pk=profile_id)

        if to_profile.user == request.user:
            return JsonResponse({'success': False, 'message': 'You cannot shortlist your own profile'}, status=400)

        # Gender guard
        my_profile = request.user.profiles.filter(datamode='A').order_by('-updated_on').first()
        if my_profile:
            allowed_gender = get_opposite_gender(my_profile)
            if allowed_gender and to_profile.gender != allowed_gender:
                return JsonResponse({'success': False, 'message': 'You can only shortlist opposite-gender profiles.'}, status=400)

        # Plan view-limit guard (wishlist counts as a view)
        from mck_master.models import ProfileView
        already_viewed = ProfileView.has_viewed(request.user, to_profile)
        views_used     = ProfileView.count_for_user(request.user)
        limit          = request.user.profile_view_limit

        if action == 'add' and not already_viewed and views_used >= limit:
            return JsonResponse({
                'success': False,
                'message': f'Profile view limit reached ({limit}). Upgrade your plan to shortlist more profiles.'
            }, status=403)

        if action == 'add':
            wishlist_item, created = Wishlist.objects.get_or_create(
                from_user=request.user,
                to_profile=to_profile
            )
            if created and not already_viewed:
                ProfileView.record(request.user, to_profile)
            return JsonResponse({
                'success': True,
                'message': 'Added to wishlist!' if created else 'Already in wishlist',
                'action': 'added',
                'wishlist_id': wishlist_item.id
            })
        else:
            Wishlist.objects.filter(from_user=request.user, to_profile=to_profile).delete()
            return JsonResponse({'success': True, 'message': 'Removed from wishlist', 'action': 'removed'})

    except Exception as e:
        logger.error(f"Error toggling wishlist: {e}")
        return JsonResponse({'success': False, 'message': 'An error occurred'}, status=500)
        


def payment_requireds(view_func):
    """Decorator to require payment for accessing a view."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('mck_auth:website_signin')
        
        # Check if user has completed profile
        if not getattr(request.user, 'is_profile_completed', False):
            messages.warning(request, "Please complete your profile first.")
            return redirect('mck_website:profile_page')
        
        # Check payment status
        has_paid = getattr(request.user, 'has_paid', False)
        if not has_paid:
            has_paid = request.user.payments.filter(status='COMPLETED').exists()
        
        if not has_paid:
            messages.warning(request, "Please complete your payment to access this page.")
            return redirect('mck_website:payment_gateway')
        
        return view_func(request, *args, **kwargs)
    return wrapper
# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def calculate_age(birth_date):
    """Calculate age from birth date"""
    if not birth_date:
        return None
    today = date.today()
    return today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )


def calculate_compatibility(profile1, profile2):
    """Calculate compatibility score between two profiles"""
    score = 0
    total_weight = 0
    
    # Religion match (weight: 30)
    if profile1.religion and profile2.religion:
        total_weight += 30
        if profile1.religion == profile2.religion:
            score += 30
    
    # Education match (weight: 20)
    if profile1.education and profile2.education:
        total_weight += 20
        if profile1.education == profile2.education:
            score += 20
    
    # Occupation match (weight: 15)
    if profile1.occupation and profile2.occupation:
        total_weight += 15
        if profile1.occupation == profile2.occupation:
            score += 15
    
    # City match (weight: 15)
    if profile1.city and profile2.city:
        total_weight += 15
        if profile1.city == profile2.city:
            score += 15
    
    # Age compatibility (weight: 20)
    if profile1.dob and profile2.dob:
        total_weight += 20
        age1 = calculate_age(profile1.dob)
        age2 = calculate_age(profile2.dob)
        if age1 and age2:
            age_diff = abs(age1 - age2)
            if age_diff <= 3:
                score += 20
            elif age_diff <= 5:
                score += 15
            elif age_diff <= 8:
                score += 10
            elif age_diff <= 10:
                score += 5
    
    if total_weight == 0:
        return 0
    
    return int((score / total_weight) * 100)


# ============================================================================
# STATIC PAGES
# ============================================================================

def pki_validation_view(request):
    """SSL certificate validation"""
    file_path = os.path.join(settings.BASE_DIR, "mck_website", "templates", "verify.txt")
    try:
        with open(file_path, "r") as file:
            content = file.read()
        return HttpResponse(content, content_type="text/plain")
    except FileNotFoundError:
        return HttpResponse("File not found", status=404)


# ============================================================================
# HELPER FUNCTION — Add to views.py
# Returns a queryset of user IDs who are on a specific plan
# ============================================================================

def get_users_on_plan(plan_key):
    """
    Returns a queryset of user IDs who have a COMPLETED payment on the given plan.
    plan_key: 'BASIC' | 'STANDARD' | 'PREMIUM'
    """
    from mck_master.models import Payment
    return Payment.objects.filter(
        status='COMPLETED',
        plan=plan_key
    ).values_list('user_id', flat=True).distinct()

# ============================================================================
# HELPER — replaces get_same_plan_profile_queryset
# ============================================================================

def get_all_paid_profile_queryset(user):
    """
    Returns profiles of all users who have a COMPLETED payment.
    Excludes the requesting user's own profile and deleted profiles.
    """
    from mck_master.models import Payment, Profile

    active_payment = user.payments.filter(status='COMPLETED').order_by('-payment_date').first()
    if not active_payment:
        return Profile.objects.none()

    paid_user_ids = Payment.objects.filter(
        status='COMPLETED'
    ).values_list('user_id', flat=True).distinct()

    return Profile.objects.filter(
        user_id__in=paid_user_ids,
        datamode='A'
    ).exclude(user=user)


def get_plan_profile_limit(user):
    """
    Returns the max number of profiles this user can see,
    based on their active plan.
    """
    active_plan = user.active_plan
    if not active_plan:
        return 0

    # Directly return the profile_limit from the active plan object
    # since it's already defined in your Payment model
    return active_plan.profile_limit


# ============================================================================
# HomePage
# ============================================================================
# ============================================================================
# ProfilePage
# ============================================================================
import random
from datetime import date
from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView


from django.core.paginator import Paginator
from django.db.models import Q, F, Case, When, Value, IntegerField
from django.db import models
from datetime import date
from dateutil.relativedelta import relativedelta
import random

import math
import random
from datetime import date


import math
import random
from datetime import date

from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Case, F, IntegerField, Q, When
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

# Adjust these imports to your actual app paths
# from your_app.decorators import payment_required
# from your_app.utils import get_all_paid_profile_queryset, apply_gender_filter, get_plan_profile_limit, calculate_age
from mck_master.models import Profile



@method_decorator(login_required(login_url=settings.LOGIN_WEB_REDIRECT_URL), name='dispatch')
@method_decorator(payment_required, name='dispatch')
class ProfilePage(TemplateView):
    template_name = "property_page.html"
    PROFILES_PER_PAGE = 9  # Define constant for profiles per page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request

        # All paid profiles, opposite gender
        profiles = get_all_paid_profile_queryset(request.user).select_related('user')
        profiles = apply_gender_filter(profiles, request.user)
        profiles = self._apply_filters(profiles, request.GET)
        
        # Process profiles (add computed fields)
        profiles_list = self._process_profiles(profiles, request.user)

        # Apply sorting and shuffle
        sort = request.GET.get('sort', 'random')
        shuffle_profiles = request.GET.get('shuffle', 'true')
        profiles_list = self._apply_sorting(profiles_list, sort, shuffle_profiles)

        # Cap list based on plan limit
        limit = get_plan_profile_limit(request.user)
        if limit and limit > 0:
            profiles_list = profiles_list[:limit]

        # Pagination
        paginator = Paginator(profiles_list, self.PROFILES_PER_PAGE)
        page_number = request.GET.get('page')
        profiles_page = paginator.get_page(page_number)

        # Get wishlist IDs
        try:
            wishlist_ids = set(request.user.wishlist_profiles.values_list('id', flat=True))
        except Exception:
            wishlist_ids = set()

        from mck_master.models import ProfileView
        active_plan = request.user.active_plan

        context.update({
            "profiles": profiles_page,
            "page_obj": profiles_page,  # For pagination template
            "filters": request.GET,
            "active_plan": active_plan,
            "plan_label": active_plan.plan_label if active_plan else "",
            "views_used": ProfileView.count_for_user(request.user),
            "view_limit": request.user.profile_view_limit,
            "can_upgrade": request.user.can_upgrade,
            "profile_limit": limit,
            "wishlist_ids": wishlist_ids,
            "PROFILES_PER_PAGE": self.PROFILES_PER_PAGE,
        })
        context.update(self._get_filter_choices())

        return context

    def _apply_filters(self, queryset, params):
        # Gender filter
        if params.get('gender'):
            queryset = queryset.filter(gender=params['gender'])
        
        # City filter (using birth_place)
        if params.get('city'):
            queryset = queryset.filter(birth_place__icontains=params['city'])
        
        # State filter
        if params.get('state'):
            queryset = queryset.filter(state__icontains=params['state'])
        
        # Religion filter
        if params.get('religion'):
            queryset = queryset.filter(religion=params['religion'])
        
        # Caste filter
        if params.get('caste'):
            queryset = queryset.filter(caste=params['caste'])
        
        # Age filter
        age_min = params.get('age_min')
        age_max = params.get('age_max')
        if age_min or age_max:
            today = date.today()
            if age_min and age_min.isdigit():
                max_birth = today - relativedelta(years=int(age_min))
                queryset = queryset.filter(dob__lte=max_birth)
            if age_max and age_max.isdigit():
                min_birth = today - relativedelta(years=int(age_max) + 1)
                queryset = queryset.filter(dob__gte=min_birth)
        
        # Photo filter
        if params.get('with_photo'):
            queryset = queryset.filter(
                Q(photo1__isnull=False) | Q(photo2__isnull=False) |
                Q(photo3__isnull=False) | Q(photo4__isnull=False) | 
                Q(photo5__isnull=False)
            )
        
        return queryset

    def _process_profiles(self, queryset, user):
        profiles_list = []
        for profile in queryset:
            profile.age = calculate_age(profile.dob)
            profile.name = profile.full_name or (
                f"{profile.user.first_name} {profile.user.last_name}".strip()
                if profile.user else "Profile"
            )
            profile.profile_photo = None
            for field in ['photo1', 'photo2', 'photo3', 'photo4', 'photo5']:
                photo = getattr(profile, field, None)
                if photo:
                    profile.profile_photo = photo
                    break
            if profile.user:
                profile.premium = getattr(profile.user, 'is_premium', False)
                profile.verified = getattr(profile.user, 'is_verified', False)
            profiles_list.append(profile)
        return profiles_list

    def _apply_sorting(self, profiles_list, sort, shuffle):
        if shuffle == 'true' and sort == 'random':
            random.shuffle(profiles_list)
        elif sort == "age_low":
            profiles_list.sort(key=lambda x: x.dob if x.dob else date(1900, 1, 1), reverse=True)
        elif sort == "age_high":
            profiles_list.sort(key=lambda x: x.dob if x.dob else date(2100, 1, 1))
        elif sort == "income_high":
            profiles_list.sort(key=lambda x: x.annual_income or 0, reverse=True)
        elif sort == "newest":
            profiles_list.sort(key=lambda x: x.created_on or date(1900, 1, 1), reverse=True)
        return profiles_list

    def _get_filter_choices(self):
        base_qs = Profile.objects.filter(datamode='A')  # Active profiles only
        
        # Get birth place choices for city dropdown
        city_choices = base_qs.exclude(birth_place__isnull=True).exclude(birth_place='').values_list('birth_place', flat=True).distinct().order_by('birth_place')
        
        return {
            "gender_choices": Profile.GENDER_CHOICES,
            "city_choices": city_choices,  # Now using birth_place as city
            "state_choices": base_qs.exclude(state__isnull=True).exclude(state='').values_list('state', flat=True).distinct().order_by('state'),
            "religion_choices": base_qs.exclude(religion__isnull=True).exclude(religion='').values_list('religion', flat=True).distinct().order_by('religion'),
            "caste_choices": base_qs.exclude(caste__isnull=True).exclude(caste='').values_list('caste', flat=True).distinct().order_by('caste'),
            "complexion_choices": base_qs.exclude(complexion__isnull=True).exclude(complexion='').values_list('complexion', flat=True).distinct().order_by('complexion'),
            "education_choices": base_qs.exclude(education__isnull=True).exclude(education='').values_list('education', flat=True).distinct().order_by('education'),
            "profession_choices": base_qs.exclude(occupation__isnull=True).exclude(occupation='').values_list('occupation', flat=True).distinct().order_by('occupation'),
            "marital_status_choices": Profile.MARITAL_STATUS_CHOICES,
        }

@method_decorator(login_required(login_url=settings.LOGIN_WEB_REDIRECT_URL), name='dispatch')
@method_decorator(payment_required, name='dispatch')
class ofilePage(TemplateView):
    template_name = "property_page.html"
    PROFILES_PER_PAGE = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request  = self.request
        params   = request.GET

        # 1. Base queryset
        profiles_qs = get_all_paid_profile_queryset(request.user).select_related('user')
        profiles_qs = apply_gender_filter(profiles_qs, request.user)

        # 2. Apply filters
        profiles_qs = self._apply_filters(profiles_qs, params)

        # 3. Sorting
        sort         = params.get('sort', 'random')
        shuffle_flag = params.get('shuffle', 'true')

        if shuffle_flag == 'true' and sort == 'random':
            raw_seed = params.get('seed', '')
            seed     = int(raw_seed) if raw_seed.isdigit() else random.randint(1, 999_999)
            context['current_seed'] = seed
            profile_ids = list(profiles_qs.values_list('id', flat=True))
            rng = random.Random(seed)
            rng.shuffle(profile_ids)
            order = Case(
                *[When(id=pid, then=pos) for pos, pid in enumerate(profile_ids)],
                output_field=IntegerField(),
            )
            profiles_qs = profiles_qs.filter(id__in=profile_ids).order_by(order)
        else:
            profiles_qs = self._apply_queryset_sorting(profiles_qs, sort)

        # 4. Plan limit
        limit = get_plan_profile_limit(request.user)

        # 5. Paginate BEFORE any slicing — sliced querysets cannot be paginated
        paginator = Paginator(profiles_qs, self.PROFILES_PER_PAGE)

        if limit and limit > 0:
            max_allowed_page = min(paginator.num_pages, math.ceil(limit / self.PROFILES_PER_PAGE))
        else:
            max_allowed_page = paginator.num_pages

        try:
            page_number = max(1, min(int(params.get('page', 1) or 1), max_allowed_page))
        except (ValueError, TypeError):
            page_number = 1

        profiles_page = paginator.get_page(page_number)

        # 6. Enrich — pass a plain list, NOT the Page object
        profiles_list = self._enrich_profiles(list(profiles_page.object_list), request.user)

        # 7. All-profiles slider (no filters, latest 100)
        all_profiles_raw = list(
            get_all_paid_profile_queryset(request.user)
            .select_related('user')
            .order_by('-id')[:100]
        )
        all_profiles_list = self._enrich_profiles(all_profiles_raw, request.user)

        # 8. Meta
        from mck_master.models import ProfileView
        active_plan = request.user.active_plan

        try:
            wishlist_ids = set(request.user.wishlist_profiles.values_list('id', flat=True))
        except Exception:
            wishlist_ids = set()

        context.update({
            # profiles  → plain list for the {% for %} loop in the grid
            # page_obj  → Django Page object for ALL pagination controls
            "profiles":           profiles_list,
            "page_obj":           profiles_page,
            "profiles_page":      profiles_page,
            "all_profiles":       all_profiles_list,
            "filters":            params,
            "active_plan":        active_plan,
            "plan_label":         active_plan.plan_label if active_plan else "",
            "views_used":         ProfileView.count_for_user(request.user),
            "profile_view_limit": request.user.profile_view_limit,
            "can_upgrade":        request.user.can_upgrade,
            "profile_limit":      limit,
            "wishlist_ids":       wishlist_ids,
            "max_allowed_page":   max_allowed_page,
        })
        context.update(self._get_filter_choices())
        return context

    def _apply_filters(self, queryset, params):
        if params.get('gender'):
            queryset = queryset.filter(gender=params['gender'])
        if params.get('birth_place'):
            queryset = queryset.filter(birth_place__iexact=params['birth_place'])
        if params.get('state'):
            queryset = queryset.filter(state__iexact=params['state'])
        if params.get('religion'):
            queryset = queryset.filter(religion__iexact=params['religion'])
        if params.get('caste'):
            queryset = queryset.filter(caste__iexact=params['caste'])
        if params.get('complexion'):
            queryset = queryset.filter(complexion__iexact=params['complexion'])
        if params.get('education'):
            queryset = queryset.filter(education__icontains=params['education'])
        if params.get('profession'):
            queryset = queryset.filter(occupation__icontains=params['profession'])
        if params.get('marital_status'):
            queryset = queryset.filter(marital_status=params['marital_status'])

        income = params.get('income')
        if income == 'below_10':
            queryset = queryset.filter(annual_income__lt=1_000_000)
        elif income == '10_25':
            queryset = queryset.filter(annual_income__gte=1_000_000,  annual_income__lt=2_500_000)
        elif income == '25_50':
            queryset = queryset.filter(annual_income__gte=2_500_000,  annual_income__lt=5_000_000)
        elif income == '50_100':
            queryset = queryset.filter(annual_income__gte=5_000_000,  annual_income__lt=10_000_000)
        elif income == 'above_100':
            queryset = queryset.filter(annual_income__gte=10_000_000)

        today   = date.today()
        age_min = params.get('age_min')
        age_max = params.get('age_max')
        if age_min and str(age_min).isdigit():
            queryset = queryset.filter(dob__lte=today - relativedelta(years=int(age_min)))
        if age_max and str(age_max).isdigit():
            queryset = queryset.filter(dob__gte=today - relativedelta(years=int(age_max) + 1))

        if params.get('height_min'):
            try:
                queryset = queryset.filter(height__gte=str(float(params['height_min'])))
            except ValueError:
                pass
        if params.get('height_max'):
            try:
                queryset = queryset.filter(height__lte=str(float(params['height_max'])))
            except ValueError:
                pass

        if params.get('with_photo'):
            queryset = queryset.filter(
                Q(photo1__isnull=False) | Q(photo2__isnull=False) |
                Q(photo3__isnull=False) | Q(photo4__isnull=False) |
                Q(photo5__isnull=False)
            )
        return queryset

    def _apply_queryset_sorting(self, queryset, sort):
        if sort == 'age_low':
            return queryset.order_by(F('dob').desc(nulls_last=True))
        elif sort == 'age_high':
            return queryset.order_by(F('dob').asc(nulls_last=True))
        elif sort == 'income_high':
            return queryset.order_by(F('annual_income').desc(nulls_last=True))
        elif sort == 'newest':
            return queryset.order_by(F('created_on').desc(nulls_last=True))
        return queryset.order_by('-id')

    def _enrich_profiles(self, profiles_list, user):
        """Accepts a plain Python list. Attaches age, name, profile_photo, premium, verified."""
        enriched = []
        for profile in profiles_list:
            profile.age = calculate_age(profile.dob) if profile.dob else None

            if getattr(profile, 'full_name', None):
                profile.name = profile.full_name
            elif profile.user:
                profile.name = f"{profile.user.first_name} {profile.user.last_name}".strip() or "Profile"
            else:
                profile.name = "Profile"

            profile.profile_photo = None
            for field in ['photo1', 'photo2', 'photo3', 'photo4', 'photo5']:
                photo = getattr(profile, field, None)
                if photo:
                    profile.profile_photo = photo
                    break

            profile.premium  = getattr(profile.user, 'is_premium', False) if profile.user else False
            profile.verified = getattr(profile.user, 'is_verified', False) if profile.user else False
            enriched.append(profile)
        return enriched

    def _get_filter_choices(self):
        base_qs = Profile.objects.filter(datamode='A')
        def dv(field):
            return (base_qs.exclude(**{f'{field}__isnull': True}).exclude(**{field: ''})
                    .values_list(field, flat=True).distinct().order_by(field))
        return {
            "gender_choices":         Profile.GENDER_CHOICES,
            "marital_status_choices": Profile.MARITAL_STATUS_CHOICES,
            "birth_place_choices":    dv('birth_place'),
            "state_choices":          dv('state'),
            "religion_choices":       dv('religion'),
            "caste_choices":          dv('caste'),
            "complexion_choices":     dv('complexion'),
            "education_choices":      dv('education'),
            "profession_choices":     dv('occupation'),
        }


@method_decorator(login_required(login_url=settings.LOGIN_WEB_REDIRECT_URL), name='dispatch')
@method_decorator(payment_required, name='dispatch')
class rofilePage(TemplateView):
    template_name = "property_page.html"

    PROFILES_PER_PAGE = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request
        params  = request.GET

        # ── 1. Base queryset ──────────────────────────────────────────────
        profiles_qs = get_all_paid_profile_queryset(request.user).select_related('user')
        profiles_qs = apply_gender_filter(profiles_qs, request.user)
        profiles_qs = self._apply_filters(profiles_qs, params)

        # ── 2. Convert to list & enrich ───────────────────────────────────
        profiles_list = self._process_profiles(profiles_qs, request.user)

        # ── 3. Sort / shuffle ─────────────────────────────────────────────
        sort         = params.get('sort', 'random')
        shuffle_flag = params.get('shuffle', 'true')

        if shuffle_flag == 'true' and sort == 'random':
            raw_seed = params.get('seed', '')
            seed = int(raw_seed) if raw_seed.isdigit() else random.randint(1, 999_999)
            rng  = random.Random(seed)
            rng.shuffle(profiles_list)
            context['current_seed'] = seed
        else:
            context['current_seed'] = ''
            profiles_list = self._apply_sorting(profiles_list, sort, shuffle_flag)

        # ── 4. Cap to plan limit ──────────────────────────────────────────
        limit = get_plan_profile_limit(request.user)
        profiles_list = profiles_list[:limit]

        # ── 5. Paginate ───────────────────────────────────────────────────
        paginator     = Paginator(profiles_list, self.PROFILES_PER_PAGE)
        page_number   = params.get('page', 1)
        profiles_page = paginator.get_page(page_number)

        # ── 6. Plan / view meta ───────────────────────────────────────────
        from mck_master.models import ProfileView
        active_plan = request.user.active_plan

        try:
            wishlist_ids = set(
                request.user.wishlist_profiles.values_list('id', flat=True)
            )
        except Exception:
            wishlist_ids = set()

        context.update({
            "profiles":           profiles_page,
            "filters":            params,
            "active_plan":        active_plan,
            "plan_label":         active_plan.plan_label if active_plan else "",
            "views_used":         ProfileView.count_for_user(request.user),
            "profile_view_limit": request.user.profile_view_limit,
            "can_upgrade":        request.user.can_upgrade,
            "profile_limit":      limit,
            "wishlist_ids":       wishlist_ids,
        })
        context.update(self._get_filter_choices())
        return context

    # ─────────────────────────────────────────────────────────────────────

    def _apply_filters(self, queryset, params):
        if params.get('gender'):
            queryset = queryset.filter(gender=params['gender'])

        # ✅ FIXED: filter on birth_place instead of city
        if params.get('birth_place'):
            queryset = queryset.filter(birth_place__iexact=params['birth_place'])

        if params.get('state'):
            queryset = queryset.filter(state__icontains=params['state'])
        if params.get('religion'):
            queryset = queryset.filter(religion=params['religion'])
        if params.get('caste'):
            queryset = queryset.filter(caste=params['caste'])
        if params.get('complexion'):
            queryset = queryset.filter(complexion__iexact=params['complexion'])
        if params.get('education'):
            queryset = queryset.filter(education__icontains=params['education'])
        if params.get('profession'):
            queryset = queryset.filter(occupation__icontains=params['profession'])
        if params.get('marital_status'):
            queryset = queryset.filter(marital_status=params['marital_status'])

        # Income filter
        income = params.get('income')
        if income == 'below_10':
            queryset = queryset.filter(annual_income__lt=1_000_000)
        elif income == '10_25':
            queryset = queryset.filter(annual_income__gte=1_000_000,  annual_income__lt=2_500_000)
        elif income == '25_50':
            queryset = queryset.filter(annual_income__gte=2_500_000,  annual_income__lt=5_000_000)
        elif income == '50_100':
            queryset = queryset.filter(annual_income__gte=5_000_000,  annual_income__lt=10_000_000)
        elif income == 'above_100':
            queryset = queryset.filter(annual_income__gte=10_000_000)

        # Age filter
        today   = date.today()
        age_min = params.get('age_min')
        age_max = params.get('age_max')
        if age_min and str(age_min).isdigit():
            queryset = queryset.filter(dob__lte=today - relativedelta(years=int(age_min)))
        if age_max and str(age_max).isdigit():
            queryset = queryset.filter(dob__gte=today - relativedelta(years=int(age_max)))

        # Height filter (stored as "5.8" string → convert to float for comparison)
        height_min = params.get('height_min')
        height_max = params.get('height_max')
        if height_min:
            try:
                queryset = queryset.filter(height__gte=str(float(height_min)))
            except ValueError:
                pass
        if height_max:
            try:
                queryset = queryset.filter(height__lte=str(float(height_max)))
            except ValueError:
                pass

        if params.get('with_photo'):
            queryset = queryset.filter(
                Q(photo1__isnull=False) | Q(photo2__isnull=False) |
                Q(photo3__isnull=False) | Q(photo4__isnull=False) |
                Q(photo5__isnull=False)
            )
        return queryset

    def _process_profiles(self, queryset, user):
        profiles_list = []
        for profile in queryset:
            profile.age  = calculate_age(profile.dob)
            profile.name = profile.full_name or (
                f"{profile.user.first_name} {profile.user.last_name}".strip()
                if profile.user else "Profile"
            )
            profile.profile_photo = None
            for field in ['photo1', 'photo2', 'photo3', 'photo4', 'photo5']:
                photo = getattr(profile, field, None)
                if photo:
                    profile.profile_photo = photo
                    break
            if profile.user:
                profile.premium  = getattr(profile.user, 'is_premium',  False)
                profile.verified = getattr(profile.user, 'is_verified', False)
            profiles_list.append(profile)
        return profiles_list

    def _apply_sorting(self, profiles_list, sort, shuffle):
        if sort == 'age_low':
            profiles_list.sort(key=lambda x: x.dob or date(1900, 1, 1), reverse=True)
        elif sort == 'age_high':
            profiles_list.sort(key=lambda x: x.dob or date(2100, 1, 1))
        elif sort == 'income_high':
            profiles_list.sort(key=lambda x: x.annual_income or 0, reverse=True)
        elif sort == 'newest':
            profiles_list.sort(key=lambda x: x.created_on or date(1900, 1, 1), reverse=True)
        elif shuffle == 'true':
            random.shuffle(profiles_list)
        return profiles_list

    def _get_filter_choices(self):
        base_qs = Profile.objects.filter(datamode='A')
        return {
            "gender_choices":         Profile.GENDER_CHOICES,
            "marital_status_choices": Profile.MARITAL_STATUS_CHOICES,

            # ✅ FIXED: birth_place choices from birth_place field
            "birth_place_choices":    (
                base_qs
                .exclude(birth_place__isnull=True)
                .exclude(birth_place='')
                .values_list('birth_place', flat=True)
                .distinct()
                .order_by('birth_place')
            ),
            "state_choices":          (
                base_qs
                .exclude(state__isnull=True).exclude(state='')
                .values_list('state', flat=True).distinct().order_by('state')
            ),
            "religion_choices":       (
                base_qs
                .exclude(religion__isnull=True).exclude(religion='')
                .values_list('religion', flat=True).distinct().order_by('religion')
            ),
            "caste_choices":          (
                base_qs
                .exclude(caste__isnull=True).exclude(caste='')
                .values_list('caste', flat=True).distinct().order_by('caste')
            ),
            "complexion_choices":     (
                base_qs
                .exclude(complexion__isnull=True).exclude(complexion='')
                .values_list('complexion', flat=True).distinct().order_by('complexion')
            ),
            "education_choices":      (
                base_qs
                .exclude(education__isnull=True).exclude(education='')
                .values_list('education', flat=True).distinct().order_by('education')
            ),
            "profession_choices":     (
                base_qs
                .exclude(occupation__isnull=True).exclude(occupation='')
                .values_list('occupation', flat=True).distinct().order_by('occupation')
            ),
        }   



class HomePage(TemplateView):
    """Home page"""
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            context['page_kwargs'] = seo.get_page_tags("home_page")
            
            
            
            context["profiles"] = Profile.objects.exclude(datamode='D')\
                .order_by('-updated_on')[:8]
            
            context['gallery_list'] = Gallery.objects.filter(datamode="A")\
                .order_by('-updated_on')[:12]
          
            
            if self.request.user.is_authenticated:
                context['user_has_paid'] = Payment.objects.filter(
                    user=self.request.user,
                    status='COMPLETED'
                ).exists()
                # context['user_wishlist'] = self.request.user.wishlist_set.all()[:5]
        except Exception as e:
            logger.error(f"Error loading home page: {str(e)}")
        
        return context


class AboutPage(TemplateView):
    """About page"""
    template_name = "about.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("about_page")
        return context


class OurServicesPage(TemplateView):
    """Our services page"""
    template_name = "our_services.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("about_page")
        return context


class PrivacyPolicyPage(TemplateView):
    """Privacy policy page"""
    template_name = "privacy_policy.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("privacy_policy_page")
        return context


class TermsPage(TemplateView):
    """Terms and conditions page"""
    template_name = "terms.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("terms_page")
        return context


class PropertyLegalServicesPage(TemplateView):
    """Property legal services page"""
    template_name = "property_legal_services.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("property_legal_services_page")
        return context


class SolarPage(TemplateView):
    """Solar services page"""
    template_name = "solar.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("solar")
        return context


class FencingPage(TemplateView):
    """Fencing services page"""
    template_name = "fencing.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("fencing")
        return context


class LandLevellingPage(TemplateView):
    """Land levelling services page"""
    template_name = "pages/land_leveling.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("land_levelling")
        return context


class GalleryPageView(TemplateView):
    """Gallery page"""
    template_name = "gallery.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['gallery_list'] = Gallery.objects.filter(datamode="A").order_by('-updated_on')
        return context


class SucessStoryPageView(TemplateView):
    """Success stories page"""
    template_name = "sucess_stories.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['gallery_list'] = Gallery.objects.filter(datamode="A").order_by('-updated_on')
        return context
    
class VIPPageView(TemplateView):
    """Success stories page"""
    template_name = "vip_page.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['gallery_list'] = Gallery.objects.filter(datamode="A").order_by('-updated_on')
        return context


class SupportPageView(TemplateView):
    """Support page"""
    template_name = "support.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['gallery_list'] = Gallery.objects.filter(datamode="A").order_by('-updated_on')
        return context

class PackagePageView(TemplateView):
    """Package page"""
    template_name = "package.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['gallery_list'] = Gallery.objects.filter(datamode="A").order_by('-updated_on')
        return context



# ============================================================================
# PROPERTY VIEWS
# ============================================================================






# ============================================================================
# PROFILE VIEWS
# ============================================================================

@method_decorator(login_required(login_url=settings.LOGIN_WEB_REDIRECT_URL), name='dispatch')
@method_decorator(payment_required, name='dispatch')
class ProfilePages(TemplateView):
    
    """Profile listing page with filters"""
    template_name = "property_page.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request
        
        profiles = Profile.objects.exclude(datamode='D').select_related('user')
        
        # Apply filters
        profiles = self._apply_filters(profiles, request.GET)
        
        # Process profiles with age calculation
        profiles_list = self._process_profiles(profiles, request.user)
        
        # Apply sorting
        sort = request.GET.get('sort', 'random')
        shuffle_profiles = request.GET.get('shuffle', 'true')
        profiles_list = self._apply_sorting(profiles_list, sort, shuffle_profiles)

        # Pagination
        paginator = Paginator(profiles_list, 9)
        page_number = request.GET.get('page')
        profiles_page = paginator.get_page(page_number)

        context["profiles"] = profiles_page
        context["filters"] = request.GET
        context.update(self._get_filter_choices())
        
        return context
    
    def _apply_filters(self, queryset, params):
        """Apply all filters to queryset"""
        # Basic filters
        if params.get('gender'):
            queryset = queryset.filter(gender=params['gender'])
        
        if params.get('city'):
            queryset = queryset.filter(city__icontains=params['city'])
        
        if params.get('state'):
            queryset = queryset.filter(state__icontains=params['state'])
        
        # Religion filters
        if params.get('religion'):
            queryset = queryset.filter(religion=params['religion'])
        
        if params.get('caste'):
            queryset = queryset.filter(caste=params['caste'])
        
        # Age filter
        age_min = params.get('age_min')
        age_max = params.get('age_max')
        if age_min or age_max:
            today = date.today()
            if age_min and age_min.isdigit():
                max_birth = today - relativedelta(years=int(age_min))
                queryset = queryset.filter(dob__lte=max_birth)
            if age_max and age_max.isdigit():
                min_birth = today - relativedelta(years=int(age_max))
                queryset = queryset.filter(dob__gte=min_birth)
        
        # Photo filter
        if params.get('with_photo'):
            queryset = queryset.filter(
                Q(photo1__isnull=False) | Q(photo2__isnull=False) | 
                Q(photo3__isnull=False) | Q(photo4__isnull=False) | Q(photo5__isnull=False)
            )
        
        return queryset
    
    def _process_profiles(self, queryset, user):
        """Process profiles with calculated fields"""
        profiles_list = []
        today = date.today()
        
        for profile in queryset:
            # Calculate age
            profile.age = calculate_age(profile.dob)
            
            # Set display name
            profile.name = profile.full_name or (
                f"{profile.user.first_name} {profile.user.last_name}".strip() if profile.user else "Profile"
            )
            
            # Get profile photo
            profile.profile_photo = None
            for field in ['photo1', 'photo2', 'photo3', 'photo4', 'photo5']:
                photo = getattr(profile, field, None)
                if photo:
                    profile.profile_photo = photo
                    break
            
            # Premium/verified status
            if profile.user:
                profile.premium = getattr(profile.user, 'is_premium', False)
                profile.verified = getattr(profile.user, 'is_verified', False)
            
            profiles_list.append(profile)
        
        return profiles_list
    
    def _apply_sorting(self, profiles_list, sort, shuffle):
        """Apply sorting to profile list"""
        if shuffle == 'true' and sort == 'random':
            random.shuffle(profiles_list)
        elif sort == "age_low":
            profiles_list.sort(key=lambda x: x.dob if x.dob else date(1900,1,1), reverse=True)
        elif sort == "age_high":
            profiles_list.sort(key=lambda x: x.dob if x.dob else date(2100,1,1))
        elif sort == "income_high":
            profiles_list.sort(key=lambda x: x.annual_income or 0, reverse=True)
        elif sort == "newest":
            profiles_list.sort(key=lambda x: x.created_on or date(1900,1,1), reverse=True)
        
        return profiles_list
    
    def _get_filter_choices(self):
        """Get distinct values for filter dropdowns"""
        base_qs = Profile.objects.exclude(datamode='D')
        
        return {
            "gender_choices": Profile.GENDER_CHOICES,
            "city_choices": base_qs.exclude(city__isnull=True).exclude(city='').values_list('city', flat=True).distinct().order_by('city'),
            "state_choices": base_qs.exclude(state__isnull=True).exclude(state='').values_list('state', flat=True).distinct().order_by('state'),
            "religion_choices": base_qs.exclude(religion__isnull=True).exclude(religion='').values_list('religion', flat=True).distinct().order_by('religion'),
            "caste_choices": base_qs.exclude(caste__isnull=True).exclude(caste='').values_list('caste', flat=True).distinct().order_by('caste'),
            "complexion_choices": base_qs.exclude(complexion__isnull=True).exclude(complexion='').values_list('complexion', flat=True).distinct().order_by('complexion'),
            "education_choices": base_qs.exclude(education__isnull=True).exclude(education='').values_list('education', flat=True).distinct().order_by('education'),
            "profession_choices": base_qs.exclude(occupation__isnull=True).exclude(occupation='').values_list('occupation', flat=True).distinct().order_by('occupation'),
            "marital_status_choices": Profile.MARITAL_STATUS_CHOICES,
        }

@method_decorator(login_required(login_url=settings.LOGIN_WEB_REDIRECT_URL), name='dispatch')
@method_decorator(payment_required, name='dispatch')
class ProfileDetailPages(DetailView):
    """Profile detail view"""
    model = Profile
    template_name = "profile_detail.html"
    context_object_name = "profile"
    
    def get_queryset(self):
        return Profile.objects.exclude(datamode='D')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.object
        
        # Calculate age
        context['age'] = calculate_age(profile.dob)
        
        # Format income
        if profile.annual_income:
            context['formatted_income'] = f"₹{profile.annual_income:,.0f}"
        
        # Get all photos
        photos = []
        for i in range(1, 6):
            photo = getattr(profile, f'photo{i}', None)
            if photo and photo.url:
                photos.append({'url': photo.url, 'number': i})
        context['photos'] = photos
        
        # Profile photo
        context['profile_photo'] = profile.photo1.url if profile.photo1 else None
        
        # Display maps
        context['marital_status_display'] = dict(Profile.MARITAL_STATUS_CHOICES).get(profile.marital_status, 'Not Specified')
        context['gender_display'] = dict(Profile.GENDER_CHOICES).get(profile.gender, 'Not Specified')
        context['dosham_display'] = profile.dosham or 'Not Specified'
        
        # Verification status
        context['is_verified'] = bool(profile.phone and profile.email and profile.photo1)
        context['profile_completeness'] = self._calculate_completeness(profile)
        
        return context
    
    def _calculate_completeness(self, profile):
        """Calculate profile completion percentage"""
        fields = [
            'full_name', 'gender', 'dob', 'marital_status',
            'religion', 'caste', 'education', 'occupation',
            'annual_income', 'phone', 'email', 'city',
            'bio', 'photo1'
        ]
        
        filled = sum(1 for field in fields if getattr(profile, field, None))
        return int((filled / len(fields)) * 100)


class MyProfilePage(LoginRequiredMixin, TemplateView):

    """My Profile page with edit functionality"""
    template_name = "my_profile.html"
    login_url = "/login/"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            profile = Profile.objects.filter(
                user=self.request.user
            ).exclude(datamode='D').order_by('-updated_on').first()
            
            if not profile:
                profile = Profile.objects.create(
                    user=self.request.user,
                    created_by=self.request.user.username,
                    updated_by=self.request.user.username,
                    datamode='A',
                    marital_status='S'
                )
                logger.info(f"Created new profile for user: {self.request.user.username}")
            
            # Calculate age
            context['age'] = calculate_age(profile.dob)
            
            # Get all photos
            photos = []
            for i in range(1, 6):
                photo = getattr(profile, f'photo{i}', None)
                if photo and photo.url:
                    photos.append({'url': photo.url, 'number': i})
            
            context.update({
                'profile': profile,
                'photos': photos,
                'profile_photo_url': profile.photo1.url if profile.photo1 else None,
                'formatted_income': f"${profile.annual_income:,.0f}" if profile.annual_income else None
            })
            
        except Exception as e:
            logger.error(f"Error loading profile: {str(e)}")
            context['profile'] = None
            context['error'] = "Could not load profile. Please try again."
        
        return context


# ============================================================================
# AJAX VIEWS
# ============================================================================

class PropertySaveView(View):
    """Save property via AJAX"""
    
    def post(self, request, *args, **kwargs):
        try:
            result, message = api.ajax_property_save(request)
            status = "success" if result else "fail"
            return JsonResponse({"status": status, "message": message})
        except Exception as e:
            logger.exception("Error in PropertySaveView")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


class MaintenanceSaveView(View):
    """Save maintenance request via AJAX"""
    
    def post(self, request, *args, **kwargs):
        try:
            result, message = api.ajax_maintenance_save(request)
            status = "success" if result else "fail"
            return JsonResponse({"status": status, "message": message})
        except Exception as e:
            logger.exception("Error in MaintenanceSaveView")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


class EnquirySaveView(View):
    """Save enquiry via AJAX"""
    
    def post(self, request, *args, **kwargs):
        try:
            result, message = api.ajax_enquiry_save(request)
            status = "success" if result else "fail"
            return JsonResponse({"status": status, "message": message})
        except Exception as e:
            logger.exception("Error in EnquirySaveView")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


@require_POST
@login_required
@ensure_csrf_cookie
def ajax_my_profile_save(request):
    """AJAX endpoint for my profile page - reuses ajax_profile_save logic"""
    return ajax_profile_save(request)


# ============================================================================
# WISHLIST VIEWS
# ============================================================================

@login_required
def my_wishlist(request):
    """Wishlist page"""
    return render(request, 'wishlist.html')


@login_required
@require_POST
@csrf_protect
def toggle_wishlists(request):
    """Add or remove profile from wishlist"""
    try:
        data = json.loads(request.body) if request.body else request.POST
        profile_id = data.get('profile_id')
        action = data.get('action', 'add')
        
        to_profile = get_object_or_404(Profile.objects.exclude(datamode='D'), pk=profile_id)
        
        if to_profile.user == request.user:
            return JsonResponse({
                'success': False,
                'message': 'You cannot shortlist your own profile'
            }, status=400)
        
        if action == 'add':
            wishlist_item, created = Wishlist.objects.get_or_create(
                from_user=request.user,
                to_profile=to_profile
            )
            return JsonResponse({
                'success': True,
                'message': 'Profile added to wishlist!' if created else 'Profile already in wishlist',
                'action': 'added',
                'wishlist_id': wishlist_item.id
            })
        else:
            deleted = Wishlist.objects.filter(
                from_user=request.user,
                to_profile=to_profile
            ).delete()
            return JsonResponse({
                'success': True,
                'message': 'Profile removed from wishlist',
                'action': 'removed'
            })
        
    except Profile.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Profile not found'}, status=404)
    except Exception as e:
        logger.error(f"Error toggling wishlist: {str(e)}")
        return JsonResponse({'success': False, 'message': 'An error occurred'}, status=500)


@login_required
def get_wishlist(request):
    """Get all wishlist items for current user"""
    try:
        wishlist_items = Wishlist.objects.filter(
            from_user=request.user
        ).select_related('to_profile', 'to_profile__user').order_by('-created_on')
        
        data = []
        for item in wishlist_items:
            profile = item.to_profile
            if profile:
                data.append({
                    'id': item.id,
                    'profile_id': profile.id,
                    'profile_name': profile.full_name or profile.user.get_full_name() or 'Unknown',
                    'profile_photo': profile.photo1.url if profile.photo1 else None,
                    'age': calculate_age(profile.dob),
                    'gender': dict(Profile.GENDER_CHOICES).get(profile.gender, 'Not Specified'),
                    'location': profile.city or profile.location or 'Location not specified',
                    'occupation': profile.occupation or 'Not specified',
                    'education': profile.education or 'Not specified',
                    'created_on': item.created_on.strftime('%B %d, %Y'),
                })
        
        return JsonResponse({'success': True, 'wishlist': data, 'count': len(data)})
        
    except Exception as e:
        logger.error(f"Error getting wishlist: {str(e)}")
        return JsonResponse({'success': False, 'message': str(e), 'wishlist': []}, status=500)


@login_required
@require_POST
def remove_from_wishlist(request, wishlist_id):
    """Remove item from wishlist"""
    try:
        wishlist_item = get_object_or_404(Wishlist, id=wishlist_id, from_user=request.user)
        profile_name = wishlist_item.to_profile.full_name or 'Profile'
        wishlist_item.delete()
        return JsonResponse({'success': True, 'message': f'{profile_name} removed from wishlist'})
    except Exception as e:
        logger.error(f"Error removing from wishlist: {str(e)}")
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


# ============================================================================
# MATCHMAKING VIEWS
# ============================================================================

class MutualMatchView(LoginRequiredMixin, TemplateView):
    """Daily mutual match view"""
    template_name = "mutual_match.html"
    login_url = '/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        my_profile = Profile.objects.filter(
            user=self.request.user, datamode='A'
        ).order_by('-updated_on').first()
        
        if not my_profile:
            context["error"] = "Please create your profile first to find mutual matches."
            return context
        
        # Match rules
        MATCH_RULES = [
            {"name": "Location", "field": "location", "icon": "fa-map-marker-alt"},
            {"name": "Caste", "field": "caste", "icon": "fa-users"},
            {"name": "Religion", "field": "religion", "icon": "fa-pray"},
            {"name": "Education", "field": "education", "icon": "fa-graduation-cap"},
            {"name": "Profession", "field": "occupation", "icon": "fa-briefcase"},
        ]
        
        rule_index = date.today().toordinal() % len(MATCH_RULES)
        today_rule = MATCH_RULES[rule_index]
        
        # Opposite gender
        target_gender = 'F' if my_profile.gender == 'M' else 'M'
        
        # Base queryset
        profiles = Profile.objects.filter(
            gender=target_gender, datamode='A'
        ).exclude(user=self.request.user)
        
        # Apply today's rule
        field_value = getattr(my_profile, today_rule["field"], None)
        if field_value:
            profiles = profiles.filter(**{today_rule["field"]: field_value})
        
        # Calculate compatibility
        mutual_matches = []
        for profile in profiles:
            profile.age = calculate_age(profile.dob)
            profile.name = profile.full_name or profile.user.get_full_name()
            profile.compatibility = self._calculate_compatibility(my_profile, profile, today_rule["field"])
            mutual_matches.append(profile)
        
        # Sort and paginate
        mutual_matches.sort(key=lambda x: x.compatibility['score'], reverse=True)
        paginator = Paginator(mutual_matches, 6)
        page_number = self.request.GET.get('page')
        
        context.update({
            "matches": paginator.get_page(page_number),
            "match_rule": today_rule,
            "my_profile": my_profile,
            "all_rules": MATCH_RULES,
            "rule_index": rule_index,
        })
        
        return context
    
    def _calculate_compatibility(self, my_profile, other_profile, rule_field):
        """Calculate compatibility score"""
        score = 0
        factors = 0
        matching_points = []
        
        # Today's rule match (40 points)
        my_value = getattr(my_profile, rule_field, None)
        other_value = getattr(other_profile, rule_field, None)
        
        if my_value and other_value and my_value.lower() == other_value.lower():
            score += 40
            matching_points.append(f"Same {rule_field}")
        factors += 1
        
        # Age compatibility (30 points)
        if my_profile.dob and other_profile.dob:
            age_diff = abs(calculate_age(my_profile.dob) - calculate_age(other_profile.dob))
            if age_diff <= 3:
                score += 30
                matching_points.append("Perfect age match")
            elif age_diff <= 5:
                score += 20
                matching_points.append("Good age match")
            factors += 1
        
        # Calculate percentage
        total_possible = factors * 100
        final_score = min(int((score / total_possible) * 100), 100)
        
        return {"score": final_score, "matching_points": matching_points, "rule_field": rule_field}


@login_required
@method_decorator(payment_required, name='dispatch')
def community_match(request):
    """Community matchmaking page"""
    user_profile = Profile.objects.filter(user=request.user).first()
    
    # Base queryset
    profiles = Profile.objects.exclude(
        Q(user=request.user) | Q(datamode='D')
    ).select_related('user')
    
    # Apply filters
    filters = {}
    
    if request.GET.get('gender'):
        profiles = profiles.filter(gender=request.GET['gender'])
        filters['gender'] = request.GET['gender']
    
    # Age filter
    age_min = request.GET.get('age_min')
    age_max = request.GET.get('age_max')
    if age_min or age_max:
        today = date.today()
        if age_min:
            max_birth = today - relativedelta(years=int(age_min))
            profiles = profiles.filter(dob__lte=max_birth)
        if age_max:
            min_birth = today - relativedelta(years=int(age_max))
            profiles = profiles.filter(dob__gte=min_birth)
        filters.update({'age_min': age_min, 'age_max': age_max})
    
    # Location filter
    if request.GET.get('city'):
        profiles = profiles.filter(city=request.GET['city'])
        filters['city'] = request.GET['city']
    
    # Religion filter
    if request.GET.get('religion'):
        profiles = profiles.filter(religion=request.GET['religion'])
        filters['religion'] = request.GET['religion']
    
    # Education filter
    if request.GET.get('education'):
        profiles = profiles.filter(education=request.GET['education'])
        filters['education'] = request.GET['education']
    
    # Calculate compatibility scores
    if user_profile:
        for profile in profiles:
            profile.compatibility_score = calculate_compatibility(user_profile, profile)
    
    # Sorting
    sort_by = request.GET.get('sort', 'compatibility')
    filters['sort'] = sort_by
    
    if sort_by == 'newest':
        profiles = profiles.order_by('-created_on')
    elif sort_by == 'age_low':
        profiles = profiles.order_by('dob')
    elif sort_by == 'age_high':
        profiles = profiles.order_by('-dob')
    else:  # compatibility
        if user_profile:
            profiles = sorted(profiles, key=lambda x: getattr(x, 'compatibility_score', 0), reverse=True)
    
    # Get wishlist IDs
    wishlist_ids = Wishlist.objects.filter(from_user=request.user).values_list('to_profile_id', flat=True)
    
    # Pagination
    paginator = Paginator(profiles, 12)
    page_number = request.GET.get('page', 1)
    
    # Get filter options
    base_qs = Profile.objects.exclude(user=request.user)
    
    context = {
        'profiles': paginator.get_page(page_number),
        'filters': filters,
        'cities': base_qs.exclude(city__isnull=True).values_list('city', flat=True).distinct().order_by('city'),
        'religions': base_qs.exclude(religion__isnull=True).values_list('religion', flat=True).distinct().order_by('religion'),
        'educations': base_qs.exclude(education__isnull=True).values_list('education', flat=True).distinct().order_by('education'),
        'occupations': base_qs.exclude(occupation__isnull=True).values_list('occupation', flat=True).distinct().order_by('occupation'),
        'user_profile': user_profile,
        'wishlist_ids': list(wishlist_ids),
    }
    
    return render(request, 'community_match.html', context)


class Newmatches(TemplateView):
    """New matches page"""
    template_name = "new_match.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("Profile")
        context['profiles'] = Profile.objects.exclude(datamode='D').order_by('-updated_on')
        return context


# ============================================================================
# PAYMENT VIEWS
# ============================================================================
# views.py — COMPLETE FIXED PAYMENT SECTION

import razorpay
import logging
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# FIXED: ajax_profile_save — always redirect to payment if not paid
# ─────────────────────────────────────────────
@require_POST
@login_required
@ensure_csrf_cookie
def ajax_profile_save(request):
    """Save/update profile via AJAX"""
    try:
        profile, created = Profile.objects.get_or_create(
            user=request.user,
            defaults={
                'created_by': request.user.username,
                'updated_by': request.user.username,
                'datamode': 'A',
                'marital_status': 'S'
            }
        )

        pDict = request.POST
        files = request.FILES

        profile.full_name = pDict.get("full_name", "").strip()
        profile.gender = pDict.get("gender", "")

        dob_str = pDict.get("dob")
        if dob_str:
            try:
                profile.dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
            except ValueError:
                profile.dob = None

        birth_time_str = pDict.get("birth_time")
        if birth_time_str:
            try:
                profile.birth_time = datetime.strptime(birth_time_str, "%H:%M").time()
            except ValueError:
                profile.birth_time = None

        profile.religion = pDict.get("religion", "").strip()
        profile.caste = pDict.get("caste", "").strip()
        profile.sub_caste = pDict.get("sub_caste", "").strip()
        profile.gothram = pDict.get("gothram", "").strip()
        profile.rasi = pDict.get("rasi", "").strip()
        profile.nakshatra = pDict.get("nakshatra", "").strip()
        profile.dosham = pDict.get("dosham", "")
        profile.education = pDict.get("education", "").strip()
        profile.occupation = pDict.get("occupation", "").strip()
        profile.company_name = pDict.get("company_name", "").strip()
        profile.job_location = pDict.get("job_location", "").strip()

        income_str = pDict.get("annual_income")
        if income_str:
            try:
                profile.annual_income = Decimal(income_str.replace(',', '').strip())
            except (ValueError, DecimalException):
                profile.annual_income = None

        profile.phone = pDict.get("phone", "").strip()
        profile.whatsapp_number = pDict.get("whatsapp_number", "").strip()
        profile.email = pDict.get("email", "").strip()
        profile.address = pDict.get("address", "").strip()
        profile.city = pDict.get("city", "").strip()
        profile.state = pDict.get("state", "").strip()
        profile.country = pDict.get("country", "").strip()
        profile.pincode = pDict.get("pincode", "").strip()

        for field in ['photo1', 'photo2', 'photo3', 'photo4', 'photo5']:
            if field in files:
                try:
                    setattr(profile, field, files[field])
                except Exception as e:
                    logger.error(f"Error uploading {field}: {str(e)}")

        profile.updated_by = request.user.username
        profile.datamode = 'A'
        profile.save()

        if not request.user.is_profile_completed:
            request.user.is_profile_completed = True
            request.user.save()

        logger.info(f"Profile saved for user {request.user.username}")

        # ✅ KEY FIX: Always go to payment if not paid yet
        if not request.user.has_paid:
            redirect_url = reverse("mck_website:payment_gateway")
        else:
            redirect_url = reverse("mck_website:my_profile")

        return JsonResponse({
            "success": True,
            "message": "Profile saved successfully!",
            "profile_id": profile.id,
            "redirect_url": redirect_url
        })

    except Exception as e:
        logger.exception(f"Error saving profile: {str(e)}")
        return JsonResponse({"success": False, "message": str(e)}, status=400)


# ─────────────────────────────────────────────
# FIXED: PaymentGatewayView — correct amount display
# ─────────────────────────────────────────────
class PaymentGatewayViews(LoginRequiredMixin, TemplateView):
    """Payment gateway page"""
    template_name = "website/payment_gateway.html"
    login_url = '/auth/website/login/'

    def get(self, request, *args, **kwargs):
        # ✅ Redirect away if already paid
        if request.user.has_paid:
            messages.info(request, "You have already completed your payment.")
            return redirect('mck_website:home_page')

        # ✅ Redirect to profile if not completed
        if not request.user.is_profile_completed:
            messages.warning(request, "Please complete your profile first.")
            return redirect('mck_website:profile_page')

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        profile = self.request.user.profiles.first()
        if not profile:
            return context

        try:
            AMOUNT_PAISE = 99900  # ₹999 in paise

            # Check for existing PENDING payment
            existing_payment = Payment.objects.filter(
                user=self.request.user,
                status='PENDING'
            ).first()

            if existing_payment:
                order_id = existing_payment.order_id
                order_amount = int(existing_payment.amount * 100)
            else:
                client = razorpay.Client(
                    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
                )
                razorpay_order = client.order.create({
                    'amount': AMOUNT_PAISE,
                    'currency': 'INR',
                    'receipt': f"rcpt_{self.request.user.id}_{int(timezone.now().timestamp())}",
                    'payment_capture': 1,
                    'notes': {
                        'user_id': str(self.request.user.id),
                        'email': self.request.user.email,
                    }
                })
                order_id = razorpay_order['id']
                order_amount = AMOUNT_PAISE

                Payment.objects.create(
                    user=self.request.user,
                    profile=profile,
                    order_id=order_id,
                    payment_id=f"PENDING_{order_id}",
                    amount=Decimal(order_amount) / 100,  # Store in ₹
                    currency='INR',
                    status='PENDING',
                    response_data=razorpay_order
                )

            context.update({
                'razorpay_key': settings.RAZORPAY_KEY_ID,
                'order_id': order_id,
                'amount_paise': order_amount,           # For Razorpay SDK (paise)
                'amount_rupees': order_amount / 100,    # For display (₹)
                'user_name': profile.full_name or self.request.user.get_full_name() or self.request.user.email,
                'user_email': self.request.user.email,
                'user_phone': profile.phone or '',
                'payment_success_url': reverse('mck_website:payment_success'),
                'payment_failure_url': reverse('mck_website:payment_failure'),
            })
            # Temporary debug - add to get_context_data


        except Exception as e:
            logger.error(f"Payment gateway error: {str(e)}")
            messages.error(self.request, "Unable to initialize payment. Please try again.")


        return context


# ─────────────────────────────────────────────
# FIXED: PaymentSuccessView — robust verification + redirect
# ─────────────────────────────────────────────
@method_decorator(csrf_exempt, name='dispatch')
class PaymentSuccessView(View):
    """Handle Razorpay payment success callback (POST from frontend JS)"""

    def post(self, request, *args, **kwargs):
        try:
            razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            razorpay_signature = request.POST.get('razorpay_signature', '')

            logger.info(
                f"Payment success callback: order={razorpay_order_id}, "
                f"payment={razorpay_payment_id}"
            )

            # ─── Handle undefined values from Razorpay ───
            if razorpay_payment_id in ('undefined', '', None) or \
               razorpay_order_id in ('undefined', '', None):
                return self._handle_undefined_payment(request)

            # ─── Find Payment record ───
            payment = None
            try:
                payment = Payment.objects.get(order_id=razorpay_order_id)
            except Payment.DoesNotExist:
                # Try to find by user
                if request.user.is_authenticated:
                    payment = Payment.objects.filter(
                        user=request.user,
                        status='PENDING'
                    ).first()
                    if payment:
                        payment.order_id = razorpay_order_id
                        payment.save()

            if not payment:
                logger.error(f"No payment record for order: {razorpay_order_id}")
                return JsonResponse(
                    {'status': 'failed', 'message': 'Payment record not found'},
                    status=404
                )

            # ─── Already completed? Return success ───
            if payment.status == 'COMPLETED':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Payment already verified',
                    'redirect_url': reverse('mck_website:payment_success_page')
                })

            # ─── Verify Razorpay Signature ───
            try:
                client = razorpay.Client(
                    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
                )
                client.utility.verify_payment_signature({
                    'razorpay_order_id': razorpay_order_id,
                    'razorpay_payment_id': razorpay_payment_id,
                    'razorpay_signature': razorpay_signature
                })
                logger.info(f"Signature verified for order: {razorpay_order_id}")
            except razorpay.errors.SignatureVerificationError:
                logger.warning(f"Signature verification failed for order: {razorpay_order_id}")
                if not settings.DEBUG:
                    return JsonResponse(
                        {'status': 'failed', 'message': 'Signature verification failed'},
                        status=400
                    )

            # ─── Mark payment complete ───
            payment.mark_completed(razorpay_payment_id, razorpay_signature)
            logger.info(
                f"Payment COMPLETED: order={razorpay_order_id}, "
                f"payment={razorpay_payment_id}, user={payment.user.email}"
            )

            # ─── Set session flag ───
            request.session['payment_success'] = True
            request.session['payment_order_id'] = razorpay_order_id
            request.session.modified = True

            return JsonResponse({
                'status': 'success',
                'message': 'Payment verified successfully',
                'redirect_url': reverse('mck_website:payment_success_page')
            })

        except Exception as e:
            logger.exception(f"Payment success handler error: {str(e)}")
            return JsonResponse(
                {'status': 'failed', 'message': 'Internal server error'},
                status=500
            )

    def _handle_undefined_payment(self, request):
        if request.user.is_authenticated and request.user.has_paid:
            return JsonResponse({
                'status': 'success',
                'message': 'Payment already completed',
                'redirect_url': reverse('mck_website:payment_success_page')
            })
        return JsonResponse(
            {'status': 'failed', 'message': 'Payment was not completed'},
            status=400
        )


# ─────────────────────────────────────────────
# FIXED: PaymentSuccessPageView — no more redirect loop
# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
# STEP 1: Handles POST from Razorpay → verifies → redirects to success page
# ─────────────────────────────────────────────
class PaymentSuccessView(LoginRequiredMixin, View):
    """Receives POST from Razorpay, verifies signature, marks payment completed."""
    login_url = '/auth/website/login/'

    def get(self, request, *args, **kwargs):
        # Block direct GET access
        return redirect('mck_website:payment_gateway')

    def post(self, request, *args, **kwargs):
        payment_id = request.POST.get('razorpay_payment_id', '')
        order_id   = request.POST.get('razorpay_order_id', '')
        signature  = request.POST.get('razorpay_signature', '')

        try:
            # Verify Razorpay signature
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            client.utility.verify_payment_signature({
                'razorpay_order_id':   order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature':  signature,
            })

            # Mark payment completed (sets valid_from, valid_until, status)
            payment = Payment.objects.get(order_id=order_id)
            payment.mark_completed(payment_id, signature)

            # Set session flag for success page
            request.session['payment_success'] = True
            messages.success(request, f"🎉 Payment successful! Your {payment.plan_label} plan is now active.")
            return redirect('mck_website:payment_success_page')

        except Payment.DoesNotExist:
            logger.error(f"Payment not found for order_id: {order_id}")
            messages.error(request, "Payment record not found. Please contact support.")
            return redirect('mck_website:payment_gateway')

        except razorpay.errors.SignatureVerificationError:
            logger.error(f"Signature verification failed for order_id: {order_id}")
            try:
                payment = Payment.objects.get(order_id=order_id)
                payment.mark_failed("Signature verification failed")
            except Payment.DoesNotExist:
                pass
            messages.error(request, "Payment verification failed. Please contact support.")
            return redirect('mck_website:payment_gateway')

        except Exception as e:
            logger.exception(f"PaymentSuccessView POST error: {e}")
            messages.error(request, "Something went wrong. Please contact support.")
            return redirect('mck_website:payment_gateway')


# ─────────────────────────────────────────────
# STEP 2: Displays the success page (your existing view — unchanged)
# ─────────────────────────────────────────────
class PaymentSuccessPageView(LoginRequiredMixin, TemplateView):
    """Payment success display page"""
    template_name = "website/payment_success.html"
    login_url = '/auth/website/login/'

    def get(self, request, *args, **kwargs):
        if not request.user.has_paid:
            messages.warning(request, "No completed payment found.")
            return redirect('mck_website:payment_gateway')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payment = self.request.user.payments.filter(status='COMPLETED').order_by('-payment_date').first()
        if payment:
            context.update({
                'payment':      payment,
                'payment_id':   payment.payment_id,
                'amount':       payment.amount,
                'payment_date': payment.payment_date,
                'plan_label':   payment.plan_label,
                'valid_until':  payment.valid_until,
                'days_remaining': payment.days_remaining,
            })
        self.request.session.pop('payment_success', None)
        return context
# ─────────────────────────────────────────────
# PaymentFailureView (unchanged, works fine)
# ─────────────────────────────────────────────
@method_decorator(csrf_exempt, name='dispatch')
class PaymentFailureView(View):
    def post(self, request, *args, **kwargs):
        razorpay_order_id = request.POST.get('razorpay_order_id', '')
        error_description = request.POST.get('error_description', 'Payment failed')

        try:
            payment = Payment.objects.get(order_id=razorpay_order_id)
            payment.mark_failed(error_description)
        except Payment.DoesNotExist:
            logger.error(f"Payment not found for failure callback: {razorpay_order_id}")
        except Exception as e:
            logger.error(f"Error recording failure: {str(e)}")

        return JsonResponse({'status': 'failed', 'message': error_description})


@method_decorator(csrf_exempt, name='dispatch')
class PaymentCallbackView(PaymentSuccessView):
    """Payment success display page"""
    template_name = "website/payment_success.html"
    login_url = '/auth/website/login/'

    def get(self, request, *args, **kwargs):
        # ✅ Check DB (not just session) — most reliable
        if not request.user.has_paid:
            messages.warning(request, "No completed payment found.")
            return redirect('mck_website:payment_gateway')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payment = self.request.user.payments.filter(status='COMPLETED').first()
        if payment:
            context.update({
                'payment': payment,
                'payment_id': payment.payment_id,
                'amount': payment.amount,
                'payment_date': payment.payment_date,
            })
        # Clear session flag
        self.request.session.pop('payment_success', None)
        return context
   

# ============================================================================
# OTHER VIEWS
# ============================================================================

class MaintenancesCreatePage(TemplateView):
    """Maintenance requests page"""
    template_name = "pages/faq.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_kwargs"] = seo.get_page_tags("maintenance")
        context["maintenance"] = MaintenanceRequest.objects.exclude(datamode='D').order_by('-updated_on')
        return context


class EnquiryCreatePage(TemplateView):
    """Enquiry form page"""
    template_name = "includes/enquiry.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["selected_property_type"] = self.request.GET.get('property_type', '')
        return context


class ProfileFilterView(ListView):
    """Profile filter view"""
    model = Profile
    template_name = 'profile_filter.html'
    context_object_name = 'profiles'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Profile.objects.exclude(datamode='D')
        filters = Q()
        
        # Apply filters
        if self.request.GET.get('gender'):
            filters &= Q(gender=self.request.GET['gender'])
        
        if self.request.GET.get('city'):
            filters &= Q(city__icontains=self.request.GET['city'])
        
        if self.request.GET.get('religion'):
            filters &= Q(religion=self.request.GET['religion'])
        
        if self.request.GET.get('caste'):
            filters &= Q(caste=self.request.GET['caste'])
        
        if self.request.GET.get('education'):
            filters &= Q(education__icontains=self.request.GET['education'])
        
        if self.request.GET.get('profession'):
            filters &= Q(occupation__icontains=self.request.GET['profession'])
        
        if self.request.GET.get('with_photo'):
            filters &= (Q(photo1__isnull=False) | Q(photo2__isnull=False) | Q(photo3__isnull=False) |
                       Q(photo4__isnull=False) | Q(photo5__isnull=False))
        
        queryset = queryset.filter(filters)
        
        # Apply sorting
        sort_by = self.request.GET.get('sort', 'newest')
        if sort_by == 'newest':
            queryset = queryset.order_by('-created_on')
        elif sort_by == 'age_low':
            queryset = queryset.order_by('-dob')
        elif sort_by == 'age_high':
            queryset = queryset.order_by('dob')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get filter choices
        base_qs = Profile.objects.exclude(datamode='D')
        
        context.update({
            'religion_choices': base_qs.exclude(religion='').values_list('religion', flat=True).distinct().order_by('religion'),
            'caste_choices': base_qs.exclude(caste='').values_list('caste', flat=True).distinct().order_by('caste'),
            'city_choices': base_qs.exclude(city='').values_list('city', flat=True).distinct().order_by('city'),
            'complexion_choices': base_qs.exclude(complexion='').values_list('complexion', flat=True).distinct().order_by('complexion'),
            'filters': self.request.GET.dict(),
        })
        
        # Add ages to profiles
        for profile in context['profiles']:
            profile.age = calculate_age(profile.dob)
        
        return context


class ProfileCompletionView(LoginRequiredMixin, TemplateView):
    """Profile completion page"""
    template_name = "website/profile_completion.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.profiles.exists():
            self.request.user.is_profile_completed = True
            self.request.user.save()
            context['redirect_url'] = reverse('mck_website:payment_gateway')
        
        return context
    
    def post(self, request, *args, **kwargs):
        profile, created = Profile.objects.get_or_create(
            user=request.user,
            defaults={'full_name': request.POST.get('full_name', '')}
        )
        
        if not created:
            profile.full_name = request.POST.get('full_name', profile.full_name)
            profile.gender = request.POST.get('gender', profile.gender)
            profile.phone = request.POST.get('phone', profile.phone)
            profile.save()
        
        request.user.is_profile_completed = True
        request.user.save()
        
        messages.success(request, "Profile completed! Please proceed to payment.")
        return redirect('mck_website:payment_gateway')


# Deprecated/Compatibility views
class ProfilSaveView(PropertySaveView):
    """Deprecated - use ProfileSaveView instead"""
    pass


class ProfileCreatePage(TemplateView):
    """Deprecated - kept for backward compatibility"""
    template_name = "includes/enquiry.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = Profile.objects.exclude(datamode='D').order_by('-updated_on')
        return context


# ============================================================================
# UPDATED: CommunitySearchPage in views.py
# Replace the existing class entirely with this
@method_decorator(login_required(login_url=settings.LOGIN_WEB_REDIRECT_URL), name='dispatch')
@method_decorator(payment_required, name='dispatch')
class CommunitySearchPage(TemplateView):
    template_name = "community_search.html"

    def get_distinct_values(self, field_name, base_qs=None):
        qs = base_qs if base_qs is not None else Profile.objects.exclude(datamode='D')
        return qs.exclude(
            **{f"{field_name}__isnull": True}
        ).exclude(
            **{f"{field_name}": ""}
        ).values_list(field_name, flat=True).distinct().order_by(field_name)

    def get_city_list(self, base_qs=None):
        """
        Get distinct cities from birth_place field
        """
        qs = base_qs if base_qs is not None else Profile.objects.exclude(datamode='D')
        cities = qs.exclude(
            birth_place__isnull=True
        ).exclude(
            birth_place=""
        ).values_list('birth_place', flat=True).distinct().order_by('birth_place')
        return list(cities)

    def get(self, request, *args, **kwargs):
        from mck_master.models import ProfileView

        context = {}
        user = request.user

        # ── Plan / limit info ────────────────────────────────────────────────
        active_plan  = user.active_plan
        view_limit   = user.profile_view_limit
        views_used   = ProfileView.count_for_user(user)
        can_upgrade  = user.can_upgrade
        plan_label   = active_plan.plan_label if active_plan else ""

        # ── Profile limit based on plan (Basic=5, Silver=10, Gold=15 …) ─────
        profile_limit = get_plan_profile_limit(user)

        # ── Base queryset: ALL paid profiles ─────────────────────────────────
        profiles = get_all_paid_profile_queryset(user).select_related('user')

        # ── Opposite gender only ─────────────────────────────────────────────
        profiles = apply_gender_filter(profiles, user)

        # ── Current user's profile (for compatibility scoring) ───────────────
        user_profile = user.profiles.filter(datamode='A').order_by('-updated_on').first()

        # ── Read filters ─────────────────────────────────────────────────────
        city       = request.GET.get('city')
        gender     = request.GET.get('gender')
        religion   = request.GET.get('religion')
        education  = request.GET.get('education')
        profession = request.GET.get('profession')
        status     = request.GET.get('status')
        income     = request.GET.get('income')
        age_min    = request.GET.get('age_min')
        age_max    = request.GET.get('age_max')
        sort       = request.GET.get('sort', 'compatibility')

        # ── Apply filters ────────────────────────────────────────────────────
        # City filter - now using birth_place
        if city:
            profiles = profiles.filter(birth_place__icontains=city)

        if gender:
            gender_map = {'male': 'M', 'female': 'F', 'other': 'O'}
            if gender in gender_map:
                profiles = profiles.filter(gender=gender_map[gender])

        if religion:
            profiles = profiles.filter(religion__iexact=religion)

        if education:
            profiles = profiles.filter(education__icontains=education)

        if profession:
            profiles = profiles.filter(occupation__icontains=profession)

        if status:
            profiles = profiles.filter(marital_status=status)

        if age_min or age_max:
            today = date.today()
            if age_min and age_min.isdigit():
                profiles = profiles.filter(dob__lte=today - relativedelta(years=int(age_min)))
            if age_max and age_max.isdigit():
                profiles = profiles.filter(dob__gte=today - relativedelta(years=int(age_max)))

        INCOME_FILTERS = {
            "below_10":  dict(annual_income__lt=1_000_000),
            "10_25":     dict(annual_income__gte=1_000_000,  annual_income__lte=2_500_000),
            "25_50":     dict(annual_income__gte=2_500_000,  annual_income__lte=5_000_000),
            "50_100":    dict(annual_income__gte=5_000_000,  annual_income__lte=10_000_000),
            "above_100": dict(annual_income__gt=10_000_000),
        }
        if income and income in INCOME_FILTERS:
            profiles = profiles.filter(**INCOME_FILTERS[income])

        # ── Build profile list with compatibility + view-limit awareness ──────
        profiles_list = []
        today = date.today()

        for profile in profiles:
            profile.age = (
                today.year - profile.dob.year -
                ((today.month, today.day) < (profile.dob.month, profile.dob.day))
            ) if profile.dob else None

            profile.name = (
                profile.full_name or
                (f"{profile.user.first_name} {profile.user.last_name}".strip() if profile.user else "") or
                "Profile"
            )

            # Set location from birth_place
            profile.location = profile.birth_place or ""

            profile.profile_photo = None
            for pf in ['photo1', 'photo2', 'photo3', 'photo4', 'photo5']:
                photo = getattr(profile, pf, None)
                if photo:
                    profile.profile_photo = photo
                    break

            # ── VIEW-LIMIT: mark whether this profile can be fully viewed ──
            already_viewed = ProfileView.has_viewed(user, profile)
            profile.can_view   = already_viewed or (views_used < view_limit)
            profile.is_blurred = not profile.can_view

            # ── Compatibility score ────────────────────────────────────────
            compatibility_score = 0
            if user_profile:
                score, factors = 0, 0

                checks = [
                    ('religion',    20, lambda a, b: a == b, None),
                    ('caste',       15, lambda a, b: a == b, None),
                    ('sub_caste',   10, lambda a, b: a == b, None),
                    ('education',   15, None,                'edu_special'),
                    ('occupation',  15, None,                'occ_special'),
                    ('birth_place', 10, lambda a, b: a == b, None),  # Changed from job_location
                    ('dosham',      10, lambda a, b: a == b, None),
                    ('rasi',         5, lambda a, b: a == b, None),
                    ('nakshatra',    5, lambda a, b: a == b, None),
                ]

                for field, pts, cmp_fn, special in checks:
                    val_p = getattr(profile,      field, None)
                    val_u = getattr(user_profile, field, None)
                    if not (val_p and val_u):
                        continue
                    factors += 1

                    if special == 'edu_special':
                        if val_p == val_u:
                            score += pts
                        elif any(k in val_p.lower() for k in ['phd','master','mba']) and \
                             any(k in val_u.lower() for k in ['phd','master','mba']):
                            score += 10

                    elif special == 'occ_special':
                        categories = {
                            'software': ['it','developer','engineer','programmer'],
                            'doctor':   ['medical','surgeon','physician','dentist'],
                            'business': ['entrepreneur','management','ceo','owner'],
                            'engineer': ['mechanical','civil','electrical','chemical'],
                            'teacher':  ['professor','lecturer','educator'],
                            'banking':  ['finance','accountant','analyst'],
                        }
                        matched = any(
                            all(any(k in v.lower() for k in kws) for v in [val_p, val_u])
                            for kws in categories.values()
                        )
                        score += pts if matched else (10 if val_p == val_u else 0)

                    else:
                        if cmp_fn and cmp_fn(val_p, val_u):
                            score += pts

                if factors > 0:
                    compatibility_score = min(int((score / (factors * 15)) * 100), 100)

            profile.compatibility_score = compatibility_score
            profiles_list.append(profile)

        # ── Sort ─────────────────────────────────────────────────────────────
        sort_keys = {
            'compatibility': (lambda x: x.compatibility_score, True),
            'age_low':       (lambda x: x.age or 0,           False),
            'age_high':      (lambda x: x.age or 0,           True),
            'income_high':   (lambda x: x.annual_income or 0, True),
            'newest':        (lambda x: x.updated_on,         True),
        }
        key_fn, rev = sort_keys.get(sort, sort_keys['compatibility'])
        profiles_list.sort(key=key_fn, reverse=rev)

        # ── Cap to plan limit AFTER sorting ──────────────────────────────────
        profiles_list = profiles_list[:profile_limit]

        # ── Pagination ───────────────────────────────────────────────────────
        paginator     = Paginator(profiles_list, 12)
        profiles_page = paginator.get_page(request.GET.get('page'))

        # ── Wishlist IDs for this user ───────────────────────────────────────
        wishlist_ids = list(
            Wishlist.objects.filter(from_user=user).values_list('to_profile_id', flat=True)
        )

        # ── Filter dropdowns — scoped to all paid profiles ───────────────────
        all_paid_qs = get_all_paid_profile_queryset(user)

        context.update({
            "profiles":      profiles_page,
            "filters":       request.GET,
            "user_profile":  user_profile,
            "wishlist_ids":  wishlist_ids,
            # Filter dropdown options
            "cities":        self.get_city_list(all_paid_qs),  # Now using birth_place
            "religions":     self.get_distinct_values('religion',   all_paid_qs),
            "educations":    self.get_distinct_values('education',  all_paid_qs),
            "occupations":   self.get_distinct_values('occupation', all_paid_qs),
            # Plan info
            "active_plan":   active_plan,
            "plan_label":    plan_label,
            "views_used":    views_used,
            "view_limit":    view_limit,
            "can_upgrade":   can_upgrade,
            "profile_limit": profile_limit,  # show in template: "Viewing X of Y profiles"
        })

        return render(request, self.template_name, context)


@method_decorator(login_required(login_url=settings.LOGIN_WEB_REDIRECT_URL), name='dispatch')
@method_decorator(payment_required, name='dispatch')
class CommunitySearchPages(TemplateView):
    template_name = "community_search.html"
    
    def get_distinct_values(self, field_name):
        """Get distinct non-null values for a field from active profiles"""
        return Profile.objects.exclude(
            datamode='D'
        ).exclude(
            **{f"{field_name}__isnull": True}
        ).exclude(
            **{f"{field_name}": ""}
        ).values_list(field_name, flat=True).distinct().order_by(field_name)
    
    def get_education_list(self):
        """Get distinct education values"""
        return self.get_distinct_values('education')
    
    def get_occupation_list(self):
        """Get distinct occupation values"""
        return self.get_distinct_values('occupation')
    
    def get_religion_list(self):
        """Get distinct religion values"""
        return self.get_distinct_values('religion')
    
    def get_city_list(self):
        """Get distinct city values from all location fields"""
        cities = set()
        
        # Get from city field
        city_values = Profile.objects.exclude(
            datamode='D'
        ).exclude(
            city__isnull=True
        ).exclude(
            city=""
        ).values_list('city', flat=True).distinct()
        cities.update(city_values)
        
        # Get from current_location
        current_location_values = Profile.objects.exclude(
            datamode='D'
        ).exclude(
            current_location__isnull=True
        ).exclude(
            current_location=""
        ).values_list('current_location', flat=True).distinct()
        cities.update(current_location_values)
        
        # Get from job_location
        job_location_values = Profile.objects.exclude(
            datamode='D'
        ).exclude(
            job_location__isnull=True
        ).exclude(
            job_location=""
        ).values_list('job_location', flat=True).distinct()
        cities.update(job_location_values)
        
        return sorted(list(cities))
    
    def get(self, request, *args, **kwargs):
        context = {}
        
        # Base queryset - exclude deleted profiles
        profiles = Profile.objects.exclude(datamode='D').select_related('user')
        
        # Get active profile for logged-in user (for compatibility scoring)
        user_profile = None
        if request.user.is_authenticated:
            user_profile = Profile.objects.filter(
                user=request.user, 
                datamode='A'
            ).order_by('-updated_on').first()
        
        # ------------------ FILTERS ------------------
        city = request.GET.get('city')
        gender = request.GET.get('gender')
        religion = request.GET.get('religion')
        education = request.GET.get('education')
        profession = request.GET.get('profession')
        status = request.GET.get('status')
        income = request.GET.get('income')
        age_min = request.GET.get('age_min')
        age_max = request.GET.get('age_max')
        sort = request.GET.get('sort', 'compatibility')
        
        # ------------------ APPLY FILTERS ------------------
        if city:
            profiles = profiles.filter(
                Q(city__icontains=city) | 
                Q(current_location__icontains=city) |
                Q(job_location__icontains=city)
            )
        
        if gender:
            gender_map = {'male': 'M', 'female': 'F', 'other': 'O'}
            if gender in gender_map:
                profiles = profiles.filter(gender=gender_map[gender])
        
        if religion:
            profiles = profiles.filter(religion__iexact=religion)
        
        if education:
            profiles = profiles.filter(education__icontains=education)
        
        if profession:
            profiles = profiles.filter(occupation__icontains=profession)
        
        if status:
            profiles = profiles.filter(marital_status=status)
        
        # ------------------ AGE FILTER ------------------
        if age_min or age_max:
            today = date.today()
            
            if age_min and age_min.isdigit():
                max_birth_date = today - relativedelta(years=int(age_min))
                profiles = profiles.filter(dob__lte=max_birth_date)
            
            if age_max and age_max.isdigit():
                min_birth_date = today - relativedelta(years=int(age_max))
                profiles = profiles.filter(dob__gte=min_birth_date)
        
        # ------------------ INCOME FILTER ------------------
        if income:
            if income == "below_10":
                profiles = profiles.filter(annual_income__lt=1000000)
            elif income == "10_25":
                profiles = profiles.filter(annual_income__gte=1000000, annual_income__lte=2500000)
            elif income == "25_50":
                profiles = profiles.filter(annual_income__gte=2500000, annual_income__lte=5000000)
            elif income == "50_100":
                profiles = profiles.filter(annual_income__gte=5000000, annual_income__lte=10000000)
            elif income == "above_100":
                profiles = profiles.filter(annual_income__gt=10000000)
        
        # ------------------ EXCLUDE OWN PROFILE ------------------
        if user_profile:
            profiles = profiles.exclude(id=user_profile.id)
        
        # ------------------ CALCULATE COMPATIBILITY ------------------
        profiles_list = []
        today = date.today()
        
        for profile in profiles:
            # Calculate age from dob
            if profile.dob:
                age = today.year - profile.dob.year - (
                    (today.month, today.day) < (profile.dob.month, profile.dob.day)
                )
                profile.age = age
            else:
                profile.age = None
            
            # Set display name
            if profile.full_name:
                profile.name = profile.full_name
            elif profile.user:
                profile.name = f"{profile.user.first_name} {profile.user.last_name}".strip()
            else:
                profile.name = "Profile"
            
            # Set location for display
            profile.location = profile.city or profile.current_location or profile.job_location or ""
            
            # Set profile photo
            profile.profile_photo = None
            for photo_field in ['photo1', 'photo2', 'photo3', 'photo4', 'photo5']:
                photo = getattr(profile, photo_field, None)
                if photo:
                    profile.profile_photo = photo
                    break
            
            # Calculate compatibility score if user has a profile
            compatibility_score = 0
            if user_profile:
                score = 0
                factors = 0
                
                # Religion compatibility (20 points)
                if profile.religion and user_profile.religion:
                    if profile.religion == user_profile.religion:
                        score += 20
                    factors += 1
                
                # Caste compatibility (15 points)
                if profile.caste and user_profile.caste:
                    if profile.caste == user_profile.caste:
                        score += 15
                    factors += 1
                
                # Sub-caste compatibility (10 points)
                if profile.sub_caste and user_profile.sub_caste:
                    if profile.sub_caste == user_profile.sub_caste:
                        score += 10
                    factors += 1
                
                # Education compatibility (15 points)
                if profile.education and user_profile.education:
                    if profile.education == user_profile.education:
                        score += 15
                    elif any(edu in profile.education.lower() for edu in ['phd', 'master', 'mba']) and \
                         any(edu in user_profile.education.lower() for edu in ['phd', 'master', 'mba']):
                        score += 10
                    factors += 1
                
                # Occupation compatibility (15 points)
                if profile.occupation and user_profile.occupation:
                    similar_professions = {
                        'software': ['it', 'developer', 'engineer', 'programmer'],
                        'doctor': ['medical', 'surgeon', 'physician', 'dentist'],
                        'business': ['entrepreneur', 'management', 'ceo', 'owner'],
                        'engineer': ['mechanical', 'civil', 'electrical', 'chemical'],
                        'teacher': ['professor', 'lecturer', 'educator'],
                        'banking': ['finance', 'accountant', 'analyst']
                    }
                    
                    matched = False
                    for category, keywords in similar_professions.items():
                        if any(keyword in profile.occupation.lower() for keyword in keywords) and \
                           any(keyword in user_profile.occupation.lower() for keyword in keywords):
                            score += 15
                            matched = True
                            break
                    
                    if not matched and profile.occupation == user_profile.occupation:
                        score += 10
                    factors += 1
                
                # Job location compatibility (10 points)
                if profile.job_location and user_profile.job_location:
                    if profile.job_location == user_profile.job_location:
                        score += 10
                    elif profile.city and user_profile.city and profile.city == user_profile.city:
                        score += 8
                    factors += 1
                
                # Dosham compatibility (10 points)
                if profile.dosham and user_profile.dosham:
                    if profile.dosham == user_profile.dosham:
                        score += 10
                    factors += 1
                
                # Rasi compatibility (5 points)
                if profile.rasi and user_profile.rasi:
                    if profile.rasi == user_profile.rasi:
                        score += 5
                    factors += 1
                
                # Nakshatra compatibility (5 points)
                if profile.nakshatra and user_profile.nakshatra:
                    if profile.nakshatra == user_profile.nakshatra:
                        score += 5
                    factors += 1
                
                # Calculate final percentage (max 100)
                if factors > 0:
                    compatibility_score = min(int((score / (factors * 15)) * 100), 100)
            
            profile.compatibility_score = compatibility_score
            profiles_list.append(profile)
        
        # ------------------ SORTING ------------------
        if sort == "compatibility":
            profiles_list.sort(key=lambda x: x.compatibility_score, reverse=True)
        elif sort == "age_low":
            profiles_list.sort(key=lambda x: x.age if x.age else 0)
        elif sort == "age_high":
            profiles_list.sort(key=lambda x: x.age if x.age else 0, reverse=True)
        elif sort == "income_high":
            profiles_list.sort(key=lambda x: x.annual_income if x.annual_income else 0, reverse=True)
        elif sort == "newest":
            profiles_list.sort(key=lambda x: x.updated_on, reverse=True)
        
        # ------------------ PAGINATION ------------------
        paginator = Paginator(profiles_list, 12)
        page_number = request.GET.get('page')
        profiles_page = paginator.get_page(page_number)
        
        # Add filter lists to context
        context["profiles"] = profiles_page
        context["filters"] = request.GET
        context["user_profile"] = user_profile
        context["cities"] = self.get_city_list()
        context["religions"] = self.get_religion_list()
        context["educations"] = self.get_education_list()
        context["occupations"] = self.get_occupation_list()
        
        return render(request, self.template_name, context)


# views.py
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render


@method_decorator(login_required(login_url=settings.LOGIN_WEB_REDIRECT_URL), name='dispatch')
def payment_dashboard(request):
    payments = Payment.objects.select_related('user').order_by('-created_on')
    return render(request, 'website/payment_dashboard.html', {'payments': payments})


class ContactPageView(TemplateView):
    """Contact page"""
    template_name = "contact_us.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle regular form submission (non-AJAX)"""
        context = self.get_context_data(**kwargs)
        
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Let the AJAX endpoint handle it
            return ajax_contact_submit(request)
        
        # Regular form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        message = request.POST.get('message')
        
        if name and email and message:
            try:
                contact = Contact(
                    name=name,
                    email=email,
                    phone=phone,
                    message=message,
                    created_by='0',
                    updated_by='0',
                    datamode='A'
                )
                contact.save()
                messages.success(request, 'Thank you! Your message has been sent successfully.')
                return redirect('mck_website:contact-us')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.error(request, 'Please fill in all required fields.')
        
        return render(request, self.template_name, context)




@require_POST
@csrf_exempt
def ajax_contact_submit(request):
    """AJAX endpoint for contact form submission"""
    try:
        print("="*50)
        print("AJAX contact submission received")
        print("POST data:", request.POST)
        
        # Get data from POST request
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        message = request.POST.get('message')
        
        print(f"Name: {name}, Email: {email}, Phone: {phone}, Message: {message}")
        
        # Validate required fields
        if not name or not name.strip():
            return JsonResponse({
                'success': False,
                'message': 'Name is required.'
            })
        
        if not email or not email.strip():
            return JsonResponse({
                'success': False,
                'message': 'Email is required.'
            })
        
        if not message or not message.strip():
            return JsonResponse({
                'success': False,
                'message': 'Message is required.'
            })
        
        # Create contact object
        contact = Contact(
            name=name.strip(),
            email=email.strip(),
            phone=phone.strip() if phone else '',
            message=message.strip(),
            created_by='0',  # Public submission
            updated_by='0',
            datamode='A'
        )
        contact.save()
        
        print(f"Contact saved with ID: {contact.id}")
        
        return JsonResponse({
            'success': True,
            'message': 'Thank you! Your message has been sent successfully.'
        })
        
    except Exception as e:
        print(f"Error in ajax_contact_submit: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


class AboutUsView(TemplateView):
    template_name = "page/about-us.html"

class PrivacyPolicyView(TemplateView):
    template_name = "page/privacy-policy.html"

class TermsView(TemplateView):
    template_name = "page/terms.html"

class RefundPolicyView(TemplateView):
    template_name = "page/refund-policy.html"
    
    
import json
from django.shortcuts        import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http   import require_POST
from django.http             import JsonResponse
from django.core.mail        import EmailMultiAlternatives
from django.template.loader  import render_to_string
from django.utils.html       import strip_tags
from django.conf             import settings
from django.utils            import timezone

from .models import UPIPaymentRequest          # adjust import path as needed


# ── Plan meta ──────────────────────────────────────────────────────────────────
PLAN_META = {
    'THREE_MONTH': {'label': '3 Month Plan',  'amount': 2999,  'months': 3},
    'SIX_MONTH':   {'label': '6 Month Plan',  'amount': 5999,  'months': 6},
    'ONE_YEAR':    {'label': '1 Year Plan',   'amount': 11999, 'months': 12},
}


# ── Pricing page (unchanged, kept here for reference) ──────────────────────────
@login_required
def pricing_page(request):
    """Your existing pricing view — attach UPI scanner QR context."""
    from .models import UserPaymentPlan          # your existing plan model
    active_plan = UserPaymentPlan.objects.filter(
        user=request.user, valid_until__gte=timezone.now().date()
    ).order_by('-valid_until').first()

    return render(request, 'mck_website/pricing.html', {
        'active_plan':  active_plan,
        'plan_meta':    PLAN_META,
        'upi_id':       settings.MCK_UPI_ID,       # e.g. "mckmatrimony@upi"
        'upi_qr_url':   settings.MCK_UPI_QR_URL,   # path/URL to your QR image
    })


# ── Upload screenshot ──────────────────────────────────────────────────────────
@login_required
@require_POST
def upi_upload_screenshot(request):
    plan_key   = request.POST.get('plan', '').strip()
    utr        = request.POST.get('utr_number', '').strip()
    screenshot = request.FILES.get('screenshot')

    # ── Basic validation ───────────────────────────────────────────────────────
    if plan_key not in PLAN_META:
        return JsonResponse({'success': False, 'message': 'Invalid plan selected.'}, status=400)

    if not screenshot:
        return JsonResponse({'success': False, 'message': 'Please upload a payment screenshot.'}, status=400)

    allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
    if screenshot.content_type not in allowed_types:
        return JsonResponse({'success': False, 'message': 'Only JPG, PNG, or WEBP images are accepted.'}, status=400)

    if screenshot.size > 5 * 1024 * 1024:          # 5 MB limit
        return JsonResponse({'success': False, 'message': 'File size must be under 5 MB.'}, status=400)

    meta = PLAN_META[plan_key]

    # ── Save request ───────────────────────────────────────────────────────────
    payment_req = UPIPaymentRequest.objects.create(
        user       = request.user,
        plan       = plan_key,
        amount     = meta['amount'],
        utr_number = utr,
        screenshot = screenshot,
        status     = 'PENDING',
    )

    # ── Notify admin ───────────────────────────────────────────────────────────
    _send_admin_notification(payment_req, request)

    return JsonResponse({'success': True, 'message': 'Screenshot uploaded! Pending admin approval.'})


# ── Internal: send admin email ─────────────────────────────────────────────────
def _send_admin_notification(payment_req, request):
    """
    Sends a rich HTML email to ADMINS with payment details.
    Falls back gracefully if email fails (logs error, doesn't crash the upload).
    """
    try:
        admin_emails = [email for _, email in settings.ADMINS]
        if not admin_emails:
            admin_emails = [settings.DEFAULT_FROM_EMAIL]

        user     = payment_req.user
        username = getattr(user, 'get_full_name', lambda: user.username)() or user.username

        # Build absolute URL for the screenshot (useful for admin review)
        screenshot_url = request.build_absolute_uri(payment_req.screenshot.url)

        # Admin panel deep-link (adjust app label / model name if needed)
        admin_url = request.build_absolute_uri(
            f'/admin/mck_website/upipaymnetrequest/{payment_req.id}/change/'
        )

        subject = f"[MCK] New UPI Payment — {payment_req.plan_label} by {username}"

        html_body = render_to_string('mck_website/emails/admin_upi_notification.html', {
            'payment':       payment_req,
            'user':          user,
            'username':      username,
            'screenshot_url': screenshot_url,
            'admin_url':     admin_url,
        })
        text_body = strip_tags(html_body)

        msg = EmailMultiAlternatives(
            subject      = subject,
            body         = text_body,
            from_email   = settings.DEFAULT_FROM_EMAIL,
            to           = admin_emails,
        )
        msg.attach_alternative(html_body, 'text/html')
        msg.send(fail_silently=False)

    except Exception as exc:
        # Log and continue — never let email failure break the upload response
        import logging
        logging.getLogger(__name__).error(
            "Admin UPI notification email failed: %s", exc, exc_info=True
        )