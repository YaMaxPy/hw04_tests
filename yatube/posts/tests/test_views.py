import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Follow, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
CREATE_PAGE = reverse('posts:post_create')
INDEX_PAGE = reverse('posts:index')
FOLLOW_PAGE = reverse('posts:follow_index')


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

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
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        self.post = Post.objects.create(
            author=self.user,
            group=self.group,
            text='test-post',
            image=uploaded
        )
        self.comment = Comment.objects.create(
            author=self.user,
            post=self.post,
            text='test-comment'
        )
        self.GROUP_PAGE = reverse('posts:group_list', kwargs={
                                  'slug': self.group.slug})
        self.PROFILE_PAGE = reverse('posts:profile', kwargs={
                                    'username': self.user.username})
        self.DETAIL_PAGE = reverse('posts:post_detail', kwargs={
                                   'post_id': self.post.id})
        self.EDIT_PAGE = reverse('posts:post_edit', kwargs={
                                 'post_id': self.post.id})

    def test_views(self):
        templates = {
            INDEX_PAGE: 'posts/index.html',
            self.GROUP_PAGE: 'posts/group_list.html',
            self.PROFILE_PAGE: 'posts/profile.html',
            self.DETAIL_PAGE: 'posts/post_detail.html',
            self.EDIT_PAGE: 'posts/create_post.html',
            CREATE_PAGE: 'posts/create_post.html',
        }
        for reverse_name, template in templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_pages_show_correct_context(self):
        response = self.authorized_client.get(INDEX_PAGE)
        first_object = response.context['page_obj'][0]
        object_element = {
            first_object.text: self.post.text,
            first_object.group: self.post.group,
            first_object.author: self.post.author,
            first_object.image: self.post.image,
        }
        for context, expected in object_element.items():
            self.assertEqual(context, expected)

    def test_group_list_pages_show_correct_context(self):
        response = self.authorized_client.get(self.GROUP_PAGE)
        for post in response.context['page_obj']:
            self.assertEqual(post.group.slug, self.group.slug)
            self.assertEqual(post.image, self.post.image)

    def test_profile_posts_pages_show_correct_context(self):
        response = self.authorized_client.get(self.PROFILE_PAGE)
        for post in response.context['page_obj']:
            self.assertEqual(post.author.username, self.user.username)
            self.assertEqual(post.image, self.post.image)

    def test_post_detail_show_correct_context(self):
        response = self.authorized_client.get(self.DETAIL_PAGE)
        post_details = {response.context['post'].text: self.post.text,
                        response.context['post'].group: self.group,
                        response.context['post'].image: self.post.image,
                        response.context['post'].author.username:
                        self.user.username}
        for value, expected in post_details.items():
            self.assertEqual(post_details[value], expected)

    def test_post_create_show_correct_context(self):
        response = (self.authorized_client.get(CREATE_PAGE))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_added_correctly(self):
        pages: tuple = (INDEX_PAGE,
                        self.PROFILE_PAGE,
                        self.GROUP_PAGE)
        for page in pages:
            response = self.authorized_client.get(page)
            context = response.context['page_obj']
            self.assertIn(self.post, context)

    def test_post_added_correctly_user2(self):
        group_2 = Group.objects.create(
            title='test-group_2',
            slug='test-slug_2'
        )
        post_2 = Post.objects.create(
            text='test-post_2',
            author=self.user,
            group=group_2,
        )
        response = (self.authorized_client.get(self.GROUP_PAGE))
        posts = response.context['page_obj']
        self.assertNotIn(post_2, posts)

    def test_comment_added_correctly(self):
        response = self.authorized_client.get(self.DETAIL_PAGE)
        self.assertEqual(response.context['post'].comments, self.post.comments)

    def test_cache(self):
        post = Post.objects.filter(id=self.post.id)
        response = self.authorized_client.get(INDEX_PAGE)
        post.delete()
        response_2 = self.authorized_client.get(INDEX_PAGE)
        self.assertEqual(response.content, response_2.content)
        cache.clear()
        response_3 = self.authorized_client.get(INDEX_PAGE)
        self.assertNotEqual(response.content, response_3.content)

    def test_authorized_client_can_follow_unfollow(self):
        self.user_following = User.objects.create_user(username='following')
        self.post = Post.objects.create(
            author=self.user_following,
            text='Тестовая запись для тестирования подписки.'
        )
        self.authorized_client.get(reverse(
            'posts:profile_follow', kwargs={
                'username': self.user_following.username}))
        self.assertEqual(Follow.objects.all().count(), 1)
        response = self.authorized_client.get(FOLLOW_PAGE)
        test_post = response.context['page_obj']
        self.assertIn(self.post, test_post)
        self.authorized_client.get(reverse(
            'posts:profile_unfollow', kwargs={
                'username': self.user_following.username}))
        self.assertEqual(Follow.objects.all().count(), 0)
        response_2 = self.authorized_client.get(FOLLOW_PAGE)
        test_post_2 = response_2.context['page_obj']
        self.assertNotIn(self.post, test_post_2)
