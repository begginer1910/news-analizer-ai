class auxiliary:
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
    def u_language(self):
        while True:
            user_language = self.text("In which language do you want the news? "
                                    "(enter the full name of language, for example english): ")
            if user_language in self.avaible_languages:
                return self.available_languages[user_language]
            if user_language in self.avaible_languages.values():
                return user_language
            print("Wrong language !!")

