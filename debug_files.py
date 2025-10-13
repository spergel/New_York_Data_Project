#!/usr/bin/env python3
from pathlib import Path

# Check if any academic output files exist
academic_dir = Path('academic')
scraper_names = [
    'columbia_classics_events',
    'columbia_general_events',
    'columbia_math_events',
    'cooper_union_events',
    'cornell_tech_events',
    'fordham_events',
    'gallatin_events',
    'isaw_events',
    'jtsa_events',
    'juilliard_events',
    'miller_events',
    'new_school_events',
    'nyu_api_events',
    'nyu_cims_events',
    'nyu_education_events',
    'nyu_engineering',
    'nyu_law_events',
    'nyu_medicine_events',
    'nyu_neuroscience_events',
    'nyu_physics_events',
    'nyu_steinhardt_events',
    'nyu_steinhardt_music_events',
    'nyu_stern_events',
    'pratt_events',
    'simons_foundation_events',
]

found_files = []
for scraper in scraper_names:
    possible_paths = [
        academic_dir / 'scrapers' / f'{scraper}_debug.json',
        academic_dir / 'scrapers' / 'data' / f'{scraper}_events.json',
        academic_dir / f'{scraper}_debug.json',
        academic_dir / 'data' / f'{scraper.replace("_scraper", "")}_events.json',
        academic_dir / f'{scraper.replace("_scraper", "")}_events_debug.json',
    ]

    for path in possible_paths:
        if path.exists():
            found_files.append((scraper, path))
            break

print(f'Found {len(found_files)} output files:')
for scraper, path in found_files[:10]:  # Show first 10
    print(f'  {scraper}: {path}')

if len(found_files) == 0:
    print('No output files found!')
    # List what files do exist in academic directory
    print('\\nFiles in academic directory:')
    for file in academic_dir.glob('*_debug.json'):
        print(f'  {file.name}')




