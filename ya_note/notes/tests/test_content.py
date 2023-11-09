from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm


User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.otheruser = User.objects.create(username='Пользователь')
        cls.auth_client_otheruser = Client()
        cls.auth_client_otheruser.force_login(cls.otheruser)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )

    def test_notes_list_for_different_users(self):
        users_statuses = (
            (self.auth_client, True),
            (self.auth_client_otheruser, False),
        )
        for user, status in users_statuses:
            with self.subTest(user=user):
                url = reverse('notes:list')
                response = user.get(url)
                object_list = response.context.get('object_list')
                self.assertEqual(self.note in object_list, status)

    def test_pages_contains_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.auth_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context.get('form'), NoteForm)
