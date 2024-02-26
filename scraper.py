import requests
from bs4 import BeautifulSoup

class PA_Scraper:
    """
    Scraper of the Black Desert Online website hosted by Pearl Abyss.
    """

    def __init__(self, guild, region):
        """
        Initialise with components and urls
        """
        # Listener preparation
        self.sessy = requests.Session()  # Initialise session
        # URL of the webpage to scrape
        self.url = f'https://www.naeu.playblackdesert.com/en-US/Adventure/Guild/GuildProfile?guildName={guild}&region={region}'
        # Holder for response
        self.response = None

    def parse_roster(self, html_loc=None):
        # Differentiate between reading html from disk or actually scraping it from the website
        if html_loc:
            # Read HTML from disk
            with open(html_loc) as html_file:
                soup = BeautifulSoup(html_file, 'html.parser')
        else:
            # Send a GET request to the URL
            self.response = requests.get(self.url)

            # Create a BeautifulSoup object and specify the parser
            soup = BeautifulSoup(self.response.text, 'html.parser')

        # Find the table (ul) of members by selecting it by class (adventure_list_table)
        members = soup.select('.adventure_list_table li div span .text a')

        # Check if the table was found
        if members:
            # Extract (name, link to family page) tuples and return those
            return [(member.text.strip(), member['href']) for member in members]
        else:
            raise Exception(f'Cannot find any members on {self.url}!')

    def dummy_roster(self):
        return ['Adventurer', 'Master', 'Member', 'Apprentice', 'Staff']