import pdfkit
from html_format import html_format_t


fields_to_end_with_br = [
    ('release_date', 'RELEASE DATE: '),
    ('genres', 'GENRES: '),
    ('locations', 'LOCATIONS: '),
    ('producers', 'PRODUCER: '),
    ('writers', 'WRITER: '),
    ('directors', 'DIRECTOR: '),
    ('cast', 'CAST: '),
    ('production_companies', '')
]

movie = {
    'url': 'http://altitudefilment.com/film/production/8/guns-akimbo',
    'id': '8',
    'title': 'GUNS AKIMBO',
    'aka_title': '',
    'studios': [],
    'release_date': '2019',
    'genres': [],
    'plot': [
        'GUNS AKIMBO follows a man whose mundane existence is turned upside-down when '
        'he finds himself enrolled on a dark net website that forces complete '
        'strangers to fight in a city-wide game of death, so that their gladiatorial '
        'battles can be live-streamed worldwide to a fanatical audience. '
        'After being pitted against a seemingly unstoppable killing machine, '
        'he at first manages to avoid conflict, but when his ex-girlfriend is '
        'kidnapped, he must overcome his fears and stop running.'
    ],
    'start_wrap_schedule': '',
    'photography_start_date': '',
    'project_type': '',
    'cast': [],
    'writers': ['Jason Lei Howden'],
    'directors': ['Jason Lei Howden'],
    'producers': [
        'Tom Hern', 'Will Clarke', 'Robyn Grace', 'Belindalee Hope', 'John Jencks',
        'Stefan Kapelari', 'Philipp Kreuzer', 'Michael J. Mailis', 'Felipe Marino',
        'Andy Mayson', 'Joe Neurauter', 'Mortiz Peters', 'Adrian Politowski',
        'Jörg Schulze', 'Joe Simpson', 'Bastien Sirodot', 'Jay Taylor'
    ],
    'production_companies': [],
    'locations': [],
    'project_issue_date': ''
}

movie['plot'] = ', '.join(movie['plot'] or [])
movie['genres'] = ', '.join(movie['genres'] or [])
movie['studios'] = ' - '.join(movie['studios'] or [])
movie['producers'] = ' - '.join(movie['producers'] or [])
movie['writers'] = ' - '.join(movie['writers'] or [])
movie['cast'] = ' - '.join(movie['cast'] or [])
movie['directors'] = ' - '.join(movie['directors'] or [])
movie['production_companies'] = ', '.join(movie['production_companies'] or [])
movie['locations'] = ' - '.join(movie['locations'] or [])

for field, suffix in fields_to_end_with_br:
    if movie[field]:
        movie[field] = f'{movie[field]}<br>'

if movie['aka_title']:
    movie['aka_title'] = f'(aka "{movie["aka_title"]}")'

# html = html_format_t.format(**movie)
pdfkit.from_string(html_format_t, 'out.pdf')
