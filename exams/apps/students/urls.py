app_name = 'students'
from django.urls import path
from .views import TestListView, TakenTestListView, take_test


urlpatterns = [
    path('', TestListView.as_view(), name='test_list'),
    path('taken/', TakenTestListView.as_view(),name='taken_test_list'),
    path('test/<int:pk>/', take_test, name='take_test')
]