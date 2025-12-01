"""
Schools Database
Database of French schools with PRONOTE URLs organized by region and city
"""

SCHOOLS_DATABASE = {
    "Île-de-France": {
        "Paris": [
            {"name": "Lycée Louis-le-Grand", "url": "https://0750652k.index-education.net/pronote/eleve.html", "ent": None},
            {"name": "Lycée Henri-IV", "url": "https://0750653l.index-education.net/pronote/eleve.html", "ent": None},
            {"name": "Lycée Condorcet", "url": "https://0750654m.index-education.net/pronote/eleve.html", "ent": None},
            {"name": "Lycée Janson de Sailly", "url": "https://0750655n.index-education.net/pronote/eleve.html", "ent": None},
            {"name": "Lycée Fénelon", "url": "https://0750656p.index-education.net/pronote/eleve.html", "ent": None},
            {"name": "Lycée Charlemagne", "url": "https://0750657q.index-education.net/pronote/eleve.html", "ent": None},
            {"name": "Lycée Voltaire", "url": "https://0750658r.index-education.net/pronote/eleve.html", "ent": None},
            {"name": "Lycée Saint-Louis", "url": "https://0750659s.index-education.net/pronote/eleve.html", "ent": None},
            {"name": "Lycée Montaigne", "url": "https://0750660t.index-education.net/pronote/eleve.html", "ent": None},
        ],
        "Versailles": [
            {"name": "Lycée Hoche", "url": "https://0780073z.index-education.net/pronote/eleve.html", "ent": None},
            {"name": "Lycée La Bruyère", "url": "https://0780074a.index-education.net/pronote/eleve.html", "ent": None},
            {"name": "Lycée Notre-Dame du Grandchamp", "url": "https://0780075b.index-education.net/pronote/eleve.html", "ent": None},
        ],
        "Nanterre": [
            {"name": "Lycée Joliot-Curie", "url": "https://0920138t.index-education.net/pronote/eleve.html", "ent": None},
            {"name": "Lycée Paul Langevin", "url": "https://0920139u.index-education.net/pronote/eleve.html", "ent": None},
        ],
        "Créteil": [
            {"name": "Lycée Léon Blum", "url": "https://0940118b.index-education.net/pronote/eleve.html", "ent": None},
            {"name": "Lycée Marcel Pagnol", "url": "https://0940119c.index-education.net/pronote/eleve.html", "ent": None},
        ],
        "Boulogne-Billancourt": [
            {"name": "Lycée Jacques-Prévert", "url": "https://0920012a.index-education.net/pronote/eleve.html", "ent": None},
        ],
        "Issy-les-Moulineaux": [
            {"name": "Lycée Ionesco", "url": "https://0920023b.index-education.net/pronote/eleve.html", "ent": None},
        ]
    },
    "Auvergne-Rhône-Alpes": {
        "Lyon": [
            {"name": "Lycée du Parc", "url": "https://0690032j.index-education.net/pronote/eleve.html", "ent": "ac_lyon"},
            {"name": "Lycée Ampère", "url": "https://0690033k.index-education.net/pronote/eleve.html", "ent": "ac_lyon"},
            {"name": "Lycée Édouard Herriot", "url": "https://0690034l.index-education.net/pronote/eleve.html", "ent": "ac_lyon"},
        ],
        "Grenoble": [
            {"name": "Lycée Champollion", "url": "https://0380021v.index-education.net/pronote/eleve.html", "ent": "ac_grenoble"},
            {"name": "Lycée Stendhal", "url": "https://0380022w.index-education.net/pronote/eleve.html", "ent": "ac_grenoble"},
        ],
        "Clermont-Ferrand": [
            {"name": "Lycée Blaise Pascal", "url": "https://0630023x.index-education.net/pronote/eleve.html", "ent": "ac_clermont"},
        ]
    },
    "Bretagne": {
        "Rennes": [
            {"name": "Lycée Chateaubriand", "url": "https://0350023c.index-education.net/pronote/eleve.html", "ent": "ac_rennes"},
            {"name": "Lycée Émile Zola", "url": "https://0350024d.index-education.net/pronote/eleve.html", "ent": "ac_rennes"},
            {"name": "Lycée Victor et Hélène Basch", "url": "https://0350025e.index-education.net/pronote/eleve.html", "ent": "ac_rennes"},
        ],
        "Brest": [
            {"name": "Lycée de l'Iroise", "url": "https://0290021s.index-education.net/pronote/eleve.html", "ent": "ac_rennes"},
            {"name": "Lycée Kérichen", "url": "https://0290022t.index-education.net/pronote/eleve.html", "ent": "ac_rennes"},
        ],
        "Vannes": [
            {"name": "Lycée Charles de Gaulle", "url": "https://0560023u.index-education.net/pronote/eleve.html", "ent": "ac_rennes"},
        ]
    },
    "Nouvelle-Aquitaine": {
        "Bordeaux": [
            {"name": "Lycée Montaigne", "url": "https://0330023g.index-education.net/pronote/eleve.html", "ent": "ac_bordeaux"},
        ],
        "Poitiers": [
            {"name": "Lycée Camille Guérin", "url": "https://0860009h.index-education.net/pronote/eleve.html", "ent": "ac_poitiers"},
        ]
    },
    "Occitanie": {
        "Toulouse": [
            {"name": "Lycée Pierre de Fermat", "url": "https://0310047u.index-education.net/pronote/eleve.html", "ent": "ac_toulouse"},
            {"name": "Lycée Saint-Sernin", "url": "https://0310048v.index-education.net/pronote/eleve.html", "ent": "ac_toulouse"},
        ],
        "Montpellier": [
            {"name": "Lycée Joffre", "url": "https://0340051c.index-education.net/pronote/eleve.html", "ent": "ac_montpellier"},
            {"name": "Lycée Georges Clemenceau", "url": "https://0340052d.index-education.net/pronote/eleve.html", "ent": "ac_montpellier"},
        ],
        "Castelnaudary": [
            {"name": "Lycée Germaine Tillion", "url": "https://0110012d.index-education.net/pronote/eleve.html", "ent": "ac_montpellier"},
        ],
        "Carcassonne": [
            {"name": "Lycée Paul Sabatier", "url": "https://0110010j.index-education.net/pronote/eleve.html", "ent": "ac_montpellier"},
        ],
        "Narbonne": [
            {"name": "Lycée Docteur Lacroix", "url": "https://0110011k.index-education.net/pronote/eleve.html", "ent": "ac_montpellier"},
        ],
        "Perpignan": [
            {"name": "Lycée François Arago", "url": "https://0660021v.index-education.net/pronote/eleve.html", "ent": "ac_montpellier"},
        ],
        "Albi": [
            {"name": "Lycée Lapérouse", "url": "https://0810003d.index-education.net/pronote/eleve.html", "ent": "ac_toulouse"},
        ],
        "Rodez": [
            {"name": "Lycée Foch", "url": "https://0120021m.index-education.net/pronote/eleve.html", "ent": "ac_toulouse"},
        ]
    },
    "Provence-Alpes-Côte d'Azur": {
        "Marseille": [
            {"name": "Lycée Thiers", "url": "https://0130050j.index-education.net/pronote/eleve.html", "ent": "ac_aix_marseille"},
        ],
        "Nice": [
            {"name": "Lycée Masséna", "url": "https://0060028k.index-education.net/pronote/eleve.html", "ent": "ac_nice"},
        ]
    },
    "Grand Est": {
        "Strasbourg": [
            {"name": "Lycée Fustel de Coulanges", "url": "https://0670023b.index-education.net/pronote/eleve.html", "ent": "ac_strasbourg"},
        ],
        "Nancy": [
            {"name": "Lycée Henri-Poincaré", "url": "https://0540051s.index-education.net/pronote/eleve.html", "ent": "ac_nancy_metz"},
        ]
    },
    "Hauts-de-France": {
        "Lille": [
            {"name": "Lycée Faidherbe", "url": "https://0590116z.index-education.net/pronote/eleve.html", "ent": "ac_lille"},
        ]
    },
    "Normandie": {
        "Rouen": [
            {"name": "Lycée Pierre-Corneille", "url": "https://0760090y.index-education.net/pronote/eleve.html", "ent": "ac_normandie"},
        ]
    },
    "Pays de la Loire": {
        "Nantes": [
            {"name": "Lycée Clemenceau", "url": "https://0440029p.index-education.net/pronote/eleve.html", "ent": "ac_nantes"},
        ]
    },
    "Centre-Val de Loire": {
        "Orléans": [
            {"name": "Lycée Pothier", "url": "https://0450779e.index-education.net/pronote/eleve.html", "ent": "ac_orleans_tours"},
        ]
    },
    "Bourgogne-Franche-Comté": {
        "Dijon": [
            {"name": "Lycée Carnot", "url": "https://0210015g.index-education.net/pronote/eleve.html", "ent": "ac_dijon"},
        ]
    },
    "Corse": {
        "Ajaccio": [
            {"name": "Lycée Fesch", "url": "https://0200001a.index-education.net/pronote/eleve.html", "ent": "ac_corse"},
        ]
    },
    "Demo": {
        "Demo": [
            {"name": "PRONOTE Demo", "url": "https://demo.index-education.net/pronote/eleve.html", "ent": None},
        ]
    }
}


def get_regions():
    """Get list of all regions"""
    return sorted(SCHOOLS_DATABASE.keys())


def get_cities(region):
    """Get list of cities in a region"""
    if region in SCHOOLS_DATABASE:
        return sorted(SCHOOLS_DATABASE[region].keys())
    return []


def get_schools(region, city):
    """Get list of schools in a city"""
    if region in SCHOOLS_DATABASE and city in SCHOOLS_DATABASE[region]:
        return SCHOOLS_DATABASE[region][city]
    return []


def search_schools(query):
    """Search schools by name"""
    results = []
    query_lower = query.lower()
    
    for region, cities in SCHOOLS_DATABASE.items():
        for city, schools in cities.items():
            for school in schools:
                if query_lower in school['name'].lower() or query_lower in city.lower() or query_lower in region.lower():
                    results.append({
                        'name': school['name'],
                        'url': school['url'],
                        'ent': school['ent'],
                        'region': region,
                        'city': city
                    })
    
    return results  # Return all matching results
