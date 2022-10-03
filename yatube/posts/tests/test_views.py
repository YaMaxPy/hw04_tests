from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User

CREATE_PAGE = reverse('posts:post_create')
INDEX_PAGE = reverse('posts:index')


class PostsViewsTests(TestCase):
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
        }
        for context, expected in object_element.items():
            self.assertEqual(context, expected)

    def test_group_list_pages_show_correct_context(self):
        response = self.authorized_client.get(self.GROUP_PAGE)
        for post in response.context['page_obj']:
            self.assertEqual(post.group.slug, self.group.slug)

    def test_profile_posts_pages_show_correct_context(self):
        response = self.authorized_client.get(self.PROFILE_PAGE)
        for post in response.context['page_obj']:
            self.assertEqual(post.author.username, self.user.username)

    def test_post_detail_show_correct_context(self):
        response = self.authorized_client.get(self.DETAIL_PAGE)
        post_details = {response.context['post'].text: self.post.text,
                        response.context['post'].group: self.group,
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
