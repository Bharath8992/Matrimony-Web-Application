"""
Views - mck Master App
"""


import json
import sys
from django.shortcuts import render 
from django.views.generic import TemplateView, View
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.generic.base import RedirectView
from django.contrib.auth import logout as auth_logout
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from config import app_logger
from config import app_seo as seo
from config import settings
from mck_auth import build_table as bt
from mck_auth import role_validations as rv
from mck_master import api
from mck_master import forms
from datetime import datetime
from datetime import date, datetime
from mck_master.models import Profile, Payment  # ✅ add Payment here

LOG_NAME = "app"
logger = app_logger.createLogger(LOG_NAME)


@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class SupportPageContentList(TemplateView):
    template_name = "table_data_list.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs']= seo.get_page_tags("SupportPageContentList")
        has_permission, accountuser = rv.validate_requested_user_function(request)
        if not has_permission: return render(request, "access_denied.html", context)
        context['table_data'] = bt.build_support_page_content_table(request)
        return render(request, self.template_name, context)
    
    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, *args, **kwargs):
        context = dict()
        try:
            context['page_kwargs'] = seo.get_page_tags("SupportPageContentList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            table_data = bt.build_support_page_content_table(request)
            context['table_data'] = table_data
            result, msg, data = api.support_page_content_load_data(request, table_data)
            return HttpResponse(json.dumps(data))
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return HttpResponse(json.dumps(context))


@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class SupportPageContentCreateView(TemplateView):

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = dict()
        try:
            template_name = "common_cu.html"
            context['name'] = "Support Page Content"
            context['page_kwargs'] = seo.get_page_tags("SupportPageContentList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            form = forms.SupportPageContentCreateUpdateForm()
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
            context['name'] = "Support Page Content"
            context['page_kwargs'] = seo.get_page_tags("SupportPageContentList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            form = forms.SupportPageContentCreateUpdateForm(request.POST, request.FILES)
            logger.debug(request.POST)
            if form.is_valid():
                result, msg, data = api.support_page_content_create_update(request)
                logger.debug(data)
                return HttpResponseRedirect(reverse("mck_auth:mck_support_page_content_list"))
            else:
                context['form'] = form
                logger.warning(form.errors)
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)


@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class SupportPageContentUpdateView(TemplateView):

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, id=None, *args, **kwargs):
        context = dict()
        try:
            mode = "edit"
            template_name = "common_cu.html"
            context['name'] = "Support Page Content"
            context['page_kwargs'] = seo.get_page_tags("SupportPageContentList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            context['mode'] = mode
            result, msg, data = api.support_page_content_retrieve_data(request, id)
            form = forms.SupportPageContentCreateUpdateForm(instance=data.get("support_page_content"), mode=mode)
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
            context['name'] = "Support Page Content"
            context['page_kwargs'] = seo.get_page_tags("SupportPageContentList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            result, msg, data = api.support_page_content_retrieve_data(request, id)
            form = forms.SupportPageContentCreateUpdateForm(request.POST, request.FILES, mode=mode)
            if form.is_valid():
                result, msg, data = api.support_page_content_create_update(request, id, mode)
                return HttpResponseRedirect(reverse("mck_auth:mck_support_page_content_list"))
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
class SupportPageContentDeleteView(TemplateView):

    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, id=None, *args, **kwargs):
        context = dict()
        try:
            template_name = "support_page_content_cu.html"
            context['page_kwargs'] = seo.get_page_tags("SupportPageContentList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            result, msg = api.support_page_content_update_status(request, id)
            return JsonResponse(dict(result=result))
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)



@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class CategoryList(TemplateView):
    template_name = "table_data_list.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs']= seo.get_page_tags("CategoryList")
        has_permission, accountuser = rv.validate_requested_user_function(request)
        if not has_permission: return render(request, "access_denied.html", context)
        context['table_data'] = bt.build_category_table(request)
        return render(request, self.template_name, context)
    
    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, *args, **kwargs):
        context = dict()
        try:
            context['page_kwargs'] = seo.get_page_tags("CategoryList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            table_data = bt.build_category_table(request)
            context['table_data'] = table_data
            result, msg, data = api.category_load_data(request, table_data)
            return HttpResponse(json.dumps(data))
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return HttpResponse(json.dumps(context))


@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class CategoryCreateView(TemplateView):

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = dict()
        try:
            template_name = "common_cu.html"
            context['name'] = "Category"
            context['page_kwargs'] = seo.get_page_tags("CategoryList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            form = forms.CategoryCreateUpdateForm()
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
            context['name'] = "Category"
            context['page_kwargs'] = seo.get_page_tags("CategoryList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            form = forms.CategoryCreateUpdateForm(request.POST, request.FILES)
            logger.debug(request.POST)
            if form.is_valid():
                result, msg, data = api.category_create_update(request)
                logger.debug(data)
                return HttpResponseRedirect(reverse("mck_master:mck_category_list"))
            else:
                context['form'] = form
                logger.warning(form.errors)
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)


@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class CategoryUpdateView(TemplateView):

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, id=None, *args, **kwargs):
        context = dict()
        try:
            mode = "edit"
            template_name = "common_cu.html"
            context['name'] = "Category"
            context['page_kwargs'] = seo.get_page_tags("CategoryList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            context['mode'] = mode
            result, msg, data = api.category_retrieve_data(request, id)
            form = forms.CategoryCreateUpdateForm(instance=data.get("category"), mode=mode)
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
            context['name'] = "Category"
            context['page_kwargs'] = seo.get_page_tags("CategoryList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            result, msg, data = api.category_retrieve_data(request, id)
            form = forms.CategoryCreateUpdateForm(request.POST, request.FILES, mode=mode)
            if form.is_valid():
                result, msg, data = api.category_create_update(request, id, mode)
                return HttpResponseRedirect(reverse("mck_master:mck_category_list"))
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
class CategoryDeleteView(TemplateView):

    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, id=None, *args, **kwargs):
        context = dict()
        try:
            template_name = "common_cu.html"
            context['name'] = "Category"
            context['page_kwargs'] = seo.get_page_tags("CategoryList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            result, msg = api.category_update_status(request, id)
            return JsonResponse(dict(result=result))
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)



@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class SubCategoryList(TemplateView):
    template_name = "table_data_list.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs']= seo.get_page_tags("SubCategoryList")
        has_permission, accountuser = rv.validate_requested_user_function(request)
        if not has_permission: return render(request, "access_denied.html", context)
        context['table_data'] = bt.build_sub_category_table(request)
        return render(request, self.template_name, context)
    
    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, *args, **kwargs):
        context = dict()
        try:
            context['page_kwargs'] = seo.get_page_tags("SubCategoryList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            table_data = bt.build_sub_category_table(request)
            context['table_data'] = table_data
            result, msg, data = api.sub_category_load_data(request, table_data)
            return HttpResponse(json.dumps(data))
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return HttpResponse(json.dumps(context))


@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class SubCategoryCreateView(TemplateView):

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = dict()
        try:
            template_name = "common_cu.html"
            context['name'] = "SubCategory"
            context['page_kwargs'] = seo.get_page_tags("SubCategoryList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            form = forms.SubCategoryCreateUpdateForm()
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
            context['name'] = "SubCategory"
            context['page_kwargs'] = seo.get_page_tags("SubCategoryList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            form = forms.SubCategoryCreateUpdateForm(request.POST, request.FILES)
            logger.debug(request.POST)
            if form.is_valid():
                result, msg, data = api.sub_category_create_update(request)
                logger.debug(data)
                return HttpResponseRedirect(reverse("mck_master:mck_sub_category_list"))
            else:
                context['form'] = form
                logger.warning(form.errors)
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)


@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class SubCategoryUpdateView(TemplateView):

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, id=None, *args, **kwargs):
        context = dict()
        try:
            mode = "edit"
            template_name = "common_cu.html"
            context['name'] = "SubCategory"
            context['page_kwargs'] = seo.get_page_tags("SubCategoryList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            context['mode'] = mode
            result, msg, data = api.sub_category_retrieve_data(request, id)
            form = forms.SubCategoryCreateUpdateForm(instance=data.get("sub_category"), mode=mode)
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
            context['name'] = "SubCategory"
            context['page_kwargs'] = seo.get_page_tags("SubCategoryList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            result, msg, data = api.sub_category_retrieve_data(request, id)
            form = forms.SubCategoryCreateUpdateForm(request.POST, request.FILES, mode=mode)
            if form.is_valid():
                result, msg, data = api.sub_category_create_update(request, id, mode)
                return HttpResponseRedirect(reverse("mck_master:mck_sub_category_list"))
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
class SubCategoryDeleteView(TemplateView):

    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, id=None, *args, **kwargs):
        context = dict()
        try:
            template_name = "sub_category_cu.html"
            context['page_kwargs'] = seo.get_page_tags("SubCategoryList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            result, msg = api.sub_category_update_status(request, id)
            return JsonResponse(dict(result=result))
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)


@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class CategoryBasedSubCategoryAjax(View):
    template_name = "table_data_list.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        result, message, sub_category_list = api.ajax_category_based_sub_category(request)
        return JsonResponse(dict(result=result, message=message, sub_category_list=sub_category_list))


@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class BannerList(TemplateView):
    template_name = "table_data_list.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs']= seo.get_page_tags("BannerList")
        has_permission, accountuser = rv.validate_requested_user_function(request)
        if not has_permission: return render(request, "access_denied.html", context)
        context['table_data'] = bt.build_banner_table(request)
        return render(request, self.template_name, context)
    
    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, *args, **kwargs):
        context = dict()
        try:
            context['page_kwargs'] = seo.get_page_tags("BannerList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            table_data = bt.build_banner_table(request)
            context['table_data'] = table_data
            result, msg, data = api.banner_load_data(request, table_data)
            return HttpResponse(json.dumps(data))
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return HttpResponse(json.dumps(context))


@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class BannerCreateView(TemplateView):

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = dict()
        try:
            template_name = "common_cu.html"
            context['name'] = "Banner"
            context['page_kwargs'] = seo.get_page_tags("BannerList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            form = forms.BannerCreateUpdateForm()
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
            context['name'] = "Banner"
            context['page_kwargs'] = seo.get_page_tags("BannerList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            form = forms.BannerCreateUpdateForm(request.POST, request.FILES)
            logger.debug(request.POST)
            if form.is_valid():
                result, msg, data = api.banner_create_update(request)
                logger.debug(data)
                return HttpResponseRedirect(reverse("mck_master:mck_banner_list"))
            else:
                context['form'] = form
                logger.warning(form.errors)
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)


@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class BannerUpdateView(TemplateView):

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, id=None, *args, **kwargs):
        context = dict()
        try:
            mode = "edit"
            template_name = "common_cu.html"
            context['name'] = "Banner"
            context['page_kwargs'] = seo.get_page_tags("BannerList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            context['mode'] = mode
            result, msg, data = api.banner_retrieve_data(request, id)
            form = forms.BannerCreateUpdateForm(instance=data.get("banner"), mode=mode)
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
            context['name'] = "Banner"
            context['page_kwargs'] = seo.get_page_tags("BannerList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            result, msg, data = api.banner_retrieve_data(request, id)
            form = forms.BannerCreateUpdateForm(request.POST, request.FILES, mode=mode)
            if form.is_valid():
                result, msg, data = api.banner_create_update(request, id, mode)
                return HttpResponseRedirect(reverse("mck_master:mck_banner_list"))
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
class BannerDeleteView(TemplateView):

    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, id=None, *args, **kwargs):
        context = dict()
        try:
            template_name = "common_cu.html"
            context['name'] = "Banner"
            context['page_kwargs'] = seo.get_page_tags("BannerList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            result, msg = api.banner_update_status(request, id)
            return JsonResponse(dict(result=result))
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)


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
                return HttpResponseRedirect(reverse("mck_master:mck_gallery_list"))
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
                return HttpResponseRedirect(reverse("mck_master:mck_gallery_list"))
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
            template_name = "gallery_cu.html"
            context['page_kwargs'] = seo.get_page_tags("GalleryList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            result, msg = api.gallery_update_status(request, id)
            return JsonResponse(dict(result=result))
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)


#state
@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class StateList(TemplateView):
    template_name = "table_data_list.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("StateList")

        has_permission, accountuser = rv.validate_requested_user_function(request)
        if not has_permission:
            return render(request, "access_denied.html", context)

        context['table_data'] = bt.build_state_table(request)
        return render(request, self.template_name, context)

    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, *args, **kwargs):
        context = {
            'page_kwargs': seo.get_page_tags("StateList")
        }

        has_permission, accountuser = rv.validate_requested_user_function(request)
        if not has_permission:
            return render(request, "access_denied.html", context)

        try:
            table_data = bt.build_state_table(request)
            context['table_data'] = table_data
            result, msg, data = api.state_load_data(request, table_data)
            return JsonResponse(data, safe=False)
        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class StateCreateView(TemplateView):
    template_name = "common_cu.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = {
            'name': "State",
            'page_kwargs': seo.get_page_tags("StateList"),
        }

        has_permission, accountuser = rv.validate_requested_user_function(request)
        if not has_permission:
            return render(request, "access_denied.html", context)

        form = forms.StateCreateUpdateForm()
        context['form'] = form
        return render(request, self.template_name, context)

    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, *args, **kwargs):
        context = {
            'name': "State",
            'page_kwargs': seo.get_page_tags("StateList"),
        }

        has_permission, accountuser = rv.validate_requested_user_function(request)
        if not has_permission:
            return render(request, "access_denied.html", context)

        form = forms.StateCreateUpdateForm(request.POST, request.FILES)
        if form.is_valid():
            result, msg, data = api.state_create_update(request)
            return HttpResponseRedirect(reverse("mck_master:mck_state_list"))
        else:
            context['form'] = form
            logger.warning(form.errors)

        return render(request, self.template_name, context)


@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class StateUpdateView(TemplateView):

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, id=None, *args, **kwargs):
        context = dict()
        try:
            mode = "edit"
            template_name = "common_cu.html"
            context['name'] = "State"
            context['page_kwargs'] = seo.get_page_tags("StateList")
            
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission:
                return render(request, "access_denied.html", context)

            context['mode'] = mode
            result, msg, data = api.state_retrieve_data(request, id)
           
            form = forms.StateCreateUpdateForm(instance=data.get("state"), mode=mode)
            context['form'] = form
            context['data'] = data
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error(f'Error at {exc_traceback.tb_lineno}: {e}')
            context['error_message'] = "An error occurred while retrieving data."
        
        return render(request, template_name, context)

    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, id=None, mode=None, *args, **kwargs):
        context = dict()
        try:
            mode = "edit"
            template_name = "common_cu.html"
            context['name'] = "State"
            context['page_kwargs'] = seo.get_page_tags("StateList")
            
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission:
                return render(request, "access_denied.html", context)

            form = forms.StateCreateUpdateForm(request.POST, request.FILES, mode=mode)
            if form.is_valid():
                result, msg, data = api.state_create_update(request, id, mode)
                return HttpResponseRedirect(reverse("mck_master:mck_state_list"))
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
class StateDeleteView(TemplateView):
    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, id=None, *args, **kwargs):
        context = {
            'page_kwargs': seo.get_page_tags("StateList")
        }

        has_permission, accountuser = rv.validate_requested_user_function(request)
        if not has_permission:
            return render(request, "access_denied.html", context)

        result, msg = api.state_update_status(request, id)
        return JsonResponse({'result': result})


#city
@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class CityList(TemplateView):
    template_name = "table_data_list.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("CityList")
        
        has_permission, accountuser = rv.validate_requested_user_function(request)
        if not has_permission:
            return render(request, "access_denied.html", context)
        
        context['table_data'] = bt.build_city_table(request)
        return render(request, self.template_name, context)

    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, *args, **kwargs):
        context = {
            'page_kwargs': seo.get_page_tags("CityList")
        }

        has_permission, accountuser = rv.validate_requested_user_function(request)
        if not has_permission:
            return render(request, "access_denied.html", context)

        try:
            table_data = bt.build_city_table(request)
            context['table_data'] = table_data
            result, msg, data = api.city_load_data(request, table_data)
            return JsonResponse(data, safe=False)
        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class CityCreateView(TemplateView):
    template_name = "common_cu.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = {
            'name': "City",
            'page_kwargs': seo.get_page_tags("CityList"),
        }

        has_permission, accountuser = rv.validate_requested_user_function(request)
        if not has_permission:
            return render(request, "access_denied.html", context)

        form = forms.CityCreateUpdateForm()
        context['form'] = form
        return render(request, self.template_name, context)

    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, *args, **kwargs):
        context = {
            'name': "City",
            'page_kwargs': seo.get_page_tags("CityList"),
        }

        has_permission, accountuser = rv.validate_requested_user_function(request)
        if not has_permission:
            return render(request, "access_denied.html", context)

        form = forms.CityCreateUpdateForm(request.POST, request.FILES)
        if form.is_valid():
            result, msg, data = api.city_create_update(request)
            return HttpResponseRedirect(reverse("mck_master:mck_city_list"))
        else:
            context['form'] = form
            logger.warning(form.errors)
        
        return render(request, self.template_name, context)


@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class CityUpdateView(TemplateView):

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, id=None, *args, **kwargs):
        context = dict()
        try:
            mode = "edit"
            template_name = "common_cu.html"
            context['name'] = "City"
            context['page_kwargs'] = seo.get_page_tags("CityList")
            
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission:
                return render(request, "access_denied.html", context)

            context['mode'] = mode
            result, msg, data = api.city_retrieve_data(request, id)
           
            form = forms.CityCreateUpdateForm(instance=data.get("city"), mode=mode)
            context['form'] = form
            context['data'] = data
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error(f'Error at {exc_traceback.tb_lineno}: {e}')
            context['error_message'] = "An error occurred while retrieving data."
        
        return render(request, template_name, context)

    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, id=None, mode=None, *args, **kwargs):
        context = dict()
        try:
            mode = "edit"
            template_name = "common_cu.html"
            context['name'] = "City"
            context['page_kwargs'] = seo.get_page_tags("CityList")
            
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission:
                return render(request, "access_denied.html", context)

            form = forms.CityCreateUpdateForm(request.POST, request.FILES, mode=mode)
            if form.is_valid():
                result, msg, data = api.city_create_update(request, id, mode)
                return HttpResponseRedirect(reverse("mck_master:mck_city_list"))
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
class CityDeleteView(TemplateView):
    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, id=None, *args, **kwargs):
        context = {
            'page_kwargs': seo.get_page_tags("CityList")
        }

        has_permission, accountuser = rv.validate_requested_user_function(request)
        if not has_permission:
            return render(request, "access_denied.html", context)

        result, msg = api.city_update_status(request, id)
        return JsonResponse({'result': result})


@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class OfferList(TemplateView):
    template_name = "table_data_list.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("OfferList")
        has_permission, accountuser = rv.validate_requested_user_function(request)
        if not has_permission: return render(request, "access_denied.html", context)
        context['table_data'] = bt.build_offer_table(request)
        return render(request, self.template_name, context)

    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, *args, **kwargs):
        context = dict()
        try:
            context['page_kwargs'] = seo.get_page_tags("OfferList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            table_data = bt.build_offer_table(request)
            context['table_data'] = table_data
            result, msg, data = api.offer_load_data(request, table_data)
            return HttpResponse(json.dumps(data))
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return HttpResponse(json.dumps(context))

@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class OfferCreateView(TemplateView):

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = dict()
        try:
            template_name = "common_cu.html"
            context['name'] = "Offer"
            context['page_kwargs'] = seo.get_page_tags("OfferList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            form = forms.OfferCreateUpdateForm()
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
            context['name'] = "Offer"
            context['page_kwargs'] = seo.get_page_tags("OfferList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            form = forms.OfferCreateUpdateForm(request.POST, request.FILES)
            logger.debug(request.POST)
            if form.is_valid():
                result, msg, data = api.offer_create_update(request)
                logger.debug(data)
                return HttpResponseRedirect(reverse("mck_master:mck_offer_list"))
            else:
                context['form'] = form
                logger.warning(form.errors)
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)

@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class OfferUpdateView(TemplateView):

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, id=None, *args, **kwargs):
        context = dict()
        try:
            mode = "edit"
            template_name = "common_cu.html"
            context['name'] = "Offer"
            context['page_kwargs'] = seo.get_page_tags("OfferList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            context['mode'] = mode
            result, msg, data = api.offer_retrieve_data(request, id)
            form = forms.OfferCreateUpdateForm(instance=data.get("offer"), mode=mode)
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
            context['name'] = "Offer"
            context['page_kwargs'] = seo.get_page_tags("OfferList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            result, msg, data = api.offer_retrieve_data(request, id)
            form = forms.OfferCreateUpdateForm(request.POST, request.FILES, mode=mode)
            if form.is_valid():
                result, msg, data = api.offer_create_update(request, id, mode)
                return HttpResponseRedirect(reverse("mck_master:mck_offer_list"))
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
class OfferDeleteView(TemplateView):

    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, id=None, *args, **kwargs):
        context = dict()
        try:
            template_name = "offer_cu.html"
            context['page_kwargs'] = seo.get_page_tags("OfferList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            result, msg = api.offer_update_status(request, id)
            return JsonResponse(dict(result=result))
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)

@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class ClientFeedbackList(TemplateView):
    template_name = "table_data_list.html"
    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("ClientFeedbackList")
        has_permission, accountuser = rv.validate_requested_user_function(request)
        if not has_permission: return render(request, "access_denied.html", context)
        context['table_data'] = bt.build_client_feedback_table(request)
        return render(request, self.template_name, context)
    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, *args, **kwargs):
        context = dict()
        try:
            context['page_kwargs'] = seo.get_page_tags("ClientFeedbackList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            table_data = bt.build_client_feedback_table(request)
            context['table_data'] = table_data
            result, msg, data = api.clientfeedback_load_data(request, table_data)
            return HttpResponse(json.dumps(data))
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return HttpResponse(json.dumps(context))
@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class ClientFeedbackCreateView(TemplateView):
    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = dict()
        try:
            template_name = "common_cu.html"
            context['name'] = "Client Feedback"
            context['page_kwargs'] = seo.get_page_tags("ClientFeedbackList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            form = forms.ClientFeedbackCreateUpdateForm()
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
            context['name'] = "Client Feedback"
            context['page_kwargs'] = seo.get_page_tags("ClientFeedbackList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            form = forms.ClientFeedbackCreateUpdateForm(request.POST, request.FILES)
            logger.debug(request.POST)
            if form.is_valid():
                result, msg, data = api.clientfeedback_create_update(request)
                logger.debug(data)
                return HttpResponseRedirect(reverse("mck_master:mck_client_feedback_list"))
            else:
                context['form'] = form
                logger.warning(form.errors)
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)
@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class ClientFeedbackUpdateView(TemplateView):
    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, id=None, *args, **kwargs):
        context = dict()
        try:
            mode = "edit"
            template_name = "common_cu.html"
            context['name'] = "Client Feedback"
            context['page_kwargs'] = seo.get_page_tags("ClientFeedbackList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            context['mode'] = mode
            result, msg, data = api.clientfeedback_retrieve_data(request, id)
            form = forms.ClientFeedbackCreateUpdateForm(instance=data.get("clientfeedback"), mode=mode)
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
            context['name'] = "Client Feedback"
            context['page_kwargs'] = seo.get_page_tags("ClientFeedbackList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            result, msg, data = api.clientfeedback_retrieve_data(request, id)
            form = forms.ClientFeedbackCreateUpdateForm(request.POST, request.FILES, mode=mode)
            if form.is_valid():
                result, msg, data = api.clientfeedback_create_update(request, id, mode)
                return HttpResponseRedirect(reverse("mck_master:mck_client_feedback_list"))
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
class ClientFeedbackDeleteView(TemplateView):
    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, id=None, *args, **kwargs):
        context = dict()
        try:
            template_name = "client_feedback_cu.html"
            context['page_kwargs'] = seo.get_page_tags("ClientFeedbackList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            result, msg = api.clientfeedback_update_status(request, id)
            return JsonResponse(dict(result=result))
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)




@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class ProfileList(TemplateView):
    template_name = "table_data_list.html"
    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("ProfileList")
        has_permission, accountuser = rv.validate_requested_user_function(request)
        if not has_permission: return render(request, "access_denied.html", context)
        context['table_data'] = bt.build_profile_table(request)
        return render(request, self.template_name, context)
    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, *args, **kwargs):
        context = dict()
        try:
            context['page_kwargs'] = seo.get_page_tags("ProfileList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            table_data = bt.build_profile_table(request)
            context['table_data'] = table_data
            result, msg, data = api.profile_load_data(request, table_data)
            return HttpResponse(json.dumps(data))
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return HttpResponse(json.dumps(context))
@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class ProfileCreateView(TemplateView):
    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = dict()
        try:
            template_name = "common_cu.html"
            context['name'] = "Client Feedback"
            context['page_kwargs'] = seo.get_page_tags("ProfileList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission: return render(request, "access_denied.html", context)
            form = forms.ProfileCreateUpdateForm()
            context['form'] = form
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)
    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, id=None, mode=None, *args, **kwargs):
        context = dict()
        template_name = "common_cu.html"
        context['name'] = "Profile"
        context['page_kwargs'] = seo.get_page_tags("ProfileList")
        
        # ✅ Always create the form FIRST, before anything that can fail
        form = forms.ProfileCreateUpdateForm(request.POST, request.FILES)
        context['form'] = form  # ✅ Set in context immediately

        try:
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission:
                return render(request, "access_denied.html", context)

            logger.debug(request.POST)

            if form.is_valid():
                result, msg, data = api.profile_create_update(request)
                logger.debug(data)
                return HttpResponseRedirect(reverse("mck_master:mck_profile_list"))
            else:
                logger.warning(form.errors)

        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))

        # ✅ form is always in context, so template never crashes
        return render(request, template_name, context)
        
@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class ProfileUpdateView(TemplateView):
    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, id=None, *args, **kwargs):
        context = dict()
        try:
            mode = "edit"
            template_name = "common_cu.html"
            context['name'] = "Client Feedback"
            context['page_kwargs'] = seo.get_page_tags("ProfileList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission:
                return render(request, "access_denied.html", context)
            context['mode'] = mode
            result, msg, data = api.profile_retrieve_data(request, id)
            form = forms.ProfileCreateUpdateForm(instance=data.get("profile"), mode=mode)
            context['form'] = form
            context['data'] = data
        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
        return render(request, template_name, context)

    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, id=None, mode=None, *args, **kwargs):
        context = dict()
        template_name = "common_cu.html"
        try:
            mode = "edit"
            context['name'] = "Client Feedback"
            context['page_kwargs'] = seo.get_page_tags("ProfileList")
            has_permission, accountuser = rv.validate_requested_user_function(request)
            if not has_permission:
                return render(request, "access_denied.html", context)

            result, msg, data = api.profile_retrieve_data(request, id)

            # ✅ Pass instance so existing data is retained on validation failure
            form = forms.ProfileCreateUpdateForm(
                request.POST,
                request.FILES,
                instance=data.get("profile"),
                mode=mode
            )
            context['form'] = form   # ✅ Always set form in context before any branching
            context['mode'] = mode
            context['data'] = data

            if form.is_valid():
                result, msg, data = api.profile_create_update(request, id, mode)
                return HttpResponseRedirect(reverse("mck_master:mck_profile_list"))
            else:
                logger.warning(form.errors)

        except Exception as e:
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))

        return render(request, template_name, context)
        
@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class ProfileDeleteView(View):
    """Handle profile delete and restore"""
    
    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, id=None, *args, **kwargs):
        """
        Handle GET requests (for regular browser links with confirmation)
        """
        try:
            if not id:
                messages.error(request, 'Profile ID is required')
                return redirect('mck_master:mck_profile_list')
            
            # Get action from query params (default to 'delete')
            action = request.GET.get('action', 'delete')
            
            # Call the API function
            result, message = api.profile_update_status(request, id, action)
            
            if result:
                if action == 'delete':
                    messages.success(request, 'Profile deleted successfully')
                elif action == 'restore':
                    messages.success(request, 'Profile restored successfully')
                else:
                    messages.success(request, message)
            else:
                messages.error(request, message or 'Failed to update profile')
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            logger.error(f"Error in ProfileDeleteView GET: {str(e)}")
        
        return redirect('mck_master:mck_profile_list')
    
    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, id=None, *args, **kwargs):
        """
        Handle POST requests (for AJAX calls)
        """
        try:
            if not id:
                return JsonResponse({
                    'result': False,
                    'message': 'Profile ID is required'
                })
            
            # Parse JSON data if present
            data = {}
            if request.body:
                try:
                    data = json.loads(request.body)
                except json.JSONDecodeError:
                    pass
            
            # Get action from request (default to 'delete')
            action = data.get('action', request.POST.get('action', 'delete'))
            
            # Call the API function
            result, message = api.profile_update_status(request, id, action)
            
            return JsonResponse({
                'result': result,
                'message': message
            })
            
        except Profile.DoesNotExist:
            return JsonResponse({
                'result': False,
                'message': 'Profile not found'
            })
        except Exception as e:
            logger.error(f"Error in ProfileDeleteView POST: {str(e)}")
            return JsonResponse({
                'result': False,
                'message': str(e)
            })
@method_decorator(login_required(login_url=settings.LOGIN_REDIRECT_URL), name='dispatch')
class ProfileDetailJsonView(View):

    def get(self, request, profile_id, *args, **kwargs):
        try:
            if request.user.is_superuser:
                profile = Profile.objects.select_related('user').get(id=profile_id)
            else:
                profile = Profile.objects.select_related('user').get(
                    id=profile_id, user=request.user
                )

            payment = Payment.objects.filter(
                user_id=profile.user_id
            ).order_by('-payment_date').first()

            # ✅ safe() defined correctly INSIDE get(), NOT inside the class
            def safe(val):
                if val is None or val == "":
                    return None
                return str(val)

            # ✅ safe photo helper
            def safe_photo(field):
                try:
                    return field.url if field and field.name else None
                except Exception:
                    return None
           
            
            data = {
                # Basic Details
                "full_name":          safe(profile.full_name),
                "gender":             safe(profile.get_gender_display()),
                "dob":                profile.dob.strftime("%d %b %Y") if profile.dob else None,
                "birth_time": profile.birth_time.strftime("%I:%M %p") if profile.birth_time else None,
                "birth_place":        safe(profile.birth_place),
                "current_location":   safe(profile.current_location),
                "height":             safe(profile.height),
                "weight":             safe(profile.weight),
                "complexion":         safe(profile.complexion),
                "marital_status":     safe(profile.get_marital_status_display()) if profile.marital_status else None,

                # Religion & Horoscope
                "religion":           safe(profile.religion),
                "caste":              safe(profile.caste),
                "sub_caste":          safe(profile.sub_caste),
                "gothram":            safe(profile.gothram),
                "rasi":               safe(profile.rasi),
                "nakshatra":          safe(profile.nakshatra),
                "laknam":             safe(profile.laknam),
                "dosham":             safe(profile.dosham),
                "saimurai":           safe(profile.saimurai),           # ✅ NEW

                # Education & Career
                "education":          safe(profile.education),
                "occupation":         safe(profile.occupation),
                "company_name":       safe(profile.company_name),
                "job_location":       safe(profile.job_location),
                "annual_income":      safe(str(profile.annual_income)) if profile.annual_income else None,
                "job_location_type":  safe(profile.job_location_type),
                "job_state":          safe(profile.job_state),
                "job_country":        safe(profile.job_country),

                # Family
                "father_name":        safe(profile.father_name),
                "father_occupation":  safe(profile.father_occupation),
                "father_phone":       safe(profile.father_phone),       # ✅ NEW
                "mother_name":        safe(profile.mother_name),
                "mother_occupation":  safe(profile.mother_occupation),
                "mother_phone":       safe(profile.mother_phone),       # ✅ NEW
                "no_of_brothers":     safe(str(profile.no_of_brothers)) if profile.no_of_brothers is not None else None,
                "no_of_sisters":      safe(str(profile.no_of_sisters))  if profile.no_of_sisters  is not None else None,
                "perapu_varesai":     safe(profile.perapu_varesai),     # ✅ NEW

                # Contact
                "phone":              safe(profile.phone),
                "whatsapp_number":    safe(profile.whatsapp_number),
                "email":              safe(profile.email),
                "address":            safe(profile.address),
                "city":               safe(profile.city),
                "state":              safe(profile.state),
                "country":            safe(profile.country),
                "pincode":            safe(profile.pincode),

                # Additional Details
                "wanted":             safe(profile.wanted),             # ✅ NEW
                "assets":             safe(profile.assets),             # ✅ NEW
                "erpu_thisai":        safe(profile.erpu_thisai),        # ✅ NEW

                # About
                "bio":                safe(profile.bio),
                "hobbies":            safe(profile.hobbies),

                # Payment
                "payment_status":     payment.status if payment else "UNPAID",
                "payment_amount":     f"₹{payment.amount:.0f}" if payment and payment.status == "COMPLETED" else None,
                "payment_date":       payment.payment_date.strftime("%d %b %Y") if payment and payment.payment_date else None,

                # Photos
                "photo1":             safe_photo(profile.photo1),
                "photo2":             safe_photo(profile.photo2),
                "photo3":             safe_photo(profile.photo3),
                "photo4":             safe_photo(profile.photo4),
                "photo5":             safe_photo(profile.photo5),
            }

            return JsonResponse({"result": True, "data": data})

        except Profile.DoesNotExist:
            return JsonResponse({"result": False, "message": "Profile not found"}, status=404)

        except Exception as e:
            import traceback
            return JsonResponse({
                "result": False,
                "message": str(e),
                "traceback": traceback.format_exc()
            }, status=500)


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def profile_filter_options(request):
    """Returns distinct filter values from DB for dropdowns."""
    from django.db.models import Q

    qs = Profile.objects.exclude(datamode='D')

    def distinct(field):
        return list(
            qs.exclude(**{f"{field}__isnull": True})
              .exclude(**{f"{field}__exact": ''})
              .values_list(field, flat=True)
              .distinct()
              .order_by(field)
        )

    return JsonResponse({
        "gender":         distinct('gender'),
        "religion":       distinct('religion'),
        "caste":          distinct('caste'),
        "rasi":           distinct('rasi'),
        "nakshatra":      distinct('nakshatra'),
        "marital_status": distinct('marital_status'),
        "datamode":       distinct('datamode'),
    })

from django.http import HttpResponse
from openpyxl import Workbook
from .models import Profile


def export_profiles_excel(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Profiles"

    # Header Row
    headers = [
        "ID", "Username", "Full Name", "Gender", "DOB", "Birth Time", "Birth Place",
        "Height", "Weight", "Complexion",
        "Religion", "Caste", "Sub Caste", "Gothram",
        "Rasi", "Nakshatra", "Laknam", "Dosham",
        "Education", "Occupation", "Company", "Job Location", "Annual Income",
        "Father Name", "Father Occupation",
        "Mother Name", "Mother Occupation",
        "No of Brothers", "No of Sisters",
        "Phone", "WhatsApp", "Email",
        "Address", "City", "State", "Country", "Pincode",
        "Bio", "Hobbies", "Wanted", "Assets", "Saimurai", "Erpu thisai", "Perapu Varesai", "Father Phone", "Mother Phone", "Marital Status",
        "Photo1", "Photo2", "Photo3", "Photo4", "Photo5",
        "Data Mode", "Created On", "LAST NAME"
    ]

    ws.append(headers)

    profiles = Profile.objects.select_related('user').all()

    for p in profiles:
        ws.append([
            p.id,
            p.user.username if p.user else "",
            p.full_name,
            p.get_gender_display(),
            p.dob,
            p.birth_time,
            p.birth_place,
            p.height,
            p.weight,
            p.complexion,
            p.religion,
            p.caste,
            p.sub_caste,
            p.gothram,
            p.rasi,
            p.nakshatra,
            p.laknam,
            p.get_dosham_display() if p.dosham else "",
            p.education,
            p.occupation,
            p.company_name,
            p.job_location,
            p.annual_income,
            p.father_name,
            p.father_occupation,
            p.mother_name,
            p.mother_occupation,
            p.no_of_brothers,
            p.no_of_sisters,
            p.phone,
            p.whatsapp_number,
            p.email,
            p.address,
            p.city,
            p.state,
            p.country,
            p.pincode,
            p.bio,
            p.hobbies,
            p.wanted,
            p.assets,
            p.saimurai,
            p.erpu_thisai,
            p.perapu_varesai,
            p.father_phone,
            p.mother_phone,
            p.get_marital_status_display() if hasattr(p, 'get_marital_status_display') else "",
            p.photo1.url if p.photo1 else "",
            p.photo2.url if p.photo2 else "",
            p.photo3.url if p.photo3 else "",
            p.photo4.url if p.photo4 else "",
            p.photo5.url if p.photo5 else "",
            p.get_datamode_display(),
            p.created_on,
            getattr(p, 'last_name', '')
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = 'attachment; filename=all_profiles.xlsx'

    wb.save(response)
    return response


from datetime import datetime
import pandas as pd
import re

import pandas as pd
from datetime import datetime, date
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import Profile
from .forms import ProfileUploadForm

User = get_user_model()


# ──────────────────────────────────────────────
# ALIAS MAPS  (Excel value → DB choice key)
# ──────────────────────────────────────────────

CASTE_ALIAS = {
    # Excel spelling  →  CASTE_CHOICES key
    "chettiyar":            "Chettiar",
    "chettiar":             "Chettiar",
    "muthaliyar":           "Mudaliar",
    "mudaliar":             "Mudaliar",
    "vaniyar":              "Vanniyar",
    "vanniyar":             "Vanniyar",
    "sc":                   "Adi Dravida",
    "scheduled caste":      "Adi Dravida",
    "jaathi thadai illai":  "Jaathi Thadai Illai",
    "naidu":                "Naidu",
}

RASI_ALIAS = {
    # All lowercase for matching
    "mesham": "Mesham", "aries": "Mesham",
    "rishabam": "Rishabam", "rishaba": "Rishabam", "taurus": "Rishabam",
    "midhunam": "Midhunam", "mithuna": "Midhunam", "gemini": "Midhunam",
    "kadagam": "Kadagam", "cancer": "Kadagam",
    "simmam": "Simmam", "simha": "Simmam", "leo": "Simmam",
    "kanni": "Kanni", "virgo": "Kanni",
    "thulam": "Thulam", "tulam": "Thulam", "libra": "Thulam",
    "viruchigam": "Viruchigam", "scorpio": "Viruchigam",
    "dhanusu": "Dhanusu", "sagittarius": "Dhanusu",
    "magaram": "Magaram", "capricorn": "Magaram",
    "kumbam": "Kumbam", "aquarius": "Kumbam",
    "meenam": "Meenam", "pisces": "Meenam",
}

LAKNAM_ALIAS = {
    # All lowercase for matching
    # Mesham / Aries
    "mesham": "Mesham", 
    "mesha": "Mesham",
    "maesham": "Mesham",
    "maysham": "Mesham",
    "may": "Mesham",
    "aries": "Mesham",
    
    # Rishabam / Taurus
    "rishabam": "Rishabam", 
    "rishaba": "Rishabam",
    "rishbam": "Rishabam",
    "rishbham": "Rishabam",
    "risabam": "Rishabam",
    "risabham": "Rishabam",
    "rishabham": "Rishabam",
    "rishbam": "Rishabam",
    "taurus": "Rishabam",
    
    # Midhunam / Gemini
    "midhunam": "Midhunam", 
    "mithunam": "Midhunam",
    "mithuam": "Midhunam",
    "mithuna": "Midhunam",
    "mithun": "Midhunam",
    "gemini": "Midhunam",
    
    # Kadagam / Cancer
    "kadagam": "Kadagam", 
    "katagam": "Kadagam",
    "cancer": "Kadagam",
    
    # Simmam / Leo
    "simmam": "Simmam", 
    "simam": "Simmam",
    "simham": "Simmam",
    "simha": "Simmam",
    "leo": "Simmam",
    
    # Kanni / Virgo
    "kanni": "Kanni", 
    "kanii": "Kanni",
    "virgo": "Kanni",
    
    # Thulam / Libra
    "thulam": "Thulam", 
    "tulam": "Thulam",
    "tulm": "Thulam",
    "thulm": "Thulam",
    "libra": "Thulam",
    
    # Viruchigam / Scorpio
    "viruchigam": "Viruchigam", 
    "viruchagam": "Viruchigam",
    "virchigam": "Viruchigam",
    "virchagam": "Viruchigam",
    "viruchagm": "Viruchigam",
    "viruchigam": "Viruchigam",
    "viruchagam": "Viruchigam",
    "scorpio": "Viruchigam",
    
    # Dhanusu / Sagittarius
    "dhanusu": "Dhanusu", 
    "danusu": "Dhanusu",
    "dhanus": "Dhanusu",
    "sagittarius": "Dhanusu",
    
    # Magaram / Capricorn
    "magaram": "Magaram", 
    "magarm": "Magaram",
    "magarm": "Magaram",
    "capricorn": "Magaram",
    
    # Kumbam / Aquarius
    "kumbam": "Kumbam", 
    "kumbm": "Kumbam",
    "kumbam": "Kumbam",
    "aquarius": "Kumbam",
    
    # Meenam / Pisces
    "meenam": "Meenam", 
    "menam": "Meenam",
    "mennam": "Meenam",
    "pisces": "Meenam",
}


NAKSHATRA_ALIAS = {
    "ashwini": "Ashwini",
    "bharani": "Bharani",
    "karthigai": "Karthigai", "krittika": "Karthigai",
    "rohini": "Rohini",
    "mirugashirisham": "Mirugashirisham", "mrigashira": "Mirugashirisham",
    "thiruvadhirai": "Thiruvadhirai", "ardra": "Thiruvadhirai",
    "punarpoosam": "Punarpoosam", "punarvasu": "Punarpoosam",
    "poosam": "Poosam", "pushya": "Poosam",
    "ayilyam": "Ayilyam", "ashlesha": "Ayilyam",
    "magam": "Magam", "magha": "Magam",
    "pooram": "Pooram", "pubba": "Pooram",
    "uthiram": "Uthiram", "uttara": "Uthiram",
    "hastham": "Hastham", "hasta": "Hastham",
    "chithirai": "Chithirai", "chitra": "Chithirai",
    "swathi": "Swathi", "swati": "Swathi",
    "visakam": "Visakam", "vishakha": "Visakam",
    "anusham": "Anusham", "anuradha": "Anusham",
    "kettai": "Kettai", "jyeshtha": "Kettai",
    "moolam": "Moolam", "moola": "Moolam",
    "pooradam": "Pooradam", "purvashadha": "Pooradam",
    "uthiradam": "Uthiradam", "uttarashadha": "Uthiradam",
    "thiruvonam": "Thiruvonam", "shravana": "Thiruvonam",
    "avittam": "Avittam", "dhanishta": "Avittam",
    "sadayam": "Sadayam", "shatabhisha": "Sadayam",
    "poorattathi": "Poorattathi", "purvabhadra": "Poorattathi",
    "uthirattathi": "Uthirattathi", "uttarabhadra": "Uthirattathi",
    "revathi": "Revathi",
}

DOSHAM_ALIAS = {
    "no dosham":      "No Dosham",
    "no":             "No Dosham",
    "none":           "No Dosham",
    "n":              "No Dosham",
    "chevvai dosham": "Chevvai Dosham",
    "chevvai":        "Chevvai Dosham",
    "mangal":         "Chevvai Dosham",
    "rahu dosham":    "Rahu Dosham",
    "rahu":           "Rahu Dosham",
    "ketu dosham":    "Ketu Dosham",
    "ketu":           "Ketu Dosham",
    "shani dosham":   "Shani Dosham",
    "shani":          "Shani Dosham",
    "naga dosham":    "Naga Dosham",
    "naga":           "Naga Dosham",
    "unknown":        "Unknown",
    "y":              "Unknown",   # old Yes/No value → Unknown
    "yes":            "Unknown",
}

MARITAL_STATUS_ALIAS = {
    "single":   "S",
    "married":  "M",
    "divorced": "D",
    "widowed":  "W",
    "widow":    "W",
    "s": "S", "m": "M", "d": "D", "w": "W",
}

GENDER_ALIAS = {
    "male": "M", "m": "M",
    "female": "F", "f": "F",
    "other": "O", "o": "O",
}

DISTRICT_ALIAS = {d.lower(): d for d in [
    "Ariyalur","Chengalpattu","Chennai","Coimbatore","Cuddalore",
    "Dharmapuri","Dindigul","Erode","Kallakurichi","Kancheepuram",
    "Kanniyakumari","Karur","Krishnagiri","Madurai","Mayiladuthurai",
    "Nagapattinam","Namakkal","Nilgiris","Perambalur","Pudukkottai",
    "Ramanathapuram","Ranipet","Salem","Sivaganga","Tenkasi",
    "Thanjavur","Theni","Thiruvallur","Thiruvarur","Thoothukudi",
    "Tiruchirappalli","Tirunelveli","Tirupathur","Tiruppur",
    "Tiruvannamalai","Vellore","Viluppuram","Virudhunagar",
]}


# ──────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────

def safe_str(value):
    """Return stripped string or empty string for NaN/None."""
    if value is None:
        return ''
    try:
        if pd.isna(value):
            return ''
    except Exception:
        pass
    return str(value).strip()


def map_choice(value, alias_dict, default=''):
    """Lowercase-lookup in alias dict, return default if not found."""
    key = safe_str(value).lower()
    return alias_dict.get(key, default)


def convert_dob(value):
    if value is None:
        return None
    try:
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, (int, float)):
            import xlrd
            return xlrd.xldate_as_datetime(value, 0).date()
        value_str = str(value).strip()
        if not value_str or value_str.lower() in ('nan', 'none', 'nat', ''):
            return None
        for fmt in ('%d-%m-%Y','%d/%m/%Y','%d.%m.%Y','%d-%m-%y',
                    '%d/%m/%y','%Y-%m-%d','%Y/%m/%d','%m-%d-%Y',
                    '%m/%d/%Y','%d %b %Y','%d %B %Y','%b %d, %Y','%B %d, %Y'):
            try:
                return datetime.strptime(value_str, fmt).date()
            except ValueError:
                continue
        return pd.to_datetime(value_str, dayfirst=True).date()
    except Exception:
        return None

def convert_birth_time(value):
    if value is None:
        return None
    try:
        from datetime import time as time_type
        if isinstance(value, time_type):
            return value
        if isinstance(value, datetime):
            return value.time()

        value_str = str(value).strip()
        if not value_str or value_str.lower() in ('nan', 'none', 'nat', ''):
            return None

        # ✅ Handle formats like "2.00AM", "11.30PM", "2.30AM"
        import re
        dot_match = re.match(r'^(\d{1,2})\.(\d{2})\s*(AM|PM)$', value_str, re.IGNORECASE)
        if dot_match:
            hour   = int(dot_match.group(1))
            minute = int(dot_match.group(2))
            period = dot_match.group(3).upper()
            if period == 'PM' and hour != 12:
                hour += 12
            if period == 'AM' and hour == 12:
                hour = 0
            return time_type(hour, minute)

        # Standard formats fallback
        for fmt in ('%H:%M:%S', '%H:%M', '%I:%M %p', '%I:%M:%S %p', '%I%p'):
            try:
                return datetime.strptime(value_str, fmt).time()
            except ValueError:
                continue

        return None

    except Exception:
        return None


def clean_integer(value):
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except Exception:
        pass
    try:
        return int(float(str(value).strip()))
    except (ValueError, TypeError):
        return None


def clean_decimal(value):
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except Exception:
        pass
    try:
        return float(str(value).strip().replace(',', ''))
    except (ValueError, TypeError):
        return None


def clean_height(value):
    if value is None:
        return ''
    try:
        if pd.isna(value):
            return ''
    except Exception:
        pass
    return str(value).strip()


# ──────────────────────────────────────────────
# MAIN UPLOAD VIEW
# ──────────────────────────────────────────────
def upload_profiles_excel(request):
    if request.method == 'POST':
        form = ProfileUploadForm(request.POST, request.FILES)

        if form.is_valid():
            excel_file = request.FILES['file']
            success_count = 0
            error_count = 0
            error_rows = []

            try:
                df = pd.read_excel(excel_file)

                # ✅ Normalize all column names: strip + lowercase for safe matching
                df.columns = [str(c).strip() for c in df.columns]

                for index, row in df.iterrows():
                    try:
                        # ✅ Helper to get value by exact or case-insensitive column name
                        def get(col):
                            # Try exact match first
                            if col in row.index:
                                return row[col]
                            # Try case-insensitive match
                            col_lower = col.lower()
                            for c in row.index:
                                if str(c).lower() == col_lower:
                                    return row[c]
                            return None

                        username = safe_str(get('Username'))
                        if not username:
                            error_rows.append(f"Row {index + 2}: Username missing — skipped")
                            continue

                        user, _ = User.objects.get_or_create(
                            username=username,
                            defaults={
                                'email': safe_str(get('Email'))
                            }
                        )

                        # ── Choice fields with alias maps ──
                        gender         = map_choice(get('Gender'),         GENDER_ALIAS,         'M')
                        caste          = map_choice(get('Caste'),           CASTE_ALIAS,          safe_str(get('Caste')))
                        rasi           = map_choice(get('Rasi'),            RASI_ALIAS,           '')
                        nakshatra      = map_choice(get('Nakshatra'),       NAKSHATRA_ALIAS,      '')
                        laknam         = map_choice(get('Laknam'),          LAKNAM_ALIAS,           '')
                        dosham         = map_choice(get('Dosham'),          DOSHAM_ALIAS,         'No Dosham')
                        marital_status = map_choice(get('Marital Status'),  MARITAL_STATUS_ALIAS, '')
                        birth_place    = map_choice(get('Birth Place'),     DISTRICT_ALIAS,       '')

                        # ── Father / Mother — set flags if data present ──
                        father_name       = safe_str(get('Father Name'))
                        father_occupation = safe_str(get('Father Occupation'))
                        father_phone      = safe_str(get('Father Phone'))      # ✅ matches export header
                        mother_name       = safe_str(get('Mother Name'))
                        mother_occupation = safe_str(get('Mother Occupation'))
                        mother_phone      = safe_str(get('Mother Phone'))      # ✅ matches export header

                        has_father   = 'Y' if (father_name or father_occupation) else 'N'
                        has_mother   = 'Y' if (mother_name or mother_occupation) else 'N'

                        # ── Siblings ──
                        brothers     = clean_integer(get('No of Brothers')) or 0
                        sisters      = clean_integer(get('No of Sisters'))  or 0
                        has_siblings = 'Y' if (brothers + sisters) > 0 else 'N'

                        # ── New fields ──                       ✅ match export headers exactly
                        wanted         = safe_str(get('Wanted'))
                        assets         = safe_str(get('Assets'))
                        saimurai       = safe_str(get('Saimurai'))
                        erpu_thisai    = safe_str(get('Erpu thisai'))       # ✅ matches "Erpu thisai"
                        perapu_varesai = safe_str(get('Perapu Varesai'))

                        Profile.objects.create(
                            user               = user,
                            full_name          = safe_str(get('Full Name')),
                            gender             = gender,
                            dob                = convert_dob(get('DOB')),
                            birth_time         = convert_birth_time(get('Birth Time')),
                            birth_place        = birth_place,
                            height             = clean_height(get('Height')),
                            weight             = safe_str(get('Weight')),
                            complexion         = safe_str(get('Complexion')),

                            # Religion & Horoscope
                            religion           = safe_str(get('Religion')),
                            caste              = caste,
                            sub_caste          = safe_str(get('Sub Caste')),
                            gothram            = safe_str(get('Gothram')),
                            rasi               = rasi,
                            nakshatra          = nakshatra,
                            laknam             = laknam,
                            dosham             = dosham,
                            saimurai           = saimurai,              # ✅ NEW

                            # Education & Career
                            education          = safe_str(get('Education')),
                            occupation         = safe_str(get('Occupation')),
                            company_name       = safe_str(get('Company')),
                            job_location       = safe_str(get('Job Location')),
                            annual_income      = clean_decimal(get('Annual Income')),

                            # Family
                            has_father_details = has_father,
                            father_name        = father_name,
                            father_occupation  = father_occupation,
                            father_phone       = father_phone,          # ✅ NEW
                            has_mother_details = has_mother,
                            mother_name        = mother_name,
                            mother_occupation  = mother_occupation,
                            mother_phone       = mother_phone,          # ✅ NEW
                            has_siblings       = has_siblings,
                            no_of_brothers     = brothers,
                            no_of_sisters      = sisters,
                            perapu_varesai     = perapu_varesai,        # ✅ NEW

                            # Contact
                            phone              = safe_str(get('Phone')),
                            whatsapp_number    = safe_str(get('WhatsApp')),
                            email              = safe_str(get('Email')),
                            address            = safe_str(get('Address')),
                            city               = safe_str(get('City')),
                            state              = safe_str(get('State')),
                            country            = safe_str(get('Country')) or 'India',
                            pincode            = safe_str(get('Pincode')),

                            # About
                            bio                = safe_str(get('Bio')),
                            hobbies            = safe_str(get('Hobbies')),
                            marital_status     = marital_status,

                            # Additional Details
                            wanted             = wanted,                # ✅ NEW
                            assets             = assets,                # ✅ NEW
                            erpu_thisai        = erpu_thisai,           # ✅ NEW

                            datamode           = 'A',
                            created_by         = request.user.username if request.user.is_authenticated else "SYSTEM"
                        )
                        success_count += 1

                    except Exception as e:
                        error_count += 1
                        error_rows.append(f"Row {index + 2}: {str(e)}")
                        continue

                # ✅ Show detailed result
                if error_rows:
                    error_details = " | ".join(error_rows[:10])  # show max 10 errors
                    messages.warning(
                        request,
                        f"Import done: ✅ {success_count} added, ❌ {error_count} errors. "
                        f"First errors: {error_details}"
                    )
                else:
                    messages.success(
                        request,
                        f"Import complete! ✅ {success_count} profiles added successfully."
                    )

                return redirect("mck_master:mck_profile_list")

            except Exception as e:
                messages.error(request, f"Error reading file: {e}")

    else:
        form = ProfileUploadForm()

    return render(request, 'profile_upload.html', {'form': form})