
from django.urls import path
from mck_auth import views

app_name = "mck_auth"

urlpatterns = [
    path('', views.LandingPage.as_view(), name='mck_landing_page'),
    path('login/', views.SignIn.as_view(), name='mck_signin'),
    path('logout/',views.LogOut.as_view(),name='mck_logout'),
    
    path('website/login/', views.WebsiteSignIn.as_view(), name='website_signin'),
    path('website/register/', views.WebsiteSignUp.as_view(), name='website_signup'),
    path('website/verify-otp/', views.OTPVerificationView.as_view(), name='verify_otp'),
    path('website/resend-otp/', views.ResendOTPView.as_view(), name='resend_otp'),
    path('website/logout/', views.WebsiteLogOut.as_view(), name='website_logout'),
    # ... existing patterns
    path('website/password-reset/', views.WebsitePasswordReset.as_view(), name='website_password_reset'),

    path('mck-auth/role/list/', views.AccountTypeRoleList.as_view(),name='mck_role_list'),
    path('mck-auth/role/create/', views.AccountTypeRoleCreateView.as_view(),name='mck_role_create'),
    path('mck-auth/role/<id>/edit/', views.AccountTypeRoleUpdateView.as_view(),name='mck_role_update'),
    path('mck-auth/role/<id>/delete/', views.AccountTypeRoleDeleteView.as_view(),name='mck_role_delete'),
    path('mck-auth/role/<id>/update-permission/', views.AccountTypeRoleUpdatePermissionView.as_view(),name='mck_role_update_permission'),

]