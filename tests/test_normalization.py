from app.normalization import normalize_url


def test_normalize_url_removes_tracking():
    url = "https://Example.com/path/?utm_source=newsletter&foo=bar"
    assert normalize_url(url) == "https://example.com/path?foo=bar"


def test_normalize_url_handles_trailing_slash():
    url = "https://example.com/path/"
    assert normalize_url(url) == "https://example.com/path"
