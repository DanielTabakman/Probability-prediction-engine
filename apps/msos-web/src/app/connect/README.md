# Personal QR landing page (/connect)

A small mobile-first digital business card for Daniel Tabakman.

- Page: `https://marketstructureos.com/connect`
- Contact download: `https://marketstructureos.com/connect/contact.vcf`
- Links: LinkedIn, WhatsApp, Market Structure OS; no new dependencies
- Phone numbers are **not** hardcoded in the public GitHub repository.

## Before release

1. Owner confirms the WhatsApp number to expose publicly on the landing page and downloadable contact card.
2. Configure the **runtime** VPS environment variable `MSOS_CONNECT_WHATSAPP_NUMBER` as international digits with country code (no `+`, spaces, or punctuation), e.g. `1XXXXXXXXXX`. This is not an auth secret, but avoiding a Git commit reduces accidental disclosure and simplifies updates.
3. Verify the production Next.js app receives the variable. Restart/recreate the `msos_web` container after configuration; do not assume a build-arg-only env is available at runtime.
4. Preview the page, use a phone to test the LinkedIn and WhatsApp links, and download/import the vCard. Confirm the number is correct.
5. Owner explicitly approves merge to `main` (which auto-deploys the VPS). Do **not** auto-merge this draft.
6. After production passes checks, print a 30–35 mm QR code aimed at the **canonical** `https://marketstructureos.com/connect`. Do not use the QR code before the route responds successfully.

### Privacy/ops
This page is public. The WhatsApp link and vCard will reveal the configured phone number to anyone, including bots and search scrapers. `robots.noindex` reduces ordinary indexing but does not provide access control. The existing root layout may include the site's analytics beacon.
