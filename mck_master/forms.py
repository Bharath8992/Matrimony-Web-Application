from django import forms
from crispy_forms.helper import FormHelper
from django.shortcuts import redirect
from crispy_forms.layout import Layout, Fieldset, ButtonHolder
from crispy_forms.helper import *
from crispy_forms.layout import *
from crispy_forms.bootstrap import *
from mck_master import models 


class SupportPageContentCreateUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        mode = kwargs.pop('mode', None)
        super(SupportPageContentCreateUpdateForm, self).__init__(*args, **kwargs)
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
                
                Row(Column(Field('support_key')), css_class='col-12'),
                Row(Column(Field('support_value')), css_class='col-12'),
                Row(Column(Field('support_description')), css_class='col-12'),
                Row(Column(Field('content_type')), css_class='col-12'),
            ),
            ButtonHolder(
                Div(HTML('<a class="btn btn-secondary me-3" href="javascript:void();" onclick="history.back()">CANCEL</a>'),Submit('create_button', save_button_name, css_class='btn btn-lg btn-primary'),
                            css_class="d-flex text-right justify-content-end pt-10 col-12"), css_class="row col-12 pe-5",
            )
        )
    class Meta:
        model = models.SupportPageContent
        exclude = ['image', 'created_on', 'updated_on', 'created_by', 'updated_by', 'datamode']


class CategoryCreateUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        mode = kwargs.pop('mode', None)
        super(CategoryCreateUpdateForm, self).__init__(*args, **kwargs)
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
                Row(Column(Field('name')), Column(Field('image')), css_class='col-12'),
            ),
            ButtonHolder(
                Div(HTML('<a class="btn btn-secondary me-3" href="javascript:void();" onclick="history.back()">CANCEL</a>'),Submit('create_button', save_button_name, css_class='btn btn-lg btn-primary'),
                            css_class="d-flex text-right justify-content-end pt-10 col-12"), css_class="row col-12 pe-5",
            )
        )
    class Meta:
        model = models.Category
        exclude = ['created_on', 'updated_on', 'created_by', 'updated_by', 'datamode']


class SubCategoryCreateUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        mode = kwargs.pop('mode', None)
        super(SubCategoryCreateUpdateForm, self).__init__(*args, **kwargs)
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
                Row(Column(Field('category', css_class="form-select form-select-lg form-select-solid", data_control='select2',)), Column(Field('name')), Column(Field('image')), css_class='col-12'),
            ),
            ButtonHolder(
                Div(HTML('<a class="btn btn-secondary me-3" href="javascript:void();" onclick="history.back()">CANCEL</a>'),Submit('create_button', save_button_name, css_class='btn btn-lg btn-primary'),
                            css_class="d-flex text-right justify-content-end pt-10 col-12"), css_class="row col-12 pe-5",
            )
        )
    class Meta:
        model = models.SubCategory
        exclude = ['created_on', 'updated_on', 'created_by', 'updated_by', 'datamode']


class BannerCreateUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        mode = kwargs.pop('mode', None)
        super(BannerCreateUpdateForm, self).__init__(*args, **kwargs)
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
                Row(Column(Field('name')), Column(Field('image')), css_class='col-12'),
            ),
            ButtonHolder(
                Div(HTML('<a class="btn btn-secondary me-3" href="javascript:void();" onclick="history.back()">CANCEL</a>'),Submit('create_button', save_button_name, css_class='btn btn-lg btn-primary'),
                            css_class="d-flex text-right justify-content-end pt-10 col-12"), css_class="row col-12 pe-5",
            )
        )
    class Meta:
        model = models.Banner
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
                Row(Column(Field('name')), Column(Field('image')), css_class='col-12'),
            ),
            ButtonHolder(
                Div(HTML('<a class="btn btn-secondary me-3" href="javascript:void();" onclick="history.back()">CANCEL</a>'),Submit('create_button', save_button_name, css_class='btn btn-lg btn-primary'),
                            css_class="d-flex text-right justify-content-end pt-10 col-12"), css_class="row col-12 pe-5",
            )
        )
    class Meta:
        model = models.GalleryS
        exclude = ['created_on', 'updated_on', 'created_by', 'updated_by', 'datamode']


# State
class StateCreateUpdateForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        mode = kwargs.pop('mode', None)
        super(StateCreateUpdateForm, self).__init__(*args, **kwargs)
        self.fields['country'].empty_label = "Please select"

        # Apply Bootstrap styles to all fields
        for field_name in self.fields:
            self.fields[field_name].label = str(self.fields[field_name].label).upper()
            self.fields[field_name].widget.attrs['class'] = "form-control form-control-solid"
        
        # If edit mode, handle instance
        if mode == "edit":
            instance = kwargs.get('instance', None)

        save_button_name = "SAVE"

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                '',
                Row(Column(Field('name')), Column(Field('code')), css_class='col-12'),
                Row(Column(Field('country')), css_class='col-12'),
            ),
            ButtonHolder(
                Div(
                    HTML('<a class="btn btn-lg btn-secondary me-3" href="javascript:void();" onclick="history.back()">CANCEL</a>'),
                    Submit('create_button', save_button_name, css_class='btn btn-lg btn-primary'),
                    css_class="d-flex text-right justify-content-end pt-10 col-12"
                ),
                css_class="row col-12 pe-5 mt-3",
            )
        )

    class Meta:
        model = models.State
        exclude = ['created_on', 'updated_on', 'datamode']


# City
class CityCreateUpdateForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        mode = kwargs.pop('mode', None)
        super(CityCreateUpdateForm, self).__init__(*args, **kwargs)
        self.fields['state'].empty_label = "Please select"
        
        # Apply Bootstrap styles to all fields
        for field_name in self.fields:
            self.fields[field_name].label = str(self.fields[field_name].label).upper()
            self.fields[field_name].widget.attrs['class'] = "form-control form-control-solid"
        
        # If edit mode, handle instance
        if mode == "edit":
            instance = kwargs.get('instance', None)
        save_button_name = "SAVE"

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                '',
                Row(Column(Field('name')), Column(Field('code')), css_class='col-12'),
                Row(Column(Field('state')), css_class='col-12'),
            ),
            ButtonHolder(
                Div(HTML('<a class="btn btn-lg btn-secondary me-3" href="javascript:void();" onclick="history.back()">CANCEL</a>'),
                    Submit('create_button', save_button_name, css_class='btn btn-lg btn-primary'),
                    css_class="d-flex text-right justify-content-end pt-10 col-12"),
                css_class="row col-12 pe-5 mt-3",
            )
        )

    class Meta:
        model = models.City
        exclude = ['created_on', 'updated_on', 'datamode']


class OfferCreateUpdateForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        mode = kwargs.pop('mode', None)
        super(OfferCreateUpdateForm, self).__init__(*args, **kwargs)
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
                Row(
                    Column(Field('name')),  
                    Column(Field('image')),  
                    css_class='col-12'
                ),
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
        model = models.Offers
        exclude = ['created_on', 'updated_on', 'created_by', 'updated_by', 'datamode']
        

class ClientFeedbackCreateUpdateForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        mode = kwargs.pop('mode', None)
        super(ClientFeedbackCreateUpdateForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].label = str(self.fields[field_name].label).upper()
            self.fields[field_name].widget.attrs['class'] = "form-control form-control-solid"
        
        if mode == "edit":
            instance = kwargs.get('instance', None)
        save_button_name = "SAVE"

        # Form layout using crispy-forms
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                '',
                Row(
                    Column(Field('name')),  
                    Column(Field('feedback')),
                    css_class='col-12'
                ),
                Row(
                    Column(Field('image')),  
                    Column(Field('place')),
                    css_class='col-12'
                ),
            ),
            ButtonHolder(
                Div(
                    HTML('<a class="btn btn-lg btn-secondary me-3" href="javascript:void();" onclick="history.back()">CANCEL</a>'),
                    Submit('create_button', save_button_name, css_class='btn btn-lg btn-primary'),
                    css_class="d-flex text-right justify-content-end pt-10 col-12"
                ),
                css_class="row col-12 pe-5 mt-3",
            )
        )

    class Meta:
        model = models.ClientFeedback
        exclude = ['created_on', 'updated_on', 'created_by', 'updated_by', 'datamode']



from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, HTML, Div, ButtonHolder, Submit
from . import models
from datetime import date, datetime


class ProfileCreateUpdateForm(forms.ModelForm):
    is_currently_living = forms.BooleanField(
        required=False, initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = models.Profile
        exclude = ['user', 'created_on', 'updated_on', 'created_by', 'updated_by', 'datamode']
        widgets = {
            'dob':                forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-solid'}),
            'birth_time':         forms.TimeInput(attrs={'type': 'time', 'class': 'form-control form-control-solid'}),
            'gender':             forms.Select(attrs={'class': 'form-control form-control-solid'}),
            # 'religion':           forms.Select(attrs={'class': 'form-control form-control-solid'}),
            # 'caste':              forms.Select(attrs={'class': 'form-control form-control-solid'}),
            # # 'sub_caste':          forms.Select(attrs={'class': 'form-control form-control-solid'}),
            # 'dosham':             forms.Select(attrs={'class': 'form-control form-control-solid'}),
            # 'job_location_type':  forms.RadioSelect(attrs={'class': 'form-check-input'}),
            # 'job_state':          forms.Select(attrs={'class': 'form-control form-control-solid'}),
            # 'birth_place':        forms.Select(attrs={'class': 'form-control form-control-solid'}),
            'marital_status':     forms.Select(attrs={'class': 'form-control form-control-solid'}),
            'has_father_details': forms.Select(attrs={'class': 'form-control form-control-solid'}),
            'has_mother_details': forms.Select(attrs={'class': 'form-control form-control-solid'}),
            'has_siblings':       forms.Select(attrs={'class': 'form-control form-control-solid'}),
        }

    def __init__(self, *args, **kwargs):
        self.mode = kwargs.pop('mode', None)
        super(ProfileCreateUpdateForm, self).__init__(*args, **kwargs)

        # Set field choices from model
        self.fields['gender'].choices        = models.Profile.GENDER_CHOICES
        # self.fields['religion'].choices      = models.Profile.RELIGION_CHOICES
        # self.fields['caste'].choices         = models.Profile.CASTE_CHOICES
        # self.fields['sub_caste'].choices     = models.Profile.SUB_CASTE_CHOICES
        # self.fields['dosham'].choices        = models.Profile.DOSHAM_CHOICES
        # self.fields['job_location_type'].choices = models.Profile.JOB_LOCATION_TYPE
        # self.fields['job_state'].choices     = models.Profile.INDIAN_STATES
        # self.fields['birth_place'].choices   = models.Profile.TAMILNADU_DISTRICTS
        # self.fields['marital_status'].choices = models.Profile.MARITAL_STATUS_CHOICES

        yes_no_choices = [('', '---------')] + list(models.Profile.YES_NO_CHOICES)
        self.fields['has_father_details'].choices = yes_no_choices
        self.fields['has_mother_details'].choices = yes_no_choices
        self.fields['has_siblings'].choices       = yes_no_choices

        # if 'job_location_type' in self.fields:
        #     self.fields['job_location_type'].initial = 'India'

        self.fields['has_father_details'].initial = 'N'
        self.fields['has_mother_details'].initial = 'N'
        self.fields['has_siblings'].initial       = 'N'

        # Optional integer fields
        for f in ['no_of_brothers', 'no_of_sisters']:
            if f in self.fields:
                self.fields[f].required = False
                self.fields[f].widget.attrs['placeholder'] = 'Enter number'

        # Optional parent fields
        for f in ['father_name', 'father_occupation', 'mother_name', 'mother_occupation']:
            if f in self.fields:
                self.fields[f].required = False
                self.fields[f].widget.attrs['placeholder'] = f'Enter {self.fields[f].label.lower()}'

        # ✅ New fields — all optional plain text
        new_plain_fields = [
            'wanted', 'assets', 'saimurai',
            'erpu_thisai', 'perapu_varesai',
            'father_phone', 'mother_phone',
        ]
        for f in new_plain_fields:
            if f in self.fields:
                self.fields[f].required = False
                self.fields[f].widget.attrs['placeholder'] = f'Enter {self.fields[f].label.lower()}'

        # Apply styling to all fields
        for field_name in self.fields:
            if self.fields[field_name].label:
                self.fields[field_name].label = str(self.fields[field_name].label).upper()

            if field_name not in ('job_location_type', 'is_currently_living'):
                if not isinstance(self.fields[field_name].widget, (forms.CheckboxInput, forms.RadioSelect)):
                    if field_name not in ['has_father_details', 'has_mother_details', 'has_siblings']:
                        self.fields[field_name].widget.attrs['class'] = 'form-control form-control-solid'

        # Photo fields
        for i in range(1, 6):
            fn = f'photo{i}'
            if fn in self.fields:
                self.fields[fn].widget.attrs['class'] = 'form-control-file'
                self.fields[fn].required = False

        # Crispy layout
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(

            # BASIC DETAILS
            Fieldset(
                'BASIC DETAILS',
                Row(
                    Column('full_name',     css_class='col-md-6'),
                    Column('gender',        css_class='col-md-6'),
                ),
                Row(
                    Column('dob',           css_class='col-md-4'),
                    Column('birth_time',    css_class='col-md-4'),
                    Column('birth_place',   css_class='col-md-4'),
                ),
                Row(
                    Column('height',        css_class='col-md-4'),
                    Column('weight',        css_class='col-md-4'),
                    Column('complexion',    css_class='col-md-4'),
                ),
                Row(
                    Column('marital_status',css_class='col-md-4'),
                ),
            ),

            # CURRENT LIVING
            Fieldset(
                'CURRENT LIVING DETAILS',
                Row(
                    Column('is_currently_living', css_class='col-md-4'),
                    Column('current_location',    css_class='col-md-8'),
                ),
            ),

            # RELIGION & HOROSCOPE
            Fieldset(
                'RELIGION & HOROSCOPE',
                Row(
                    Column('religion',   css_class='col-md-4'),
                    Column('caste',      css_class='col-md-4'),
                    Column('sub_caste',  css_class='col-md-4'),
                ),
                Row(
                    Column('gothram',    css_class='col-md-4'),
                    Column('rasi',       css_class='col-md-4'),
                    Column('nakshatra',  css_class='col-md-4'),
                ),
                Row(
                    Column('laknam',     css_class='col-md-4'),
                    Column('dosham',     css_class='col-md-4'),
                    Column('saimurai',   css_class='col-md-4'),  # ✅ NEW
                ),
            ),

            # EDUCATION & CAREER
            Fieldset(
                'EDUCATION & CAREER',
                Row(
                    Column('education',     css_class='col-md-6'),
                    Column('occupation',    css_class='col-md-6'),
                ),
                Row(
                    Column('company_name',  css_class='col-md-6'),
                    Column('job_location',  css_class='col-md-6'),
                ),
                Row(
                    Column('annual_income', css_class='col-md-6'),
                ),
            ),

            # JOB LOCATION
            Fieldset(
                'JOB LOCATION',
                Row(
                    Column('job_location_type', css_class='col-md-12'),
                ),
                Row(
                    Column('job_state',   css_class='col-md-6', css_id='div_job_state'),
                    Column('job_country', css_class='col-md-6', css_id='div_job_country'),
                ),
            ),

            # FAMILY DETAILS
            Fieldset(
                'FAMILY DETAILS',
                Row(
                    Column('has_father_details', css_class='col-md-4'),
                    Column('has_mother_details', css_class='col-md-4'),
                    Column('has_siblings',        css_class='col-md-4'),
                ),
                Row(
                    Column('father_name',       css_class='col-md-6', css_id='div_father_name'),
                    Column('father_occupation', css_class='col-md-6', css_id='div_father_occupation'),
                ),
                Row(
                    Column('father_phone',      css_class='col-md-6'),  # ✅ NEW
                ),
                Row(
                    Column('mother_name',       css_class='col-md-6', css_id='div_mother_name'),
                    Column('mother_occupation', css_class='col-md-6', css_id='div_mother_occupation'),
                ),
                Row(
                    Column('mother_phone',      css_class='col-md-6'),  # ✅ NEW
                ),
                Row(
                    Column('no_of_brothers', css_class='col-md-6', css_id='div_no_of_brothers'),
                    Column('no_of_sisters',  css_class='col-md-6', css_id='div_no_of_sisters'),
                ),
                Row(
                    Column('perapu_varesai', css_class='col-md-6'),  # ✅ NEW
                ),
            ),

            # CONTACT DETAILS
            Fieldset(
                'CONTACT DETAILS',
                Row(
                    Column('phone',          css_class='col-md-4'),
                    Column('whatsapp_number',css_class='col-md-4'),
                    Column('email',          css_class='col-md-4'),
                ),
                Row(
                    Column('address',        css_class='col-md-12'),
                ),
                Row(
                    Column('city',           css_class='col-md-4'),
                    Column('state',          css_class='col-md-4'),
                    Column('country',        css_class='col-md-4'),
                ),
                Row(
                    Column('pincode',        css_class='col-md-4'),
                ),
            ),

            # ADDITIONAL DETAILS  ✅ NEW SECTION
            Fieldset(
                'ADDITIONAL DETAILS',
                Row(
                    Column('wanted',      css_class='col-md-4'),
                    Column('assets',      css_class='col-md-4'),
                    Column('erpu_thisai', css_class='col-md-4'),
                ),
            ),

            # PHOTOS
            Fieldset(
                'PHOTOS',
                HTML("""
                <div class="card shadow-sm mt-4">
                    <div class="card-header bg-dark text-white text-center">
                        <h5 class="mb-0">📸 Upload Photos</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                """),
                Row(
                    Column('photo1', css_class='col-md-4 mb-4'),
                    Column('photo2', css_class='col-md-4 mb-4'),
                    Column('photo3', css_class='col-md-4 mb-4'),
                ),
                Row(
                    Column('photo4', css_class='col-md-4 mb-4'),
                    Column('photo5', css_class='col-md-4 mb-4'),
                ),
                HTML("""
                        </div>
                    </div>
                </div>
                """),
            ),

            # ABOUT
            Fieldset(
                'ABOUT',
                Row(
                    Column('bio',     css_class='col-md-6'),
                    Column('hobbies', css_class='col-md-6'),
                ),
            ),

            ButtonHolder(
                Submit('submit', 'SAVE PROFILE', css_class='btn btn-primary')
            )
        )

    def clean_dob(self):
        dob = self.cleaned_data.get('dob')
        if dob:
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if age < 18:
                raise forms.ValidationError("You must be at least 18 years old to register.")
        return dob

    def clean_no_of_brothers(self):
        value = self.cleaned_data.get('no_of_brothers')
        if value == '' or value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def clean_no_of_sisters(self):
        value = self.cleaned_data.get('no_of_sisters')
        if value == '' or value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def clean_annual_income(self):
        value = self.cleaned_data.get('annual_income')
        if value == '' or value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def clean(self):
        cleaned_data = super().clean()

        has_father   = cleaned_data.get('has_father_details') == 'Y'
        has_mother   = cleaned_data.get('has_mother_details') == 'Y'
        has_siblings = cleaned_data.get('has_siblings') == 'Y'

        job_location_type = cleaned_data.get('job_location_type')
        if job_location_type == 'India':
            cleaned_data['job_country'] = None
        elif job_location_type == 'Other':
            cleaned_data['job_state'] = None

        if has_father:
            if not cleaned_data.get('father_name'):
                self.add_error('father_name', 'Father name is required when father details are enabled')
        else:
            cleaned_data['father_name']       = ''
            cleaned_data['father_occupation'] = ''
            cleaned_data['father_phone']      = ''  # ✅ NEW

        if has_mother:
            if not cleaned_data.get('mother_name'):
                self.add_error('mother_name', 'Mother name is required when mother details are enabled')
        else:
            cleaned_data['mother_name']       = ''
            cleaned_data['mother_occupation'] = ''
            cleaned_data['mother_phone']      = ''  # ✅ NEW

        if has_siblings:
            no_of_brothers = cleaned_data.get('no_of_brothers')
            no_of_sisters  = cleaned_data.get('no_of_sisters')
            if (not no_of_brothers or no_of_brothers == 0) and (not no_of_sisters or no_of_sisters == 0):
                self.add_error('no_of_brothers', 'Please specify number of brothers or sisters')
        else:
            cleaned_data['no_of_brothers'] = None
            cleaned_data['no_of_sisters']  = None

        return cleaned_data
        

from django import forms
from .models import Wishlist

class WishlistForm(forms.ModelForm):
    """Form for shortlisting profiles"""
    
    class Meta:
        model = Wishlist
        fields = []  # No fields needed since we only need profile_id
from django import forms

class ProfileUploadForm(forms.Form):
    file = forms.FileField()
