import pytest
import random

from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings

from news.forms import BAD_WORDS
from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )
    return news


@pytest.fixture
def pk_news_for_args(news):
    return news.pk,


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        text='Текст комментария',
        author=author,
    )
    return comment


@pytest.fixture
def pk_comment_for_args(comment):
    return comment.pk,


@pytest.fixture
def paginate_news():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)
    return News.objects.all()


@pytest.fixture
def two_comment(news, author):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return Comment.objects.all()


@pytest.fixture
def form_comment():
    return {
        'text': 'Второй комментарий в фикстурах',
    }


@pytest.fixture
def form_comment_with_bad_word():
    return {
        'text': f'Tекст, {random.choice(BAD_WORDS)}, еще текст',
    }
