import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
CREATE_PAGE = reverse('posts:post_create')


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormsTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

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
        self.PROFILE_PAGE = reverse('posts:profile', kwargs={
                                    'username': self.user.username})
        self.EDIT_PAGE = reverse('posts:post_edit', kwargs={
                                 'post_id': self.post.id})

    def test_create_post(self):
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
        posts_count = Post.objects.count()
        form_data = {'text': 'test-post',
                     'group': self.group.id,
                     'author': self.user,
                     'image': uploaded}
        response = self.authorized_client.post(CREATE_PAGE,
                                               data=form_data,
                                               follow=True)
        self.assertRedirects(response, self.PROFILE_PAGE)
        self.assertTrue(
            Post.objects.filter(
                text='test-post',
                group=self.group.id,
                author=self.user,
                image=self.post.image,
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
            self.EDIT_PAGE,
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Post.objects.filter(
                        group=self.group,
                        author=self.user,
                        pub_date=self.post.pub_date
                        ).exists())
        self.assertNotEqual(original_text.text, form_data['text'])
