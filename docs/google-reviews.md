# Google reviews

The desktop homepage displays a snapshot of the public Wix widget captured on 1 November 2026 until a Google API key is configured. This snapshot does not update automatically. Once configured, it loads the business rating, review count and up to five reviews directly from Google Maps Platform, and stays hidden if the request fails. Mobile stays hidden like the Wix widget. No site backend is used.

To activate it, a Google Cloud administrator must:

1. Select or create a Google Cloud project, enable billing, and enable Maps JavaScript API and Places API (New).
2. Create a **browser** API key, restrict it to the required APIs and HTTP referrers for the actual site origins (local development, the GitHub Pages test site, and the approved preview and production domains as needed). Use a separate development key if appropriate. The key is visible to visitors; do not use a server or unrestricted key. Set usage quotas and billing alerts.
3. Set `browserApiKey` in `data/googleReviews.json` to the restricted key. The existing `placeId` identifies Elisa's listing. Rebuild and test on each allowed origin, including a valid response and failure behavior.
4. Before production, review [Google Maps JavaScript API policies](https://developers.google.com/maps/documentation/javascript/policies), including attribution, publicly accessible terms and privacy policy requirements, and the applicable EEA terms. Google controls review selection and may return fewer than five. Do not store API responses or present the captured snapshot as current.

The owner has not yet supplied a key or configured billing. Google requests can incur charges; see [Google Maps pricing](https://developers.google.com/maps/billing-and-pricing/overview). A local build alone does not authorize pushing or deploying the site.
