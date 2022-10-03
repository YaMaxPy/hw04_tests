from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

FIRST_CHARACTERS_POST: int = 15
User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_post_have_correct_text(self):
        post = PostModelTest.post
        expected_object_name = post.text[:FIRST_CHARACTERS_POST]
        self.assertEqual(expected_object_name, str(post))

    def test_group_have_correct_title(self):
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
