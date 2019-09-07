from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)


class Test(models.Model):
    PERCENTAGE = (
        ('30', '30'),
        ('40', '40'),
        ('50', '50'),
        ('60', '60'),
        ('70', '70'),
        ('80', '80'),
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tests')
    name = models.CharField(max_length=255)
    pass_percentage = models.CharField(choices=PERCENTAGE, default="30",
                                       max_length=2,
                                       verbose_name='Pass Percentage')

    def __str__(self):
        return self.name


class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE,
                             related_name='questions')
    text = models.CharField(verbose_name='Question', max_length=255)


    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(verbose_name='Answer', max_length=255)
    is_correct = models.BooleanField(verbose_name='Correct answer', default=False)

    def __str__(self):
        return self.text


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    tests = models.ManyToManyField(Test, through='TakenTest')

    first_name = models.CharField(max_length=100, verbose_name='First Name')
    surname = models.CharField(max_length=100, verbose_name='Surname',
                               blank=True, null=True)
    email = models.EmailField(verbose_name='Email')

    def get_unanswered_questions(self, test):
        answered_questions = self.test_answers \
            .filter(answer__question__test=test) \
            .values_list('answer__question__pk', flat=True)
        questions = test.questions.exclude(pk__in=answered_questions).order_by(
            'text')
        return questions

    def __str__(self):
        return self.user.username


class TakenTest(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE,
                                related_name='taken_tests')
    test = models.ForeignKey(Test, on_delete=models.CASCADE,
                             related_name='taken_tests')
    score = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)


class StudentAnswer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE,
                                related_name='test_answers')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='+')
