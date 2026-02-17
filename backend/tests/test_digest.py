from clara.jobs.digest import _build_digest_html


def test_digest_html_escapes_user_name():
    html = _build_digest_html("<script>xss</script>", ["item"], "Title")
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_digest_html_escapes_items():
    html = _build_digest_html("Bob", ["<b>bold</b>"], "Title")
    assert "<b>bold</b>" not in html
    assert "&lt;b&gt;" in html


def test_digest_html_escapes_title():
    html = _build_digest_html("Bob", ["item"], "<img onerror=alert(1)>")
    assert "<img " not in html
    assert "&lt;img " in html
