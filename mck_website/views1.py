"""
Views - VLR Website App
"""

from django.http import HttpResponse
import os
from django.conf import settings
from django.shortcuts import render
from django.views.generic import TemplateView
from django.shortcuts import render, get_object_or_404
from config import app_logger
from config import app_seo as seo

from mck_website.api import *
from mck_website.models import *
from django.urls import reverse 
from django.db.models import Prefetch
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from mck_auth import build_table as bt
from mck_auth import role_validations as rv

from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic import TemplateView
from django.shortcuts import render
from django.core.paginator import Paginator
from datetime import date
from dateutil.relativedelta import relativedelta
from mck_master.models import Profile,Notification,Wishlist
from mck_admin_console.models import Gallery

import razorpay
import json
import logging
import uuid
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views import View
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.urls import reverse  # This is the missing import
from django.db import IntegrityError
from django.db.models import Prefetch

LOG_NAME = "app"
logger = app_logger.createLogger(LOG_NAME)


def pki_validation_view(request):
    file_path = os.path.join(settings.BASE_DIR, "mck_website", "templates", "verify.txt")
    try:
        with open(file_path, "r") as file:
            content = file.read()
        return HttpResponse(content, content_type="text/plain")
    except FileNotFoundError:
        return HttpResponse("File not found", status=404)


def payment_required(view_func):
    """Decorator to require payment for accessing a view."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('mck_auth:website_signin')
        
        has_paid = getattr(request.user, 'has_paid', False)
        if not has_paid:
            has_paid = request.user.payments.filter(status='COMPLETED').exists()
        
        if not has_paid:
            messages.warning(request, "Please complete your payment to view this page.")
            return redirect('mck_website:payment_gateway')
        
        return view_func(request, *args, **kwargs)
    return wrapper

from django.views.generic import TemplateView
from django.shortcuts import render
from django.db.models import Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin
import logging
# from .models import Property, Profile, PropertyType, PropertyImage, Gallery, Lead

# Setup logger
logger = logging.getLogger(__name__)

class HomePage(TemplateView):
    """
    Home Page - Landing page for the Real Estate Platform
    Accessible to all users (authenticated and non-authenticated)
    """
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        """
        Get context data for the template
        """
        context = super().get_context_data(**kwargs)
        
        # Add SEO tags
        context['page_kwargs'] = seo.get_page_tags("home_page")
        
        # Get all active properties with their images prefetched
        context["properties"] = Property.objects.exclude(datamode='D')\
            .prefetch_related(
                Prefetch('images', 
                        queryset=PropertyImage.objects.exclude(datamode='D'),
                        to_attr='property_images')
            )\
            .order_by('-updated_on')[:12]  # Limit to 12 latest properties
        
        # Get all active profiles
        context["profiles"] = Profile.objects.exclude(datamode='D')\
            .order_by('-updated_on')[:8]  # Limit to 8 latest profiles
        
        # Get property types
       
        
        # Get gallery images
        context['gallery_list'] = Gallery.objects.filter(datamode="A")\
            .order_by('-updated_on')[:12]  # Limit to 12 latest gallery items
        
        # Get distinct cities for search/filter
        context["cities"] = Property.objects.exclude(datamode='D')\
            .values_list('city', flat=True)\
            .distinct()\
            .order_by('city')
        
        # Get featured/trending properties (you can add logic here)
    
        
        # Get recent leads (if user is staff/admin, you might want to hide this)
        if self.request.user.is_staff:
            context["recent_leads"] = Lead.objects.exclude(datamode='D')\
                .order_by('-updated_on')[:10]
        
        # Add user payment status if authenticated
        if self.request.user.is_authenticated:
            try:
                # Check if user has paid
                from .models import Payment
                has_paid = Payment.objects.filter(
                    user=self.request.user,
                    status='COMPLETED'
                ).exists()
                context['user_has_paid'] = has_paid
                
                # Get user's wishlist if any
                context['user_wishlist'] = self.request.user.wishlist_set.all()[:5]
            except:
                context['user_has_paid'] = False
        
        return context

    def get(self, request, *args, **kwargs):
        """
        Handle GET request
        """
        try:
            # Log the request
            logger.info(f"Home page accessed - User: {request.user.email if request.user.is_authenticated else 'Anonymous'}")
            logger.info(f"GET parameters: {request.GET}")
            
            # Get context data
            context = self.get_context_data(**kwargs)
            
            # Render template
            return render(request, self.template_name, context)
            
        except Exception as e:
            # Log the error
            logger.error(f"Error loading home page: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Return a basic context even if there's an error
            context = {
                'page_kwargs': seo.get_page_tags("home_page"),
                'error_message': "Some content couldn't be loaded. Please refresh the page."
            }
            return render(request, self.template_name, context)


# Optional: Add a dedicated dashboard view for logged-in users
class DashboardView(LoginRequiredMixin, TemplateView):
    """
    User Dashboard - Only accessible to authenticated users who have paid
    """
    template_name = "dashboard.html"
    login_url = '/auth/website/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Check if user has paid
        try:
            from .models import Payment
            payment = Payment.objects.filter(
                user=user,
                status='COMPLETED'
            ).first()
            context['has_paid'] = payment is not None
            context['payment'] = payment
        except:
            context['has_paid'] = False
        
        # Get user's profile
        try:
            context['profile'] = user.profiles.first()
        except:
            context['profile'] = None
        
        # Get user's properties (if any)
        context['user_properties'] = Property.objects.filter(
            created_by=user,
            datamode='A'
        ).order_by('-updated_on')[:5]
        
        # Get user's wishlist
        context['wishlist'] = user.wishlist_set.all()[:10]
        
        # Get user's recent activity
        context['recent_activity'] = []  # Add logic for recent activity
        
        return context
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user has completed profile
        if not hasattr(request.user, 'is_profile_completed') or not request.user.is_profile_completed:
            messages.warning(request, "Please complete your profile first.")
            return redirect('mck_website:profile_completion')
        
        # Check if user has paid (optional - if you want to restrict dashboard access)
        # Uncomment if you want to restrict dashboard to paid users only
        # if not request.user.has_paid:
        #     messages.warning(request, "Please complete your payment to access dashboard.")
        #     return redirect('mck_website:payment_gateway')
        
        return super().dispatch(request, *args, **kwargs)

class PropertyPage(TemplateView):
    template_name = "property_page.html"

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all properties excluding deleted ones
        qs = Property.objects.exclude(datamode='D')
        
        # Apply filters
        city = request.GET.get('city')
        listing_type = request.GET.get("listing_type")
        property_type = request.GET.get('property_type')
        budget = request.GET.get('budget')
        sort = request.GET.get('sort', 'newest')

        if city:
            qs = qs.filter(city__icontains=city)

        if property_type:
            qs = qs.filter(property_type__name__iexact=property_type)

        if listing_type:
            qs = qs.filter(listing_type__iexact=listing_type)

        if budget:
            if budget == "Below 100k":
                qs = qs.filter(price__lt=100000)
            elif budget == "100k - 300k":
                qs = qs.filter(price__range=(100000, 300000))
            elif budget == "Above 300k":
                qs = qs.filter(price__gt=300000)

        # Apply sorting
        if sort == 'price_low':
            qs = qs.order_by('price')
        elif sort == 'price_high':
            qs = qs.order_by('-price')
        else:  # newest
            qs = qs.order_by('-updated_on')

       

        # Pagination
        paginator = Paginator(qs, 9)  # Show 9 properties per page
        page_number = request.GET.get('page')
        properties = paginator.get_page(page_number)
        
        # Prefetch related images
        properties.object_list = properties.object_list.prefetch_related(
            Prefetch(
                'images',  
                queryset=PropertyImage.objects.exclude(datamode='D').order_by('-updated_on'),
                to_attr='property_images_list'  
            )
        )

        context["properties"] = properties
        context["property_types"] = PropertyType.objects.exclude(datamode='D').order_by('-updated_on')
        context["cities"] = (
            Property.objects.exclude(datamode='D')
            .values_list('city', flat=True)
            .distinct()
            .order_by('city')
        )

        return render(request, self.template_name, context)


class PropertyDetailPage(TemplateView):
    template_name = "resources.html"

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        property_id = kwargs.get('pk')  # from URL
        property_obj = get_object_or_404(
            Property.objects.prefetch_related(
                Prefetch(
                    'images',
                    queryset=PropertyImage.objects.exclude(datamode='D').order_by('-updated_on')
                )
            ),
            pk=property_id
        )

        context["property"] = property_obj
        return render(request, self.template_name, context)

class PropertyCreatePage(TemplateView):
    template_name = "pages/property_create.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_kwargs"] = seo.get_page_tags("property_create")
        property = Property.objects.exclude(datamode='D').order_by('-updated_on')
        context["property"] = property
        logger.info(request.GET)
        return render(request, self.template_name, context)
    
    
class MaintenancesCreatePage(TemplateView):
    template_name = "pages/faq.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_kwargs"] = seo.get_page_tags("maintenance")
        maintenance = MaintenanceRequest.objects.exclude(datamode='D').order_by('-updated_on')
        context["maintenance"] = maintenance
        logger.info(request.GET)
        return render(request, self.template_name, context)
    

class PropertySaveView(TemplateView):
    def post(self, request, *args, **kwargs):
        try:
            logger.info("Received property save request")
            logger.info("POST data: %s", request.POST)
            logger.info("FILES data: %s", request.FILES)
            
            result, message = api.ajax_property_save(request)
            if result:
                logger.info("Property saved successfully")
                return JsonResponse({"status": "success", "message": message})
            else:
                logger.error("Failed to save property: %s", message)
                return JsonResponse({"status": "fail", "message": message}, status=400)
                
        except Exception as e:
            logger.exception("Unexpected error in PropertySaveView")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
        

class MaintenanceSaveView(TemplateView):
    def post(self, request, *args, **kwargs):
        try:
            logger.info("Received Maintenance save request")
            logger.info("POST data: %s", request.POST)
            logger.info("FILES data: %s", request.FILES)
            
            result, message = api.ajax_maintenance_save(request)
            if result:
                logger.info("maintenance saved successfully")
                return JsonResponse({"status": "success", "message": message})
            else:
                logger.error("Failed to save maintenance: %s", message)
                return JsonResponse({"status": "fail", "message": message}, status=400)
                
        except Exception as e:
            logger.exception("Unexpected error in maintenanceSaveView")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
        
        


class EnquirySaveView(TemplateView):
    def post(self, request, *args, **kwargs):
        try:
            logger.info("Received lead save request")
            logger.info("POST data: %s", request.POST)
            logger.info("FILES data: %s", request.FILES)
            
            result, message = api.ajax_enquiry_save(request)
            if result:
                logger.info("lead saved successfully")
                return JsonResponse({"status": "success", "message": message})
            else:
                logger.error("Failed to save lead: %s", message)
                return JsonResponse({"status": "fail", "message": message}, status=400)
                
        except Exception as e:
            logger.exception("Unexpected error in leadSaveView")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

class AboutPage(TemplateView):
    """
    About Page
    """
    template_name = "about.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("about_page")
        logger.info(request.GET)
        return render(request, self.template_name, context)
    
class OurServicesPage(TemplateView):
    """
    ourservices Page
    """
    template_name = "our_services.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("about_page")
        logger.info(request.GET)
        return render(request, self.template_name, context)
    

class PrivacyPolicyPage(TemplateView):
    """
    ourservices Page
    """
    template_name = "privacy_policy.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("privacy_policy_page")
        logger.info(request.GET)
        return render(request, self.template_name, context)

class TermsPage(TemplateView):
    """
    terms Page
    """
    template_name = "terms.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("terms_page")
        logger.info(request.GET)
        return render(request, self.template_name, context)
    
class PropertyLegalServicesPage(TemplateView):
    """
    terms Page
    """
    template_name = "property_legal_services.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("property_legal_services_page")
        logger.info(request.GET)
        return render(request, self.template_name, context)

class SolarPage(TemplateView):
    template_name = "solar.html"
    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("solar")
        logger.info(request.GET)
        return render(request, self.template_name, context)


class FencingPage(TemplateView):
    template_name = "fencing.html"
    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("fencing")
        logger.info(request.GET)
        return render(request, self.template_name, context)
    
class LandLevellingPage(TemplateView):
    template_name = "pages/land_leveling.html"
    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("land_levelling")
        logger.info(request.GET)
        return render(request, self.template_name, context)

class ProfileCreatePage(TemplateView):
    template_name = "includes/enquiry.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_kwargs"] = seo.get_page_tags("profile")
        profile = Profile.objects.exclude(datamode='D').order_by('-updated_on')
        context["profile"] = profile
        # property_type = request.GET.get('property_type', '')
        # context["selected_property_type"] = property_type  
        logger.info(request.GET)
        return render(request, self.template_name, context)




class MyProfilePage(TemplateView):
    template_name = "my_profile.html"
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        context = {}

        # ✅ Get ALL profiles of the user
        profiles = Profile.objects.filter(user=request.user).order_by("-created_on")

        # ✅ If user has no profile, create ONE default
        if not profiles.exists():
            Profile.objects.create(
                user=request.user,
                created_by="USER",
                updated_by="USER",
                gender=""
            )
            profiles = Profile.objects.filter(user=request.user)

        profile_data = []
        for profile in profiles:
            age = None
            if profile.dob:
                today = date.today()
                age = today.year - profile.dob.year - (
                    (today.month, today.day) < (profile.dob.month, profile.dob.day)
                )

            profile_data.append({
                "profile": profile,
                "age": age
            })

        context["profiles"] = profile_data
        context["is_my_profile"] = True

        return render(request, self.template_name, context)

        

import logging
from datetime import datetime
from decimal import Decimal
from django.urls import reverse
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)

class ProfileSaveView(LoginRequiredMixin, TemplateView):
    """API view for saving profile (AJAX)"""
    
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        try:
            data = request.POST
            files = request.FILES
            
            # Debug logging
            logger.info(f"Profile save request from user: {request.user.username}")
            logger.info(f"POST data keys: {list(data.keys())}")
            logger.info(f"FILES keys: {list(files.keys())}")
            
            # Get or create profile for logged-in user
            profile_obj, created = Profile.objects.get_or_create(
                user=request.user,
                defaults={
                    "created_by": request.user.username,
                    "full_name": data.get("full_name", "")
                }
            )
            
            # ============ BASIC DETAILS ============
            profile_obj.full_name = data.get("full_name", profile_obj.full_name)
            profile_obj.gender = data.get("gender", profile_obj.gender)
            
            # Handle date of birth
            dob_str = data.get("dob")
            if dob_str:
                try:
                    profile_obj.dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
                except ValueError:
                    logger.warning(f"Invalid date format for dob: {dob_str}")
                    profile_obj.dob = None
            else:
                profile_obj.dob = None
            
            # Handle birth time
            birth_time_str = data.get("birth_time")
            if birth_time_str:
                try:
                    # Handle time format (HH:MM)
                    profile_obj.birth_time = datetime.strptime(birth_time_str, "%H:%M").time()
                except ValueError:
                    logger.warning(f"Invalid time format for birth_time: {birth_time_str}")
                    profile_obj.birth_time = None
            else:
                profile_obj.birth_time = None
            
            profile_obj.birth_place = data.get("birth_place", profile_obj.birth_place)
            profile_obj.height = data.get("height", profile_obj.height)
            profile_obj.weight = data.get("weight", profile_obj.weight)
            profile_obj.complexion = data.get("complexion", profile_obj.complexion)
            # profile_obj.marital_status = data.get("marital_status", profile_obj.marital_status)
            
            # ============ RELIGION & HOROSCOPE ============
            profile_obj.religion = data.get("religion", profile_obj.religion)
            profile_obj.caste = data.get("caste", profile_obj.caste)
            profile_obj.sub_caste = data.get("sub_caste", profile_obj.sub_caste)
            profile_obj.gothram = data.get("gothram", profile_obj.gothram)
            profile_obj.rasi = data.get("rasi", profile_obj.rasi)
            profile_obj.nakshatra = data.get("nakshatra", profile_obj.nakshatra)
            profile_obj.laknam = data.get("laknam", profile_obj.laknam)
            profile_obj.dosham = data.get("dosham", profile_obj.dosham)
            
            # ============ EDUCATION & CAREER ============
            profile_obj.education = data.get("education", profile_obj.education)
            profile_obj.occupation = data.get("occupation", profile_obj.occupation)
            profile_obj.company_name = data.get("company_name", profile_obj.company_name)
            profile_obj.job_location = data.get("job_location", profile_obj.job_location)
            
            # Handle annual income
            income_str = data.get("annual_income")
            if income_str and income_str.strip():
                try:
                    # Remove any non-numeric characters except decimal point
                    income_clean = ''.join(c for c in income_str if c.isdigit() or c == '.')
                    if income_clean:
                        profile_obj.annual_income = Decimal(income_clean)
                    else:
                        profile_obj.annual_income = None
                except (ValueError, DecimalException) as e:
                    logger.warning(f"Invalid income format: {income_str}, error: {e}")
                    profile_obj.annual_income = None
            else:
                profile_obj.annual_income = None
            
            # ============ FAMILY DETAILS ============
            # Father details toggle
            profile_obj.has_father_details = data.get("has_father_details", "N")
            if profile_obj.has_father_details == "Y":
                profile_obj.father_name = data.get("father_name", profile_obj.father_name)
                profile_obj.father_occupation = data.get("father_occupation", profile_obj.father_occupation)
            else:
                profile_obj.father_name = ""
                profile_obj.father_occupation = ""
            
            # Mother details toggle
            profile_obj.has_mother_details = data.get("has_mother_details", "N")
            if profile_obj.has_mother_details == "Y":
                profile_obj.mother_name = data.get("mother_name", profile_obj.mother_name)
                profile_obj.mother_occupation = data.get("mother_occupation", profile_obj.mother_occupation)
            else:
                profile_obj.mother_name = ""
                profile_obj.mother_occupation = ""
            
            # Siblings toggle
            profile_obj.has_siblings = data.get("has_siblings", "N")
            if profile_obj.has_siblings == "Y":
                # Handle number of brothers
                brothers_str = data.get("no_of_brothers")
                if brothers_str and brothers_str.strip():
                    try:
                        profile_obj.no_of_brothers = int(brothers_str)
                    except ValueError:
                        logger.warning(f"Invalid brothers count: {brothers_str}")
                        profile_obj.no_of_brothers = None
                else:
                    profile_obj.no_of_brothers = None
                
                # Handle number of sisters
                sisters_str = data.get("no_of_sisters")
                if sisters_str and sisters_str.strip():
                    try:
                        profile_obj.no_of_sisters = int(sisters_str)
                    except ValueError:
                        logger.warning(f"Invalid sisters count: {sisters_str}")
                        profile_obj.no_of_sisters = None
                else:
                    profile_obj.no_of_sisters = None
            else:
                profile_obj.no_of_brothers = None
                profile_obj.no_of_sisters = None
            
            # ============ CONTACT INFORMATION ============
            profile_obj.phone = data.get("phone", profile_obj.phone)
            profile_obj.whatsapp_number = data.get("whatsapp_number", profile_obj.whatsapp_number)
            profile_obj.email = data.get("email", profile_obj.email)
            profile_obj.address = data.get("address", profile_obj.address)
            profile_obj.city = data.get("city", profile_obj.city)
            profile_obj.state = data.get("state", profile_obj.state)
            profile_obj.country = data.get("country", profile_obj.country)
            profile_obj.pincode = data.get("pincode", profile_obj.pincode)
            
            # Location field (backward compatibility)
            # profile_obj.location = data.get("location", profile_obj.location)
            
            # ============ ABOUT ============
            profile_obj.bio = data.get("bio", profile_obj.bio)
            profile_obj.hobbies = data.get("hobbies", profile_obj.hobbies)
            
            # ============ PROFILE PHOTOS ============
            # Handle multiple photo uploads
            photo_fields = ['photo1', 'photo2', 'photo3', 'photo4', 'photo5']
            for field in photo_fields:
                if field in files:
                    try:
                        # Delete old photo if exists
                        old_photo = getattr(profile_obj, field)
                        if old_photo and old_photo.name:
                            old_photo.delete(save=False)
                        # Set new photo
                        setattr(profile_obj, field, files[field])
                        logger.info(f"Uploaded {field}: {files[field].name}")
                    except Exception as e:
                        logger.error(f"Error uploading {field}: {str(e)}")
            
            # Handle single profile_photo field (backward compatibility)
            if "profile_photo" in files:
                try:
                    if profile_obj.photo1 and profile_obj.photo1.name:
                        profile_obj.photo1.delete(save=False)
                    profile_obj.photo1 = files["profile_photo"]
                    logger.info(f"Uploaded profile_photo to photo1: {files['profile_photo'].name}")
                except Exception as e:
                    logger.error(f"Error uploading profile_photo: {str(e)}")
            
            # ============ SYSTEM FIELDS ============
            profile_obj.updated_by = data.get("updated_by", request.user.username)
            profile_obj.datamode = data.get("datamode", "A")
            
            # Save the profile
            profile_obj.save()
            
            logger.info(f"Profile {'created' if created else 'updated'} successfully for user: {request.user.username}")
            
            # Return success response with redirect URL
            return JsonResponse({
                "success": True,
                "message": "Profile saved successfully",
                "profile_id": profile_obj.id,
                "created": created,
                "redirect_url": reverse("mck_website:home_page")
            })
            
        except Profile.DoesNotExist:
            logger.error(f"Profile does not exist for user: {request.user.username}")
            return JsonResponse({
                "success": False,
                "message": "Profile not found"
            }, status=404)
            
        except Exception as e:
            logger.exception(f"Error saving profile for user {request.user.username}: {str(e)}")
            return JsonResponse({
                "success": False,
                "message": f"Error saving profile: {str(e)}",
                "error_type": type(e).__name__
            }, status=400)

class ProfilSaveView(TemplateView):
    def post(self, request, *args, **kwargs):
        try:
            logger.info("Received profile save request")
            logger.info("POST data: %s", request.POST)
            logger.info("FILES data: %s", request.FILES)
            
            result, message = api.ajax_profile_save(request)
            if result:
                logger.info("profile saved successfully")
                return JsonResponse({"status": "success", "message": message})
            else:
                logger.error("Failed to save profile: %s", message)
                return JsonResponse({"status": "fail", "message": message}, status=400)
                
        except Exception as e:
            logger.exception("Unexpected error in profileSaveView")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


from django.db.models import Q
from random import shuffle
import random

@method_decorator(login_required(login_url=settings.LOGIN_WEB_REDIRECT_URL), name='dispatch')
class ProfilePage(TemplateView):
    template_name = "property_page.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request
        
        # Base queryset - exclude deleted profiles
        profiles = Profile.objects.exclude(datamode='D').select_related('user')
        
        # ------------------ GET ALL FILTER PARAMS ------------------
        # Basic Filters
        gender = request.GET.get('gender')
        current_location = request.GET.get('current_location')
        city = request.GET.get('city')
        state = request.GET.get('state')
        country = request.GET.get('country')
        
        # Physical Attributes
        height_min = request.GET.get('height_min')
        height_max = request.GET.get('height_max')
        weight_min = request.GET.get('weight_min')
        weight_max = request.GET.get('weight_max')
        complexion = request.GET.get('complexion')
        
        # Religion & Community
        religion = request.GET.get('religion')
        caste = request.GET.get('caste')
        sub_caste = request.GET.get('sub_caste')
        gothram = request.GET.get('gothram')
        
        # Horoscope
        rasi = request.GET.get('rasi')
        nakshatra = request.GET.get('nakshatra')
        laknam = request.GET.get('laknam')
        dosham = request.GET.get('dosham')
        
        # Education & Career
        education = request.GET.get('education')
        profession = request.GET.get('profession')
        company_name = request.GET.get('company_name')
        job_location = request.GET.get('job_location')
        job_location_type = request.GET.get('job_location_type')
        job_state = request.GET.get('job_state')
        job_country = request.GET.get('job_country')
        
        # Income Filter
        income = request.GET.get('income')
        
        # Personal Details
        marital_status = request.GET.get('marital_status')
        age_min = request.GET.get('age_min')
        age_max = request.GET.get('age_max')
        
        # Family Details
        has_father_details = request.GET.get('has_father_details')
        has_mother_details = request.GET.get('has_mother_details')
        has_siblings = request.GET.get('has_siblings')
        no_of_brothers = request.GET.get('no_of_brothers')
        no_of_sisters = request.GET.get('no_of_sisters')
        
        # Other Filters
        verified_only = request.GET.get('verified_only')
        with_photo = request.GET.get('with_photo')
        is_currently_living = request.GET.get('is_currently_living')
        
        # Sorting and Shuffle
        sort = request.GET.get('sort', 'random')
        shuffle_profiles = request.GET.get('shuffle', 'true')

        # ------------------ APPLY FILTERS ------------------
        
        # Location Filters
        if current_location:
            profiles = profiles.filter(current_location__icontains=current_location)
        
        if city:
            profiles = profiles.filter(city__icontains=city)
        
        if state:
            profiles = profiles.filter(state__icontains=state)
        
        if country:
            profiles = profiles.filter(country__icontains=country)

        # Gender Filter
        if gender:
            profiles = profiles.filter(gender=gender)

        # Physical Attributes
        if height_min and height_min.isdigit():
            profiles = profiles.filter(height__gte=float(height_min))
        if height_max and height_max.isdigit():
            profiles = profiles.filter(height__lte=float(height_max))
            
        if weight_min and weight_min.isdigit():
            profiles = profiles.filter(weight__gte=float(weight_min))
        if weight_max and weight_max.isdigit():
            profiles = profiles.filter(weight__lte=float(weight_max))
        
        if complexion:
            profiles = profiles.filter(complexion__iexact=complexion)

        # Religion & Caste Filters
        if religion:
            profiles = profiles.filter(religion=religion)
        
        if caste:
            profiles = profiles.filter(caste=caste)
        
        if sub_caste:
            profiles = profiles.filter(sub_caste=sub_caste)
        
        if gothram:
            profiles = profiles.filter(gothram__iexact=gothram)

        # Horoscope Filters
        if rasi:
            profiles = profiles.filter(rasi__iexact=rasi)
        
        if nakshatra:
            profiles = profiles.filter(nakshatra__iexact=nakshatra)
        
        if laknam:
            profiles = profiles.filter(laknam__iexact=laknam)
        
        if dosham:
            profiles = profiles.filter(dosham=dosham)

        # Education & Career Filters
        if education:
            profiles = profiles.filter(education__icontains=education)
        
        if profession:
            profiles = profiles.filter(occupation__icontains=profession)
        
        if company_name:
            profiles = profiles.filter(company_name__icontains=company_name)
        
        if job_location:
            profiles = profiles.filter(job_location__icontains=job_location)
        
        if job_location_type:
            profiles = profiles.filter(job_location_type=job_location_type)
        
        if job_state:
            profiles = profiles.filter(job_state=job_state)
        
        if job_country:
            profiles = profiles.filter(job_country__icontains=job_country)

        # Income Filter
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

        # Marital Status Filter
        if marital_status:
            profiles = profiles.filter(marital_status=marital_status)

        # Age Filter
        if age_min or age_max:
            today = date.today()
            
            if age_min and age_min.isdigit():
                max_birth_date = today - relativedelta(years=int(age_min))
                profiles = profiles.filter(dob__lte=max_birth_date)
            
            if age_max and age_max.isdigit():
                min_birth_date = today - relativedelta(years=int(age_max))
                profiles = profiles.filter(dob__gte=min_birth_date)

        # Family Details Filters
        if has_father_details:
            profiles = profiles.filter(has_father_details=has_father_details)
        if has_mother_details:
            profiles = profiles.filter(has_mother_details=has_mother_details)
        if has_siblings:
            profiles = profiles.filter(has_siblings=has_siblings)
        if no_of_brothers and no_of_brothers.isdigit():
            profiles = profiles.filter(no_of_brothers__gte=int(no_of_brothers))
        if no_of_sisters and no_of_sisters.isdigit():
            profiles = profiles.filter(no_of_sisters__gte=int(no_of_sisters))

        # Other Filters
        if is_currently_living:
            profiles = profiles.filter(is_currently_living=True)
        
        if verified_only:
            profiles = profiles.filter(user__is_verified=True)
        
        if with_photo:
            profiles = profiles.filter(
                Q(photo1__isnull=False) | 
                Q(photo2__isnull=False) | 
                Q(photo3__isnull=False) | 
                Q(photo4__isnull=False) | 
                Q(photo5__isnull=False)
            )

        # ------------------ SORTING & SHUFFLING ------------------
        profiles_list = list(profiles)
        
        if shuffle_profiles == 'true' and sort == 'random':
            random.shuffle(profiles_list)
        elif sort == "age_low":
            profiles_list = sorted(profiles_list, key=lambda x: x.dob if x.dob else date(1900,1,1), reverse=True)
        elif sort == "age_high":
            profiles_list = sorted(profiles_list, key=lambda x: x.dob if x.dob else date(2100,1,1))
        elif sort == "income_high":
            profiles_list = sorted(profiles_list, key=lambda x: x.annual_income or 0, reverse=True)
        elif sort == "income_low":
            profiles_list = sorted(profiles_list, key=lambda x: x.annual_income or 0)
        elif sort == "name_asc":
            profiles_list = sorted(profiles_list, key=lambda x: x.user.first_name if x.user else '')
        elif sort == "name_desc":
            profiles_list = sorted(profiles_list, key=lambda x: x.user.first_name if x.user else '', reverse=True)
        elif sort == "newest":
            profiles_list = sorted(profiles_list, key=lambda x: x.created_on or date(1900,1,1), reverse=True)
        elif sort == "oldest":
            profiles_list = sorted(profiles_list, key=lambda x: x.created_on or date(2100,1,1))
        elif sort == "updated":
            profiles_list = sorted(profiles_list, key=lambda x: x.updated_on or date(1900,1,1), reverse=True)

        # ------------------ ANNOTATE ADDITIONAL FIELDS ------------------
        today = date.today()
        
        for profile in profiles_list:
            # Calculate age
            if profile.dob:
                age = today.year - profile.dob.year - (
                    (today.month, today.day) < (profile.dob.month, profile.dob.day)
                )
                profile.age = age
            else:
                profile.age = None
            
            # Get name
            if profile.user:
                profile.name = f"{profile.user.first_name} {profile.user.last_name}".strip()
            else:
                profile.name = "Profile"
            
            # Get profile photo
            profile.profile_photo = None
            for photo_field in ['photo1', 'photo2', 'photo3', 'photo4', 'photo5']:
                photo = getattr(profile, photo_field)
                if photo:
                    profile.profile_photo = photo
                    break
            
            # Premium status
            profile.premium = getattr(profile.user, 'is_premium', False) if profile.user else False
            profile.verified = getattr(profile.user, 'is_verified', False) if profile.user else False
            
            # Format height and weight
            if profile.height:
                try:
                    profile.height_display = f"{float(profile.height):.1f} cm"
                except:
                    profile.height_display = profile.height
            else:
                profile.height_display = "Not specified"
                
            if profile.weight:
                try:
                    profile.weight_display = f"{float(profile.weight):.1f} kg"
                except:
                    profile.weight_display = profile.weight
            else:
                profile.weight_display = "Not specified"

        # ------------------ PAGINATION ------------------
        paginator = Paginator(profiles_list, 9)
        page_number = request.GET.get('page')
        profiles_page = paginator.get_page(page_number)

        # ------------------ CONTEXT ------------------
        context["profiles"] = profiles_page
        context["filters"] = request.GET
        
        # Get all distinct values from database for dropdowns
        # Gender choices from model
        context["gender_choices"] = Profile.GENDER_CHOICES
        
        # Location choices from database
        context["current_location_choices"] = Profile.objects.exclude(datamode='D').exclude(current_location__isnull=True).exclude(current_location='').values_list('current_location', flat=True).distinct().order_by('current_location')
        context["city_choices"] = Profile.objects.exclude(datamode='D').exclude(city__isnull=True).exclude(city='').values_list('city', flat=True).distinct().order_by('city')
        context["state_choices"] = Profile.objects.exclude(datamode='D').exclude(state__isnull=True).exclude(state='').values_list('state', flat=True).distinct().order_by('state')
        context["country_choices"] = Profile.objects.exclude(datamode='D').exclude(country__isnull=True).exclude(country='').values_list('country', flat=True).distinct().order_by('country')
        
        # Religion & Community choices
        context["religion_choices"] = Profile.objects.exclude(datamode='D').exclude(religion__isnull=True).exclude(religion='').values_list('religion', flat=True).distinct().order_by('religion')
        context["caste_choices"] = Profile.objects.exclude(datamode='D').exclude(caste__isnull=True).exclude(caste='').values_list('caste', flat=True).distinct().order_by('caste')
        context["sub_caste_choices"] = Profile.objects.exclude(datamode='D').exclude(sub_caste__isnull=True).exclude(sub_caste='').values_list('sub_caste', flat=True).distinct().order_by('sub_caste')
        context["gothram_choices"] = Profile.objects.exclude(datamode='D').exclude(gothram__isnull=True).exclude(gothram='').values_list('gothram', flat=True).distinct().order_by('gothram')
        
        # Horoscope choices
        context["rasi_choices"] = Profile.objects.exclude(datamode='D').exclude(rasi__isnull=True).exclude(rasi='').values_list('rasi', flat=True).distinct().order_by('rasi')
        context["nakshatra_choices"] = Profile.objects.exclude(datamode='D').exclude(nakshatra__isnull=True).exclude(nakshatra='').values_list('nakshatra', flat=True).distinct().order_by('nakshatra')
        context["laknam_choices"] = Profile.objects.exclude(datamode='D').exclude(laknam__isnull=True).exclude(laknam='').values_list('laknam', flat=True).distinct().order_by('laknam')
        context["dosham_choices"] = Profile.DOSHAM_CHOICES
        
        # Physical attributes
        context["complexion_choices"] = Profile.objects.exclude(datamode='D').exclude(complexion__isnull=True).exclude(complexion='').values_list('complexion', flat=True).distinct().order_by('complexion')
        
        # Education & Career choices from database
        context["education_choices"] = Profile.objects.exclude(datamode='D').exclude(education__isnull=True).exclude(education='').values_list('education', flat=True).distinct().order_by('education')
        context["profession_choices"] = Profile.objects.exclude(datamode='D').exclude(occupation__isnull=True).exclude(occupation='').values_list('occupation', flat=True).distinct().order_by('occupation')
        context["company_name_choices"] = Profile.objects.exclude(datamode='D').exclude(company_name__isnull=True).exclude(company_name='').values_list('company_name', flat=True).distinct().order_by('company_name')
        context["job_location_choices"] = Profile.objects.exclude(datamode='D').exclude(job_location__isnull=True).exclude(job_location='').values_list('job_location', flat=True).distinct().order_by('job_location')
        context["job_state_choices"] = Profile.objects.exclude(datamode='D').exclude(job_state__isnull=True).exclude(job_state='').values_list('job_state', flat=True).distinct().order_by('job_state')
        context["job_country_choices"] = Profile.objects.exclude(datamode='D').exclude(job_country__isnull=True).exclude(job_country='').values_list('job_country', flat=True).distinct().order_by('job_country')
        
        # Model choices
        context["job_location_type_choices"] = Profile.JOB_LOCATION_TYPE
        context["marital_status_choices"] = Profile.MARITAL_STATUS_CHOICES
        
        # Theme preference
        context["theme"] = request.COOKIES.get('theme', 'light')
        
        return context
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        response = render(request, self.template_name, context)
        
        # Set theme cookie if theme parameter is present
        if 'theme' in request.GET:
            response.set_cookie('theme', request.GET.get('theme'), max_age=365*24*60*60)
        
        return response


from datetime import date, timedelta


class MutualMatchView(TemplateView):
    template_name = "mutual_match.html"

    def get(self, request, *args, **kwargs):
        context = {}

        if not request.user.is_authenticated:
            return render(request, self.template_name, context)

        # ✅ Use LATEST active profile (NOT get)
        my_profile = (
            Profile.objects
            .filter(user=request.user, datamode='A')
            .order_by('-updated_on')
            .first()
        )

        if not my_profile:
            context["profile"] = None
            context["error"] = "No active profile found."
            return render(request, self.template_name, context)

        # 🔁 Opposite gender
        gender_map = {'M': 'F', 'F': 'M'}
        target_gender = gender_map.get(my_profile.gender)

        # 🔄 Rotational match rules
        MATCH_RULES = {
            0: "location",
            1: "caste",
            2: "religion",
        }

        rule_index = date.today().toordinal() % len(MATCH_RULES)
        today_rule = MATCH_RULES[rule_index]

        # 🎯 Base queryset (ADMIN-created + USER-created profiles)
        profiles = Profile.objects.filter(
            gender=target_gender,
            datamode='A'
        ).exclude(user=request.user)

        # 🧠 Apply today’s rule
        if today_rule == "location":
            profiles = profiles.filter(location__iexact=my_profile.location)

        elif today_rule == "caste":
            profiles = profiles.filter(caste__iexact=my_profile.caste)

        elif today_rule == "religion":
            profiles = profiles.filter(religion__iexact=my_profile.religion)

        # 🎂 Optional: age similarity
        if my_profile.dob:
            min_dob = my_profile.dob - timedelta(days=365)
            max_dob = my_profile.dob + timedelta(days=365)
            profiles = profiles.filter(dob__range=(min_dob, max_dob))

        # 🥇 Pick ONE profile for today
        match = profiles.order_by('-updated_on').first()

        context["profile"] = match
        context["match_rule"] = today_rule.capitalize()

        return render(request, self.template_name, context)


# views.py
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView
from django.db.models import Q
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.core.paginator import Paginator

from django.contrib.auth.mixins import LoginRequiredMixin
@method_decorator(login_required(login_url=settings.LOGIN_WEB_REDIRECT_URL), name='dispatch')
class CommunitySearchPage(TemplateView):
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


class MutualMatchView(LoginRequiredMixin, TemplateView):
    template_name = "mutual_match.html"
    login_url = '/login/'
    
    def get(self, request, *args, **kwargs):
        context = {}
        
        # Get user's active profile
        my_profile = (
            Profile.objects
            .filter(user=request.user, datamode='A')
            .order_by('-updated_on')
            .first()
        )
        
        if not my_profile:
            context["error"] = "Please create your profile first to find mutual matches."
            return render(request, self.template_name, context)
        
        # Get today's match rule
        MATCH_RULES = [
            {"name": "Location", "field": "location", "icon": "fa-map-marker-alt"},
            {"name": "Caste", "field": "caste", "icon": "fa-users"},
            {"name": "Religion", "field": "religion", "icon": "fa-pray"},
            {"name": "Education", "field": "education", "icon": "fa-graduation-cap"},
            {"name": "Profession", "field": "occupation", "icon": "fa-briefcase"},
            {"name": "Interests", "field": "interests", "icon": "fa-heart"},
        ]
        
        rule_index = date.today().toordinal() % len(MATCH_RULES)
        today_rule = MATCH_RULES[rule_index]
        
        # Opposite gender
        gender_map = {'M': 'F', 'F': 'M'}
        target_gender = gender_map.get(my_profile.gender, 'F' if my_profile.gender == 'M' else 'M')
        
        # Base queryset
        profiles = Profile.objects.filter(
            gender=target_gender,
            datamode='A'
        ).exclude(user=request.user)
        
        # Apply today's rule
        if today_rule["field"] == "location" and my_profile.location:
            profiles = profiles.filter(location__iexact=my_profile.location)
        elif today_rule["field"] == "caste" and my_profile.caste:
            profiles = profiles.filter(caste__iexact=my_profile.caste)
        elif today_rule["field"] == "religion" and my_profile.religion:
            profiles = profiles.filter(religion__iexact=my_profile.religion)
        elif today_rule["field"] == "education" and my_profile.education:
            profiles = profiles.filter(education__iexact=my_profile.education)
        elif today_rule["field"] == "occupation" and my_profile.occupation:
            profiles = profiles.filter(occupation__iexact=my_profile.occupation)
        elif today_rule["field"] == "interests" and hasattr(my_profile, 'interests') and my_profile.interests:
            # Split interests and search for any match
            my_interests = [i.strip() for i in my_profile.interests.split(',')]
            queries = Q()
            for interest in my_interests:
                queries |= Q(interests__icontains=interest)
            profiles = profiles.filter(queries)
        
        
        mutual_matches = []
        
        for profile in profiles:
            # Calculate age
            if profile.dob:
                age = today.year - profile.dob.year - (
                    (today.month, today.day) < (profile.dob.month, profile.dob.day)
                )
                profile.age = age
            
            # Add full name
            if profile.user:
                profile.name = f"{profile.user.first_name} {profile.user.last_name}"
            
            # Calculate detailed compatibility
            compatibility = self.calculate_compatibility(my_profile, profile, today_rule["field"])
            profile.compatibility = compatibility
            
            mutual_matches.append(profile)
        
        # Sort by compatibility score
        mutual_matches.sort(key=lambda x: x.compatibility['score'], reverse=True)
        
        # Pagination
        paginator = Paginator(mutual_matches, 6)
        page_number = request.GET.get('page')
        matches_page = paginator.get_page(page_number)
        
        context.update({
            "matches": matches_page,
            "match_rule": today_rule,
            "my_profile": my_profile,
            "all_rules": MATCH_RULES,
            "rule_index": rule_index,
        })
        
        return render(request, self.template_name, context)
    
    def calculate_compatibility(self, my_profile, other_profile, rule_field):
        score = 0
        factors = 0
        matching_points = []
        
        # Today's rule match (40 points)
        if rule_field == "location":
            if my_profile.location and other_profile.location:
                if my_profile.location.lower() == other_profile.location.lower():
                    score += 40
                    matching_points.append("Same city")
                elif my_profile.location.split(',')[0].lower() == other_profile.location.split(',')[0].lower():
                    score += 30
                    matching_points.append("Same region")
                factors += 1
        
        elif rule_field == "caste":
            if my_profile.caste and other_profile.caste:
                if my_profile.caste.lower() == other_profile.caste.lower():
                    score += 40
                    matching_points.append("Same caste")
                factors += 1
        
        elif rule_field == "religion":
            if my_profile.religion and other_profile.religion:
                if my_profile.religion.lower() == other_profile.religion.lower():
                    score += 40
                    matching_points.append("Same religion")
                factors += 1
        
        elif rule_field == "education":
            if my_profile.education and other_profile.education:
                if my_profile.education.lower() == other_profile.education.lower():
                    score += 40
                    matching_points.append("Same education level")
                elif any(edu in my_profile.education for edu in ['PhD', 'Master']) and \
                     any(edu in other_profile.education for edu in ['PhD', 'Master']):
                    score += 30
                    matching_points.append("Similar education level")
                factors += 1
        
        elif rule_field == "occupation":
            if my_profile.occupation and other_profile.occupation:
                if my_profile.occupation.lower() == other_profile.occupation.lower():
                    score += 40
                    matching_points.append("Same profession")
                elif any(word in my_profile.occupation.lower() for word in ['engineer', 'developer']) and \
                     any(word in other_profile.occupation.lower() for word in ['engineer', 'developer']):
                    score += 30
                    matching_points.append("Similar profession")
                factors += 1
        
        # Age compatibility (30 points)
        if my_profile.age and other_profile.age:
            age_diff = abs(my_profile.age - other_profile.age)
            if age_diff <= 3:
                score += 30
                matching_points.append("Perfect age match")
            elif age_diff <= 5:
                score += 20
                matching_points.append("Good age match")
            elif age_diff <= 8:
                score += 10
                matching_points.append("Acceptable age difference")
            factors += 1
        
        # Marital status compatibility (20 points)
        if my_profile.marital_status and other_profile.marital_status:
            if my_profile.marital_status == other_profile.marital_status:
                score += 20
                matching_points.append("Similar marital status")
            factors += 1
        
        # Calculate percentage
        total_possible = factors * 100 if factors > 0 else 100
        final_score = min(int((score / total_possible) * 100), 100)
        
        return {
            "score": final_score,
            "matching_points": matching_points,
            "rule_field": rule_field
        }



class Newmatches(TemplateView):
    template_name = "new_match.html"
    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("Profile")
        profile = Profile.objects.exclude(datamode='D').order_by('-updated_on')
        logger.info(request.GET)
        return render(request, self.template_name, context)


import logging
from datetime import datetime
from decimal import Decimal
from django.urls import reverse
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import traceback

logger = logging.getLogger(__name__)

class EnquiryCreatePage(TemplateView):
    template_name = "includes/enquiry.html"

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_kwargs"] = {}  # Replace with actual SEO function
        context["selected_property_type"] = request.GET.get('property_type', '')
        logger.info(f"GET params: {request.GET}")
        return render(request, self.template_name, context)

import json
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import reverse
from django.utils import timezone
from datetime import datetime
from decimal import Decimal, DecimalException
import logging

logger = logging.getLogger(__name__)
@require_POST
@login_required
@ensure_csrf_cookie
def ajax_profile_save(request):
    print(f"✅ ajax_profile_save view reached! User: {request.user.username}")
    """
    Single unified AJAX endpoint for saving profiles
    """
    try:
        # Log request details
        logger.info(f"ajax_profile_save called by user: {request.user.username}")
        
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            return JsonResponse({
                "success": False,
                "message": "This endpoint only accepts AJAX requests"
            }, status=400)

        # Check if user already has a profile
        existing_profile = Profile.objects.filter(user=request.user).first()
        if existing_profile:
            return JsonResponse({
                "success": False,
                "message": "You already have a profile. Please edit your existing profile instead.",
                "redirect_url": reverse("mck_master:mck_profile_update", args=[existing_profile.id])
            }, status=400)

        # Create new profile
        profile_obj = Profile(
            user=request.user,
            created_by=request.user.username,
            updated_by=request.user.username,
            datamode="A"
        )

        pDict = request.POST
        files = request.FILES

        # BASIC DETAILS
        profile_obj.full_name = pDict.get("full_name", "").strip()
        profile_obj.gender = pDict.get("gender", "")
        
        dob_str = pDict.get("dob")
        if dob_str and dob_str.strip():
            try:
                profile_obj.dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
            except ValueError:
                profile_obj.dob = None
        
        birth_time_str = pDict.get("birth_time")
        if birth_time_str and birth_time_str.strip():
            try:
                profile_obj.birth_time = datetime.strptime(birth_time_str, "%H:%M").time()
            except ValueError:
                profile_obj.birth_time = None
        
        profile_obj.birth_place = pDict.get("birth_place", "").strip()
        profile_obj.is_currently_living = pDict.get("is_currently_living", "false").lower() == "true"
        profile_obj.current_location = pDict.get("current_location", "").strip()
        profile_obj.height = pDict.get("height", "").strip()
        profile_obj.weight = pDict.get("weight", "").strip()
        profile_obj.complexion = pDict.get("complexion", "").strip()
        profile_obj.marital_status = pDict.get("marital_status", "")

        # RELIGION & HOROSCOPE
        profile_obj.religion = pDict.get("religion", "").strip()
        profile_obj.caste = pDict.get("caste", "").strip()
        profile_obj.sub_caste = pDict.get("sub_caste", "").strip()
        profile_obj.gothram = pDict.get("gothram", "").strip()
        profile_obj.rasi = pDict.get("rasi", "").strip()
        profile_obj.nakshatra = pDict.get("nakshatra", "").strip()
        profile_obj.laknam = pDict.get("laknam", "").strip()
        profile_obj.dosham = pDict.get("dosham", "")

        # EDUCATION & CAREER
        profile_obj.education = pDict.get("education", "").strip()
        profile_obj.occupation = pDict.get("occupation", "").strip()
        profile_obj.company_name = pDict.get("company_name", "").strip()
        profile_obj.job_location = pDict.get("job_location", "").strip()
        profile_obj.job_location_type = pDict.get("job_location_type", "India")
        
        if profile_obj.job_location_type == "India":
            profile_obj.job_state = pDict.get("job_state", "").strip()
            profile_obj.job_country = ""
        else:
            profile_obj.job_state = ""
            profile_obj.job_country = pDict.get("job_country", "").strip()
        
        income_str = pDict.get("annual_income")
        if income_str and income_str.strip():
            try:
                profile_obj.annual_income = Decimal(income_str.replace(',', '').strip())
            except (ValueError, DecimalException):
                profile_obj.annual_income = None

        # FAMILY DETAILS
        profile_obj.has_father_details = pDict.get("has_father_details", "N")
        if profile_obj.has_father_details == "Y":
            profile_obj.father_name = pDict.get("father_name", "").strip()
            profile_obj.father_occupation = pDict.get("father_occupation", "").strip()

        profile_obj.has_mother_details = pDict.get("has_mother_details", "N")
        if profile_obj.has_mother_details == "Y":
            profile_obj.mother_name = pDict.get("mother_name", "").strip()
            profile_obj.mother_occupation = pDict.get("mother_occupation", "").strip()

        profile_obj.has_siblings = pDict.get("has_siblings", "N")
        if profile_obj.has_siblings == "Y":
            brothers_str = pDict.get("no_of_brothers")
            if brothers_str and brothers_str.strip():
                try:
                    profile_obj.no_of_brothers = int(brothers_str)
                except ValueError:
                    profile_obj.no_of_brothers = None
            
            sisters_str = pDict.get("no_of_sisters")
            if sisters_str and sisters_str.strip():
                try:
                    profile_obj.no_of_sisters = int(sisters_str)
                except ValueError:
                    profile_obj.no_of_sisters = None

        # CONTACT INFORMATION
        profile_obj.phone = pDict.get("phone", "").strip()
        profile_obj.whatsapp_number = pDict.get("whatsapp_number", "").strip()
        profile_obj.email = pDict.get("email", "").strip()
        profile_obj.address = pDict.get("address", "").strip()
        profile_obj.city = pDict.get("city", "").strip()
        profile_obj.state = pDict.get("state", "").strip()
        profile_obj.country = pDict.get("country", "").strip()
        profile_obj.pincode = pDict.get("pincode", "").strip()

        # ABOUT
        profile_obj.bio = pDict.get("bio", "").strip()
        profile_obj.hobbies = pDict.get("hobbies", "").strip()

        # PROFILE PHOTOS
        photo_fields = ['photo1', 'photo2', 'photo3', 'photo4', 'photo5']
        for field in photo_fields:
            if field in files:
                try:
                    setattr(profile_obj, field, files[field])
                except Exception as e:
                    logger.error(f"Error uploading {field}: {str(e)}")

        # Save the profile
        profile_obj.save()
        
        # Mark profile as completed
        request.user.is_profile_completed = True
        request.user.save()
        
        logger.info(f"Profile saved successfully for user {request.user.username}")
        
        return JsonResponse({
            "success": True,
            "message": "Profile created successfully!",
            "profile_id": profile_obj.id,
            "redirect_url": reverse("vlr_website:payment_gateway")
        })
        
    except Exception as e:
        logger.exception(f"Error saving profile: {str(e)}")
        return JsonResponse({
            "success": False,
            "message": str(e)
        }, status=400)
from datetime import date
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from decimal import Decimal
import logging
import traceback

logger = logging.getLogger(__name__)

class MyProfilePage(LoginRequiredMixin, TemplateView):
    """My Profile page with display and edit functionality"""
    template_name = "my_profile.html"
    login_url = "/login/"
    
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # Get the active profile (or most recent if none active)
            profile = Profile.objects.filter(
                user=request.user
            ).exclude(
                datamode='D'
            ).order_by('-updated_on').first()
            
            # If no profile exists, create one
            if not profile:
                profile = Profile.objects.create(
                    user=request.user,
                    created_by=request.user.username,
                    updated_by=request.user.username,
                    datamode='A',
                    gender='',  # Empty default
                    marital_status='S'  # Default to Single
                )
                logger.info(f"Created new profile for user: {request.user.username}")
            
            # Calculate age
            age = None
            if profile.dob:
                today = date.today()
                age = today.year - profile.dob.year
                # Subtract a year if birthday hasn't occurred yet this year
                if (today.month, today.day) < (profile.dob.month, profile.dob.day):
                    age -= 1
            
            # Format profile photo URL
            profile_photo_url = None
            if profile.photo1 and profile.photo1.url:
                profile_photo_url = profile.photo1.url
            elif profile.profile_photo and profile.profile_photo.url:  # Backward compatibility
                profile_photo_url = profile.profile_photo.url
            
            # Add to context
            context['profile'] = profile
            context['age'] = age
            context['profile_photo_url'] = profile_photo_url
            
            # Get all photos
            photos = []
            for i in range(1, 6):
                photo = getattr(profile, f'photo{i}', None)
                if photo and photo.url:
                    photos.append({
                        'url': photo.url,
                        'number': i
                    })
            context['photos'] = photos
            
            # Format income for display
            if profile.annual_income:
                context['formatted_income'] = f"${profile.annual_income:,.0f}"
            
            logger.info(f"Loaded profile for user: {request.user.username}")
            
        except Exception as e:
            logger.error(f"Error loading profile: {str(e)}")
            context['profile'] = None
            context['error'] = "Could not load profile. Please try again."
        
        return render(request, self.template_name, context)


from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from decimal import Decimal
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@require_POST
@login_required
@ensure_csrf_cookie
def ajax_my_profile_save(request):
    """AJAX endpoint for saving/updating profile"""

    try:
        profile, created = Profile.objects.get_or_create(
            user=request.user,
            defaults={
                'created_by': request.user.username,
                'updated_by': request.user.username,
                'datamode': 'A',
                'gender': '',
                'marital_status': 'S'
            }
        )

        if profile.datamode == 'D':
            profile.datamode = 'A'

        pDict = request.POST
        files = request.FILES

        # ================= BASIC DETAILS =================
        profile.full_name = pDict.get('full_name', '').strip()
        profile.gender = pDict.get('gender', '')

        # DOB
        dob_str = pDict.get('dob')
        if dob_str:
            try:
                profile.dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
            except ValueError:
                profile.dob = None
        else:
            profile.dob = None

        # Birth Time
        birth_time_str = pDict.get('birth_time')
        if birth_time_str:
            try:
                profile.birth_time = datetime.strptime(birth_time_str, '%H:%M').time()
            except ValueError:
                profile.birth_time = None
        else:
            profile.birth_time = None

        profile.birth_place = pDict.get('birth_place', '').strip()
        profile.marital_status = pDict.get('marital_status', 'S')
        profile.height = pDict.get('height', '').strip()
        profile.weight = pDict.get('weight', '').strip()
        profile.complexion = pDict.get('complexion', '').strip()

        # ================= RELIGION =================
        profile.religion = pDict.get('religion', '').strip()
        profile.caste = pDict.get('caste', '').strip()
        profile.sub_caste = pDict.get('sub_caste', '').strip()
        profile.gothram = pDict.get('gothram', '').strip()
        profile.rasi = pDict.get('rasi', '').strip()
        profile.nakshatra = pDict.get('nakshatra', '').strip()
        profile.laknam = pDict.get('laknam', '').strip()
        profile.dosham = pDict.get('dosham', '')

        # ================= EDUCATION =================
        profile.education = pDict.get('education', '').strip()
        profile.occupation = pDict.get('occupation', '').strip()
        profile.company_name = pDict.get('company_name', '').strip()
        profile.job_location = pDict.get('job_location', '').strip()

        # Annual Income
        income_str = pDict.get('annual_income')
        if income_str:
            try:
                income_clean = income_str.replace(',', '').replace('$', '').strip()
                profile.annual_income = Decimal(income_clean)
            except:
                profile.annual_income = None
        else:
            profile.annual_income = None

        # ================= FAMILY =================
        profile.has_father_details = pDict.get('has_father_details', 'N')
        if profile.has_father_details == 'Y':
            profile.father_name = pDict.get('father_name', '').strip()
            profile.father_occupation = pDict.get('father_occupation', '').strip()
        else:
            profile.father_name = ''
            profile.father_occupation = ''

        profile.has_mother_details = pDict.get('has_mother_details', 'N')
        if profile.has_mother_details == 'Y':
            profile.mother_name = pDict.get('mother_name', '').strip()
            profile.mother_occupation = pDict.get('mother_occupation', '').strip()
        else:
            profile.mother_name = ''
            profile.mother_occupation = ''

        profile.has_siblings = pDict.get('has_siblings', 'N')
        if profile.has_siblings == 'Y':
            try:
                profile.no_of_brothers = int(pDict.get('no_of_brothers') or 0)
            except:
                profile.no_of_brothers = None

            try:
                profile.no_of_sisters = int(pDict.get('no_of_sisters') or 0)
            except:
                profile.no_of_sisters = None
        else:
            profile.no_of_brothers = None
            profile.no_of_sisters = None

        # ================= CONTACT =================
        profile.phone = pDict.get('phone', '').strip()
        profile.whatsapp_number = pDict.get('whatsapp_number', '').strip()
        profile.email = pDict.get('email', '').strip()
        profile.address = pDict.get('address', '').strip()
        profile.city = pDict.get('city', '').strip()
        profile.state = pDict.get('state', '').strip()
        profile.country = pDict.get('country', '').strip()
        profile.pincode = pDict.get('pincode', '').strip()

        if profile.city or profile.state or profile.country:
            profile.location = ", ".join(
                filter(None, [profile.city, profile.state, profile.country])
            )

        # ================= ABOUT =================
        profile.bio = pDict.get('bio', '').strip()
        profile.hobbies = pDict.get('hobbies', '').strip()

        # ================= PHOTOS =================
        photo_fields = ['photo1', 'photo2', 'photo3', 'photo4', 'photo5']

        for field in photo_fields:
            if field in files:
                try:
                    old_photo = getattr(profile, field, None)
                    if old_photo:
                        old_photo.delete(save=False)

                    setattr(profile, field, files[field])

                except Exception as e:
                    logger.error(f"Error uploading {field}: {str(e)}")

        # ================= SYSTEM =================
        profile.updated_by = request.user.username
        profile.datamode = 'A'

        profile.save()

        # ================= RESPONSE =================
        response_data = {
            'success': True,
            'message': 'Profile updated successfully!',
            'profile_id': profile.id,
            'redirect_url': reverse('mck_website:my_profile')
        }

        if profile.photo1:
            response_data['photo1_url'] = profile.photo1.url

        return JsonResponse(response_data)

    except Exception as e:
        logger.error(f"Error saving profile: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


from django.views.generic import TemplateView, DetailView
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import date
import logging

logger = logging.getLogger(__name__)

@method_decorator(login_required(login_url=settings.LOGIN_WEB_REDIRECT_URL), name='dispatch')
class ProfileDetailPage(DetailView):
    """Professional profile detail view with complete information"""
    model = Profile
    template_name = "profile_detail.html"
    context_object_name = "profile"
    
    def get_queryset(self):
        """Exclude deleted profiles"""
        return Profile.objects.exclude(datamode='D')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.object
        
        # Calculate age from DOB
        if profile.dob:
            today = date.today()
            age = today.year - profile.dob.year
            if (today.month, today.day) < (profile.dob.month, profile.dob.day):
                age -= 1
            context['age'] = age
        
        # Format annual income
        if profile.annual_income:
            context['formatted_income'] = f"₹{profile.annual_income:,.0f}"
        
        # Get all photos
        photos = []
        for i in range(1, 6):
            photo = getattr(profile, f'photo{i}', None)
            if photo and hasattr(photo, 'url') and photo.url:
                photos.append({
                    'url': photo.url,
                    'number': i
                })
        context['photos'] = photos
        
        # Get main profile photo
        if profile.photo1:
            context['profile_photo'] = profile.photo1.url
        else:
            context['profile_photo'] = None

        
        # Format address
        address_parts = []
        if profile.address:
            address_parts.append(profile.address)
        if profile.city:
            address_parts.append(profile.city)
        if profile.state:
            address_parts.append(profile.state)
        if profile.country:
            address_parts.append(profile.country)
        if profile.pincode:
            address_parts.append(profile.pincode)
        context['full_address'] = ', '.join(address_parts) if address_parts else None
        
        # Get marital status display
        marital_status_map = {
            'S': 'Single',
            'M': 'Married',
            'D': 'Divorced',
            'W': 'Widowed'
        }
        context['marital_status_display'] = marital_status_map.get(profile.marital_status, 'Not Specified')
        
        # Get gender display
        gender_map = {
            'M': 'Male',
            'F': 'Female',
            'O': 'Other'
        }
        context['gender_display'] = gender_map.get(profile.gender, 'Not Specified')
        
        # Get dosham display
        dosham_map = {
            'Yes': 'Yes',
            'No': 'No',
            'Unknown': 'Unknown'
        }
        context['dosham_display'] = dosham_map.get(profile.dosham, 'Not Specified')
        
        # Get verification status (you can customize this logic)
        context['is_verified'] = bool(profile.phone and profile.email and profile.photo1)
        context['profile_completeness'] = self.calculate_profile_completeness(profile)
        
        return context
    
    def calculate_profile_completeness(self, profile):
        """Calculate profile completion percentage"""
        fields = [
            'full_name', 'gender', 'dob', 'marital_status',
            'religion', 'caste', 'education', 'occupation',
            'annual_income', 'phone', 'email', 'city',
            'bio', 'photo1'
        ]
        
        filled = 0
        for field in fields:
            value = getattr(profile, field, None)
            if value and str(value).strip():
                filled += 1
        
        return int((filled / len(fields)) * 100)



from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
import json
import logging

logger = logging.getLogger(__name__)


# views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q, Case, When, IntegerField, Value, FloatField, F
from django.core.paginator import Paginator
from django.utils import timezone
import json
import logging
from datetime import date

logger = logging.getLogger(__name__)

@login_required
def community_match(request):
    """Community matchmaking page with filters"""
    user_profile = Profile.objects.filter(user=request.user).first()
    
    # Base queryset - exclude current user's profiles and deleted profiles
    profiles = Profile.objects.exclude(
        Q(user=request.user) | Q(datamode='D')
    ).select_related('user')
    
    # Apply filters
    filters = {}
    
    # Gender filter (looking for)
    if request.GET.get('gender'):
        gender = request.GET.get('gender')
        profiles = profiles.filter(gender=gender)
        filters['gender'] = gender
    
    # Age range filter
    age_min = request.GET.get('age_min')
    age_max = request.GET.get('age_max')
    
    if age_min or age_max:
        today = date.today()
        if age_min:
            min_birth_year = today.year - int(age_min) - 1
            max_birth_date = date(min_birth_year, today.month, today.day)
            profiles = profiles.filter(dob__lte=max_birth_date)
            filters['age_min'] = age_min
        
        if age_max:
            max_birth_year = today.year - int(age_max)
            min_birth_date = date(max_birth_year, today.month, today.day)
            profiles = profiles.filter(dob__gte=min_birth_date)
            filters['age_max'] = age_max
    
    # City filter
    if request.GET.get('city'):
        city = request.GET.get('city')
        profiles = profiles.filter(city=city)
        filters['city'] = city
    
    # Religion filter
    if request.GET.get('religion'):
        religion = request.GET.get('religion')
        profiles = profiles.filter(religion=religion)
        filters['religion'] = religion
    
    # Education filter
    if request.GET.get('education'):
        education = request.GET.get('education')
        profiles = profiles.filter(education=education)
        filters['education'] = education
    
    # Profession filter
    if request.GET.get('profession'):
        profession = request.GET.get('profession')
        profiles = profiles.filter(occupation=profession)
        filters['profession'] = profession
    
    # Income filter
    if request.GET.get('income'):
        income = request.GET.get('income')
        if income == 'below_10':
            profiles = profiles.filter(income__lt=1000000)
        elif income == '10_25':
            profiles = profiles.filter(income__gte=1000000, income__lt=2500000)
        elif income == '25_50':
            profiles = profiles.filter(income__gte=2500000, income__lt=5000000)
        elif income == '50_100':
            profiles = profiles.filter(income__gte=5000000, income__lt=10000000)
        elif income == 'above_100':
            profiles = profiles.filter(income__gte=10000000)
        filters['income'] = income
    
    # Calculate compatibility scores if user has a profile
    if user_profile:
        for profile in profiles:
            score = calculate_compatibility(user_profile, profile)
            profile.compatibility_score = score
    
    # Sorting
    sort_by = request.GET.get('sort', 'compatibility')
    filters['sort'] = sort_by
    
    if sort_by == 'newest':
        profiles = profiles.order_by('-created_on')
    elif sort_by == 'age_low':
        profiles = profiles.order_by('dob')
    elif sort_by == 'age_high':
        profiles = profiles.order_by('-dob')
    elif sort_by == 'income_high':
        profiles = profiles.order_by('-income')
    else:  # compatibility or default
        if user_profile:
            # Sort by pre-calculated compatibility
            profiles = sorted(profiles, key=lambda x: getattr(x, 'compatibility_score', 0), reverse=True)
        else:
            profiles = profiles.order_by('-created_on')
    
    # Get user's wishlist IDs
    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = Wishlist.objects.filter(
            from_user=request.user
        ).values_list('to_profile_id', flat=True)
    
    # Pagination
    paginator = Paginator(profiles, 12)  # 12 profiles per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    cities = Profile.objects.exclude(user=request.user).exclude(city__isnull=True).exclude(city='').values_list('city', flat=True).distinct().order_by('city')
    religions = Profile.objects.exclude(user=request.user).exclude(religion__isnull=True).exclude(religion='').values_list('religion', flat=True).distinct().order_by('religion')
    educations = Profile.objects.exclude(user=request.user).exclude(education__isnull=True).exclude(education='').values_list('education', flat=True).distinct().order_by('education')
    occupations = Profile.objects.exclude(user=request.user).exclude(occupation__isnull=True).exclude(occupation='').values_list('occupation', flat=True).distinct().order_by('occupation')
    
    context = {
        'profiles': page_obj,
        'filters': filters,
        'cities': cities,
        'religions': religions,
        'educations': educations,
        'occupations': occupations,
        'user_profile': user_profile,
        'wishlist_ids': list(wishlist_ids),
    }
    
    return render(request, 'community_match.html', context)


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


def calculate_age(birth_date):
    """Calculate age from birth date"""
    if not birth_date:
        return None
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


@login_required
def my_wishlist(request):
    """Render wishlist page"""
    return render(request, 'wishlist.html')


@login_required
@require_POST
@csrf_protect
def toggle_wishlist(request):
    """Add or remove profile from wishlist"""
    try:
        data = json.loads(request.body) if request.body else request.POST
        profile_id = data.get('profile_id')
        action = data.get('action', 'add')  # 'add' or 'remove'
        
        # Get the profile
        to_profile = get_object_or_404(
            Profile.objects.exclude(datamode='D'),
            pk=profile_id
        )
        
        # Check if user is trying to shortlist their own profile
        if to_profile.user == request.user:
            return JsonResponse({
                'success': False,
                'message': 'You cannot shortlist your own profile'
            }, status=400)
        
        if action == 'add':
            # Add to wishlist
            wishlist_item, created = Wishlist.objects.get_or_create(
                from_user=request.user,
                to_profile=to_profile
            )
            
            if created:
                message = 'Profile added to wishlist!'
            else:
                message = 'Profile already in wishlist'
            
            return JsonResponse({
                'success': True,
                'message': message,
                'action': 'added',
                'wishlist_id': wishlist_item.id
            })
            
        else:  # remove
            # Remove from wishlist
            deleted = Wishlist.objects.filter(
                from_user=request.user,
                to_profile=to_profile
            ).delete()
            
            if deleted[0] > 0:
                return JsonResponse({
                    'success': True,
                    'message': 'Profile removed from wishlist',
                    'action': 'removed'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Profile not found in wishlist'
                }, status=404)
        
    except Profile.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Profile not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error toggling wishlist: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred. Please try again.'
        }, status=500)


@login_required
def get_wishlist(request):
    """Get all shortlisted profiles for the current user"""
    try:
        wishlist_items = Wishlist.objects.filter(
            from_user=request.user
        ).select_related(
            'to_profile', 
            'to_profile__user'
        ).order_by('-created_on')
        
        data = []
        for item in wishlist_items:
            profile = item.to_profile
            
            # Get profile photo
            profile_photo = None
            if profile and profile.photo1 and profile.photo1.url:
                profile_photo = profile.photo1.url
            elif profile and profile.profile_photo and profile.profile_photo.url:
                profile_photo = profile.profile_photo.url
            
            # Calculate age
            age = None
            if profile and profile.dob:
                age = calculate_age(profile.dob)
            
            # Get gender display
            gender_display = 'Not Specified'
            if profile and profile.gender:
                gender_map = dict(Profile.GENDER_CHOICES)
                gender_display = gender_map.get(profile.gender, 'Not Specified')
            
            data.append({
                'id': item.id,
                'profile_id': profile.id if profile else None,
                'profile_name': profile.full_name if profile and profile.full_name else 
                               (profile.user.get_full_name() if profile and profile.user else 'Unknown'),
                'profile_photo': profile_photo,
                'age': age,
                'gender': gender_display,
                'location': profile.city if profile and profile.city else 
                           (profile.location if profile and profile.location else 'Location not specified'),
                'occupation': profile.occupation if profile else 'Not specified',
                'education': profile.education if profile else 'Not specified',
                'created_on': item.created_on.strftime('%B %d, %Y'),
                'created_on_timestamp': item.created_on.timestamp(),
            })
        
        return JsonResponse({
            'success': True,
            'wishlist': data,
            'count': len(data)
        })
        
    except Exception as e:
        logger.error(f"Error getting wishlist: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Failed to load wishlist: {str(e)}',
            'wishlist': []
        }, status=500)


@login_required
@require_POST
def remove_from_wishlist(request, wishlist_id):
    """Remove a specific item from wishlist"""
    try:
        wishlist_item = get_object_or_404(
            Wishlist,
            id=wishlist_id,
            from_user=request.user
        )
        
        profile_name = wishlist_item.to_profile.full_name or 'Profile'
        wishlist_item.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'{profile_name} removed from wishlist'
        })
        
    except Exception as e:
        logger.error(f"Error removing from wishlist: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

        
class GalleryPageView(TemplateView):
    template_name = "gallery.html"

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        # Only Active records
        context['gallery_list'] = Gallery.objects.filter(datamode="A").order_by('-updated_on')

        return render(request, self.template_name, context)


class SucessStoryPageView(TemplateView):
    template_name = "sucess_stories.html"

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        context['gallery_list'] = Gallery.objects.filter(
            datamode="A"
        ).order_by('-updated_on')

        return render(request, self.template_name, context)



class SupportPageView(TemplateView):
    template_name = "support.html"

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        context['gallery_list'] = Gallery.objects.filter(
            datamode="A"
        ).order_by('-updated_on')

        return render(request, self.template_name, context)

class ContactPageView(TemplateView):
    template_name = "contact_us.html"

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        context['gallery_list'] = Gallery.objects.filter(
            datamode="A"
        ).order_by('-updated_on')

        return render(request, self.template_name, context)


# views.py
from django.views.generic import ListView
from django.db.models import Q, Count
from django.utils import timezone
from datetime import date
import random

class ProfileFilterView(ListView):
    model = Profile
    template_name = 'profile_filter.html'
    context_object_name = 'profiles'
    paginate_by = 12

    def get_queryset(self):
        queryset = Profile.objects.all()
        
        # Get filter parameters
        filters = Q()
        
        # Basic filters
        gender = self.request.GET.get('gender')
        if gender:
            filters &= Q(gender=gender)
        
        marital_status = self.request.GET.get('marital_status')
        if marital_status:
            filters &= Q(marital_status=marital_status)
        
        # Age range
        age_min = self.request.GET.get('age_min')
        age_max = self.request.GET.get('age_max')
        if age_min and age_max:
            today = date.today()
            from datetime import timedelta
            try:
                max_birth_date = today - timedelta(days=int(age_min)*365)
                min_birth_date = today - timedelta(days=int(age_max)*365 + 365)
                filters &= Q(dob__lte=max_birth_date, dob__gte=min_birth_date)
            except (ValueError, TypeError):
                pass
        
        # Height range
        height_min = self.request.GET.get('height_min')
        height_max = self.request.GET.get('height_max')
        if height_min and height_max:
            try:
                filters &= Q(height__gte=float(height_min), height__lte=float(height_max))
            except (ValueError, TypeError):
                pass
        
        # Location filters
        city = self.request.GET.get('city')
        if city:
            filters &= Q(city__icontains=city)
        
        state = self.request.GET.get('state')
        if state:
            filters &= Q(state=state)
        
        country = self.request.GET.get('country')
        if country:
            filters &= Q(country=country)
        
        # Religion & Community
        religion = self.request.GET.get('religion')
        if religion:
            filters &= Q(religion=religion)
        
        caste = self.request.GET.get('caste')
        if caste:
            filters &= Q(caste=caste)
        
        sub_caste = self.request.GET.get('sub_caste')
        if sub_caste:
            filters &= Q(sub_caste=sub_caste)
        
        gothram = self.request.GET.get('gothram')
        if gothram:
            filters &= Q(gothram=gothram)
        
        # Horoscope
        rasi = self.request.GET.get('rasi')
        if rasi:
            filters &= Q(rasi=rasi)
        
        nakshatra = self.request.GET.get('nakshatra')
        if nakshatra:
            filters &= Q(nakshatra=nakshatra)
        
        dosham = self.request.GET.get('dosham')
        if dosham:
            filters &= Q(dosham=dosham)
        
        # Education & Career
        education = self.request.GET.get('education')
        if education:
            filters &= Q(education__icontains=education)
        
        profession = self.request.GET.get('profession')
        if profession:
            filters &= Q(occupation__icontains=profession)
        
        # Income range
        income = self.request.GET.get('income')
        if income:
            income_map = {
                'below_10': Q(annual_income__lt=1000000),
                '10_25': Q(annual_income__gte=1000000, annual_income__lt=2500000),
                '25_50': Q(annual_income__gte=2500000, annual_income__lt=5000000),
                '50_100': Q(annual_income__gte=5000000, annual_income__lt=10000000),
                'above_100': Q(annual_income__gte=10000000),
            }
            if income in income_map:
                filters &= income_map[income]
        
        # Family filters
        has_father_details = self.request.GET.get('has_father_details')
        if has_father_details:
            filters &= Q(has_father_details=has_father_details)
        
        has_mother_details = self.request.GET.get('has_mother_details')
        if has_mother_details:
            filters &= Q(has_mother_details=has_mother_details)
        
        has_siblings = self.request.GET.get('has_siblings')
        if has_siblings:
            filters &= Q(has_siblings=has_siblings)
        
        no_of_brothers = self.request.GET.get('no_of_brothers')
        if no_of_brothers:
            try:
                filters &= Q(no_of_brothers__gte=int(no_of_brothers))
            except (ValueError, TypeError):
                pass
        
        no_of_sisters = self.request.GET.get('no_of_sisters')
        if no_of_sisters:
            try:
                filters &= Q(no_of_sisters__gte=int(no_of_sisters))
            except (ValueError, TypeError):
                pass
        
        # Additional filters
        verified_only = self.request.GET.get('verified_only')
        if verified_only:
            # Add is_verified field if it exists in your model
            # filters &= Q(is_verified=True)
            pass
        
        with_photo = self.request.GET.get('with_photo')
        if with_photo:
            filters &= (Q(photo1__isnull=False) | Q(photo2__isnull=False) | 
                       Q(photo3__isnull=False) | Q(photo4__isnull=False) | 
                       Q(photo5__isnull=False))
        
        # Apply filters
        queryset = queryset.filter(filters)
        
        # Apply sorting
        sort_by = self.request.GET.get('sort', 'newest')
        
        if sort_by == 'newest':
            queryset = queryset.order_by('-created_on')  # Using created_on instead of created_at
        elif sort_by == 'oldest':
            queryset = queryset.order_by('created_on')   # Using created_on
        elif sort_by == 'updated':
            queryset = queryset.order_by('-updated_on')  # Using updated_on
        elif sort_by == 'age_low':
            queryset = queryset.order_by('-dob')  # Younger first (recent birth dates)
        elif sort_by == 'age_high':
            queryset = queryset.order_by('dob')   # Older first
        elif sort_by == 'income_high':
            queryset = queryset.order_by('-annual_income')
        elif sort_by == 'income_low':
            queryset = queryset.order_by('annual_income')
        elif sort_by == 'name_asc':
            queryset = queryset.order_by('full_name')
        elif sort_by == 'name_desc':
            queryset = queryset.order_by('-full_name')
        elif sort_by == 'random':
            # Convert to list and shuffle for random order
            queryset = list(queryset)
            random.shuffle(queryset)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get filter choices from database
        context['religion_choices'] = Profile.objects.exclude(religion='').values_list('religion', flat=True).distinct().order_by('religion')
        context['caste_choices'] = Profile.objects.exclude(caste='').values_list('caste', flat=True).distinct().order_by('caste')
        context['sub_caste_choices'] = Profile.objects.exclude(sub_caste='').values_list('sub_caste', flat=True).distinct().order_by('sub_caste')
        context['gothram_choices'] = Profile.objects.exclude(gothram='').values_list('gothram', flat=True).distinct().order_by('gothram')
        context['rasi_choices'] = Profile.objects.exclude(rasi='').values_list('rasi', flat=True).distinct().order_by('rasi')
        context['nakshatra_choices'] = Profile.objects.exclude(nakshatra='').values_list('nakshatra', flat=True).distinct().order_by('nakshatra')
        context['city_choices'] = Profile.objects.exclude(city='').values_list('city', flat=True).distinct().order_by('city')
        context['state_choices'] = Profile.objects.exclude(state='').values_list('state', flat=True).distinct().order_by('state')
        context['country_choices'] = Profile.objects.exclude(country='').values_list('country', flat=True).distinct().order_by('country')
        context['complexion_choices'] = Profile.objects.exclude(complexion='').values_list('complexion', flat=True).distinct().order_by('complexion')
        
        # Preserve filter values
        context['filters'] = self.request.GET.dict()
        
        # Add ages to profiles
        today = date.today()
        profiles_with_age = []
        for profile in context['profiles']:
            if profile.dob:
                age = today.year - profile.dob.year - ((today.month, today.day) < (profile.dob.month, profile.dob.day))
                profile.age = age
            else:
                profile.age = None
            profiles_with_age.append(profile)
        
        context['profiles'] = profiles_with_age
        context['total_count'] = len(self.get_queryset()) if isinstance(self.get_queryset(), list) else self.get_queryset().count()
        
        return context

@method_decorator(login_required, name='dispatch')
class ProfileCompletionView(TemplateView):
    template_name = "website/profile_completion.html"
    
    def get(self, request, *args, **kwargs):
        # Check if user already has a profile
        if hasattr(request.user, 'profiles') and request.user.profiles.exists():
            # User already has profile, mark as completed
            request.user.is_profile_completed = True
            request.user.save()
            
            # Check if already paid
            if request.user.has_paid:
                return redirect('mck_website:dashboard')
            else:
                return redirect('mck_website:payment_gateway')
        
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        # Get or create profile
        profile, created = Profile.objects.get_or_create(
            user=request.user,
            defaults={
                'full_name': request.POST.get('full_name', ''),
                'gender': request.POST.get('gender', ''),
                'phone': request.POST.get('phone', ''),
                # ... map other fields
            }
        )
        
        if not created:
            # Update existing profile
            profile.full_name = request.POST.get('full_name', profile.full_name)
            profile.gender = request.POST.get('gender', profile.gender)
            profile.phone = request.POST.get('phone', profile.phone)
            # ... update other fields
            profile.save()
        
        # Mark profile as completed
        request.user.is_profile_completed = True
        request.user.save()
        
        messages.success(request, "Profile completed! Please proceed to payment.")
        return redirect('mck_website:payment_gateway')

import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.utils import timezone
import json


logger = logging.getLogger(__name__)
class PaymentGatewayView(LoginRequiredMixin, TemplateView):
    template_name = "website/payment_gateway.html"
    login_url = '/auth/website/login/'
    
    def get(self, request, *args, **kwargs):
        try:
            # Check if already paid
            if request.user.has_paid:
                messages.info(request, "You have already completed your payment. Welcome to your dashboard!")
                return redirect('mck_website:home_page')
            
            # Get profile
            profile = request.user.profiles.first()
            
            # If no profile, redirect to profile completion
            if not profile:
                messages.warning(request, "Please complete your profile first.")
                return redirect('mck_website:profile_completion')
            
            # Check for existing completed payment (double-check)
            if request.user.payments.filter(status='COMPLETED').exists():
                messages.info(request, "You have already completed your payment.")
                return redirect('mck_website:home_page')
            
            # Check for existing pending payment
            existing_payment = Payment.objects.filter(
                user=request.user,
                status='PENDING'
            ).first()
            
            if existing_payment:
                # Use existing pending order
                razorpay_order_id = existing_payment.order_id
                order_amount = int(existing_payment.amount * 100)  # Convert to paise
                logger.info(f"Using existing pending order: {razorpay_order_id}")
            else:
                # Initialize Razorpay client
                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                
                # Create Razorpay order - ₹999 in paise
                order_amount = 99900  # ₹999 in paise
                order_currency = 'INR'
                order_receipt = f"receipt_{request.user.id}_{int(timezone.now().timestamp())}"
                
                # Create order in Razorpay
                razorpay_order = client.order.create({
                    'amount': order_amount,
                    'currency': order_currency,
                    'receipt': order_receipt,
                    'payment_capture': 1,
                    'notes': {
                        'user_id': str(request.user.id),
                        'email': request.user.email,
                        'name': profile.full_name or request.user.get_full_name()
                    }
                })
                
                logger.info(f"✅ Razorpay order created: {razorpay_order['id']}")
                
                # Create payment with temporary payment_id
                temp_payment_id = f"PENDING_{razorpay_order['id']}_{int(timezone.now().timestamp())}"
                
                # Save order to database
                payment = Payment.objects.create(
                    user=request.user,
                    profile=profile,
                    order_id=razorpay_order['id'],
                    payment_id=temp_payment_id,  # Temporary unique ID
                    amount=order_amount / 100,  # Convert to rupees for storage
                    currency='INR',
                    status='PENDING',
                    payment_method='RAZORPAY',
                    response_data=dict(razorpay_order)
                )
                
                razorpay_order_id = razorpay_order['id']
            
            # Prepare context
            context = super().get_context_data(**kwargs)
            context.update({
                'razorpay_key': settings.RAZORPAY_KEY_ID,
                'order_id': razorpay_order_id,
                'amount': order_amount,  # In paise for Razorpay
                'amount_in_rupees': order_amount / 100,  # For display
                'user_name': profile.full_name or request.user.get_full_name() or request.user.email,
                'user_email': request.user.email,
                'user_phone': profile.phone or '',
                'debug': settings.DEBUG,
                'payment_success_url': reverse('mck_website:payment_success'),
                'payment_failure_url': reverse('mck_website:payment_failure'),
                'success_page_url': reverse('mck_website:payment_success_page'),
                'home_page_url': reverse('mck_website:home_page')
            })
            
            # Debug print
            print("\n" + "="*50)
            print("✅ PAYMENT GATEWAY LOADED")
            print(f"Order ID: {razorpay_order_id}")
            print(f"Amount: ₹{order_amount/100}")
            print(f"Key: {settings.RAZORPAY_KEY_ID[:10]}...")
            print(f"Success URL: {reverse('mck_website:payment_success')}")
            print(f"Success Page URL: {reverse('mck_website:payment_success_page')}")
            print("="*50 + "\n")
            
            return render(request, self.template_name, context)
            
        except razorpay.errors.BadRequestError as e:
            logger.error(f"❌ Razorpay BadRequestError: {str(e)}")
            messages.error(request, "Payment gateway configuration error. Please check your Razorpay keys.")
            return redirect('mck_website:profile_page')
            
        except Exception as e:
            logger.error(f"❌ Payment gateway error: {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(request, f"Unable to initialize payment. Please try again later.")
            return redirect('mck_website:profile_page')


@method_decorator(csrf_exempt, name='dispatch')
class PaymentCallbackView(TemplateView):
    template_name = "website/payment_callback.html"
    
    def post(self, request, *args, **kwargs):
        # Similar verification logic as above
        try:
            razorpay_payment_id = request.POST.get('razorpay_payment_id')
            razorpay_order_id = request.POST.get('razorpay_order_id')
            razorpay_signature = request.POST.get('razorpay_signature')
            
            payment = Payment.objects.get(order_id=razorpay_order_id)
            
            # Verify signature
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            
            client.utility.verify_payment_signature(params_dict)
            
            # Update payment and user
            payment.mark_completed(razorpay_payment_id, razorpay_signature)
            payment.user.has_paid = True
            payment.user.save()
            
            messages.success(request, "Payment successful! Welcome to your dashboard.")
            return redirect('mck_website:dashboard')  # or home page
            
        except Exception as e:
            messages.error(request, f"Payment verification failed: {str(e)}")
            return redirect('mck_website:payment_failure')

# In mck_website/views.py, add this if it doesn't exist


import razorpay
import json
import logging
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.views import View
from django.utils import timezone



logger = logging.getLogger(__name__)
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class PaymentSuccessView(View):
    """Handle payment success callback from Razorpay"""
    
    def get(self, request, *args, **kwargs):
        # Handle GET request - show success page if user has paid
        if request.user.is_authenticated and request.user.has_paid:
            return redirect('mck_website:payment_success_page')
        return redirect('mck_website:payment_gateway')
    
    def post(self, request, *args, **kwargs):
        try:
            # Log the raw request for debugging
            print("\n" + "="*50)
            print("PAYMENT SUCCESS CALLBACK RECEIVED")
            print(f"POST data: {request.POST}")
            print("="*50 + "\n")
            
            # Get payment details from Razorpay
            razorpay_payment_id = request.POST.get('razorpay_payment_id')
            razorpay_order_id = request.POST.get('razorpay_order_id')
            razorpay_signature = request.POST.get('razorpay_signature')
            
            # Check for undefined values (happens when payment wasn't completed)
            if razorpay_payment_id == 'undefined' or razorpay_order_id == 'undefined':
                print("❌ Payment was not completed properly")
                
                # Check if user is authenticated
                if request.user.is_authenticated:
                    # Check if user already has a completed payment
                    if request.user.has_paid:
                        return JsonResponse({
                            'status': 'success',
                            'message': 'Payment already completed',
                            'redirect_url': reverse('mck_website:payment_success_page')
                        })
                    
                    # Try to find any pending payment
                    pending_payment = request.user.payments.filter(status='PENDING').first()
                    if pending_payment:
                        # Use the pending payment's order_id
                        razorpay_order_id = pending_payment.order_id
                        print(f"Using pending order_id: {razorpay_order_id}")
                    else:
                        return JsonResponse({
                            'status': 'failed',
                            'message': 'Payment was not completed. Please try again.'
                        }, status=400)
                else:
                    return JsonResponse({
                        'status': 'failed',
                        'message': 'Payment was not completed. Please try again.'
                    }, status=400)
            
            # Validate required fields
            if not all([razorpay_payment_id, razorpay_order_id, razorpay_signature]) and razorpay_payment_id != 'undefined':
                return JsonResponse({
                    'status': 'failed',
                    'message': 'Missing required payment details'
                }, status=400)
            
            # Find the payment record by order_id
            try:
                payment = Payment.objects.get(order_id=razorpay_order_id)
                print(f"✅ Found payment record: {payment.id}")
            except Payment.DoesNotExist:
                print(f"❌ Payment record not found for order: {razorpay_order_id}")
                
                # Try to find payment by user if order_id not found
                if request.user.is_authenticated:
                    payment = Payment.objects.filter(
                        user=request.user,
                        status='PENDING'
                    ).first()
                    
                    if payment:
                        print(f"✅ Found pending payment for user: {payment.order_id}")
                        # Update the order_id to match what Razorpay sent
                        payment.order_id = razorpay_order_id
                        payment.save()
                    else:
                        return JsonResponse({
                            'status': 'failed',
                            'message': 'Payment record not found'
                        }, status=404)
                else:
                    return JsonResponse({
                        'status': 'failed',
                        'message': 'Payment record not found'
                    }, status=404)
            
            # If payment_id is 'undefined', we need to handle it specially
            if razorpay_payment_id == 'undefined':
                # This might be a test payment or already processed
                if payment.status == 'COMPLETED':
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Payment already completed',
                        'redirect_url': reverse('mck_website:payment_success_page')
                    })
                
                # For test mode, we can mark as completed with a dummy payment_id
                if settings.DEBUG:
                    dummy_payment_id = f"TEST_{razorpay_order_id}_{int(timezone.now().timestamp())}"
                    payment.mark_completed(dummy_payment_id, razorpay_signature or 'test_signature')
                    print(f"✅ Test payment marked as completed: {payment.id}")
                    
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Test payment completed successfully',
                        'redirect_url': reverse('mck_website:payment_success_page')
                    })
            
            # Verify signature with Razorpay (skip for test mode with undefined values)
            if razorpay_payment_id != 'undefined' and razorpay_signature != 'undefined':
                try:
                    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                    
                    params_dict = {
                        'razorpay_order_id': razorpay_order_id,
                        'razorpay_payment_id': razorpay_payment_id,
                        'razorpay_signature': razorpay_signature
                    }
                    
                    # Verify payment signature
                    client.utility.verify_payment_signature(params_dict)
                    print(f"✅ Signature verified for payment: {razorpay_payment_id}")
                    
                except razorpay.errors.SignatureVerificationError as e:
                    print(f"❌ Signature verification failed: {str(e)}")
                    # In test mode, we might still want to proceed
                    if not settings.DEBUG:
                        return JsonResponse({
                            'status': 'failed',
                            'message': 'Payment signature verification failed'
                        }, status=400)
            
            # Mark payment as completed
            if payment.status != 'COMPLETED':
                payment.mark_completed(razorpay_payment_id, razorpay_signature)
                print(f"✅ Payment marked as completed: {payment.id}")
            
            # Store payment success in session
            request.session['payment_success'] = True
            request.session['payment_id'] = razorpay_payment_id
            request.session['payment_completed'] = True
            
            # Return success with redirect URL
            response_data = {
                'status': 'success',
                'message': 'Payment verified successfully',
                'redirect_url': reverse('mck_website:payment_success_page')
            }
            print(f"✅ Sending response: {response_data}")
            
            return JsonResponse(response_data)
            
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return JsonResponse({
                'status': 'failed',
                'message': str(e)
            }, status=500)
            
class PaymentSuccessPageView(LoginRequiredMixin, TemplateView):
    """Display payment success page after successful payment"""
    template_name = "website/payment_success.html"
    
    def get(self, request, *args, **kwargs):
        # Check if user has actually paid
        if not request.user.has_paid:
            messages.warning(request, "No payment record found. Please complete payment first.")
            return redirect('mck_website:payment_gateway')
        
        context = self.get_context_data(**kwargs)
        context['payment_success'] = True
        context['message'] = 'Payment completed successfully!'
        
        # Get payment details
        payment = request.user.payments.filter(status='COMPLETED').first()
        if payment:
            context['payment'] = payment
            context['payment_id'] = payment.payment_id
            context['amount'] = payment.amount
            context['payment_date'] = payment.payment_date
        
        return render(request, self.template_name, context)


@method_decorator(csrf_exempt, name='dispatch')
class PaymentFailureView(View):
    """Handle payment failure callback from Razorpay"""
    
    def post(self, request, *args, **kwargs):
        razorpay_order_id = request.POST.get('razorpay_order_id')
        error_description = request.POST.get('error_description', 'Payment failed')
        error_code = request.POST.get('error_code', '')
        
        print(f"❌ Payment failed: {error_description} (Code: {error_code})")
        
        try:
            # Find the payment record
            payment = Payment.objects.get(order_id=razorpay_order_id)
            
            # Mark payment as failed
            error_message = f"{error_description} ({error_code})" if error_code else error_description
            payment.mark_failed(error_message)
            
            return JsonResponse({
                'status': 'failed',
                'message': 'Payment recorded as failed'
            })
            
        except Payment.DoesNotExist:
            print(f"Payment record not found for order: {razorpay_order_id}")
            return JsonResponse({
                'status': 'failed',
                'message': 'Payment recorded as failed'
            })
        except Exception as e:
            print(f"Error recording payment failure: {str(e)}")
            return JsonResponse({
                'status': 'failed',
                'message': 'Payment failed'
            })