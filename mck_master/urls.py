
from django.urls import path
from mck_master import views

app_name = "mck_master"

urlpatterns = [

    # Support Page Content
    path('support_page_content/list/', views.SupportPageContentList.as_view(),name='mck_support_page_content_list'),
    path('support_page_content/create/', views.SupportPageContentCreateView.as_view(),name='mck_support_page_content_create'),
    path('support_page_content/<id>/edit/', views.SupportPageContentUpdateView.as_view(),name='mck_support_page_content_update'),
    path('support_page_content/<id>/delete/', views.SupportPageContentDeleteView.as_view(),name='mck_support_page_content_delete'),

    # Category
    path('category/list/', views.CategoryList.as_view(),name='mck_category_list'),
    path('category/create/', views.CategoryCreateView.as_view(),name='mck_category_create'),
    path('category/<id>/edit/', views.CategoryUpdateView.as_view(),name='mck_category_update'),
    path('category/<id>/delete/', views.CategoryDeleteView.as_view(),name='mck_category_delete'),

    # Sub Category
    path('sub_category/list/', views.SubCategoryList.as_view(),name='mck_sub_category_list'),
    path('sub_category/create/', views.SubCategoryCreateView.as_view(),name='mck_sub_category_create'),
    path('sub_category/<id>/edit/', views.SubCategoryUpdateView.as_view(),name='mck_sub_category_update'),
    path('sub_category/<id>/delete/', views.SubCategoryDeleteView.as_view(),name='mck_sub_category_delete'),
    path('ajax/category-based/sub_category/', views.CategoryBasedSubCategoryAjax.as_view(),name='mck_category_based_sub_categories'),

    path('states/', views.StateList.as_view(), name='mck_state_list'),
    path('states/create/', views.StateCreateView.as_view(), name='mck_state_create'),
    path('states/update/<id>/edit/', views.StateUpdateView.as_view(), name='mck_state_update'),
    path('states/delete/<id>/delete/', views.StateDeleteView.as_view(), name='mck_state_delete'),
    
    
    path('citys/', views.CityList.as_view(), name='mck_city_list'),
    path('citys/create/', views.CityCreateView.as_view(), name='mck_city_create'),
    path('citys/update/<id>/edit/', views.CityUpdateView.as_view(), name='mck_city_update'),
    path('citys/delete/<id>/delete/', views.CityDeleteView.as_view(), name='mck_city_delete'),

    # Banner
    path('banner/list/', views.BannerList.as_view(),name='mck_banner_list'),
    path('banner/create/', views.BannerCreateView.as_view(),name='mck_banner_create'),
    path('banner/<id>/edit/', views.BannerUpdateView.as_view(),name='mck_banner_update'),
    path('banner/<id>/delete/', views.BannerDeleteView.as_view(),name='mck_banner_delete'),

    # Gallery
    path('gallery/list/', views.GalleryList.as_view(),name='mck_gallery_list'),
    path('gallery/create/', views.GalleryCreateView.as_view(),name='mck_gallery_create'),
    path('gallery/<id>/edit/', views.GalleryUpdateView.as_view(),name='mck_gallery_update'),
    path('gallery/<id>/delete/', views.GalleryDeleteView.as_view(),name='mck_gallery_delete'),
    
    
    path('offer/list/', views.OfferList.as_view(), name='mck_offer_list'),
    path('offer/create/', views.OfferCreateView.as_view(), name='mck_offer_create'),
    path('offer/<id>/edit/', views.OfferUpdateView.as_view(), name='mck_offer_update'),
    path('offer/<id>/delete/', views.OfferDeleteView.as_view(), name='mck_offer_delete'),


    path('client_feedback/list/', views.ClientFeedbackList.as_view(), name='mck_client_feedback_list'),
    path('client_feedback/create/', views.ClientFeedbackCreateView.as_view(), name='mck_client_feedback_create'),
    path('client_feedback/<id>/edit/', views.ClientFeedbackUpdateView.as_view(), name='mck_client_feedback_update'),
    path('client_feedback/<id>/delete/', views.ClientFeedbackDeleteView.as_view(), name='mck_client_feedback_delete'),

    path('profile/list/', views.ProfileList.as_view(), name='mck_profile_list'),
    path('profile/create/', views.ProfileCreateView.as_view(), name='mck_profile_create'),
    path('profile/<id>/edit/', views.ProfileUpdateView.as_view(), name='mck_profile_update'),
    path('profile/<id>/delete/', views.ProfileDeleteView.as_view(), name='mck_profile_delete'),
    path('profile/download/', views.export_profiles_excel, name='mck_profile_download'),
    path('profile/upload/', views.upload_profiles_excel, name='mck_profile_upload'),
    path(
    'profile/filter-options/',
    views.profile_filter_options,
    name='mck_profile_filter_options'
),
    path(
        'profile/detail/<int:profile_id>/',
        views.ProfileDetailJsonView.as_view(),
        name='mck_profile_detail_json'
    )
  


    
]    