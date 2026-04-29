import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

PLAN_CHOICES = [
    ('THREE_MONTH', '3 Months'),
    ('SIX_MONTH',   '6 Months'),
    ('ONE_YEAR',    '1 Year'),
]

STATUS_CHOICES = [
    ('PENDING',  'Pending Review'),
    ('APPROVED', 'Approved'),
    ('REJECTED', 'Rejected'),
]


class UPIPaymentRequest(models.Model):
    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user          = models.ForeignKey(User, on_delete=models.CASCADE, related_name='upi_payments')
    plan          = models.CharField(max_length=20, choices=PLAN_CHOICES)
    amount        = models.DecimalField(max_digits=8, decimal_places=2)
    utr_number    = models.CharField(max_length=50, blank=True,
                                     help_text="UTR / Transaction reference number (optional)")
    screenshot    = models.ImageField(upload_to='upi_screenshots/%Y/%m/')
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    admin_note    = models.TextField(blank=True)
    submitted_at  = models.DateTimeField(auto_now_add=True)
    reviewed_at   = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name        = 'UPI Payment Request'
        verbose_name_plural = 'UPI Payment Requests'

    def __str__(self):
        return f"{self.user} | {self.plan} | {self.status} | {self.submitted_at:%d %b %Y}"

    @property
    def plan_label(self):
        return dict(PLAN_CHOICES).get(self.plan, self.plan)

    @property
    def amount_display(self):
        return f"₹{self.amount:,.0f}"