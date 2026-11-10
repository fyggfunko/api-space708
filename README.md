# intartlecture — Google Ads preparation build

Clean bilingual (FR/DE) presentation landing with Mux video steps and an optional lead form.

## Design direction

White / institutional visual system aimed at reducing typical Google Ads landing complaints:

- Calm teal accent instead of purple funnel styling
- Source Serif 4 + Source Sans 3
- Light video placeholder (not a dark “VSL player” shell)
- Soft status gate instead of urgency-countdown look
- Explicit risk, operator, privacy and terms sections

## Included

- Immediate German/French language-choice dialog on the first page; language links remain in the header.
- Original language-specific Mux IDs on each corresponding page (six IDs total).
- Original first-page button destination restored: `index2.php` for French, `de/index2.php` for German. Completion highlights the Continue button; it does not force navigation.
- Explicit user click before the external video player is loaded.
- Native video controls; no autoplay, fake progress, forced completion, fake viewer counts, fake availability, or redirects.
- Privacy, terms and operator-information sections.

## Before advertising

1. Confirm operator details: KALEO 1 LTD, company number 17383494, 28 Kingfisher Road, Upminster, RM14 1ER, United Kingdom; +44 7412 655101.
2. Review the spoken and visual content of all videos. The page cannot make a non-compliant video compliant.
3. Add a real privacy/consent implementation if analytics, advertising tags, cookies or a contact form are later introduced.
4. Confirm that the product, financial permissions, claims, fees, risk disclosure and target-country requirements are accurate.
5. Host over HTTPS and test both `/index.html` and `/de/index.html` on the production domain.

The build is policy-oriented preparation, not a guarantee of Google Ads approval.
