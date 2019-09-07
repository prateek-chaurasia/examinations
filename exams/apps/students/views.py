from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from datetime import datetime

from ..forms import StudentSignUpForm, TakeTestForm
from ..models import Test, TakenTest, User


class StudentSignUpView(CreateView):
    model = User
    form_class = StudentSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'student'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('students:test_list')


@method_decorator([login_required], name='dispatch')
class TestListView(ListView):
    model = Test
    ordering = ('name', )
    context_object_name = 'tests'
    template_name = 'students/test_list.html'

    def get_queryset(self):
        student = self.request.user.student
        taken_tests = student.tests.values_list('pk', flat=True)
        queryset = Test.objects.all() \
            .exclude(pk__in=taken_tests) \
            .annotate(questions_count=Count('questions')) \
            .filter(questions_count__gt=0)
        return queryset


@method_decorator([login_required], name='dispatch')
class TakenTestListView(ListView):
    model = TakenTest
    context_object_name = 'taken_tests'
    template_name = 'students/taken_test_list.html'

    def get_queryset(self):
        queryset = self.request.user.student.taken_tests \
            .select_related('test') \
            .order_by('test__name')
        return queryset


@login_required
def take_test(request, pk):
    test = get_object_or_404(Test, pk=pk)
    student = request.user.student
    result = 'Passed'
    if student.tests.filter(pk=pk).exists():
        return render(request, 'students/taken_test_list.html')

    total_questions = test.questions.count()
    unanswered_questions = student.get_unanswered_questions(test)
    total_unanswered_questions = unanswered_questions.count()
    progress = 100 - round(((total_unanswered_questions - 1) / total_questions) * 100)
    question = unanswered_questions.first()

    if request.method == 'POST':
        form = TakeTestForm(question=question, data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                student_answer = form.save(commit=False)
                student_answer.student = student
                student_answer.save()
                if student.get_unanswered_questions(test).exists():
                    return redirect('students:take_test', pk)
                else:
                    correct_answers = student.test_answers.filter(answer__question__test=test, answer__is_correct=True).count()
                    score = round((correct_answers / total_questions) * 100.0, 2)
                    TakenTest.objects.create(student=student, test=test, score=score)
                    if score < float(test.pass_percentage):
                        messages.warning(request, 'Better luck next time! Your score for the test %s was %s.' % (test.name, score))
                        result = 'Failed'
                    else:
                        messages.success(request, 'Congratulations! You completed the test %s with success! You scored %s points.' % (test.name, score))
                    send_email_notification(test.name, student, result, score)
                    return redirect('students:test_list')
    else:
        form = TakeTestForm(question=question)

    return render(request, 'students/take_test_form.html', {
        'test': test,
        'question': question,
        'form': form,
        'progress': progress
    })


def send_email_notification(test_name, student, result, score):
    """
    This function takes the required parameters and shoots html
    formatted email to the user
    :param test_name: Test Taken
    :param student: Currently logged in Student
    :param result: Result "Passed" or "Failed"
    :param score: Score in the following format "30.0"
    :return:
    """
    subject, from_email, to = 'Your Test Score for {} - Examination ' \
                              'Board'.format(test_name), \
                              settings.EMAIL_HOST_USER, student.email

    html_content = render_to_string(
        'registration/result_notification.html', {
        'first_name': student.first_name,
        'test_name': test_name,
        'result': result,
        'score': score,
        'date': datetime.strftime(datetime.now(), '%d %B %Y')})
    text_content = strip_tags(
        html_content) # Strip the html tag. So people can see the pure text at least.

    # create the email, and attach the HTML version as well.
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])

    msg.attach_alternative(html_content, "text/html")
    try:
        msg.send()
    except Exception as e:
        print(e)