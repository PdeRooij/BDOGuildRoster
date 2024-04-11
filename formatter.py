from table2ascii import table2ascii, PresetStyle

class Formatter:
    """
    Format pretty stuff.
    """

    def list_to_table(self, in_list, columns):
        """

        :param in_list:
        :param columns:
        :return:
        """
        # Convert 1D list to 2D table with defined number of columns
        table = [in_list[idx:idx + columns] for idx in range(0, len(in_list), columns)]

        # If the last row is incomplete, append empty cells
        last_length = len(table[-1])
        if last_length < columns:
            table[-1].extend([''] * (columns - last_length))

        # Deliver the final table
        return table

    def format_table(self, entries, columns=2, header=None):
        """
        Turns a given list to a printable table with specified number of columns.
        :param entries: List to convert.
        :param columns: Number of columns in the table.
        :param header: (Optional) Headers to put on the table.
        :return: Formatted table
        """
        # Convert 1D list to 2D table with defined number of columns
        table_body = self.list_to_table(entries, columns)

        # If a header has been provided, put it on top, otherwise construct a table with only a body
        if header:
            print_table = table2ascii(header=header, body=table_body, style=PresetStyle.markdown)
        print_table = table2ascii(body=table_body, style=PresetStyle.markdown)

        # Put the result in a codeblock
        return f"```{print_table}```"

    def format_roster(self, guild, members):
        """
        Returns a printable roster.

        :param guild: Guild name.
        :param members: List of (name, fammily_page) tuples of all members in the guild.
        :return: Printable roster of provided guild.
        """
        # Members is a list of (name, family_page) tuples. We only print name on a roster.
        names = [member[0] for member in members]
        return f'Players currently in {guild}:\n{self.format_table(names, columns=6)}'

    def format_roster_changes(self, guild, last_update, changes):
        """

        :param guild:
        :param changes:
        :return:
        """
        # If there are no changes, display so
        if not changes:
            return f'No roster changes in {guild} since {last_update}.'

        # Split changes into members who left and who joined
        left = []
        joined = []
        [left.append(change[1]) if change[0] == 'left' else joined.append(change[1]) for change in changes]

        # Construct message and give back
        message = f'{guild} roster changes since {last_update}:\n'
        if len(left) > 0:
            if len(left) == 1:
                message += f'{len(left)} family left:\n```{left[0]}```\n'
            else:
                message += f'{len(left)} families left:\n{self.format_table(left, columns=2)}\n'
        if len(joined) > 0:
            if len(joined) == 1:
                message += f'{len(joined)} family joined:\n```{joined[0]}```\n'
            else:
                message += f'{len(joined)} families joined:\n{self.format_table(joined, columns=2)}\n'
        return message

    def format_alias(self, disc_name, family):
        """
        Turns provided alias into a readable message
        :param disc_name:
        :param family:
        :return: Message about alias found.
        """
        # If an alias is found, print family and Discord name
        if disc_name:
            return f'Family {family} is known as {disc_name} on the Discord server.'
        else:
            return f'Could not find an alias for family {family}!'

    def format_family_page(self, family, page):
        """
        Turns provided family page into a readable message

        :param family: Family name.
        :param page: Link to family page.
        :return: Message with link to requested family's page if available. Could not find if not.
        """
        # If an alias is found, print family and Discord name
        if page:
            return f"[{family}'s webpage]({page})"
        else:
            return f'Could not find a page for family {family}!'