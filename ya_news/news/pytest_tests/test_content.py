import pytest
import itertools

from django.conf import settings
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.usefixtures('paginate_news')
def test_news_count(client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context.get('object_list')
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
@pytest.mark.usefixtures('paginate_news')
def test_news_order(client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context.get('object_list')
    all_dates, all_date_copy = itertools.tee(
        (news.date for news in object_list), 2)
    all_dates = list(all_dates)
    sorted_dates = sorted(all_date_copy, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
@pytest.mark.usefixtures('two_comment')
def test_comments_order(client, news, comment):
    url = reverse('news:detail', args=(news.pk,))
    response = client.get(url)
    assert 'news' in response.context
    news = response.context.get('news')
    all_comments = news.comment_set.all()
    all_dates = [comment.created for comments in all_comments]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, form_in_context',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('admin_client'), True),
    )
)
def test_comment_form_for_authorized_user(
    parametrized_client, form_in_context, news
):
    url = reverse('news:detail', args=(news.pk,))
    response = parametrized_client.get(url)
    assert ('form' in response.context) is form_in_context
