import pycountry
from geopy.geocoders import GeoNames


def get_all_languages():
    languages = []
    for language in pycountry.languages:
        languages.append({
            'name': language.name,
            'code': language.alpha_2 if hasattr(language, 'alpha_2') else language.alpha_3
        })
    return languages


def get_languages_by_first_letter(letter):
    letter = letter.upper()
    matching_languages = []
    for language in pycountry.languages:
        if language.name.upper().startswith(letter):
            matching_languages.append({
                'name': language.name,
                'code': language.alpha_2 if hasattr(language, 'alpha_2') else language.alpha_3
            })
    return sorted(matching_languages, key=lambda x: x['name'])


def get_language_index_letter():
    first_letter = set()
    for language in pycountry.languages:
        first_letter.add(language.name[0].upper())

    # Sort the first letters, placing special characters at the end
    sorted_first_letter = sorted(first_letter, key=lambda x: (not x.isalpha(), x))
    return list(sorted_first_letter)


def get_top25_languages():
    language_names = [
        'English', 'Mandarin Chinese', 'Hindi', 'Spanish', 'French',
        'Modern Standard Arabic', 'Bengali', 'Russian', 'Portuguese',
        'Urdu', 'Indonesian', 'German', 'Japanese', 'Nigerian Pidgin',
        'Egyptian Arabic', 'Marathi', 'Telugu', 'Turkish', 'Tamil',
        'Cantonese', 'Vietnamese', 'Wu Chinese', 'Tagalog', 'Korean', 'Farsi'
    ]

    top25_languages = []
    for name in language_names:
        language = pycountry.languages.get(name=name)
        if language:
            top25_languages.append({
                'name': language.name,
                'code': language.alpha_2 if hasattr(language, 'alpha_2') else language.alpha_3
            })
        else:
            top25_languages.append({'name': name, 'code': None})

    return top25_languages




