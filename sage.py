from db_handler import DB_Handler

class Sage:
    """
    Takes care of the complex logic of what to do with retrieved information and what is stored in the database.
    """

    def __init__(self, db_file):
        """
        Make sure database is ready.

        Args:
            db_file (str): Name (and location) of the database file
        """
        self.db = DB_Handler(db_file)
        # Connect to the database and store last update datetime
        self.db.create_connection()
        self.last_update = self.db.get_last_update()
        self.db.close_connection()

    def compare_guild_members(self, new_roster):
        """
        Checks if there are changes to the roster since last update.

        :param new_roster: List of all families (in name, page tuples) currently in the guild.
        :return: List of all changes to the roster since last update.
        """
        # Extract names from (name, family_page) tuples for comparison
        new_names = [family[0] for family in new_roster]

        # Connect to the database and update
        self.db.create_connection()
        self.last_update = self.db.get_last_update()
        self.db.update_last_update()

        # Initialise list of changes and retrieve old roster from database
        roster_changes = []
        old_names = self.db.get_all_guild_members()
        # Add new members to the database and change list
        for new_member in [family for family in new_roster if family[0] not in old_names]:
            self.db.add_guild_member(new_member[0], family_page=new_member[1])
            roster_changes.append(('joined', new_member))
        # Delete old members from the database and add to change list
        for old_member in [family for family in old_names if family not in new_names]:
            self.db.remove_guild_member(old_member)
            roster_changes.append(('left', old_member))

        # Close connection to the database and provide list of roster changes
        self.db.close_connection()
        return roster_changes

    def replace_alias(self, family, disc_name):
        """
        Replaces or adds alias to the database.

        :param family: In-game family name.
        :param disc_name: Discord name.
        """
        # Connect to the database and replace/add alias
        self.db.create_connection()
        self.db.replace_alias(family, disc_name)
        self.db.close_connection()

    def remove_alias(self, disc_name):
        """
        Removes alias from the database.

        :param disc_name: Discord name.
        """
        # Connect to the database and replace/add alias
        self.db.create_connection()
        self.db.remove_alias(disc_name)
        self.db.close_connection()

    def find_alias(self, family):
        """
        Attempts to find a discord name for given family name.

        :param family: In-game family name.
        """
        # Connect to the database and search for alias
        self.db.create_connection()
        alias = self.db.find_alias(family)
        self.db.close_connection()
        if alias:
            return alias[0]

    def find_page(self, family):
        """
        Attempts to find a webpage for given family name.

        :param family: In-game family name.
        """
        # Connect to the database and search for page
        self.db.create_connection()
        page = self.db.find_page(family)
        self.db.close_connection()
        if page:
            return page[0]

    def dummy_roster_change(self):
        return [('left', 'old_member'), ('left', 'kicked'), ('joined', 'nice_person')]
