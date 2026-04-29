import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from config import app_gv as gv
from mck_master.models import MasterPermission, Payment


# class User(AbstractUser):
#     mobile_number = PhoneNumberField(blank=True, null=True)

#     def __str__(self):
#         if self.username:
#             return self.username
#         elif self.first_name:
#             return self.first_name+" "+self.last_name
#         elif self.email:
#             return self.email
#         elif self.mobile_number:
#             return self.mobile_number.as_international
#         else:
#             return "User-"+str(self.id)


from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField

class User(AbstractUser):
    mobile_number = PhoneNumberField(blank=True, null=True)
    
    # Add these two new fields for registration tracking
    is_profile_completed = models.BooleanField(default=False)
    
    def __str__(self):
        if self.username:
            return self.username
        elif self.first_name:
            return self.first_name + " " + self.last_name
        elif self.email:
            return self.email
        elif self.mobile_number:
            return self.mobile_number.as_international
        else:
            return "User-" + str(self.id)
    
    # Add these helper methods
    @property
    def has_paid(self):
        """Check if user has any completed payment"""
        return self.payments.filter(status='COMPLETED').exists()
    
    @property
    def latest_payment(self):
        """Get user's latest completed payment"""
        return self.payments.filter(status='COMPLETED').first()
    
    @property
    def pending_payment(self):
        """Get user's pending payment if any"""
        return self.payments.filter(status='PENDING').first()
    
    @property
    def registration_status(self):
        """Get user's registration status"""
        if not self.is_profile_completed:
            return "PROFILE_PENDING"
        elif not self.has_paid:
            return "PAYMENT_PENDING"
        else:
            return "COMPLETED"

    @property
    def active_plan(self):
        """Return the user's latest COMPLETED payment (= active plan)"""
        return self.payments.filter(status='COMPLETED').order_by('-payment_date').first()
 
    @property
    def profile_view_limit(self):
        """How many profiles this user is allowed to view"""
        plan = self.active_plan
        if not plan:
            return 0
        return Payment.PLAN_CONFIG.get(plan.plan, {}).get('profile_limit', 5)
 
    @property
    def has_paid(self):
        return self.payments.filter(status='COMPLETED').exists()
 
    @property
    def can_upgrade(self):
        plan = self.active_plan
        if not plan:
            return True
        return plan.plan != 'PREMIUM'
    
    # ============================================================================
# Add these properties to your custom User model (mck_auth/models.py or wherever
# your AUTH_USER_MODEL is defined).
# They replace / upgrade the existing has_paid, active_plan, etc. properties.
# ============================================================================

from django.utils import timezone


# ─── Paste these inside your User model class ───────────────────────────────

@property
def active_plan(self):
    """
    Returns the most recent COMPLETED, non-expired Payment, or None.
    """
    return (
        self.payments
            .filter(status='COMPLETED')
            .order_by('-payment_date')
            .first()
        # filter in Python so we can use the is_active property
    ) and next(
        (p for p in self.payments.filter(status='COMPLETED').order_by('-payment_date') if p.is_active),
        None
    )

# ── Cleaner version (avoids double query) ──────────────────────────────────
# Replace the two blocks above with this single property:

@property
def active_plan(self):
    """Most recent COMPLETED payment that is still within its 6-month window."""
    now = timezone.now()
    return (
        self.payments
            .filter(
                status='COMPLETED',
                valid_until__gt=now,   # not yet expired
            )
            .order_by('-payment_date')
            .first()
    ) or (
        # Fallback: legacy rows that have no valid_until set
        self.payments
            .filter(status='COMPLETED', valid_until__isnull=True)
            .order_by('-payment_date')
            .first()
    )

    @property
    def has_paid(self):
        """True if the user has an active (non-expired) completed payment."""
        return self.active_plan is not None

    @property
    def profile_view_limit(self):
        """View limit from active plan (0 if no active plan)."""
        plan = self.active_plan
        return plan.profile_limit if plan else 0

    @property
    def can_upgrade(self):
        """True if the user can move to a higher plan."""
        plan = self.active_plan
        if not plan:
            return False
        return plan.plan != 'PREMIUM'

    @property
    def plan_days_remaining(self):
        """How many days are left on the active plan (0 if none/expired)."""
        plan = self.active_plan
        return plan.days_remaining if plan else 0


class AccountType(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=6, unique=True, db_index=True)
    is_default = models.BooleanField(default=False)
    is_registration_allowed = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    datamode = models.CharField(max_length=20, default='A', choices=gv.DATAMODE_CHOICES)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'account_type'


class AccountTypeRole(models.Model):
    account_type = models.ForeignKey(AccountType, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    is_default = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User,related_name = "%(class)s_createdby", on_delete=models.CASCADE)
    updated_by = models.ForeignKey(User,related_name = "%(class)s_updatedby", on_delete=models.CASCADE)
    datamode = models.CharField(max_length=20, default='A', choices=gv.DATAMODE_CHOICES)

    def __str__(self):
        return "{0}".format(self.name)

    class Meta:
        db_table = 'account_type_role'


class AccountTypeRolePermission(models.Model):
    account_type_role = models.ForeignKey(AccountTypeRole, on_delete=models.CASCADE)
    master_permission = models.ForeignKey(MasterPermission, on_delete=models.CASCADE)
    has_permission = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User,related_name = "%(class)s_createdby", on_delete=models.CASCADE)
    updated_by = models.ForeignKey(User,related_name = "%(class)s_updatedby", on_delete=models.CASCADE)
    datamode = models.CharField(max_length=20, default='A', choices=gv.DATAMODE_CHOICES)

    def __str__(self):
        return f"{self.account_type_role.name} - {self.master_permission.class_name} - {self.has_permission}"

    class Meta:
        db_table = 'account_type_role_permission'


class Account(models.Model):
    uid = models.CharField(max_length=20, unique=True, editable=False, db_index=True)
    account_type = models.ForeignKey(AccountType, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, db_index=True)
    created_by = models.ForeignKey(User, related_name="%(class)s_createdby", on_delete=models.CASCADE)
    updated_by = models.ForeignKey(User, related_name='%(class)s_updated_by', on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    datamode = models.CharField(max_length=20, default='A', choices=gv.DATAMODE_CHOICES)

    def __str__(self):
        return "{0}({1})".format(self.name, self.uid)

    def save(self, *args, **kwargs):
        super(Account, self).save(*args, **kwargs)
        if not self.uid:
            self.uid  = "mck-A%04d" % (int(self.id))
            super(Account, self).save()

    class Meta:
        db_table = 'account'


class AccountUser(models.Model):
    uid = models.CharField(max_length=20, unique=True, editable=False, db_index=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(AccountTypeRole, on_delete=models.CASCADE)
    is_default_account = models.BooleanField(default=True)
    is_current_account = models.BooleanField(default=True)
    last_active_on = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(User, related_name='%(class)s_created_by', on_delete=models.CASCADE)
    updated_by = models.ForeignKey(User, related_name='%(class)s_updated_by', on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    datamode = models.CharField(max_length=20, default='A', choices=gv.DATAMODE_CHOICES)

    def __str__(self):
        return "{0}({1})".format(self.user.first_name, self.uid)

    def save(self):
        super(AccountUser, self).save()
        if not self.uid:
            self.uid  = "mck-AU%04d" % (int(self.id))
            super(AccountUser, self).save()

    class Meta:
        db_table = 'account_user'

# models.py (in your mck_auth app or create a new app for OTP)
import random
import string
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class EmailOTP(models.Model):
    """
    Model to store email OTPs for verification
    """
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.otp:
            self.otp = ''.join(random.choices(string.digits, k=6))
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)  # OTP valid for 10 minutes
        super().save(*args, **kwargs)
    
    def is_valid(self):
        """Check if OTP is still valid (not expired and not verified)"""
        return not self.is_verified and timezone.now() <= self.expires_at
    
    def __str__(self):
        return f"{self.email} - {self.otp} - {'Verified' if self.is_verified else 'Pending'}"