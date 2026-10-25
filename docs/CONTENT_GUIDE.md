# Managing content

Sign in to `/admin/` using the superuser you created. Public account registration never grants staff privileges.

## Translation fields

Translated fields use a JSON object. Example:

```json
{"en":"Tomato","hi":"टमाटर","mr":"टोमॅटो","ta":"தக்காளி","bn":"টমেটো"}
```

English is required. Missing languages fall back to English. Plant detailed-care and article pages disclose fallback content; mark `translation_reviewed` only after a competent language reviewer checks the text. Main labels are in `garden/labels.json`; form/account labels currently use English. The selected language is stored in an essential cookie and switching preserves the page/filter URL.

## Plants

Edit names, science name, category, summary, care, soil, sunlight, container depth and caution text. Use plain text: paragraphs are escaped and line-broken; arbitrary HTML is intentionally not rendered. Supply sources and an actual reviewed date when reviewed. `published=false` hides the record from search/detail/planner/sitemap.

The minimum sunlight field is a coarse planner filter, not a full shade/heat model. Pothos uses zero minimum direct sunlight but still requires bright indirect light; it does not grow in a dark room. Harvest strings are illustrative ranges with their starting stage specified, not guarantees.

## Photos

Upload JPEG/PNG/WebP under 3 MB and 16 megapixels. Staff uploads are validated, resized, converted to JPEG and stripped of original metadata; random filenames prevent script-like extensions. Fill credit, source and licence fields. For new third-party assets, retain the licence URL and any attribution/change notice; the included CC images have licence links in the credits page/JSON. Do not upload images found through a search engine without verifying reuse rights.

## Regions and calendars

A region record represents the named example city/area, not an entire state. Add actual coordinates if enabling weather. Soil descriptions are general context, never a substitute for testing.

Planting windows contain plant, region, **action** (sow, transplant or plant), month numbers `[6,7,8]`, notes, source and `verified`. The starter records are all unverified drafts. For a new region, consult a local university/KVK source. Record exact varieties/elevation caveats in notes. Do not copy one state's calendar to another and mark it verified.

## Guides and blog

Use categories `home`, `soil`, `equipment` or `diary`. Add title, summary and body translations and source references. Blog entries can be created in `diary`; the included diary is explicitly a writing prompt, not a fabricated gardening experiment. Equipment articles explain purposes and selection, without invented current prices or affiliate shopping dependencies.

## Seed updates

`python manage.py seed_garden` adds missing starter records only. It does not update existing text, media credits or calendars. For deliberate content changes use admin or a reviewed data migration; do not delete your database to refresh content.

## Before public launch

Review all 12 plant profiles, 72 draft regional windows and translated content. Expand the catalogue only as sources and editorial capacity allow. The application is complete for the documented workflow; the national content library is intentionally a modest starter, not an expert-reviewed nationwide database.
