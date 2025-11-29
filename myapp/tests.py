from django.test import TestCase
from .models import MyUser


class MyUserTestCase(TestCase):
    """
    Test cases for MyUser model.
    """
    
    def setUp(self):
        """Set up test data."""
        MyUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_creation(self):
        """Test that user can be created."""
        user = MyUser.objects.get(username='testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
