import sys
from django import forms
from django.forms.widgets import HiddenInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder
from crispy_forms.helper import *
from crispy_forms.layout import *
from crispy_forms.bootstrap import *
from mck_auth import models



class AccountTypeRoleCreateUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        mode = kwargs.pop('mode', None)
        super(AccountTypeRoleCreateUpdateForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].label = str(self.fields[field_name].label).upper()
            self.fields[field_name].widget.attrs['class'] = "form-control form-control-solid"
            
            if field_name == "is_default":
                self.fields[field_name].widget.attrs['class'] = "form-control form-control-solid d-inline-block"

        if mode == "edit":
            instance = kwargs.get('instance', None)
        save_button_name = "SAVE"

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                '',
                Row(Column(Field('name'), css_class='col-9'), Column(Field('is_default'), css_class='form-check form-check-custom form-check-success form-check-solid pe-2 my-10 col-3'), css_class='col-12'),
            ),
            ButtonHolder(
                Div(HTML('<a class="btn btn-secondary me-3" href="javascript:void();" onclick="history.back()">CANCEL</a>'),Submit('create_button', save_button_name, css_class='btn btn-lg btn-primary'),
                            css_class="d-flex text-right justify-content-end pt-10 col-12"), css_class="row col-12 pe-5",
            )
        )
    class Meta:
        model = models.AccountTypeRole
        exclude = ['account_type', 'created_on', 'updated_on', 'created_by', 'updated_by', 'datamode']

