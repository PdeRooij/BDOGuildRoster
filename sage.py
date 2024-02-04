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

        :param new_roster: List of all families currently in the guild.
        :return: List of all changes to the roster since last update.
        """
        # Connect to the database and update
        self.db.create_connection()
        self.db.update_last_update()

        # Initialise list of changes and retrieve old roster from database
        roster_changes = []
        old_roster = self.db.get_all_guild_members()
        # Add new members to the database and change list
        for new_member in [family for family in new_roster if family not in old_roster]:
            self.db.add_guild_member(new_member)
            roster_changes.append(('joined', new_member))
        # Delete old members from the database and add to change list
        for old_member in [family for family in old_roster if family not in new_roster]:
            self.db.remove_guild_member(old_member)
            roster_changes.append(('left', old_member))

        # Close connection to the database and provide list of roster changes
        self.db.close_connection()
        return roster_changes

    def dummy_roster_change(self):
        return [('left', 'old_member'), ('left', 'kicked'), ('joined', 'nice_person')]