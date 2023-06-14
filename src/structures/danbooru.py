from pybooru import Danbooru


class CustomDanbooru(Danbooru):
    def is_gold(self, user_name: str):
        """
        Checks whether the user is a gold user or not.

        Args:
            user_name (str): The user name in question.
        """
        levels_range = [
            20,     # Normal members
            30      # Gold members.
        ]

        if self.user_list(name=user_name, level=levels_range[1]):
            return True
        else:
            return False


                