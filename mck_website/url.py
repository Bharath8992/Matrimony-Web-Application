
from django.urls import path
from mck_website import views

app_name = "mck_website"

urlpatterns = [

    # path(".well-known/pki-validation/0021C33903EBC802E268A3D626130F22.txt", views.pki_validation_view, name="pki_validation"),
    path('', views.HomePage.as_view(), name='home_page'),
    path('about/', views.AboutPage.as_view(), name='about_page'),
    path('pricing/', views.PropertyLegalServicesPage.as_view(), name='pricing'),
    path('our-services/', views.OurServicesPage.as_view(), name='our_services_page'),
    path('privacy-policy/', views.PrivacyPolicyPage.as_view(), name='privacy_policy_page'),
    path('terms/', views.TermsPage.as_view(), name='terms_page'),
    path('solar/',views.SolarPage.as_view(), name='solar_page'),
    path('fencing/',views.FencingPage.as_view(), name='fencing_page'),
    path('land-levelling/',views.LandLevellingPage.as_view(), name='land_levelling_page'),
    path("Profile-detail/", views.ProfilePage.as_view(), name="mck_property_page"),
    path("mutual-match/", views.MutualMatchView.as_view(), name="mutual_match"),
    path("communtiy-match/", views.CommunitySearchPage.as_view(), name="community_match"),
    path("new-match/",views.Newmatches.as_view(), name="new_match"),

    path('property-details/<int:pk>/', views.PropertyDetailPage.as_view(), name='property_detail'),
    path(
        "property_create/",
        views.PropertyCreatePage.as_view(),
        name="mck_property_create_page",
    ),
    path(
        "maintenances/",
        views.MaintenancesCreatePage.as_view(),
        name="property_maintenance_page",
    ),
    path(
        "enquiry/",
        views.EnquiryCreatePage.as_view(),
        name="property_enquiry_page",
    ),
    path('ajax/property/save/', views.PropertySaveView.as_view(),name='mck_ajax_property_save'),
    path('ajax/maintenances/save/', views.MaintenanceSaveView.as_view(),name='mck_ajax_maintenance_save'),
    path('ajax/lead/save/', views.EnquirySaveView.as_view(),name='mck_ajax_enquiry_save'),


    # path(
    #     "profile/",
    #     views.EnquiryCreatePage.as_view(),
    #     name="profile_page",
    # ),

#    path('ajax/profile/save/', views.ProfileSaveView.as_view(),name='mck_ajax_profile_save'),
#    path("profile/<int:pk>/", views.ProfileDetailPage.as_view(), name="profile_detail"),
# Correct order
            path("profile/<int:pk>/", views.ProfileDetailPage.as_view(), name="profile_detail"),
            path("profile/", views.EnquiryCreatePage.as_view(), name="profile_page"),
            path("my-profile/", views.MyProfilePage.as_view(), name="my_profile"),
            path("ajax/my-profile/save/", views.ajax_my_profile_save, name="ajax_my_profile_save"),
            # mck_website/urls.py
            # path(
            #     "ajax/my-profile/save/",
            #     views.ajax_profile_save,
            #     name="mck_ajax_my_profile_save"
            # ),

            path('ajax/profile/save/', views.ajax_profile_save, name='mck_ajax_profile_save'),


                # Interest/Wishlist URLs
    path('my-wishlist/', views.my_wishlist, name='my_wishlist'),
    path('ajax/toggle-wishlist/', views.toggle_wishlist, name='toggle_wishlist'),
    path('ajax/get-wishlist/', views.get_wishlist, name='get_wishlist'),
    path('ajax/remove-from-wishlist/<int:wishlist_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),


    path("Gallery/",views.GalleryPageView.as_view(), name="gallery"),
    path("Sucess-Stories/",views.SucessStoryPageView.as_view(), name="sucess-storeis"),
    path("Support-page/",views.SupportPageView.as_view(), name="support"),
    path("Contact-us/",views.ContactPageView.as_view(), name="contact-us"),


    path('profiles/filter/', views.ProfileFilterView.as_view(), name='profile_filter'),


    path('profile/complete/', views.ProfileCompletionView.as_view(), name='profile_completion'),
    path('payment/', views.PaymentGatewayView.as_view(), name='payment_gateway'),
    path('payment/success/', views.PaymentSuccessView.as_view(), name='payment_success'),
    path('payment/failure/', views.PaymentFailureView.as_view(), name='payment_failure'),
    path('payment_callback', views.PaymentCallbackView.as_view(), name='payment_callback'),
    path('payment/success/page/', views.PaymentSuccessPageView.as_view(), name='payment_success_page'),
]    