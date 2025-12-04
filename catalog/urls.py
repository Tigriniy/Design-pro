from django.urls import path
from . import  views
from django.contrib.auth import views as auth_views
from .views import register

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('apply/', views.ApplicationCreateView.as_view(), name='apply'),
    path('my-applications/', views.ApplicationListView.as_view(), name='my_applications'),
    path('applications/<int:pk>/delete/', views.ApplicationDeleteView.as_view(), name='application_delete'),

    path('profile/', views.profile, name='profile'),

    # только для админа, то есть is_staff
    path('admin/applications/', views.admin_applications, name='admin_applications'),
    path('admin/categories/', views.admin_categories, name='admin_categories'),
    path('admin/categories/create/', views.admin_category_create, name='admin_category_create'),
    path('admin/categories/<int:pk>/edit/', views.admin_category_edit, name='admin_category_edit'),
    path('admin/categories/<int:pk>/delete/', views.admin_category_delete, name='admin_category_delete'),
]



