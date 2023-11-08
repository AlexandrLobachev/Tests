import pytest

from django.urls import reverse
from http import HTTPStatus
from pytest_django.asserts import assertRedirects, assertFormError

from news.models import Comment
from news.forms import WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client, news, form_comment
):
    url = reverse('news:detail', args=(news.pk,))
    client.post(url, data=form_comment)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_authorized_user_can_create_comment(
    admin_client, news, form_comment,
):
    url = reverse('news:detail', args=(news.pk,))
    response = admin_client.post(url, data=form_comment)
    comments_count = Comment.objects.count()
    assertRedirects(response, f'{url}#comments')
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_comment['text']
    assert comment.news == news


@pytest.mark.django_db
def test_user_cant_use_bad_words(
    admin_client, news, form_comment_with_bad_word,
):
    url = reverse('news:detail', args=(news.pk,))
    response = admin_client.post(url, data=form_comment_with_bad_word)
    comments_count = Comment.objects.count()
    assertFormError(response, 'form', 'text', errors=(WARNING))
    assert comments_count == 0


@pytest.mark.django_db
def test_author_can_edit_comment(
    author_client, comment, form_comment,
):
    url = reverse('news:edit', args=(comment.pk,))
    author_client.post(url, data=form_comment)
    comment.refresh_from_db()
    assert comment.text == form_comment['text']


@pytest.mark.django_db
def test_author_can_delete_comment(
    author_client, news, comment,
):
    news_url = reverse('news:detail', args=(news.pk,))
    url_to_comments = news_url + '#comments'
    assert Comment.objects.count() == 1
    url = reverse('news:delete', args=(comment.pk,))
    response = author_client.post(url)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
    admin_client, comment, form_comment,
):
    comment_before_edit = comment.text
    url = reverse('news:edit', args=(comment.pk,))
    response = admin_client.post(url, data=form_comment)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == comment_before_edit


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(
    admin_client, comment,
):
    assert Comment.objects.count() == 1
    url = reverse('news:delete', args=(comment.pk,))
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
