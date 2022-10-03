from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User
from ..utils import POSTS_ON_PAGE

INDEX_PAGE = reverse('posts:index')
COUNT_TEST_POSTS: int = POSTS_ON_PAGE + 1


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
        self.GROUP_PAGE = reverse('posts:group_list', kwargs={
                                  'slug': self.group.slug})
        self.PROFILE_PAGE = reverse('posts:profile', kwargs={
                                    'username': self.user.username})

    def test_paginator_pages_contains_correct_records(self):
        pages: tuple = (INDEX_PAGE,
                        self.PROFILE_PAGE,
                        self.GROUP_PAGE)
        for page in pages:
            response_1 = self.guest_client.get(page)
            response_2 = self.guest_client.get(page + '?page=2')
            self.assertEqual(len(response_1.context['page_obj']),
                             POSTS_ON_PAGE)
            self.assertEqual(len(response_2.context['page_obj']),
                             COUNT_TEST_POSTS - POSTS_ON_PAGE)
