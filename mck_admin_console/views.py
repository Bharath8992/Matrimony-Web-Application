"""
Views - mck Admin Console App
"""
import json
import sys
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import redirect
from django.views.generic.base import RedirectView
from django.contrib.auth import logout as auth_logout
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from config import app_logger
from config import app_seo as seo
from config import settings
from mck_auth import build_table as bt
from mck_auth import role_validations as rv
from mck_admin_console import api
from mck_admin_console import forms
from django.views.generic.edit import FormView  # Change import if needed
from django.shortcuts import get_object_or_404  # Import this to fetch objects by ID
from mck_admin_console.models import *
from mck_master.models import *
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import render, HttpResponseRedirect
from django.views.generic import TemplateView, RedirectView
from django.contrib.auth import logout as auth_logout
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required




LOG_NAME = "app"
logger = app_logger.createLogger(LOG_NAME)

@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class LandingPage(TemplateView):
    """
    Landing Page
    """
    template_name = "landing_page.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        # Check if user is authenticated
        if request.user.is_authenticated:
            # Check if user is admin/staff
            if request.user.is_staff or request.user.is_superuser:
                return HttpResponseRedirect(reverse("svm_admin_console:mck_dashboard"))
            else:
                # Regular user - redirect to website home
                return HttpResponseRedirect(reverse("mck_website:home_page"))
        
        # Not authenticated - show landing page
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("landing_page")
        return render(request, self.template_name, context)

    @csrf_exempt
    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("landing_page")
        logger.info(request.GET)
        logger.info(request.POST)
        return render(request, self.template_name, context)


@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class DashboardView(TemplateView):
    template_name = "dashboard.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("DashboardView")

        # First check if user is admin/staff
        if not request.user.is_staff and not request.user.is_superuser:
            # Check if they have specific business permissions
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission:
                logger.warning(f"Non-admin user {request.user.username} attempted to access admin dashboard")
                messages.error(request, "You don't have permission to access the admin area.")
                return HttpResponseRedirect(reverse("mck_website:home_page"))

        # Validate requested user function
        has_permission, accountuser = rv.validate_requested_user_function(request)
        if not has_permission:
            return render(request, "access_denied.html", context)

        # All profiles except deleted
        profiles = Profile.objects.exclude(datamode='D').select_related('user').order_by('-updated_on')
        
        # Get all users with their payment status (optimized with prefetch)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        users = User.objects.prefetch_related('payments').all()
        
        # Calculate payment statistics
        paid_users = users.filter(payments__status='COMPLETED').distinct().count()
        total_users = users.count()
        
        # Count users with pending payments
        from django.db.models import Q, Count
        pending_users = users.filter(
            Q(payments__status='PENDING') & 
            ~Q(payments__status='COMPLETED')
        ).distinct().count()
        
        # Unpaid users (users with no completed payments and no pending payments)
        unpaid_users = total_users - paid_users - pending_users
        
        # Today's added profiles
        from django.utils import timezone
        today = timezone.now().date()
        today_added = profiles.filter(created_on__date=today).count()
        
        # This week's added profiles
        week_ago = timezone.now() - timezone.timedelta(days=7)
        week_added = profiles.filter(created_on__gte=week_ago).count()
        
        # Gender statistics
        male_profiles = profiles.filter(gender='M').count()
        female_profiles = profiles.filter(gender='F').count()
        other_profiles = profiles.exclude(gender__in=['M', 'F']).count()
        
        # Calculate percentages
        total_profiles = profiles.count()
        male_pct = (male_profiles / total_profiles * 100) if total_profiles > 0 else 0
        female_pct = (female_profiles / total_profiles * 100) if total_profiles > 0 else 0
        paid_pct = (paid_users / total_users * 100) if total_users > 0 else 0
 
        total_revenue = Payment.objects.filter(status='COMPLETED').aggregate(
            total=models.Sum('amount')
        )['total'] or 0

        context.update({
            "profile": profiles,
            "total_profiles": total_profiles,
            "total_users": total_users,
            "male_profiles": male_profiles,
            "female_profiles": female_profiles,
            "other_profiles": other_profiles,
            "male_pct": round(male_pct, 1),
            "female_pct": round(female_pct, 1),
            "today_added": today_added,
            "week_added": week_added,
            "paid_count": paid_users,
            "unpaid_count": unpaid_users,
            "pending_payments": pending_users,
            "paid_pct": round(paid_pct, 1),
            "total_revenue": total_revenue,
            "current_date": timezone.now(),
        })

        return render(request, self.template_name, context)

@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class FAQCategoryList(TemplateView):
    template_name = "table_data_list.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs']= seo.get_page_tags("FAQCategoryList")
        has_permission, accountuser = rv.validate_requested_user_function(request)
        if not has_permission: return render(request, "access_denied.html", context)
        context['table_data'] = bt.build_faq_category_table(request)
        return render(request, self.template_name, context)
    
    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, *args, **kwargs):
        context = dict()
        try:
            context['page_kwargs'] = seo.get_page_tags("FAQCategoryList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            table_data = bt.build_faq_category_table(request)
            context['table_data'] = table_data
            result, msg, data = api.faq_category_load_data(request, table_data)
            return HttpResponse(json.dumps(data))
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return HttpResponse(json.dumps(context))


@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class FAQCategoryCreateView(TemplateView):

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = dict()
        try:
            template_name = "common_cu.html"
            context['name'] = "FAQCategory"
            context['page_kwargs'] = seo.get_page_tags("FAQCategoryList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            form = forms.FAQCategoryCreateUpdateForm()
            context['form'] = form
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)

    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, id=None, mode=None, *args, **kwargs):
        context = dict()
        try:
            template_name = "common_cu.html"
            context['name'] = "FAQCategory"
            context['page_kwargs'] = seo.get_page_tags("FAQCategoryList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            form = forms.FAQCategoryCreateUpdateForm(request.POST, request.FILES)
            logger.debug(request.POST)
            if form.is_valid():
                result, msg, data = api.faq_category_create_update(request)
                logger.debug(data)
                return HttpResponseRedirect(reverse("svm_admin_console:mck_faq_category_list"))
            else:
                context['form'] = form
                logger.warning(form.errors)
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)


@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class FAQCategoryUpdateView(TemplateView):

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, id=None, *args, **kwargs):
        context = dict()
        try:
            mode = "edit"
            template_name = "common_cu.html"
            context['name'] = "FAQCategory"
            context['page_kwargs'] = seo.get_page_tags("FAQCategoryList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            context['mode'] = mode
            result, msg, data = api.faq_category_retrieve_data(request, id)
            form = forms.FAQCategoryCreateUpdateForm(instance=data.get("faq_category"), mode=mode)
            context['form'] = form
            context['data'] = data
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)

    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, id=None, mode=None, *args, **kwargs):
        context = dict()
        try:
            mode = "edit"
            template_name = "common_cu.html"
            context['name'] = "FAQCategory"
            context['page_kwargs'] = seo.get_page_tags("FAQCategoryList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            result, msg, data = api.faq_category_retrieve_data(request, id)
            form = forms.FAQCategoryCreateUpdateForm(request.POST, request.FILES, mode=mode)
            if form.is_valid():
                result, msg, data = api.faq_category_create_update(request, id, mode)
                return HttpResponseRedirect(reverse("svm_admin_console:mck_faq_category_list"))
            else:
                logger.warning(form.errors)
                context['form'] = form
                context['mode'] = mode
                context['data'] = data
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)


@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class FAQCategoryDeleteView(TemplateView):

    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, id=None, *args, **kwargs):
        context = dict()
        try:
            template_name = "faq_category.html"
            context['page_kwargs'] = seo.get_page_tags("FAQCategoryList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            result, msg = api.faq_category_update_status(request, id)
            return JsonResponse(dict(result=result))
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)

#faq


@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class GalleryList(TemplateView):
    template_name = "table_data_list.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs']= seo.get_page_tags("GalleryList")
        has_permission, accountuser = rv.validate_requested_user_function(request)
        if not has_permission: return render(request, "access_denied.html", context)
        context['table_data'] = bt.build_gallery_table(request)
        return render(request, self.template_name, context)
    
    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, *args, **kwargs):
        context = dict()
        try:
            context['page_kwargs'] = seo.get_page_tags("GalleryList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            table_data = bt.build_gallery_table(request)
            context['table_data'] = table_data
            result, msg, data = api.gallery_load_data(request, table_data)
            return HttpResponse(json.dumps(data))
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return HttpResponse(json.dumps(context))


@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class GalleryCreateView(TemplateView):

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = dict()
        try:
            template_name = "common_cu.html"
            context['name'] = "Gallery"
            context['page_kwargs'] = seo.get_page_tags("GalleryList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            form = forms.GalleryCreateUpdateForm()
            context['form'] = form
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)

    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, id=None, mode=None, *args, **kwargs):
        context = dict()
        try:
            template_name = "common_cu.html"
            context['name'] = "Gallery"
            context['page_kwargs'] = seo.get_page_tags("GalleryList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            form = forms.GalleryCreateUpdateForm(request.POST, request.FILES)
            logger.debug(request.POST)
            if form.is_valid():
                result, msg, data = api.gallery_create_update(request)
                logger.debug(data)
                return HttpResponseRedirect(reverse("svm_admin_console:mck_gallery_list"))
            else:
                context['form'] = form
                logger.warning(form.errors)
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)


@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class GalleryUpdateView(TemplateView):

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, id=None, *args, **kwargs):
        context = dict()
        try:
            mode = "edit"
            template_name = "common_cu.html"
            context['name'] = "Gallery"
            context['page_kwargs'] = seo.get_page_tags("GalleryList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            context['mode'] = mode
            result, msg, data = api.gallery_retrieve_data(request, id)
            form = forms.GalleryCreateUpdateForm(instance=data.get("gallery"), mode=mode)
            context['form'] = form
            context['data'] = data
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)

    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, id=None, mode=None, *args, **kwargs):
        context = dict()
        try:
            mode = "edit"
            template_name = "common_cu.html"
            context['name'] = "Gallery"
            context['page_kwargs'] = seo.get_page_tags("GalleryList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            result, msg, data = api.gallery_retrieve_data(request, id)
            form = forms.GalleryCreateUpdateForm(request.POST, request.FILES, mode=mode)
            if form.is_valid():
                result, msg, data = api.gallery_create_update(request, id, mode)
                return HttpResponseRedirect(reverse("svm_admin_console:mck_gallery_list"))
            else:
                logger.warning(form.errors)
                context['form'] = form
                context['mode'] = mode
                context['data'] = data
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)


@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class GalleryDeleteView(TemplateView):

    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, id=None, *args, **kwargs):
        context = dict()
        try:
            template_name = "gallery.html"
            context['page_kwargs'] = seo.get_page_tags("GalleryList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            result, msg = api.gallery_update_status(request, id)
            return JsonResponse(dict(result=result))
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)


@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class ContactListView(TemplateView):
    template_name = "table_data_list.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("ContactList")
        has_permission, accountuser = rv.validate_requested_user_function(request)
        if not has_permission: return render(request, "access_denied.html", context)
        context['table_data'] = bt.build_contact_table(request)
        return render(request, self.template_name, context)
    
    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, *args, **kwargs):
        context = dict()
        try:
            context['page_kwargs'] = seo.get_page_tags("ConatctList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            table_data = bt.build_contact_table(request)
            context['table_data'] = table_data
            result, msg, data = api.contact_load_data(request, table_data)
            return HttpResponse(json.dumps(data))
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return HttpResponse(json.dumps(context))

@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class ContactCreateView(TemplateView):

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = dict()
        try:
            template_name = "common_cu.html"
            context['name'] = "Contact"
            context['page_kwargs'] = seo.get_page_tags("ConatctList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            form = forms.ConatctCreateUpdateForm()
            context['form'] = form
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)

    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, *args, **kwargs):
        context = dict()
        try:
            template_name = "common_cu.html"
            context['name'] = "Contact"
            context['page_kwargs'] = seo.get_page_tags("ContactList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            form = forms.ConatctCreateUpdateForm(request.POST, request.FILES)
            if form.is_valid():
                result, msg, data = api.contact_create_update(request)
                return HttpResponseRedirect(reverse("svm_admin_console:mck_contact_list"))
            else:
                context['form'] = form
                logger.warning(form.errors)
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)

@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class ContactUpdateView(TemplateView):

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, id=None, *args, **kwargs):
        context = dict()
        try:
            mode = "edit"
            template_name = "common_cu.html"
            context['name'] = "Contact"
            context['page_kwargs'] = seo.get_page_tags("ConatctList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            context['mode'] = mode
            result, msg, data = api.contact_retrieve_data(request, id)
            form = forms.ContactCreateUpdateForm(instance=data.get("contact"), mode=mode)
            context['form'] = form
            context['data'] = data
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)

    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, id=None, mode=None, *args, **kwargs):
        context = dict()
        try:
            mode = "edit"
            template_name = "common_cu.html"
            context['name'] = "Contact"
            context['page_kwargs'] = seo.get_page_tags("ContactList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            result, msg, data = api.contact_retrieve_data(request, id)
            form = forms.ContactCreateUpdateForm(request.POST, request.FILES, mode=mode)
            if form.is_valid():
                result, msg, data = api.contact_create_update(request, id, mode)
                return HttpResponseRedirect(reverse("svm_admin_console:mck_contact_list"))
            else:
                logger.warning(form.errors)
                context['form'] = form
                context['mode'] = mode
                context['data'] = data
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)

@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class ContactDeleteView(TemplateView):

    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, id=None, *args, **kwargs):
        context = dict()
        try:
            context['page_kwargs'] = seo.get_page_tags("ConatctList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            result, msg = api.contact_update_status(request, id)
            return JsonResponse(dict(result=result))
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return JsonResponse(dict(result=False))


#testimonial


@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class TestimonialListView(TemplateView):
    template_name = "table_data_list.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("TestimonialList")
        has_permission, accountuser = rv.validate_requested_user_function(request)
        if not has_permission: return render(request, "access_denied.html", context)
        context['table_data'] = bt.build_testimonial_table(request)
        return render(request, self.template_name, context)
    
    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, *args, **kwargs):
        context = dict()
        try:
            context['page_kwargs'] = seo.get_page_tags("TestimonialList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            table_data = bt.build_testimonial_table(request)
            context['table_data'] = table_data
            result, msg, data = api.testimonial_load_data(request, table_data)
            return HttpResponse(json.dumps(data))
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return HttpResponse(json.dumps(context))

@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class TestimonialCreateView(TemplateView):

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = dict()
        try:
            template_name = "common_cu.html"
            context['name'] = "Testimonial"
            context['page_kwargs'] = seo.get_page_tags("TestimonialList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            form = forms.TestimonialCreateUpdateForm()
            context['form'] = form
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)

    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, id=None, mode=None, *args, **kwargs):
        context = dict()
        try:
            template_name = "common_cu.html"
            context['name'] = "Testimonial"
            context['page_kwargs'] = seo.get_page_tags("TestimonialList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            form = forms.TestimonialCreateUpdateForm(request.POST, request.FILES)
            if form.is_valid():
                result, msg, data = api.testimonial_create_update(request)
                return HttpResponseRedirect(reverse("svm_admin_console:mck_testimonial_list"))
            else:
                context['form'] = form
                logger.warning(form.errors)
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)

@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class TestimonialUpdateView(TemplateView):

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, id=None, *args, **kwargs):
        context = dict()
        try:
            mode = "edit"
            template_name = "common_cu.html"
            context['name'] = "Testimonial"
            context['page_kwargs'] = seo.get_page_tags("TestimonialList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            context['mode'] = mode
            result, msg, data = api.testimonial_retrieve_data(request, id)
            form = forms.TestimonialCreateUpdateForm(instance=data.get("testimonial"), mode=mode)
            context['form'] = form
            context['data'] = data
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)

    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, id=None, mode=None, *args, **kwargs):
        context = dict()
        try:
            mode = "edit"
            template_name = "common_cu.html"
            context['name'] = "Testimonial"
            context['page_kwargs'] = seo.get_page_tags("TestimonialList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            result, msg, data = api.testimonial_retrieve_data(request, id)
            form = forms.TestimonialCreateUpdateForm(request.POST, request.FILES, mode=mode)
            if form.is_valid():
                result, msg, data = api.testimonial_create_update(request, id, mode)
                return HttpResponseRedirect(reverse("svm_admin_console:mck_testimonial_list"))
            else:
                context['form'] = form
                context['mode'] = mode
                context['data'] = data
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)

@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class TestimonialDeleteView(TemplateView):

    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, id=None, *args, **kwargs):
        context = dict()
        try:
            template_name = "testimonial.html"
            context['page_kwargs'] = seo.get_page_tags("TestimonialList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            result, msg = api.testimonial_update_status(request, id)
            return JsonResponse(dict(result=result))
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)
