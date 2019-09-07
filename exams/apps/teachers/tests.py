from django.test import TestCase
from django.urls import reverse

from apps.models import User
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