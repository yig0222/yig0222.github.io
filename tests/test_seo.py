import json
import subprocess
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASELINE_COMMIT = "35aa8db"
PERSON_ID = "https://yig0222.github.io/#person"
WEBSITE_ID = "https://yig0222.github.io/#website"
PAGES = {
    "index.html": "https://yig0222.github.io/",
    "research.html": "https://yig0222.github.io/research.html",
    "publications.html": "https://yig0222.github.io/publications.html",
    "teaching.html": "https://yig0222.github.io/teaching.html",
}


class SeoDocumentParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.canonical = None
        self.meta = {}
        self.json_ld = []
        self._in_json_ld = False
        self._json_ld_chunks = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "link" and "canonical" in attributes.get("rel", "").split():
            self.canonical = attributes.get("href")
        elif tag == "meta" and attributes.get("property"):
            self.meta[attributes["property"]] = attributes.get("content", "")
        elif tag == "script" and attributes.get("type") == "application/ld+json":
            self._in_json_ld = True
            self._json_ld_chunks = []

    def handle_data(self, data):
        if self._in_json_ld:
            self._json_ld_chunks.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self._in_json_ld:
            self.json_ld.append(json.loads("".join(self._json_ld_chunks)))
            self._in_json_ld = False
            self._json_ld_chunks = []


def parse_document(filename):
    parser = SeoDocumentParser()
    parser.feed((ROOT / filename).read_text(encoding="utf-8"))
    return parser


def json_ld_nodes(document):
    nodes = []
    for payload in document.json_ld:
        if isinstance(payload, dict) and isinstance(payload.get("@graph"), list):
            nodes.extend(payload["@graph"])
        else:
            nodes.append(payload)
    return nodes


def body_fragment(document):
    lower = document.lower()
    start = lower.index("<body")
    end = lower.index("</body>") + len("</body>")
    return document[start:end].replace("\r\n", "\n")


class SeoMetadataTests(unittest.TestCase):
    def test_metadata(self):
        for filename, expected_url in PAGES.items():
            with self.subTest(filename=filename):
                document = parse_document(filename)
                self.assertEqual(document.canonical, expected_url)
                self.assertEqual(document.meta.get("og:url"), expected_url)
                self.assertEqual(document.meta.get("og:type"), "website")
                self.assertEqual(document.meta.get("og:site_name"), "Ingyu Yoo")
                self.assertTrue(document.meta.get("og:title"))
                self.assertTrue(document.meta.get("og:description"))

    def test_homepage_identity(self):
        nodes = json_ld_nodes(parse_document("index.html"))
        person = next((node for node in nodes if node.get("@type") == "Person"), None)
        website = next((node for node in nodes if node.get("@type") == "WebSite"), None)

        self.assertIsNotNone(person)
        self.assertIsNotNone(website)
        self.assertEqual(person.get("@id"), PERSON_ID)
        self.assertEqual(person.get("name"), "Ingyu Yoo")
        self.assertEqual(person.get("alternateName"), "유인규")
        self.assertEqual(person.get("url"), PAGES["index.html"])
        self.assertIn("https://github.com/yig0222", person.get("sameAs", []))
        self.assertEqual(website.get("@id"), WEBSITE_ID)
        self.assertEqual(website.get("author", {}).get("@id"), PERSON_ID)

    def test_subpages_reference_homepage_identity(self):
        for filename, expected_url in PAGES.items():
            if filename == "index.html":
                continue
            with self.subTest(filename=filename):
                nodes = json_ld_nodes(parse_document(filename))
                webpage = next(
                    (node for node in nodes if node.get("@type") == "WebPage"), None
                )
                self.assertIsNotNone(webpage)
                self.assertEqual(webpage.get("url"), expected_url)
                self.assertEqual(webpage.get("author", {}).get("@id"), PERSON_ID)
                self.assertEqual(webpage.get("isPartOf", {}).get("@id"), WEBSITE_ID)


class CrawlDiscoveryTests(unittest.TestCase):
    def test_robots_allows_crawling_and_advertises_sitemap(self):
        robots_path = ROOT / "robots.txt"
        self.assertTrue(robots_path.exists(), "robots.txt must exist")
        directives = {
            line.strip()
            for line in robots_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        }
        self.assertTrue(
            {
                "User-agent: *",
                "Allow: /",
                "Sitemap: https://yig0222.github.io/sitemap.xml",
            }.issubset(directives)
        )

    def test_sitemap_lists_every_canonical_page(self):
        sitemap_path = ROOT / "sitemap.xml"
        self.assertTrue(sitemap_path.exists(), "sitemap.xml must exist")
        root = ET.parse(sitemap_path).getroot()
        namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locations = {node.text for node in root.findall("sm:url/sm:loc", namespace)}
        self.assertEqual(locations, set(PAGES.values()))


class BodyPreservationTests(unittest.TestCase):
    def test_visible_body_content_matches_approved_baseline(self):
        for filename in PAGES:
            with self.subTest(filename=filename):
                baseline = subprocess.run(
                    ["git", "show", f"{BASELINE_COMMIT}:{filename}"],
                    cwd=ROOT,
                    check=True,
                    capture_output=True,
                ).stdout.decode("utf-8")
                current = (ROOT / filename).read_text(encoding="utf-8")
                self.assertEqual(body_fragment(current), body_fragment(baseline))


if __name__ == "__main__":
    unittest.main()
