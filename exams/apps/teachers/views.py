from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Avg, Count
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from ..forms import BaseAnswerInlineFormSet, QuestionForm, TeacherSignUpForm
from ..models import Answer, Question, Test, User


class TeacherSignUpView(CreateView):
    model = User
    form_class = TeacherSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'teacher'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('teachers:test_change_list')


@method_decorator([login_required],name='dispatch')
class TestListView(ListView):
    model = Test
    ordering = ('name', )
    context_object_name = 'tests'
    template_name = 'teachers/test_change_list.html'

    def get_queryset(self):
        queryset = self.request.user.tests \
            .annotate(questions_count=Count('questions', distinct=True)) \
            .annotate(taken_count=Count('taken_tests', distinct=True))
        return queryset


@method_decorator([login_required],name='dispatch')
class TestCreateView(CreateView):
    model = Test
    fields = ('name','pass_percentage')
    template_name = 'teachers/test_add_form.html'

    def form_valid(self, form):
        test = form.save(commit=False)
        test.owner = self.request.user
        test.save()
        messages.success(self.request, 'The test was created with success! Go ahead and add some questions now.')
        return redirect('teachers:test_change', test.pk)


# @method_decorator([login_required, teacher_required], name='dispatch')
class TestUpdateView(UpdateView):
    model = Test
    fields = ('name',)
    context_object_name = 'test'
    template_name = 'teachers/test_change_form.html'

    def get_context_data(self, **kwargs):
        kwargs['questions'] = self.get_object().questions.annotate(answers_count=Count('answers'))
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        '''
        This method is an implicit object-level permission management
        This view will only match the ids of existing tests that belongs
        to the logged in user.
        '''
        return self.request.user.tests.all()

    def get_success_url(self):
        return reverse('teachers:test_change', kwargs={'pk': self.object.pk})


@method_decorator([login_required],name='dispatch')
class TestDeleteView(DeleteView):
    model = Test
    context_object_name = 'test'
    template_name = 'teachers/test_delete_confirm.html'
    success_url = reverse_lazy('teachers:test_change_list')

    def delete(self, request, *args, **kwargs):
        test = self.get_object()
        messages.success(request, 'The test %s was deleted with success!' %
                         test.name)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.tests.all()


@method_decorator([login_required],name='dispatch')
class TestResultsView(DetailView):
    model = Test
    context_object_name = 'test'
    template_name = 'teachers/test_results.html'

    def get_context_data(self, **kwargs):
        test = self.get_object()
        taken_tests = test.taken_tests.select_related('student__user').order_by(
            '-date')
        total_taken_tests = taken_tests.count()
        test_score = test.taken_tests.aggregate(average_score=Avg('score'))
        extra_context = {
            'taken_tests': taken_tests,
            'total_taken_tests': total_taken_tests,
            'test_score': test_score
        }
        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return self.request.user.tests.all()


@login_required
def question_add(request, pk):
    # By filtering the test by the url keyword argument `pk` and
    # by the owner, which is the logged in user, we are protecting
    # this view at the object-level. Meaning only the owner of
    # test will be able to add questions to it.
    test = get_object_or_404(Test, pk=pk, owner=request.user)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.test = test
            question.save()
            messages.success(request, 'You may now add answers/options to the question.')
            return redirect('teachers:question_change', test.pk, question.pk)
    else:
        form = QuestionForm()

    return render(request, 'teachers/question_add_form.html',
                  {'test': test, 'form': form})


@login_required
def question_change(request, test_pk, question_pk):
    # This view is managing the permissions at object-level. By querying both
    # `test` and `question` we are making sure only the owner of the test can
    # change its details and also only questions that belongs to this
    # specific test can be changed via this url (in cases where the
    # user might have forged/player with the url params.
    test = get_object_or_404(Test, pk=test_pk, owner=request.user)
    question = get_object_or_404(Question, pk=question_pk, test=test)

    AnswerFormSet = inlineformset_factory(
        Question,  # parent model
        Answer,  # base model
        formset=BaseAnswerInlineFormSet,
        fields=('text', 'is_correct'), # Field to be displayed as inline form
        min_num=2, # Minimum number of forms should be filled by the user.
        validate_min=True, # If minimum number of forms not filled raise error
        max_num=4, # Maximum number of forms displayed and should be filled by
        # the user.
        validate_max=True # If maximum number of forms not filled raise error
    )

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        formset = AnswerFormSet(request.POST, instance=question)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            messages.success(request, 'Question and answers saved with success!')
            return redirect('teachers:test_change', test.pk)
    else:
        form = QuestionForm(instance=question)
        formset = AnswerFormSet(instance=question)

    return render(request, 'teachers/question_change_form.html', {
        'test': test,
        'question': question,
        'form': form,
        'formset': formset
    })


@method_decorator([login_required], name='dispatch')
class QuestionDeleteView(DeleteView):
    model = Question
    context_object_name = 'question'
    template_name = 'teachers/question_delete_confirm.html'
    pk_url_kwarg = 'question_pk'

    def get_context_data(self, **kwargs):
        question = self.get_object()
        kwargs['test'] = question.test
        return super().get_context_data(**kwargs)

    def delete(self, request, *args, **kwargs):
        question = self.get_object()
        messages.success(request, 'The question %s was deleted with success!' % question.text)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return Question.objects.filter(test__owner=self.request.user)

    def get_success_url(self):
        question = self.get_object()
        return reverse('teachers:test_change', kwargs={'pk': question.test_id})