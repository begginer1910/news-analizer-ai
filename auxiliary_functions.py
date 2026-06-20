class Auxiliary:
    def __init__(self):
        self.avaible_languages = {
                "arabic": "ar",
                "german": "de",
                "english": "en",
                "spanish": "es",
                "french": "fr",
                "hebrew": "he",
                "italian": "it",
                "dutch": "nl",
                "norwegian": "no",
                "portuguese": "pt",
                "russian": "ru",
                "swedish": "sv",
                "chinese": "zh"
            }
        self.validcategories = ['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology']
        self.countries = {
            'united arab emirates': 'ae', 'argentina': 'ar', 'austria': 'at', 'australia': 'au',
            'belgium': 'be', 'bulgaria': 'bg', 'brazil': 'br', 'canada': 'ca', 'switzerland': 'ch',
            'china': 'cn', 'colombia': 'co', 'cuba': 'cu', 'czech republic': 'cz', 'germany': 'de',
            'egypt': 'eg', 'france': 'fr', 'united kingdom': 'gb', 'greece': 'gr', 'hong kong': 'hk',
            'hungary': 'hu', 'indonesia': 'id', 'ireland': 'ie', 'israel': 'il', 'india': 'in',
            'italy': 'it', 'japan': 'jp', 'south korea': 'kr', 'lithuania': 'lt', 'latvia': 'lv',
            'morocco': 'ma', 'mexico': 'mx', 'malaysia': 'my', 'nigeria': 'ng', 'netherlands': 'nl',
            'norway': 'no', 'new zealand': 'nz', 'philippines': 'ph', 'pakistan': 'pk', 'poland': 'pl',
            'portugal': 'pt', 'romania': 'ro', 'serbia': 'rs', 'russia': 'ru', 'saudi arabia': 'sa',
            'sweden': 'se', 'singapore': 'sg', 'slovenia': 'si', 'slovakia': 'sk', 'thailand': 'th',
            'turkey': 'tr', 'taiwan': 'tw', 'ukraine': 'ua', 'united states': 'us', 'venezuela': 've',
            'south africa': 'za'
        }

    def text(self, msg):
        while True:
            self.t = input(msg).lower().strip()
            if self.t:
                return self.t
            print("It can't be empty")
    def numbers(self, msg):
        while True:
            try:
                return int(input(msg))
            except ValueError:
                print("Enter a number !!")
            except EOFError:
                print("No input provided")
                return None
    def validate_language(self, language: str):
        language = language.lower().strip()
        if language in self.avaible_languages:
            return self.avaible_languages[language]
        if language in self.avaible_languages.values():
            return language
        return None
    def validate_category(self, category: str):
        category = category.lower().strip()
        if category in self.validcategories:
            return category
        return None
    def validate_country(self, country: str):
        country = country.lower().strip()
        if country in self.countries:
            return self.countries[country]
        if country in self.countries.values():
            return country
        return None

