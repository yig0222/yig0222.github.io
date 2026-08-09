# Ingyu Yoo / 유인규 Name Search SEO Design

## Goal

Improve the likelihood that the existing CV homepage is discovered for searches for both `Ingyu Yoo` and `유인규`, while preserving all visible page content and styling.

Search ranking cannot be guaranteed. The implementation will give search engines clearer identity, ownership, canonical URL, and crawl-discovery signals without keyword stuffing or hidden visible text.

## Scope

The site is a static GitHub Pages site at `https://yig0222.github.io/` with four HTML pages:

- `index.html`
- `research.html`
- `publications.html`
- `teaching.html`

The implementation will modify only each page's `<head>` and add crawler-facing files at the repository root. Existing `<body>` content and CSS will remain unchanged.

## Metadata Design

Each HTML page will receive:

- An absolute canonical URL for its public GitHub Pages URL.
- Open Graph metadata identifying the page title, description, URL, site name, and website type.
- A consistent site name containing the primary English name and Korean alternate name where metadata supports it.

Existing page-specific titles and descriptions will remain semantically equivalent. The homepage metadata will identify the person directly; subpage metadata will retain its page topic and relationship to Ingyu Yoo.

`meta keywords` will not be added because Google does not use it for web ranking. Hidden keyword text will not be added.

## Structured Data Design

The homepage will include JSON-LD using Schema.org vocabulary:

- A `Person` entity whose `name` is `Ingyu Yoo` and whose `alternateName` is `유인규`.
- The canonical homepage URL as the stable entity identifier and URL.
- Existing public facts already present on the site, including job title, email, research topics, educational affiliations, and GitHub profile.
- A `WebSite` entity that connects the site to the `Person` as its author.

Subpages will include lightweight `WebPage` JSON-LD with their canonical URLs, page names, descriptions, and the homepage `Person` entity as author. All references will use the same stable person identifier so crawlers can treat the pages as belonging to one person.

No unsupported claims, unlisted social profiles, or invented identifiers will be included.

## Crawl Discovery

Add:

- `robots.txt`, allowing normal crawling and pointing to the sitemap.
- `sitemap.xml`, listing the four canonical HTML URLs.

The sitemap will use canonical public URLs and omit fabricated modification dates. It will be valid XML and remain small enough to maintain manually.

## Validation

Verification will cover:

- Parsing all HTML files and confirming exactly one canonical URL per page.
- Parsing every JSON-LD block as valid JSON.
- Confirming the sitemap is valid XML and contains all four canonical URLs.
- Confirming `robots.txt` references the correct sitemap URL.
- Reviewing the diff to ensure no `<body>` content or CSS changed.
- If practical, checking the deployed or local pages in a browser to confirm there is no visual change.

After deployment, Google Search Console registration and sitemap submission will be recommended as a separate account-level step. Indexing and ranking remain controlled by Google and can take time.
