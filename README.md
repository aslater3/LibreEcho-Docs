# LibreEcho website

Static GitHub Pages site for **LibreEcho**, an open operating system and hardware-enablement project for Amazon Echo Gen 2.

## Publish

1. Create an empty GitHub repository.
2. Extract this archive and copy its contents into the repository root.
3. Replace `YOUR-USERNAME/libreecho` in:
   - `assets/js/site.js`
   - `robots.txt`
   - `sitemap.xml`
4. Commit and push to the `main` branch.
5. In **Settings → Pages**, select **GitHub Actions** as the source.

The included workflow publishes the site automatically on every push to `main`.

## Custom domain

Add a file named `CNAME` to the repository root containing only the domain, for example:

```text
libreecho.org
```

Then configure the DNS records GitHub documents for Pages. A custom domain is optional; the site works at the standard `github.io` address.

## Replacing artwork

The repository-native SVG artwork lives in `assets/images/`. It is deliberately referenced through stable filenames. To use the original generated PNG image pack later, either replace the corresponding SVG files and update the extensions in `index.html`, or export the generated images to these names:

- `echo-hero.svg` — main product image
- `open-device.svg` — contribution section artwork
- `social-card.svg` — social preview image
- `mark.svg` — project mark

## Local preview

```bash
python3 -m http.server 8000
```

Open `http://localhost:8000`.

## Project status language

The progress cards are intentionally high-level. Update their wording in `index.html` as hardware enablement advances.
