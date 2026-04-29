"""
Views - mck Auth App
"""

import json
import sys
import logging
import traceback

from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.views.generic.base import RedirectView
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import logout as auth_logout, authenticate, login
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from config import settings
from config import app_logger

from config import app_seo as seo
from mck_auth import api
from mck_auth import forms
from mck_auth import build_table as bt
from mck_auth import role_validations as rv
from mck_auth.models import EmailOTP
from mck_auth.utils.email_utils import send_otp_email

# Get the User model
User = get_user_model()

LOG_NAME = "app"
logger = app_logger.createLogger(LOG_NAME)


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
                return HttpResponseRedirect(reverse("mck_admin_console:mck_dashboard"))
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


class DashboardView(TemplateView):
    template_name = "dashboard.html"

    # Use hardcoded URL instead of settings
    @method_decorator(login_required(login_url='/auth/login/'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

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
        try:
            from mck_company.models import Profile  # Import here to avoid circular imports
            profiles = Profile.objects.exclude(datamode='D').order_by('-updated_on')
            context["profile"] = profiles
            context["total_profiles"] = profiles.count()
        except ImportError:
            logger.warning("Profile model not found")
            context["profile"] = []
            context["total_profiles"] = 0

        return render(request, self.template_name, context)


class SignIn(TemplateView):
    """
    Admin Login Page
    """
    template_name = "signin.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("signin")
        
        if request.user.is_authenticated:
            # Redirect based on user type
            if request.user.is_staff or request.user.is_superuser:
                gDict = request.GET
                if 'next' in gDict:
                    logger.info(request.user.is_authenticated)
                    return HttpResponseRedirect(gDict.get("next"))
                return HttpResponseRedirect(reverse("mck_admin_console:mck_dashboard"))
            else:
                # Regular user trying to access admin login - redirect to website
                return HttpResponseRedirect(reverse("mck_website:home_page"))
                
        return render(request, self.template_name, context)

    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, *args, **kwargs):
        result, message, data = api.user_login(request, for_admin=True)
        logger.info(f"{result} {message} {data}")
        
        if result:
            # After successful login, check user type
            if request.user.is_staff or request.user.is_superuser:
                gDict = request.GET
                if 'next' in gDict:
                    logger.info(request.user.is_authenticated)
                    return HttpResponseRedirect(gDict.get("next"))
                return HttpResponseRedirect(reverse("mck_admin_console:mck_dashboard"))
            else:
                # If non-admin somehow logged in through admin login, logout and redirect
                auth_logout(request)
                messages.error(request, "Invalid admin credentials.")
                return HttpResponseRedirect(reverse("mck_admin_console:mck_signin"))
        
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("signin")
        context['message'] = message
        context['data'] = data
        return render(request, self.template_name, context)


class WebsiteSignIn(TemplateView):
    """
    Website User Login Page
    """
    template_name = "auth/website_signin.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("website_signin")
        
        if request.user.is_authenticated:
            # Redirect based on user type
            if request.user.is_staff or request.user.is_superuser:
                # Admin user trying to access website login - redirect to admin dashboard
                return HttpResponseRedirect(reverse("mck_admin_console:mck_dashboard"))
            else:
                # Regular user - redirect to website home
                return HttpResponseRedirect(reverse("mck_website:home_page"))
                
        return render(request, self.template_name, context)

    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, *args, **kwargs):
        result, message, data = api.user_login(request, for_admin=False)
        logger.info(f"{result} {message} {data}")
        
        if result:
            # After successful login, redirect based on user type
            if request.user.is_staff or request.user.is_superuser:
                # Admin user logging in through website - redirect to admin dashboard
                return HttpResponseRedirect(reverse("mck_admin_console:mck_dashboard"))
            else:
                # Regular user - redirect to website home
                return HttpResponseRedirect(reverse("mck_website:home_page"))
                
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("website_signin")
        context['message'] = message
        context['data'] = data
        return render(request, self.template_name, context)


class WebsiteSignUp(TemplateView):
    """
    Website User Registration Page
    """
    template_name = "auth/website_signup.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_staff or request.user.is_superuser:
                return HttpResponseRedirect(reverse("mck_admin_console:mck_dashboard"))
            else:
                return HttpResponseRedirect(reverse("mck_website:home_page"))
        
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("website_signup")
        return render(request, self.template_name, context)

    @csrf_exempt
    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, *args, **kwargs):
        # Get form data
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        # Log received data (without password)
        logger.info(f"Registration attempt for email: {email}")
        
        # Basic validation
        if not email or not password:
            context = super().get_context_data(**kwargs)
            context['page_kwargs'] = seo.get_page_tags("website_signup")
            context['message'] = "Email and password are required"
            context['form_data'] = request.POST
            return render(request, self.template_name, context)
        
        # Validate email doesn't already exist
        if User.objects.filter(email=email).exists():
            context = super().get_context_data(**kwargs)
            context['page_kwargs'] = seo.get_page_tags("website_signup")
            context['message'] = "Email already registered. Please use a different email or login."
            context['form_data'] = request.POST
            return render(request, self.template_name, context)
        
        # Store registration data in session
        request.session['registration_data'] = {
            'email': email,
            'password': password,
            'first_name': first_name,
            'last_name': last_name,
        }
        
        # Generate and send OTP
        try:
            # Delete any existing OTPs for this email
            EmailOTP.objects.filter(email=email, is_verified=False).delete()
            logger.info(f"Deleted existing OTPs for {email}")
            
            # Create new OTP
            otp = EmailOTP.objects.create(email=email)
            logger.info(f"Created new OTP for {email}: {otp.otp}")
            
            # Send OTP email
            logger.info(f"Attempting to send OTP email to {email}")
            email_sent = send_otp_email(email, otp.otp, first_name)
            
            if email_sent:
                logger.info(f"OTP email sent successfully to {email}")
                messages.success(request, f"Verification code sent to {email}")
                return redirect('mck_auth:verify_otp')
            else:
                logger.error(f"Failed to send OTP email to {email}")
                # Clean up session if email fails
                del request.session['registration_data']
                context = super().get_context_data(**kwargs)
                context['page_kwargs'] = seo.get_page_tags("website_signup")
                context['message'] = "Failed to send verification email. Please try again."
                context['form_data'] = request.POST
                return render(request, self.template_name, context)
                
        except ImportError as e:
            logger.error(f"ImportError in OTP generation: {str(e)}")
            logger.error(traceback.format_exc())
            # Clean up session on error
            if 'registration_data' in request.session:
                del request.session['registration_data']
            context = super().get_context_data(**kwargs)
            context['page_kwargs'] = seo.get_page_tags("website_signup")
            context['message'] = "A configuration error occurred. Please contact support."
            context['form_data'] = request.POST
            return render(request, self.template_name, context)
            
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            line_number = exc_traceback.tb_lineno if exc_traceback else 'unknown'
            logger.error(f"OTP generation error at line {line_number}: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error details: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Clean up session on error
            if 'registration_data' in request.session:
                del request.session['registration_data']
                
            context = super().get_context_data(**kwargs)
            context['page_kwargs'] = seo.get_page_tags("website_signup")
            context['message'] = "An error occurred. Please try again."
            context['form_data'] = request.POST
            return render(request, self.template_name, context)


class OTPVerificationView(TemplateView):
    """
    OTP Verification Page
    """
    template_name = "auth/otp_verification.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        # Check if we have registration data in session
        if 'registration_data' not in request.session:
            messages.error(request, "Registration session expired. Please register again.")
            return redirect('mck_auth:website_signup')
        
        context = super().get_context_data(**kwargs)
        context['email'] = request.session['registration_data']['email']
        return render(request, self.template_name, context)

    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, *args, **kwargs):
        # Check session
        if 'registration_data' not in request.session:
            messages.error(request, "Registration session expired. Please register again.")
            return redirect('mck_auth:website_signup')
        
        email = request.POST.get('email')
        otp_code = request.POST.get('otp')
        registration_data = request.session['registration_data']
        
        # Verify email matches session
        if email != registration_data['email']:
            messages.error(request, "Email mismatch. Please try again.")
            return redirect('mck_auth:verify_otp')
        
        # Get the latest OTP for this email
        try:
            latest_otp = EmailOTP.objects.filter(email=email).latest('created_at')
            
            # Check if OTP is valid
            if latest_otp.otp == otp_code and latest_otp.is_valid():
                # Mark OTP as verified
                latest_otp.is_verified = True
                latest_otp.save()
                
                # Create the user using the API function with registration_data
                result, message, data = api.website_user_register(request, registration_data)
                
                if result:
                    # Clear session
                    del request.session['registration_data']
                    
                    # Auto-login
                    user = authenticate(
                        request, 
                        username=email, 
                        password=registration_data['password']
                    )
                    
                    if user:
                        login(request, user)
                        messages.success(request, "Registration successful! Welcome to Real Estate Platform.")
                        
                        # Check user type for redirect
                        if user.is_staff or user.is_superuser:
                            return redirect('mck_admin_console:mck_dashboard')
                        else:
                            return redirect('mck_website:profile_page')
                    else:
                        # If auto-login fails, redirect to login page
                        messages.success(request, "Registration successful! Please login to continue.")
                        return redirect('mck_auth:website_signin')
                
                # If registration fails
                messages.error(request, message or "Registration failed. Please try again.")
                return redirect('mck_auth:website_signup')
            
            else:
                messages.error(request, "Invalid or expired OTP. Please try again.")
                return redirect('mck_auth:verify_otp')
                
        except EmailOTP.DoesNotExist:
            messages.error(request, "No OTP found for this email. Please request a new one.")
            return redirect('mck_auth:verify_otp')
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error(f"OTP verification error at line {exc_traceback.tb_lineno}: {str(e)}")
            messages.error(request, "An error occurred during verification. Please try again.")
            return redirect('mck_auth:verify_otp')


class ResendOTPView(View):
    """
    Resend OTP View
    """
    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, *args, **kwargs):
        if 'registration_data' not in request.session:
            messages.error(request, "Registration session expired. Please register again.")
            return redirect('mck_auth:website_signup')
        
        email = request.POST.get('email')
        registration_data = request.session['registration_data']
        
        # Verify email matches session
        if email != registration_data['email']:
            messages.error(request, "Email mismatch. Please try again.")
            return redirect('mck_auth:verify_otp')
        
        try:
            # Delete old unverified OTPs
            EmailOTP.objects.filter(email=email, is_verified=False).delete()
            
            # Create new OTP
            otp = EmailOTP.objects.create(email=email)
            
            # Send OTP email
            email_sent = send_otp_email(email, otp.otp, registration_data.get('first_name'))
            
            if email_sent:
                messages.success(request, f"New verification code sent to {email}")
            else:
                messages.error(request, "Failed to send verification email. Please try again.")
                
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error(f"Resend OTP error at line {exc_traceback.tb_lineno}: {str(e)}")
            messages.error(request, "An error occurred. Please try again.")
        
        return redirect('mck_auth:verify_otp')


class LogOut(RedirectView):
    """
    Admin LogOut Page
    """
    @app_logger.functionlogs(log=LOG_NAME)
    def get_redirect_url(self, **kwargs):
        auth_logout(self.request)
        return reverse("mck_admin_console:mck_landing_page")


class WebsiteLogOut(RedirectView):
    """
    Website User LogOut Page
    """
    @app_logger.functionlogs(log=LOG_NAME)
    def get_redirect_url(self, **kwargs):
        auth_logout(self.request)
        return reverse("mck_website:home_page")

# mck_auth/views.py
class WebsitePasswordReset(TemplateView):
    """
    Website User Password Reset
    """
    template_name = "website_password_reset.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("website_password_reset")
        return render(request, self.template_name, context)

    @csrf_exempt
    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, *args, **kwargs):
        # Implement password reset logic here
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("website_password_reset")
        context['message'] = "Password reset instructions sent to your email."
        return render(request, self.template_name, context)


@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class AccountTypeRoleList(TemplateView):
    template_name = "table_data_list.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs']= seo.get_page_tags("AccountTypeRoleList")
        has_permission, accountuser = rv.validate_requested_user_function(request)
        if not has_permission: return render(request, "access_denied.html", context)
        context['table_data'] = bt.build_role_table(request)
        return render(request, self.template_name, context)
    
    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, *args, **kwargs):
        context = dict()
        try:
            context['page_kwargs'] = seo.get_page_tags("AccountTypeRoleList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            table_data = bt.build_role_table(request)
            context['table_data'] = table_data
            result, msg, data = api.role_load_data(request, table_data)
            return HttpResponse(json.dumps(data))
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return HttpResponse(json.dumps(context))


@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class AccountTypeRoleCreateView(TemplateView):

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = dict()
        try:
            template_name = "role_cu.html"
            context['page_kwargs'] = seo.get_page_tags("AccountTypeRoleList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            form = forms.AccountTypeRoleCreateUpdateForm()
            context['form'] = form
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)

    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, id=None, mode=None, *args, **kwargs):
        context = dict()
        try:
            template_name = "role_cu.html"
            context['page_kwargs'] = seo.get_page_tags("AccountTypeRoleList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            form = forms.AccountTypeRoleCreateUpdateForm(request.POST)
            logger.debug(request.POST)
            if form.is_valid():
                result, msg, data = api.role_create_update(request)
                logger.debug(data)
                return HttpResponseRedirect(reverse("mck_auth:mck_role_list"))
            else:
                context['form'] = form
                logger.warning(form.errors)
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)


@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class AccountTypeRoleUpdateView(TemplateView):

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, id=None, *args, **kwargs):
        context = dict()
        try:
            mode = "edit"
            template_name = "role_cu.html"
            context['page_kwargs'] = seo.get_page_tags("AccountTypeRoleList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            context['mode'] = mode
            result, msg, data = api.role_retrieve_data(request, id)
            form = forms.AccountTypeRoleCreateUpdateForm(instance=data.get("role"), mode=mode)
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
            template_name = "role_cu.html"
            context['page_kwargs'] = seo.get_page_tags("AccountTypeRoleList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            result, msg, data = api.role_retrieve_data(request, id)
            form = forms.AccountTypeRoleCreateUpdateForm(request.POST, mode=mode)
            if form.is_valid():
                result, msg, data = api.role_create_update(request, id, mode)
                return HttpResponseRedirect(reverse("mck_auth:mck_role_list"))
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
class AccountTypeRoleDeleteView(TemplateView):

    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, id=None, *args, **kwargs):
        context = dict()
        try:
            template_name = "role_cu.html"
            context['page_kwargs'] = seo.get_page_tags("AccountTypeRoleList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            result, msg = api.role_update_status(request, id)
            return JsonResponse(dict(result=result))
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)


@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class AccountTypeRoleUpdatePermissionView(TemplateView):

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, id, *args, **kwargs):
        context = dict()
        try:
            template_name = "role_update_permission.html"
            context['page_kwargs'] = seo.get_page_tags("AccountTypeRoleList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            result, msg, data = api.role_premission_retrieve_data(request, id)
            context['data'] = data
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)

    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, id, *args, **kwargs):
        context = dict()
        try:
            template_name = "role_update_permission.html"
            context['page_kwargs'] = seo.get_page_tags("AccountTypeRoleList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            result, msg, data = api.role_update_permission(request, id)
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return HttpResponseRedirect(reverse("mck_auth:mck_role_update_permission", args=[id]))


