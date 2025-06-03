from django.urls import path
from .views import UpdateUserView,DeleteUserView,RetrieveUserView,CreateClientAdminView,CreateSupplierView,CreateEndUserView,CreateMasterAdminView,ListClientAdminView,ListSupplierView,ListEndUserView,OrganizationUserListView
from rest_framework.authtoken.views import obtain_auth_token
urlpatterns = [
    # for admin rights
    path('master-admin/create/',CreateMasterAdminView.as_view(),name='master-admin-create'),
    path('client-admin/create/',CreateClientAdminView.as_view(),name='client-admin-create'),
    path('supplier/create/',CreateSupplierView.as_view(),name='supplier-create'),
    path('end-user/create/',CreateEndUserView.as_view(),name='end-user-create'),
    path('client-admin/list/',ListClientAdminView.as_view(),name='client-admin-list'),
    path('supplier/list/',ListSupplierView.as_view(),name='supplier-list'),
    path('end-user/list/',ListEndUserView.as_view(),name='end-user-list'),
    ##CRUD
    path('user/<int:pk>/',RetrieveUserView.as_view(),name='user-retrieve'),
    path('user/<int:pk>/update/',UpdateUserView.as_view(),name='user-update'),
    path('user/<int:pk>/delete/',DeleteUserView.as_view(),name='user-delete'),
    path('organization/<str:org_name>/users/',OrganizationUserListView.as_view(),name='organization-user-list'),
    path('login/',obtain_auth_token,name='api_auth_token'),
]