from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.forms import WARNING
from http import HTTPStatus

from notes.models import Note
from pytils.translit import slugify


User = get_user_model()


class TestCreateNote(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.url = reverse('notes:add')
        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Текст заметки',
            'slug': 'note-slug',
            'author': cls.author
        }

    def test_anonymous_user_cant_create_note(self):
        notes_count_before_test = Note.objects.count()
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.url}'
        response = self.client.post(self.url, data=self.form_data)
        self.assertRedirects(response, expected_url)
        notes_count_after_test = Note.objects.count()
        self.assertEqual(notes_count_before_test, notes_count_after_test)

    def test_auth_user_can_create_note(self):
        notes_count_before_test = Note.objects.count()
        self.client.force_login(self.author)
        response = self.client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count_after_test = Note.objects.count()
        note = Note.objects.get()
        self.assertEqual(notes_count_before_test + 1, notes_count_after_test)
        self.assertEqual(note.title, self.form_data.get('title'))
        self.assertEqual(note.text, self.form_data.get('text'))
        self.assertEqual(note.slug, self.form_data.get('slug'))
        self.assertEqual(note.author, self.author)

    def test_empty_slug(self):
        self.client.force_login(self.author)
        self.form_data.pop('slug')
        response = self.client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        expected_slug = slugify(self.form_data.get('title'))
        self.assertEqual(note.slug, expected_slug)


class TestEditNote(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Автор')
        cls.first_author = User.objects.create(username='АвторПервый')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.first_author)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.first_author,
        )
        cls.form_data = {
            'title': 'Заголовок №2',
            'text': 'Текст заметки №2',
            'slug': 'note-slug-2',
            'author': cls.user
        }

    def test_not_unique_slug(self):
        notes_count_before_test = Note.objects.count()
        url = reverse('notes:add')
        slug_first_note = self.note.slug
        self.form_data['slug'] = slug_first_note
        response = self.auth_client.post(url, data=self.form_data)
        self.assertFormError(response, 'form', 'slug',
                             errors=(slug_first_note + WARNING))
        notes_count_after_test = Note.objects.count()
        self.assertEqual(notes_count_before_test, notes_count_after_test)

    def test_author_can_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.auth_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data.get('title'))
        self.assertEqual(self.note.text, self.form_data.get('text'))
        self.assertEqual(self.note.slug, self.form_data.get('slug'))

    def test_author_can_delete_note(self):
        notes_count_before_test = Note.objects.count()
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.auth_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count_after_test = Note.objects.count()
        self.assertEqual(notes_count_before_test - 1, notes_count_after_test)

    def test_other_user_cant_edit_note(self):
        self.client.force_login(self.user)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.post(url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_other_user_cant_delete_note(self):
        notes_count_before_test = Note.objects.count()
        self.client.force_login(self.user)
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client.post(url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count_after_test = Note.objects.count()
        self.assertEqual(notes_count_before_test, notes_count_after_test)
