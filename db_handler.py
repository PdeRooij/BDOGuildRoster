import sqlite3
from sqlite3 import connect, Error
from datetime import datetime

class DB_Handler:
    """
    Class handling interactions between the bot and its SQLite database.
    """

    def __init__(self, db_file):
        """
        Class is initialised by preparing a connection to a given database file.

        Args:
            db_file (str): Name (and location) of the database file
        """
        self.db_file = db_file
        self.connection = None

    def create_connection(self):
        """Try to connect to existing SQLite database."""
        try:
            self.connection = connect(self.db_file)
        except Error as e:
            print(e)
            raise

    def execute_commit(self, sql, values=None):
        """
        Execute and commit given SQL statement with inserted values.

        Args:
            sql (str): SQL statement to execute. Values are inserted for question marks '?'
            values (tuple): (Optional) Tuple of values inserted for each question mark '?' in sql
            """
        if self.connection is not None:
            # Either insert values into SQL statement or just execute without if none are provided
            if values:
                self.connection.cursor().execute(sql, values)
            else:
                self.connection.cursor().execute(sql)
            # Commit to database
            self.connection.commit()
        else:
            raise FileNotFoundError("Error! No database connection.")
    
    def get_variable(self, variable):
        """ Retrieves value of a stored variable.

        Args:
            variable (str): Name of variable to look for.

        Returns:
            str: Value of requested variable.
        """
        cur = self.connection.cursor()
        cur.execute(f"SELECT value FROM roster_status WHERE variable = '{variable}'")

        return cur.fetchone()[0]

    def replace_variable(self, variable, value):
        """Replace (add or change) specific variable in table of variables.

        Args:
            variable (str): Name of variable to replace.
            value (str): Value to associate with variable.
        """
        sql = "REPLACE INTO roster_status (variable, value) VALUES ('{}', '{}')".\
            format(variable, value)
        self.execute_commit(sql)

    def initialise_database(self, dump_file):
        """
        Initialise database based on an exported SQLite database.

        Args:
            dump_file (str): Location of the exported SQLite database.

        """
        # Don't try to populate the database if there is no connection
        if self.connection is not None:
            # Read from given dump file
            with open(dump_file, 'r') as df:
                self.connection.cursor().executescript(df.read())
        else:
            raise FileNotFoundError("Error! No database connection.")

    def get_last_update(self):
        """Queries when the last update was performed.

        Returns:
            str: Date and time of the last update.
        """
        return datetime.strptime(self.get_variable('last_update'), '%Y-%m-%d %H:%M:%S')

    def update_last_update(self):
        """Sets last update to now.
        """
        self.replace_variable('last_update', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    def add_guild_member(self, member, rank=None):
        """
        Add a (new) family to the guild_members table

        Args:
            member (str): family name of the added member
            rank (str): guild rank of the added member
        """
        # Construct sql statement and corresponding values
        sql = """INSERT INTO guild_members(family, rank)
                  VALUES(?,?)"""
        values = (member, rank)

        # Execute and commit insert
        self.execute_commit(sql, values)

    def remove_guild_member(self, member):
        """
        Delete a family from the guild_members table

        Args:
            member (str): family name of the deleted member
        """
        # Execute and commit delete
        self.execute_commit(f"DELETE FROM guild_members WHERE family='{member}'")

    def get_all_guild_members(self):
        """ Query all family names from the guild_members table.

        Returns:
            A list of all guild members (family name) in the database.
        """
        cur = self.connection.cursor()
        cur.execute("SELECT family FROM guild_members")

        return [row[0] for row in cur.fetchall()]

    def find_family(self, family):
        """ Retrieves stored information on a specified family.

        Args:
            family (str): Family name to search.
        Returns:
            Complete results found for specified family name.
        """
        cur = self.connection.cursor()
        cur.execute(f"SELECT * FROM guild_members WHERE family = '{family}'")

        # Returns dictionary with column names as keys and corresponding values
        return dict(zip([desc[0] for desc in cur.description], cur.fetchone()))

    def replace_alias(self, family, disc_name):
        """
        Add/replace a family = discord user combination to the database

        Args:
            family (str): in-game family name
            disc_name (str): username on Discord server
        """
        # Construct sql statement and corresponding values
        sql = """REPLACE INTO family_to_discord(family, discord_name)
                  VALUES(?,?)"""
        values = (family, disc_name)

        # Execute and commit insert
        self.execute_commit(sql, values)

    def remove_alias(self, disc_name):
        """
        Delete an alias from the family_to_discord table

        Args:
            disc_name (str): discord name of the deleted alias
        """
        # Execute and commit delete
        self.execute_commit(f"DELETE FROM family_to_discord WHERE discord_name='{disc_name}'")

    def find_alias(self, family):
        """ Retrieves stored alias for a specified family.

        Args:
            family (str): Family name to search.
        Returns:
            Alias (str) if found, otherwise None.
        """
        cur = self.connection.cursor()
        cur.execute(f"SELECT discord_name FROM family_to_discord WHERE family = '{family}'")

        # Return Discord name if found, otherwise None
        return cur.fetchone()

    def query(self, query):
        """ A debugging function for executing any sql statement on the database.

        Args:
            query (str): SQL statement to execute.
        Returns:
            Result of executing the query.
        """
        self.connection.row_factory = sqlite3.Row
        cur = self.connection.cursor()
        cur.execute(query)

        # Returns list of rows, where is row is a  dictionary with column names as keys and corresponding values
        return cur.fetchall()

    def dump(self, dump_file):
        """
        Dumps database to specified file.

        Args:
            dump_file (str): Location of the file to dump the database to.
        """
        with open(dump_file, 'w') as df:
            for line in self.connection.iterdump():
                df.write(line + '\n')

    def close_connection(self):
        """ Close connection to current SQLite database. """
        if self.connection:
            self.connection.close()
