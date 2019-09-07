app_name = "teachers"
from django.urls import path
from .views import (TestListView, TestCreateView, TestUpdateView,
                    TestResultsView, TestDeleteView, QuestionDeleteView,
                    question_add, question_change)

urlpatterns = [
    path('', TestListView.as_view(), name='test_change_list'),
    path('test/add/', TestCreateView.as_view(), name='test_add'),
    path('test/<int:pk>/', TestUpdateView.as_view(), name='test_change'),
    path('test/<int:pk>/delete/', TestDeleteView.as_view(),
         name='test_delete'),
    path('test/<int:pk>/results/', TestResultsView.as_view(),
         name='test_results'),
    path('test/<int:pk>/question/add/', question_add, name='question_add'),
    path('test/<int:test_pk>/question/<int:question_pk>/', question_change,
         name='question_change'),
    path('test/<int:test_pk>/question/<int:question_pk>/delete/',
         QuestionDeleteView.as_view(), name='question_delete'),
]