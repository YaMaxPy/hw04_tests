from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

COUNT_TEST_POSTS: int = 13
User = get_user_model()


class PostsPaginatorTests(TestCase):
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
        list_posts: list = []
        for i in range(COUNT_TEST_POSTS):
            list_posts.append(Post(text=f'test-post {i}',
                                   group=self.group,
                                   author=self.user))
        self.post = Post.objects.bulk_create(list_posts)

    def test_paginator_pages_contains_correct_records(self):
        pages: tuple = (reverse('posts:index'),
                        reverse('posts:profile',
                                kwargs={'username': f'{self.user.username}'}),
                        reverse('posts:group_list',
                                kwargs={'slug': f'{self.group.slug}'}))
        for page in pages:

            response_1 = self.guest_client.get(page)
            response_2 = self.guest_client.get(page + '?page=2')
            self.assertEqual(len(response_1.context['page_obj']), 10)
            self.assertEqual(len(response_2.context['page_obj']), 3)
