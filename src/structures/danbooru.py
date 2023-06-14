from pybooru import Danbooru


class CustomDanbooru(Danbooru):
    def is_gold(self):
        """
        Checks whether the user is a gold user or not.

        Args:
            user_name (str): The user name in question.
        """
        levels_range = [
            20,     # Normal members
            30,     # Gold members.
            31,     # Platinum  
            32,     # Builder
            33,     # Contributor 
            35,     # Janitor  
            40,     # Moderator  
            50      # Admin
        ]

        if any([self.user_list(name=self.username, level=i) for i in levels_range[1:]]):
            return True
        else:
            return False


                