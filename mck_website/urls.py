from django.urls import path
from mck_website import views

app_name = "mck_website"

urlpatterns = [

    # --------------------
    # Main Pages
    # --------------------
    path('', views.HomePage.as_view(), name='home_page'),
    path('about/', views.AboutPage.as_view(), name='about_page'),
    path('pricing/', views.PropertyLegalServicesPage.as_view(), name='pricing'),
    path('our-services/', views.OurServicesPage.as_view(), name='our_services_page'),
    path('privacy-policy/', views.PrivacyPolicyPage.as_view(), name='privacy_policy_page'),
    path('terms/', views.TermsPage.as_view(), name='terms_page'),
    path("Sucess-Stories/",views.SucessStoryPageView.as_view(), name="sucess-storeis"),


    path("Profile-detail/", views.ProfilePage.as_view(), name="mck_property_page"),

    # --------------------
    # Profiles
    # --------------------
    path("profile/", views.EnquiryCreatePage.as_view(), name="profile_page"),
    path("profile/<int:pk>/", views.ProfileDetailPage.as_view(), name="profile_detail"),
    path("my-profile/", views.MyProfilePage.as_view(), name="my_profile"),
    path("profile/complete/", views.ProfileCompletionView.as_view(), name='profile_completion'),

    # --------------------
    # Profile AJAX
    # --------------------
    path('ajax/profile/save/', views.ajax_profile_save, name='mck_ajax_profile_save'),
    path('ajax/my-profile/save/', views.ajax_my_profile_save, name='ajax_my_profile_save'),

    # --------------------
    # Matching System
    # --------------------
    path("mutual-match/", views.MutualMatchView.as_view(), name="mutual_match"),
    path("community-match/", views.CommunitySearchPage.as_view(), name="community_match"),
    path("new-match/", views.Newmatches.as_view(), name="new_match"),
    path('profiles/filter/', views.ProfileFilterView.as_view(), name='profile_filter'),

    # --------------------
    # Wishlist / Interest
    # --------------------
    path('my-wishlist/', views.my_wishlist, name='my_wishlist'),
    path('ajax/toggle-wishlist/', views.toggle_wishlist, name='toggle_wishlist'),
    path('ajax/get-wishlist/', views.get_wishlist, name='get_wishlist'),
    path('ajax/remove-from-wishlist/<int:wishlist_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

    # --------------------
    # Pages
    # --------------------
    path("gallery/", views.GalleryPageView.as_view(), name="gallery"),
    path("success-stories/", views.SucessStoryPageView.as_view(), name="sucess_storeis"),
    path("support-page/", views.SupportPageView.as_view(), name="support"),
    path("vip-page/", views.VIPPageView.as_view(), name="vip"),
    path("package-page/", views.PackagePageView.as_view(), name="package"),
    path('contact-us/', views.ContactPageView.as_view(), name='contact-us'),
    path('contact-us/ajax-submit/', views.ajax_contact_submit, name='contact_ajax_submit'),

    # --------------------
    # Payment Gateway
    # --------------------
    path('payment/', views.PaymentGatewayView.as_view(), name='payment_gateway'),
    path('payment/success/', views.PaymentSuccessView.as_view(), name='payment_success'),       # POST handler
    path('payment/success/page/', views.PaymentSuccessPageView.as_view(), name='payment_success_page'),  # Display page
    path('payment/failure/', views.PaymentFailureView.as_view(), name='payment_failure'),
  
    path('payment/callback/', views.PaymentCallbackView.as_view(), name='payment_callback'),

    # urls.py
    path('internal/payments/', views.payment_dashboard, name='payment_dashboard'),


    path("about-us/", views.AboutUsView.as_view(), name="about_us"),
    path("privacy-policy/", views.PrivacyPolicyView.as_view(), name="privacy_policy"),
    path("terms/", views.TermsView.as_view(), name="terms&condition"),
    path("refund-policy/", views.RefundPolicyView.as_view(), name="refund_policy"),
    
    path('payment/upi/upload/', views.upi_upload_screenshot, name='upi_upload_screenshot'),

]