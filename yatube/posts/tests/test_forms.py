from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostsFormsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='test-username')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='test-group',
            slug='test-slug',
            description='test-description',
        )
        self.post = Post.objects.create(
            author=self.user,
            group=self.group,
            text='test-post',
        )

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {'text': 'test-post',
                     'group': self.group.id,
                     'author': self.user}
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.user.username})
        )
        self.assertTrue(
            Post.objects.filter(
                text='test-post',
                group=self.group.id,
                author=self.user
            ).exists()
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post(self):
        self.post = Post.objects.create(text='test-post',
                                        author=self.user,
                                        group=self.group)
        original_text = self.post
        form_data = {'text': 'test-post changed',
                     'author': self.user,
                     'group': self.group}
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': original_text.id}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Post.objects.filter(
                        group=self.group,
                        author=self.user,
                        pub_date=self.post.pub_date
                        ).exists())
        self.assertNotEqual(original_text.text, form_data['text'])
