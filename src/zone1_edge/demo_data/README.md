# demo_data/

Put your demo images and audio here before the final test:

- `crop/` — 4-6 sample crop photos (tomato/potato/maize, healthy + diseased)
- `livestock/` — 4-6 sample cattle photos (healthy + diseased)
- `audio/` — 3-4 fixed Hindi sentences (crop / livestock / healthy / ambiguous),
  recorded by Person B for ASR testing (Hour 0:15-1:30)

These are git-ignored by default (see .gitignore) since they can be large
binary files — either commit small compressed samples deliberately, or keep
them local-only and document what you used in results/.
