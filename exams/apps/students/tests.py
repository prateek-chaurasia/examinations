from django.test import TestCase
from django.urls import reverse

from apps.models import User
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