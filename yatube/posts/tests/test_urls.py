from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User

CREATE_PAGE = reverse('posts:post_create')
INDEX_PAGE = reverse('posts:index')
UNEXISTING_PAGE = '/unexisting_page/'


class PostsURLTests(TestCase):
    def setUp(self):
        cache.clear()
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
            text='test-post',
        )
        self.GROUP_PAGE = reverse('posts:group_list', kwargs={
                                  'slug': self.group.slug})
        self.PROFILE_PAGE = reverse('posts:profile', kwargs={
                                    'username': self.user.username})
        self.DETAIL_PAGE = reverse('posts:post_detail', kwargs={
                                   'post_id': self.post.id})
        self.EDIT_PAGE = reverse('posts:post_edit', kwargs={
                                 'post_id': self.post.id})
        self.COMMENT_PAGE = reverse('posts:add_comment', kwargs={
                                    'post_id': self.post.id})

    def test_urls_available_for_guest_client(self):
        urls = {
            INDEX_PAGE: HTTPStatus.OK,
            self.GROUP_PAGE: HTTPStatus.OK,
            self.PROFILE_PAGE: HTTPStatus.OK,
            self.DETAIL_PAGE: HTTPStatus.OK,
            self.EDIT_PAGE: HTTPStatus.FOUND,
            CREATE_PAGE: HTTPStatus.FOUND,
            UNEXISTING_PAGE: HTTPStatus.NOT_FOUND,
        }
        for address, status in urls.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status)

    def test_urls_available_for_authorized_client(self):
        urls = {
            INDEX_PAGE: HTTPStatus.OK,
            self.GROUP_PAGE: HTTPStatus.OK,
            self.PROFILE_PAGE: HTTPStatus.OK,
            self.DETAIL_PAGE: HTTPStatus.OK,
            self.EDIT_PAGE: HTTPStatus.OK,
            CREATE_PAGE: HTTPStatus.OK,
            UNEXISTING_PAGE: HTTPStatus.NOT_FOUND,
        }
        for address, status in urls.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, status)

    def test_urls_redirect_guest_client(self):
        url1 = f'''{reverse('users:login')}?next={CREATE_PAGE}'''
        url2 = self.DETAIL_PAGE
        url3 = f'''{reverse('users:login')}?next={self.COMMENT_PAGE}'''
        pages = {
            CREATE_PAGE: url1,
            self.EDIT_PAGE: url2,
            self.COMMENT_PAGE: url3}
        for page, value in pages.items():
            response = self.guest_client.get(page, follow=True)
            self.assertRedirects(response, value)

    def test_templates(self):
        templates = {
            INDEX_PAGE: 'posts/index.html',
            self.GROUP_PAGE: 'posts/group_list.html',
            self.PROFILE_PAGE: 'posts/profile.html',
            self.DETAIL_PAGE: 'posts/post_detail.html',
            self.EDIT_PAGE: 'posts/create_post.html',
            CREATE_PAGE: 'posts/create_post.html',
        }
        for address, template in templates.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
