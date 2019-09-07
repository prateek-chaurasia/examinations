from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.forms.utils import ValidationError

from .models import (Answer, Question, Student, StudentAnswer, User)


class TeacherSignUpForm(UserCreationForm):
    """
    Inherited UserCreationForm so that the basic fields are available in the
    form and user creation becomes easier.
    Fields that the parent class provides are: "username","password1" and
    "password2"
    """
    class Meta(UserCreationForm.Meta):
        model = User

    def save(self, commit=True):
        """
        Adding value to is_teacher fields that will identify a User as "Teacher"
        :param commit:
        :return:
        """
        user = super().save(commit=False)
        user.is_teacher = True
        if commit:
            user.save()
        return user


class StudentSignUpForm(UserCreationForm):
    """
        Inherited UserCreationForm so that the basic fields are available in the
        form and user creation becomes easier.
        Fields that the parent class provides are: "username","password1" and
        "password2"
        Then adding the other required fields to store meta data for a Student.
    """
    first_name = forms.CharField()
    surname = forms.CharField()
    email = forms.EmailField()

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic
    def save(self):
        """
        Adding value to is_student fields that will identify a User as "Student"
        and also adding the required fields for the Student model, where User is
        a one to one key.
        :param commit:
        :return:
        """
        user = super().save(commit=False)
        user.is_student = True
        user.save()
        student = Student.objects.create(user=user)
        student.first_name = self.cleaned_data.get('first_name')
        student.surname = self.cleaned_data.get('surname')
        student.email = self.cleaned_data.get('email')
        return user


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('text',)


class BaseAnswerInlineFormSet(forms.BaseInlineFormSet):
    """
    Creating this formset in order to have the ability to display the
    required number of Answer forms for a single Question. Other
    configuration parameters are defined in the View where
    inlineformset_factory method is used.
    used
    """
    def clean(self):
        """
        This method insures atleast a single correct answer is marked for a
        Question while creating a test, if not it raises Validation Error.
        :return:
        """
        super().clean()

        has_one_correct_answer = False
        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False):
                if form.cleaned_data.get('is_correct', False):
                    has_one_correct_answer = True
                    break
        if not has_one_correct_answer:
            raise ValidationError('Mark at least one answer as correct.', code='no_correct_answer')


class TakeTestForm(forms.ModelForm):
    answer = forms.ModelChoiceField(
        queryset=Answer.objects.none(),
        widget=forms.RadioSelect(),
        required=True,
        empty_label=None)

    class Meta:
        model = StudentAnswer
        fields = ('answer', )

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question')
        super().__init__(*args, **kwargs)
        self.fields['answer'].queryset = question.answers.order_by('text')