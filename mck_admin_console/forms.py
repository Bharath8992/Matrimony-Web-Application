import sys
from django import forms
from django.forms.widgets import HiddenInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder
from crispy_forms.helper import *
from crispy_forms.layout import *
from crispy_forms.bootstrap import *
from mck_admin_console import models
from config import app_gv as gv

from mck_auth.models import AccountTypeRole


class FAQCategoryCreateUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        mode = kwargs.pop('mode', None)
        super(FAQCategoryCreateUpdateForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].label = str(self.fields[field_name].label).upper()
            self.fields[field_name].widget.attrs['class'] = "form-control form-control-solid"
        
        if mode == "edit":
            instance = kwargs.get('instance', None)
        save_button_name = "SAVE"

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                '',
                Row(Column(Field('name')), css_class='col-12'),
               
            ),
            ButtonHolder(
                 Div(HTML('<a class="btn btn-lg btn-secondary me-3" href="javascript:void();" onclick="history.back()">CANCEL</a>'),Submit('create_button', save_button_name, css_class='btn btn-lg btn-primary'),
                            css_class="d-flex text-right justify-content-end pt-10 col-12"), css_class="row col-12 pe-5",
            )
        )
        
    class Meta:
        model = models.FAQCategory
        exclude = ['created_on', 'updated_on', 'created_by', 'updated_by', 'datamode']


class GalleryCreateUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        mode = kwargs.pop('mode', None)
        super(GalleryCreateUpdateForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].label = str(self.fields[field_name].label).upper()
            self.fields[field_name].widget.attrs['class'] = "form-control form-control-solid"
        
        if mode == "edit":
            instance = kwargs.get('instance', None)
        save_button_name = "SAVE"

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                '',
                Row(Column(Field('name')), css_class='col-12'),
                Row(Column(Field('location')), css_class='col-12'),
                Row(Column(Field('photo')), css_class='col-12'),
               
            ),
            ButtonHolder(
                Div(
                    HTML('<a class="btn btn-lg btn-secondary me-3" href="javascript:void();" onclick="history.back()">CANCEL</a>'),
                    Submit('create_button', save_button_name, css_class='btn btn-lg btn-primary'),
                    css_class="d-flex text-right justify-content-end pt-10 col-12"
                ),
                css_class="row col-12 pe-5",
            )
        )
        
    class Meta:
        model = models.Gallery
        exclude = ['created_on', 'updated_on', 'created_by', 'updated_by', 'datamode']


class ConatctCreateUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        mode = kwargs.pop('mode', None)
        super(ConatctCreateUpdateForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].label = str(self.fields[field_name].label).upper()
            self.fields[field_name].widget.attrs['class'] = "form-control form-control-solid"
        
        if mode == "edit":
            instance = kwargs.get('instance', None)
        save_button_name = "SAVE"

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                '',
                # Row(Column(Field('county')), Column(Field('name')), css_class='col-12'),
                Row(Column(Field('name')), css_class='col-12'),
                Row(Column(Field('email')), css_class='col-12'),
                Row(Column(Field('phone')), css_class='col-12'),
                Row(Column(Field('message')), css_class='col-12'),
               
            ),
            ButtonHolder(
                Div(HTML('<a class="btn btn-lg btn-secondary me-3" href="javascript:void();" onclick="history.back()">CANCEL</a>'),Submit('create_button', save_button_name, css_class='btn btn-lg btn-primary'),
                            css_class="d-flex text-right justify-content-end pt-10 col-12"), css_class="row col-12 pe-5",
            )
        )
        
    class Meta:
        model = models.Contact
        exclude = ['created_on', 'updated_on', 'created_by', 'updated_by', 'datamode']


class TestimonialCreateUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        mode = kwargs.pop('mode', None)
        super(TestimonialCreateUpdateForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].label = str(self.fields[field_name].label).upper()
            self.fields[field_name].widget.attrs['class'] = "form-control form-control-solid"
        
        if mode == "edit":
            instance = kwargs.get('instance', None)
        save_button_name = "SAVE"

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                '',
                Row(Column(Field('name')), css_class='col-12'),
                Row(Column(Field('short_description')), css_class='col-12'),
                Row(Column(Field('description')), css_class='col-12'),
                Row(Column(Field('photo')), Column(Field('tags')), Column(Field('star')), css_class='col-12'),
               
            ),
            ButtonHolder(
                Div(HTML('<a class="btn btn-lg btn-secondary me-3" href="javascript:void();" onclick="history.back()">CANCEL</a>'),Submit('create_button', save_button_name, css_class='btn btn-lg btn-primary'),
                            css_class="d-flex text-right justify-content-end pt-10 col-12"), css_class="row col-12 pe-5",
            )
        )
        
    class Meta:
        model = models.Testimonial
        exclude = ['created_on', 'updated_on', 'created_by', 'updated_by', 'datamode']
