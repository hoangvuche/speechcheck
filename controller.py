from keys import *


class QCController:

    def __init__(self, keywords, view):
        # Model
        self.keywords = keywords

        # View
        self.view = view

    def refresh_keywords(self):
        self.keywords.refresh(self.view)

    def get_keywords(self):
        pass

    def save_keyword(self):
        pass

    def remove_keyword(self):
        pass
