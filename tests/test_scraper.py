from types import SimpleNamespace

import scraper


def test_clean_text_removes_html_and_links():
    assert scraper.clean_text("<b>Merhaba</b> https://example.com  dünya") == "Merhaba dünya"


def test_banned_word_filter_is_case_insensitive():
    assert scraper.check_banned_words("Bu haber intihar hakkında")
    assert not scraper.check_banned_words("Teknoloji dünyasında yeni gelişme")


def test_feed_failure_does_not_invent_content(monkeypatch):
    def fail():
        raise TimeoutError("offline")
    monkeypatch.setattr(scraper, "_fetch_feed", fail)
    assert scraper.get_content() == []


def test_turkish_news_item_has_stable_id(monkeypatch):
    entry = SimpleNamespace(
        title="Yapay zekâ araştırmalarında yeni gelişme",
        summary="Bilim insanları yeni bir yöntem açıkladı.",
        link="https://example.test/news/1",
    )
    monkeypatch.setattr(scraper, "_fetch_feed", lambda: SimpleNamespace(entries=[entry]))
    first = scraper.get_content()
    second = scraper.get_content()
    assert len(first) == 1
    assert first[0]["id"] == second[0]["id"]
    assert first[0]["source"] == "Google News RSS"
