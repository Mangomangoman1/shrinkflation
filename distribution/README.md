# Distribution kit (nothing here is submitted anywhere)

Ready-to-use metadata for listing the CC BY 4.0 case library. Each step needs Samuel's own account, so none has been done.

- **Zenodo DOI**: `.zenodo.json` and `CITATION.cff` in the repo root are read by Zenodo's GitHub integration. Log in to zenodo.org with GitHub, Account → GitHub → Sync, switch on `Mangomangoman1/shrinkflation`, then create a GitHub release (e.g. `data-2026-10`). Zenodo archives it and mints a DOI.
- **Awesome Public Datasets**: `apd-core-ShrinkRadar.yml` goes to `core/Economics/ShrinkRadar.yml` in a fork of github.com/awesomedata/apd-core, then open a PR.
- **Kaggle**: put `site/data/cases.csv` next to `kaggle/dataset-metadata.json`, replace `KAGGLE_USERNAME`, and run `kaggle datasets create -p distribution/kaggle` (or upload in the web UI).
- **Open Food Facts reuse**: tell reuse@openfoodfacts.org about the site (it uses OFF/OPF/OBF quantities and Open Prices), or use the "get your app featured" form on world.openfoodfacts.org/data.
