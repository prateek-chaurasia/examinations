from django.test import TestCase
from django.urls import reverse

from apps.models import User, Test
from apps.forms import TeacherSignUpForm


class TeacherSignUpViewTest(TestCase):

    def setUp(self):
        #Create a single user
        self.user = User.objects.create_user(username="test2",
                                             password="TSC@1234")

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/accounts/signup/teacher/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('teacher_signup'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('teacher_signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/signup_form.html')

    def test_teacher_registered_successfully(self):
        response = self.client.get(reverse('teacher_signup'))
        self.assertEqual(response.status_code, 200)
        form = TeacherSignUpForm(data={'username': "testUser1",
                                       'password1': "India@123",
                                       'password2': "India@123"})
        self.assertTrue(form.is_valid())

    def test_register_teacher_with_missing_data(self):
        response = self.client.get(reverse('teacher_signup'))
        self.assertEqual(response.status_code, 200)
        form = TeacherSignUpForm(data={'username': "testUser1",
                                       'password1': "",
                                       'password2': "India@123"})
        self.assertFalse(form.is_valid())


class TestListViewTest(TestCase):
    def setUp(self):
        #Create a user as teacher
        self.teacher_credentials = {
            'username': 'test3',
            'password': 'India@123',
            'is_teacher': True}
        self.user = User.objects.create_user(**self.teacher_credentials)


    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('teachers:test_change_list'))
        self.assertRedirects(response,
                             '/accounts/login/?next=/teachers/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='test3', password='India@123')
        response = self.client.get(reverse('teachers:test_change_list'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']),'test3')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response,'teachers/test_change_list.html')

    def test_only_not_attempted_tests_in_list(self):
        login = self.client.login(username='test3', password='India@123')
        response = self.client.get(reverse('teachers:test_change_list'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'test3')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check that initially we don't have any test
        self.assertTrue('tests' in response.context)
        self.assertEqual(len(response.context['tests']),
                         Test.objects.all().count())