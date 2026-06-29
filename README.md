# UFC GOAT Simulator

A data-driven UFC analytics engine that ranks all-time fighters, 
identifies fighting style archetypes, and simulates GOAT tournament 
brackets using probabilistic modelling.

## What it does

- **P4P Rankings** -> Glicko-2 rating system built on all historical UFC bouts, 
  normalised across weight classes and adjusted for title fight context
- **Fighter DNA** -> Unsupervised style clustering that assigns every fighter 
  a style archetype (e.g. Pressure Wrestler, Counter Striker, Submission Artist) 
  based on career statistics
- **GOAT Simulator** -> Monte Carlo tournament bracket (10,000 runs) pitting 
  all-time greats against each other at peak rating, with matchup odds 
  adjusted for stylistic compatibility

## Tech Stack

- **Scraping**: Python, BeautifulSoup, requests
- **Database**: PostgreSQL
- **Backend**: FastAPI
- **ML/Modelling**: scikit-learn, UMAP, custom Glicko-2 implementation
- **Frontend**: React

## Status

🚧 In active development
