# intartlecture — Google Ads preparation build

French presentation landing with Mux video steps and an optional lead form.

## Design direction

Dark presentation look:

- Pure black canvas, Montserrat, bold uppercase headlines
- Neon green / cyan gradient accents
- Important alert box for the watch-time gate
- Centered layout; soft status timer (not fake scarcity)


## Included

- Original language-specific Mux IDs on each corresponding page (six IDs total).
- First-page button destination: `index2.php`. Completion highlights the Continue button; it does not force navigation. The landing is French only, with no language switch.
- Explicit user click before the external video player is loaded.
- Native video controls; no autoplay, fake progress, forced completion, fake viewer counts, fake availability, or redirects.
- Privacy, terms and operator-information sections.

## Before advertising

1. Confirm operator details: KALEO 1 LTD, company number 17383494, 28 Kingfisher Road, Upminster, RM14 1ER, United Kingdom; +44 7412 655101.
2. Review the spoken and visual content of all videos. The page cannot make a non-compliant video compliant.
3. Add a real privacy/consent implementation if analytics, advertising tags, cookies or a contact form are later introduced.
4. Confirm that the product, financial permissions, claims, fees, risk disclosure and target-country requirements are accurate.
5. Host over HTTPS and test `/index.html` on the production domain.

The build is policy-oriented preparation, not a guarantee of Google Ads approval.
