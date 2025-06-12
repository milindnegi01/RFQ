from django.urls import path
from .views import (
     CreateSupplierView, CreateEndUserView,
     ListSupplierView,
    ListEndUserView, CookieTokenObtainPairView, LogoutView,
    CreateCommodityView, ListCommodityView, UpdateCommodityView,CreateRFQImportView,ListRFQImportView,RFQManagementCreateView,RFQManagementListView,RFQManagementDetailView,AutoPromoteRFQView,ClientAdminRFQImportView   
)
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .api_root import CustomAPIRootView

urlpatterns = [
    path('', CustomAPIRootView.as_view(), name='api-root'),
    # for admin rights
    # path('master-admin/create/',CreateMasterAdminView.as_view(),name='master-admin-create'),
    # path('client-admin/create/',CreateClientAdminView.as_view(),name='client-admin-create'),
    path('supplier/create/',CreateSupplierView.as_view(),name='supplier-create'),
    path('end-user/create/',CreateEndUserView.as_view(),name='end-user-create'),
    # path('client-admin/list/',ListClientAdminView.as_view(),name='client-admin-list'),
    path('supplier/list/',ListSupplierView.as_view(),name='supplier-list'),
    path('end-user/list/',ListEndUserView.as_view(),name='end-user-list'),
    path('api/clientadmin/view-rfq-imports/', ClientAdminRFQImportView.as_view(), name='clientadmin-view-rfq-imports'),

    ##CRUD
    # path('user/<int:pk>/',RetrieveUserView.as_view(),name='user-retrieve'),
    # path('user/<int:pk>/update/',UpdateUserView.as_view(),name='user-update'),
    # path('user/<int:pk>/delete/',DeleteUserView.as_view(),name='user-delete'),
    # path('organization/<str:org_name>/users/',OrganizationUserListView.as_view(),name='organization-user-list'),
    path('login/',CookieTokenObtainPairView.as_view(),name='api_auth_token'),
    path('token/refresh/',TokenRefreshView.as_view(),name='token_refresh'),
    path('token/verify/',TokenVerifyView.as_view(),name='token_verify'),
    path('api/logout/',LogoutView.as_view(),name='logout'),
    # path('',login,name='login'),
    # path('api/login/',CookieTokenObtainPairView.as_view(),name='token_obtain_pair'),
    ##commodity list view
    path('commodities/', ListCommodityView.as_view(), name='list-commodities'),
    path('commodities/create/', CreateCommodityView.as_view(), name='create-commodity'),
    path('commodities/<int:pk>/update/', UpdateCommodityView.as_view(), name='update-commodity'),
    # path('commodities/<int:pk>/delete/', DeleteCommodityView.as_view(), name='delete-commodity'),
    path('rfq/import/create/',CreateRFQImportView.as_view(),name='rfq-import-create'),
    path('rfq/import/list/',ListRFQImportView.as_view(),name='rfq-import-list'),
    #rfqmanagement
    path('rfq-management/create/', RFQManagementCreateView.as_view(), name='create-rfq-management'),
    path('rfq-management/list/', RFQManagementListView.as_view(), name='list-rfq-management'),
    path('rfq-management/<int:pk>/', RFQManagementDetailView.as_view(), name='detail-rfq-management'),
    # urls.py

    path('api/auto-promote-rfq/', AutoPromoteRFQView.as_view(), name='auto-promote-rfq'),

]