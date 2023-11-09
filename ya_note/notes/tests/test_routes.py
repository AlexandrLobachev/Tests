
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note



User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.auth_author = Client()
        cls.auth_author.force_login(cls.author)
        cls.second_user = User.objects.create(username='Второй пользователь')
        cls.auth_second_user = Client()
        cls.auth_second_user.force_login(cls.second_user)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
        )

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_availability_different_user(self):
        urls = {
            ('notes:home', None): (
                (self.client, HTTPStatus.OK),
                (self.auth_second_user, HTTPStatus.OK)
            ),
            ('users:login', None): (
                (self.client, HTTPStatus.OK),
                (self.auth_second_user, HTTPStatus.OK)
            ),
            ('users:signup', None): (
                (self.client, HTTPStatus.OK),
                (self.auth_second_user, HTTPStatus.OK)
            ),
            ('notes:list', None): ((self.auth_second_user, HTTPStatus.OK),),
            ('notes:add', None): ((self.auth_second_user, HTTPStatus.OK),),
            ('notes:success', None): ((self.auth_second_user, HTTPStatus.OK),),
            ('notes:edit', (self.note.slug,)): (
                (self.auth_second_user, HTTPStatus.NOT_FOUND),
                (self.auth_author, HTTPStatus.OK)
            ),
            ('notes:delete', (self.note.slug,)): (
                (self.auth_second_user, HTTPStatus.NOT_FOUND),
                (self.auth_author, HTTPStatus.OK)
            ),
            ('notes:detail', (self.note.slug,)): (
                (self.auth_second_user, HTTPStatus.NOT_FOUND),
                (self.auth_author, HTTPStatus.OK)
            ),
            ('users:logout', None): (
                (self.client, HTTPStatus.OK),
                (self.auth_second_user, HTTPStatus.OK)
            ),
        }
        for item in urls.items():
            name_and_args, user_statuses = item
            with self.subTest(name_and_args=name_and_args):
                name, args = name_and_args
                for user_status in user_statuses:
                    user, status = user_status
                    with self.subTest(user_status=user_status):
                        url = reverse(name, args=args)
                        response = user.get(url)
                        self.assertEqual(response.status_code, status)
