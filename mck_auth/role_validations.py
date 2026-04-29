import sys
from phonenumber_field.phonenumber import PhoneNumber
from django.urls import reverse
from django.forms.models import model_to_dict
from config import app_utils
from config import app_logger

from mck_auth.models import *

log_name = "app"
logger = app_logger.createLogger(log_name)


@app_logger.functionlogs(log=log_name)
def validate_requested_user_function(request):
    has_permission = True #False
    accountuser = None
    try:
        if request.user.is_authenticated:
            class_name = request.resolver_match._func_path.split(".")[-1]
            accountuser = AccountUser.objects.filter(user=request.user, is_current_account=True, datamode='A').first()
            if accountuser and AccountTypeRolePermission.objects.filter(account_type_role=accountuser.role, master_permission__class_name=class_name, has_permission=True).exists():
                has_permission = True
    except Exception as e:
        exc_type, exc_obj, exc_traceback = sys.exc_info()
        logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
    return has_permission, accountuser
