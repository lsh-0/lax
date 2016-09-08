from os.path import join
import json
from datetime import datetime
from base import BaseCase
from publisher import ajson_ingestor, models, utils
from publisher.ajson_ingestor import StateError

class TestAJSONIngest(BaseCase):
    def setUp(self):
        self.ajson_fixture1 = join(self.fixture_dir, 'ajson', 'elife.01968.json')
        self.valid_ajson = json.load(open(self.ajson_fixture1, 'r'))

    def tearDown(self):
        pass

    def test_article_ingest(self):
        """valid article-json is successfully ingested, creating an article, 
        an article version and storing the ingestion request"""
        self.assertEqual(models.Journal.objects.count(), 0)
        self.assertEqual(models.Article.objects.count(), 0)
        self.assertEqual(models.ArticleVersion.objects.count(), 0)

        ajson_ingestor.ingest(self.valid_ajson)

        self.assertEqual(models.Journal.objects.count(), 1)
        self.assertEqual(models.Article.objects.count(), 1)
        self.assertEqual(models.ArticleVersion.objects.count(), 1)

    def test_article_ingest_does_not_publish(self):
        """ingesting article json does not cause an article to become published 
        (gain a published date) even if a published date was supplied"""
        expected = "2016-04-13T01:00:00"
        self.valid_ajson['article']['published'] = expected
        _, _, av = ajson_ingestor.ingest(self.valid_ajson)
        self.assertNotEqual(av.datetime_published, expected)

    def test_article_ingest_update(self):
        "ingesting article data twice successfully updates the article"
        _, _, av = ajson_ingestor.ingest(self.valid_ajson)

        self.assertEqual(models.ArticleVersion.objects.count(), 1)
        self.assertEqual(av.title, self.valid_ajson['article']['title'])
        self.assertEqual(av.datetime_published, None) # not published

        # do it again to cause an update
        expected_title = 'flub'
        self.valid_ajson['article']['title'] = expected_title
        _, _, av = ajson_ingestor.ingest(self.valid_ajson)

        self.assertEqual(models.ArticleVersion.objects.count(), 1)
        self.assertEqual(av.title, expected_title)
        self.assertEqual(av.datetime_published, None) # still not published

    def test_article_update_does_not_publish(self):
        "ingesting article data twice still does not cause publication"
        _, _, av = ajson_ingestor.ingest(self.valid_ajson)
        self.assertEqual(av.datetime_published, None)

        expected = "2016-04-13T01:00:00"
        self.valid_ajson['article']['published'] = expected

        _, _, av = ajson_ingestor.ingest(self.valid_ajson)
        self.assertEqual(av.datetime_published, None)

    def test_article_ingest_fails_for_published_articles(self):
        "ingesting article data for a published article version fails"
        _, _, av = ajson_ingestor.ingest(self.valid_ajson)
        # edit data directly
        av.datetime_published = '2001-01-01'
        av.save()
        self.assertTrue(av.published())

        # attempt another ingest
        self.assertRaises(StateError, ajson_ingestor.ingest, self.valid_ajson)

    def test_article_ingest_for_published_articles_succeeds_if_forced(self):
        "ingesting article data for a published article version succeeds if force=True"
        _, _, av = ajson_ingestor.ingest(self.valid_ajson)
        # edit data directly
        av.datetime_published = '2001-01-01'
        av.save()
        self.assertTrue(av.published())

        # attempt another ingest
        expected_title = 'foo'
        self.valid_ajson['article']['title'] = expected_title
        _, _, av = ajson_ingestor.ingest(self.valid_ajson, force=True)
        self.assertEqual(av.title, expected_title)

    def test_article_ingest_bad_journal(self):
        "bad journal data will fail an ingest of article json"
        self.assertEqual(models.Journal.objects.count(), 0)
        del self.valid_ajson['journal']
        self.assertRaises(Exception, ajson_ingestor.ingest, self.valid_ajson)
        self.assertEqual(models.Journal.objects.count(), 0)

    def test_article_ingest_bad_article(self):
        "bad article data will fail an ingest of article json"
        self.assertEqual(models.Journal.objects.count(), 0)
        self.assertEqual(models.Article.objects.count(), 0)
        del self.valid_ajson['article']
        self.assertRaises(Exception, ajson_ingestor.ingest, self.valid_ajson)
        self.assertEqual(models.Journal.objects.count(), 0)
        self.assertEqual(models.Article.objects.count(), 0)

    def test_article_ingest_bad_article_version(self):
        "bad article version data will fail an ingest of article json"
        self.assertEqual(models.Journal.objects.count(), 0)
        self.assertEqual(models.Article.objects.count(), 0)
        self.assertEqual(models.ArticleVersion.objects.count(), 0)
        del self.valid_ajson['article']['title']
        self.assertRaises(Exception, ajson_ingestor.ingest, self.valid_ajson)
        self.assertEqual(models.Journal.objects.count(), 0)
        self.assertEqual(models.Article.objects.count(), 0)
        self.assertEqual(models.ArticleVersion.objects.count(), 0)

class TestAJSONPublish(BaseCase):
    def setUp(self):
        self.ajson_fixture1 = join(self.fixture_dir, 'ajson', 'elife.01968.json')
        self.ajson = json.load(open(self.ajson_fixture1, 'r'))

    def tearDown(self):
        pass

    def test_article_publish(self):
        "an unpublished article can be successfully published"
        _, _, av = ajson_ingestor.ingest(self.ajson)
        self.assertEqual(models.Journal.objects.count(), 1)
        self.assertEqual(models.Article.objects.count(), 1)
        self.assertEqual(models.ArticleVersion.objects.count(), 1)
        self.assertFalse(av.published())

        # publish
        msid = self.ajson['article']['id']
        version = self.ajson['article']['version'] # this won't be coming from the json .. will it?
        av = ajson_ingestor.publish(msid, version)

        # aaand just make sure we still have the expected number of objects
        self.assertEqual(models.Journal.objects.count(), 1)
        self.assertEqual(models.Article.objects.count(), 1)
        self.assertEqual(models.ArticleVersion.objects.count(), 1)
        
        self.assertTrue(av.published())
        self.assertTrue(isinstance(av.datetime_published, datetime))
        self.assertEqual(utils.ymd(datetime.now()), utils.ymd(av.datetime_published))
        
    def test_article_publish_fails_if_already_published(self):
        "a published article cannot be published again"
        _, _, av = ajson_ingestor.ingest(self.ajson)
        msid = self.ajson['article']['id']
        version = self.ajson['article']['version'] # this won't be coming from the json .. will it?
        av = ajson_ingestor.publish(msid, version)
        av = self.freshen(av)
        self.assertTrue(av.published())

        # publish again
        self.assertRaises(StateError, ajson_ingestor.publish, msid, version)

    def test_article_publish_succeeds_for_published_article_if_forced(self):
        _, _, av = ajson_ingestor.ingest(self.ajson)
        msid = self.ajson['article']['id']
        version = self.ajson['article']['version'] # this won't be coming from the json .. will it?
        old_publish_date = utils.todt('2001-01-01')
        av = ajson_ingestor.publish(msid, version, old_publish_date)
        av = self.freshen(av)
        self.assertEqual(av.datetime_published, old_publish_date)

        # publish again
        new_publish_date = utils.todt('2011-01-01')
        av = ajson_ingestor.publish(msid, version, new_publish_date, force=True)
        av = self.freshen(av)
        self.assertEqual(av.datetime_published, new_publish_date)
