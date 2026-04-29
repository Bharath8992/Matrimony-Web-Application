
from django.urls import path
from mck_admin_console import views

app_name = "svm_admin_console"

urlpatterns = [
    path('', views.LandingPage.as_view(), name='mck_landing_page'),
    path('dashboard/', views.DashboardView.as_view(), name='mck_dashboard'),
    
    path('faq_category/list/', views.FAQCategoryList.as_view(),name='mck_faq_category_list'),
    path('faq_category/create/', views.FAQCategoryCreateView.as_view(),name='mck_faq_category_create'),
    path('faq_category/<id>/edit/', views.FAQCategoryUpdateView.as_view(),name='mck_faq_category_update'),
    path('faq_category/<id>/delete/', views.FAQCategoryDeleteView.as_view(),name='mck_faq_category_delete'),
    
    path('gallery/list/', views.GalleryList.as_view(),name='mck_gallery_list'),
    path('gallery/create/', views.GalleryCreateView.as_view(),name='mck_gallery_create'),
    path('gallery/<id>/edit/', views.GalleryUpdateView.as_view(),name='mck_gallery_update'),
    path('gallery/<id>/delete/', views.GalleryDeleteView.as_view(),name='mck_gallery_delete'),
    
    path('contact/list/', views.ContactListView.as_view(), name='mck_contact_list'),
    path('contact/create/', views.ContactCreateView.as_view(), name='mck_contact_create'),
    path('contact/<id>/edit/', views.ContactUpdateView.as_view(), name='mck_contact_update'),
    path('contact/<id>/delete/', views.ContactDeleteView.as_view(), name='mck_contact_delete'),
    
    path('testimonial/list/', views.TestimonialListView.as_view(), name='mck_testimonial_list'),
    path('testimonial/create/', views.TestimonialCreateView.as_view(), name='mck_testimonial_create'),
    path('testimonial/<id>/edit/', views.TestimonialUpdateView.as_view(), name='mck_testimonial_update'),
    path('testimonial/<id>/delete/', views.TestimonialDeleteView.as_view(), name='mck_testimonial_delete'),

]