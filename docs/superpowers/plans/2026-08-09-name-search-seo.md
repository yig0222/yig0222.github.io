# Name Search SEO Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve discovery of the unchanged CV homepage for both `Ingyu Yoo` and `유인규` by adding standards-based identity, canonical, social, and crawl metadata.

**Architecture:** Preserve every HTML `<body>` and the stylesheet while enriching each document `<head>`. Represent the person once with a stable homepage JSON-LD identifier, reference that identifier from subpages, and expose all canonical pages through `robots.txt` and `sitemap.xml`.

**Tech Stack:** Static HTML5, Schema.org JSON-LD, Open Graph metadata, robots exclusion protocol, XML sitemap, Python 3 standard-library `unittest`.

## Global Constraints

- Keep all visible page content and styling unchanged.
- Use `Ingyu Yoo` as the primary name and `유인규` as `alternateName`.
- Use `https://yig0222.github.io/` as the canonical site root.
- Do not add `meta keywords`, hidden keyword text, unsupported claims, invented profiles, or fabricated sitemap modification dates.
- Search ranking is not guaranteed; implementation only improves machine-readable discovery signals.

## File Map

- `index.html`: homepage canonical/Open Graph metadata and authoritative `Person` plus `WebSite` JSON-LD.
- `research.html`: page canonical/Open Graph metadata and `WebPage` JSON-LD referencing the homepage person.
- `publications.html`: page canonical/Open Graph metadata and `WebPage` JSON-LD referencing the homepage person.
- `teaching.html`: page canonical/Open Graph metadata and `WebPage` JSON-LD referencing the homepage person.
- `robots.txt`: crawl permission and sitemap discovery.
- `sitemap.xml`: canonical URL inventory for the four HTML pages.
- `tests/test_seo.py`: automated checks for metadata, JSON-LD, robots, sitemap, and unchanged body content.

---

### Task 1: Add executable SEO contract tests

**Files:**
- Create: `tests/test_seo.py`

**Interfaces:**
- Consumes: the four root HTML documents and, after Task 4, `robots.txt` and `sitemap.xml`.
- Produces: a `python -m unittest tests.test_seo -v` verification command used by all later tasks.

- [ ] **Step 1: Write tests for canonical/Open Graph metadata, JSON-LD identity, crawl files, and preserved body content**

Use `html.parser.HTMLParser` to collect `<head>` links/meta tags, JSON-LD scripts, and the literal `<body>` section. Define canonical URLs as:

```python
PAGES = {
    "index.html": "https://yig0222.github.io/",
    "research.html": "https://yig0222.github.io/research.html",
    "publications.html": "https://yig0222.github.io/publications.html",
    "teaching.html": "https://yig0222.github.io/teaching.html",
}
```

The test cases must assert:

```python
self.assertEqual(document.canonical, expected_url)
self.assertEqual(document.meta["og:url"], expected_url)
self.assertEqual(document.meta["og:type"], "website")
self.assertEqual(document.meta["og:site_name"], "Ingyu Yoo")
self.assertTrue(document.meta["og:title"])
self.assertTrue(document.meta["og:description"])
```

For homepage JSON-LD, locate nodes by `@type` and assert:

```python
self.assertEqual(person["@id"], "https://yig0222.github.io/#person")
self.assertEqual(person["name"], "Ingyu Yoo")
self.assertEqual(person["alternateName"], "유인규")
self.assertIn("https://github.com/yig0222", person["sameAs"])
self.assertEqual(website["author"]["@id"], person["@id"])
```

For each subpage, assert one `WebPage` node whose `url` equals its canonical URL and whose author is `https://yig0222.github.io/#person`.

For crawl files, parse `sitemap.xml` with `xml.etree.ElementTree`, compare its `<loc>` values to `set(PAGES.values())`, and assert `robots.txt` contains:

```text
User-agent: *
Allow: /
Sitemap: https://yig0222.github.io/sitemap.xml
```

To enforce visual/body preservation, obtain the baseline body of each page from commit `35aa8db` with `git show 35aa8db:<filename>` and compare it byte-for-byte with the working page body after normalizing only line endings.

- [ ] **Step 2: Run the test to verify the SEO contract fails before implementation**

Run: `python -m unittest tests.test_seo -v`

Expected: failures for missing canonical/Open Graph/JSON-LD metadata and missing crawl files; body-preservation assertions pass.

- [ ] **Step 3: Commit the failing contract tests**

```powershell
git add -- tests/test_seo.py
git commit -m "test: define SEO metadata contract"
```

---

### Task 2: Add homepage identity metadata

**Files:**
- Modify: `index.html` inside `<head>` only
- Test: `tests/test_seo.py`

**Interfaces:**
- Consumes: canonical base URL and existing public facts in `index.html`.
- Produces: the stable person identifier `https://yig0222.github.io/#person` referenced by every subpage.

- [ ] **Step 1: Add canonical and Open Graph tags after the existing description**

```html
<link rel="canonical" href="https://yig0222.github.io/">
<meta property="og:type" content="website">
<meta property="og:url" content="https://yig0222.github.io/">
<meta property="og:title" content="Ingyu Yoo — Materials Science &amp; TEM">
<meta property="og:description" content="Ingyu Yoo — Ph.D. candidate in Materials Science and Engineering specializing in Transmission Electron Microscopy and 2D materials.">
<meta property="og:site_name" content="Ingyu Yoo">
```

- [ ] **Step 2: Add a JSON-LD graph before the stylesheet link**

Define a `Person` node with `@id`, `name`, `alternateName`, `url`, `email`, `jobTitle`, `sameAs`, `knowsAbout`, and existing university relationships. Define a `WebSite` node with `@id`, `url`, `name`, `alternateName`, and `author: {"@id": "https://yig0222.github.io/#person"}`. Serialize it as valid JSON inside `<script type="application/ld+json">`.

- [ ] **Step 3: Run the homepage-related tests**

Run: `python -m unittest tests.test_seo.SeoMetadataTests.test_homepage_identity tests.test_seo.SeoMetadataTests.test_metadata tests.test_seo.BodyPreservationTests -v`

Expected: homepage identity, homepage metadata, and all body-preservation checks pass; no `<body>` line has changed.

- [ ] **Step 4: Commit homepage metadata**

```powershell
git add -- index.html
git commit -m "feat: add structured identity metadata"
```

---

### Task 3: Add canonical metadata to topic pages

**Files:**
- Modify: `research.html` inside `<head>` only
- Modify: `publications.html` inside `<head>` only
- Modify: `teaching.html` inside `<head>` only
- Test: `tests/test_seo.py`

**Interfaces:**
- Consumes: `https://yig0222.github.io/#person` from Task 2 and each page's existing title/description.
- Produces: three canonical, independently discoverable `WebPage` entities attributed to the same person.

- [ ] **Step 1: Add page-specific canonical and Open Graph metadata**

For each file, set `rel="canonical"` and `og:url` to its value in `PAGES`, set `og:type` to `website`, set `og:site_name` to `Ingyu Yoo`, and use these exact page values:

| File | Open Graph title | Open Graph description |
| --- | --- | --- |
| `research.html` | `Research — Ingyu Yoo` | `Research interests of Ingyu Yoo: stacking sequence determination, deep learning for TEM, and displacement vector field mapping in TMD heterostructures.` |
| `publications.html` | `Publications &amp; Conferences — Ingyu Yoo` | `Publications, conference presentations, and awards of Ingyu Yoo.` |
| `teaching.html` | `Teaching &amp; Talks — Ingyu Yoo` | `Teaching experience, invited seminars, and workshops by Ingyu Yoo.` |

- [ ] **Step 2: Add one page-specific `WebPage` JSON-LD node per file**

Add these exact logical values, serialized as valid JSON:

```json
[
  {
    "file": "research.html",
    "url": "https://yig0222.github.io/research.html",
    "name": "Research — Ingyu Yoo",
    "description": "Research interests of Ingyu Yoo: stacking sequence determination, deep learning for TEM, and displacement vector field mapping in TMD heterostructures."
  },
  {
    "file": "publications.html",
    "url": "https://yig0222.github.io/publications.html",
    "name": "Publications & Conferences — Ingyu Yoo",
    "description": "Publications, conference presentations, and awards of Ingyu Yoo."
  },
  {
    "file": "teaching.html",
    "url": "https://yig0222.github.io/teaching.html",
    "name": "Teaching & Talks — Ingyu Yoo",
    "description": "Teaching experience, invited seminars, and workshops by Ingyu Yoo."
  }
]
```

For every object above, emit a `WebPage` object with `@context: "https://schema.org"`, `@type: "WebPage"`, the listed `url`, `name`, and `description`, plus `author: {"@id": "https://yig0222.github.io/#person"}` and `isPartOf: {"@id": "https://yig0222.github.io/#website"}`. The `file` key documents routing and is not emitted into JSON-LD.

- [ ] **Step 3: Run metadata and body-preservation tests**

Run: `python -m unittest tests.test_seo.SeoMetadataTests tests.test_seo.BodyPreservationTests -v`

Expected: all page metadata, JSON-LD, and body-preservation tests pass.

- [ ] **Step 4: Commit topic-page metadata**

```powershell
git add -- research.html publications.html teaching.html
git commit -m "feat: add canonical metadata to CV pages"
```

---

### Task 4: Publish crawler discovery files

**Files:**
- Create: `robots.txt`
- Create: `sitemap.xml`
- Test: `tests/test_seo.py`

**Interfaces:**
- Consumes: the four canonical URLs defined in `PAGES`.
- Produces: standards-based crawler permission and sitemap discovery at stable root URLs.

- [ ] **Step 1: Add `robots.txt`**

```text
User-agent: *
Allow: /

Sitemap: https://yig0222.github.io/sitemap.xml
```

- [ ] **Step 2: Add `sitemap.xml`**

Create a valid UTF-8 XML sitemap using the `http://www.sitemaps.org/schemas/sitemap/0.9` namespace with one `<url><loc>…</loc></url>` entry for each URL in `PAGES`. Do not add `lastmod`, `changefreq`, or `priority` values.

- [ ] **Step 3: Run the complete test suite**

Run: `python -m unittest tests.test_seo -v`

Expected: all tests pass, including exact URL-set equality for the sitemap and the robots sitemap directive.

- [ ] **Step 4: Commit crawl files**

```powershell
git add -- robots.txt sitemap.xml
git commit -m "feat: add crawler discovery files"
```

---

### Task 5: Final standards and visual verification

**Files:**
- Verify: `index.html`
- Verify: `research.html`
- Verify: `publications.html`
- Verify: `teaching.html`
- Verify: `robots.txt`
- Verify: `sitemap.xml`
- Verify: `tests/test_seo.py`

**Interfaces:**
- Consumes: all deliverables from Tasks 1–4.
- Produces: evidence that metadata parses, URLs agree, body content is untouched, and pages render without visible changes.

- [ ] **Step 1: Run automated verification from a clean command invocation**

Run: `python -m unittest tests.test_seo -v`

Expected: exit code 0 and all tests report `ok`.

- [ ] **Step 2: Check formatting and scope**

Run: `git diff --check 35aa8db..HEAD`

Expected: exit code 0 with no whitespace errors.

Run: `git status --short`

Expected: no uncommitted files after all task commits.

- [ ] **Step 3: Inspect the pages in a local browser**

Serve the repository locally, open all four HTML pages, and confirm their visible text, navigation, spacing, and styling are unchanged. Metadata must not create visible elements.

- [ ] **Step 4: Provide deployment follow-up**

Report the changed files, verification result, and the non-code next step: deploy to GitHub Pages, add `https://yig0222.github.io/` as a Google Search Console URL-prefix property, then submit `https://yig0222.github.io/sitemap.xml`. State that Google controls indexing timing and ranking.
