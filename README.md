# LibreEcho website

Static GitHub Pages site for **LibreEcho**, an open operating system and hardware-enablement project for Amazon Echo Gen 2.

## Publish

This is the public product site, deployed from the `main` branch. Development
documentation and the browser demo live in `aslater3/LibreEcho-Docs-dev`.

The included workflow publishes the site automatically on every push to `main`.
It also runs every six hours and checks out the latest
`aslater3/LibreEcho-UI` source to render the Control Centre screenshots shown
on the site. If the UI repository is private, add the existing fine-grained
`UI_REPOSITORY_TOKEN` secret to this repository with read-only Contents access;
without it, the last committed real screenshots are used as a deployment
fallback. A manual refresh is available from the workflow dispatch action.

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

Open `http://localhost:8000`. The production site keeps the onboarding, support,
privacy, release, licensing and contribution guidance on one navigable page so a
new visitor can reach each route from the header without relying on JavaScript.
The browser-local Control Centre demonstration remains a separate development
site in `aslater3/LibreEcho-Docs-dev`.

## Tests

Run the deterministic static contract check before opening a pull request:

```bash
python3 tests/site-check.py
```

The check validates required sections, in-page links, local assets, public release
filenames, maintained review date, and rejection of stale GitHub placeholders or
private device/network data.

## Project status language

The site is written for owners and first-time visitors, not developers: plain,
friendly second-person copy that says what works, what is experimental and what
is coming next. Keep internal workflow detail (branch names, run IDs, CI states,
private evidence) off the public page.

Stable release `radar-puffin-v0.13.19` is public for the Amazon Echo 2nd Gen.
LibreEcho 0.14 (adding the Echo Dot 2nd Gen) is described on the roadmap as in
final testing and has no download links until it is published. When 0.14 ships,
pin the release card, install section and `tests/site-check.py` to the new tag.
Do not publish device identifiers, private run manifests, serials, MAC
addresses, or local paths.
