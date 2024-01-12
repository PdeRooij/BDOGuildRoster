class Formatter:
    """
    Format pretty stuff.
    """

    def construct_table(self, entries, columns=2):
        """
        Turns a given list to a printable table with specified columns.
        """
        table = '-----\n'
        for idx, e in enumerate(entries):
            table += e
            if idx % columns == 0:
                table += '\n'
            else:
                table += ' | '
        table += '\n-----'
        return table