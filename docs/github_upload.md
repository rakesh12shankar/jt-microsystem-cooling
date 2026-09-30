# Upload this project to GitHub

## Suggested repository details

Name: `jt-microsystem-cooling`

Description: Computational study of Joule–Thomson cooler integration with infrared microsystems, including package heat leaks, finite elements, constrained design search and bond-defect sensitivity.

Topics: `cryogenics`, `heat-transfer`, `joule-thomson`, `microsystems`, `finite-element-method`, `thermal-management`, `python`.

## Upload

1. Extract the ZIP locally. The enclosed `jt-microsystem-cooling` folder is the repository root.
2. Create an empty GitHub repository. Leave the generated README, license and gitignore options unchecked because the bundle contains the project documentation and ignore rules.
3. Upload the extracted folder contents, not the ZIP itself. Preserve `config`, `data`, `docs`, `results` and `output` at the repository root beside `README.md`.
4. For a complete upload including hidden files, use GitHub Desktop to add this folder as a local repository and publish it, or use Git from this folder:

```sh
git init
git add .
git commit -m "Add JT microsystem cooling computational study"
git branch -M main
git remote add origin YOUR_REPOSITORY_URL
git push -u origin main
```

Replace `YOUR_REPOSITORY_URL` with the URL of your empty repository. These commands assume a new local repository and an empty remote. Authentication uses your own Git configuration.

## Included

- Python models, study runners and all 43 verification tests.
- Configuration and short numerical source records with attribution.
- Final array results, original figures, extension studies and clearly identified exploratory results.
- Methods, source audits, limitations, reproducibility guide and portfolio summary.
- Optional Word report builder; the generated Word report is excluded from this public upload.
- `UPLOAD_MANIFEST.json` with SHA256 hashes of the bundled files.

The publisher PDFs, full-text extracts, temporary rendering files, caches, local virtual environments and credentials are excluded. Numerical studies run using local inputs without the PDFs.

## Scientific interpretation and reuse

The package ratings are conditional simulated results. Numerical verification and reproduction of a published calculation do not establish experimental validation of the proposed detector package. Keep these limitations in the README and any portfolio description.

No open-source license is assigned in this bundle. Decide on a license separately before offering general reuse rights. Journal sources and third-party dependencies retain their own rights and terms.

## Verify locally

```sh
python -m pip install -r requirements.txt
python -m unittest -v
```

All 43 tests passed during packaging on 30 September 2026. This checks the existing verification suite; it does not rerun every expensive design sweep. Reproduction commands and their order are in `docs/reproducibility.md`.
