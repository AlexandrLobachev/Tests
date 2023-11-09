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
    comments_count_before_test = Comment.objects.count()
    url = reverse('news:detail', args=(news.pk,))
    client.post(url, data=form_comment)
    comments_count_after_test = Comment.objects.count()
    assert comments_count_before_test == comments_count_after_test


@pytest.mark.django_db
def test_authorized_user_can_create_comment(
    admin_client, news, form_comment,
):
    old_comments_ids = list(Comment.objects.values_list('id', flat=True))
    url = reverse('news:detail', args=(news.pk,))
    response = admin_client.post(url, data=form_comment)
    assertRedirects(response, f'{url}#comments')
    new_comments = Comment.objects.exclude(id__in=old_comments_ids)
    assert len(new_comments) == 1
    comment = new_comments[0]
    assert comment.text == form_comment.get('text')
    assert comment.news == news


@pytest.mark.django_db
def test_user_cant_use_bad_words(
    admin_client, news, form_comment_with_bad_word,
):
    comments_count_before_test = Comment.objects.count()
    url = reverse('news:detail', args=(news.pk,))
    response = admin_client.post(url, data=form_comment_with_bad_word)
    comments_count_after_test = Comment.objects.count()
    assertFormError(response, 'form', 'text', errors=(WARNING))
    assert comments_count_before_test == comments_count_after_test


@pytest.mark.django_db
def test_author_can_edit_comment(
    author_client, comment, form_comment,
):
    url = reverse('news:edit', args=(comment.pk,))
    author_client.post(url, data=form_comment)
    comment.refresh_from_db()
    assert comment.text == form_comment.get('text')


@pytest.mark.django_db
def test_author_can_delete_comment(
    author_client, news, comment,
):
    comments_count_before_test = Comment.objects.count()
    news_url = reverse('news:detail', args=(news.pk,))
    url_to_comments = news_url + '#comments'
    url = reverse('news:delete', args=(comment.pk,))
    response = author_client.post(url)
    assertRedirects(response, url_to_comments)
    comments_count_after_test = Comment.objects.count()
    assert comments_count_before_test - 1 == comments_count_after_test


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
    comments_count_before_test = Comment.objects.count()
    url = reverse('news:delete', args=(comment.pk,))
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count_after_test = Comment.objects.count()
    assert comments_count_before_test == comments_count_after_test
