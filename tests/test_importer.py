from app.importers.html import BookmarkHtmlImporter


HTML_SAMPLE = """
<!DOCTYPE NETSCAPE-Bookmark-file-1>
<TITLE>Bookmarks</TITLE>
<DL><p>
    <DT><A HREF="https://example.com" ADD_DATE="1714000000" TAGS="research,example">Example</A>
    <DT><A HREF="https://example.com" ADD_DATE="1714000001">Duplicate</A>
</DL><p>
"""


def test_html_importer_deduplicates():
    importer = BookmarkHtmlImporter()
    bookmarks = list(importer.parse(HTML_SAMPLE))
    assert len(bookmarks) == 2
    assert bookmarks[0].title == "Example"
    assert bookmarks[0].tags == ["research", "example"]
