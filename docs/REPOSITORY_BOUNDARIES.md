# Repository boundaries

## Ownership

`DanielTabakman/Probability-prediction-engine` owns two tightly related product
surfaces:

- Probability Prediction Engine (PPE)
- Market Structure OS (MSOS)

It is not a general-purpose host for Daniel's other products, prototypes, or
collaborators' applications.

## Allowed cross-repository relationships

PPE/MSOS may:

- link to a separate product's canonical site or repository;
- call an external service through an explicitly documented API boundary;
- depend on a versioned package when that dependency is part of PPE/MSOS.

PPE/MSOS must not:

- copy another product's source or built assets into this repository;
- create a route whose purpose is to run an unrelated product;
- proxy another repository's HTML, JavaScript, or CSS to make it appear hosted
  by MSOS;
- use an iframe to embed an unrelated application;
- treat the `/daniel` namespace as a loophole for storing product code.

## Where experiments belong

An experiment belongs in the repository for the product whose hypothesis it is
testing. If no repository exists, create or designate one before implementation.
The hosting choice follows repository ownership; available MSOS infrastructure
is not, by itself, a reason to put the experiment in PPE.

## Enforcement

`python scripts/check_repository_boundaries.py` runs in the local pushable gate
and in CI. It enforces:

- the approved top-level MSOS route families;
- a link-only `/daniel` page with no nested applications or public assets;
- no runtime iframes;
- no runtime proxying from GitHub Pages or raw GitHub content.

Changing the allowlist or an enforcement rule is a product-ownership decision,
not routine implementation cleanup. The change must explain which PPE/MSOS
capability owns the new surface and why a separate repository is insufficient.

## Incident note: PitchPacks

On 2026-08-17, PitchPacks prototype code and proxy routes were added under the
MSOS web application so the game could be played on an existing site. That
optimized for immediate hosting but violated product ownership. The code is
owned by `DanielTabakman/pitch-packs`; PPE/MSOS should not host it.
