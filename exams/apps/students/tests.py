from django.test import TestCase
from django.urls import reverse

from apps.models import User, Test, Student
from apps.forms import StudentSignUpForm


class StudentSignUpViewTest(TestCase):

    def setUp(self):
        #Create a single user
        self.user = User.objects.create_user(username="test2",
                                             password="TSC@1234")

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/accounts/signup/student/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('student_signup'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('student_signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/signup_form.html')

    def test_student_registered_successfully(self):
        response = self.client.get(reverse('student_signup'))
        self.assertEqual(response.status_code, 200)
        form = StudentSignUpForm(data={'email': "new1@gmail.com",
                                       'password1': "India@123",
                                       'password2': "India@123",
                                    'first_name': "testuser",
                                    'surname': "User1",
                                       'username': "testUser1"})
        self.assertTrue(form.is_valid())

    def test_register_student_with_missing_data(self):
        response = self.client.get(reverse('student_signup'))
        self.assertEqual(response.status_code, 200)
        form = StudentSignUpForm(data={'email': "new1@gmail.com",
                                       'password1': "India@123",
                                       'password2': "India@123",
                                    'first_name': "",
                                    'surname': "",
                                       'username': "testUser1"})
        self.assertFalse(form.is_valid())


class TestListViewTest(TestCase):
    def setUp(self):
        #Create a user as student
        self.student_credentials = {
            'username': 'test3',
            'password': 'India@123',
            'is_student': True}
        self.user = User.objects.create_user(**self.student_credentials)
        self.student = Student.objects.create(user=self.user,
                                              email='test@email.com',
                                              first_name='test3',
                                              surname='passtest')

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('students:test_list'))
        self.assertRedirects(response,
                             '/accounts/login/?next=/students/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='test3', password='India@123')
        response = self.client.get(reverse('students:test_list'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']),'test3')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response,'students/test_list.html')

    def test_only_not_attempted_tests_in_list(self):
        login = self.client.login(username='test3', password='India@123')
        response = self.client.get(reverse('students:test_list'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'test3')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check that initially we don't have any test
        self.assertTrue('tests' in response.context)
        self.assertEqual(len(response.context['tests']),
                         Test.objects.all().count())