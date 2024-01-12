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

    def parse_roster(self):
        # Send a GET request to the URL
        response = requests.get(url)

        # Create a BeautifulSoup object and specify the parser
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the table (ul) of members by selecting it by class (adventure_list_table)
        members = soup.select('.adventure_list_table li div span .text a')
        names = [member.text.strip() for member in members]

        # Check if the table was found
        if members:
            # Extract the names and return those
            names = [member.text.strip() for member in members]
            return names

        else:
            raise Exception(f'Cannot find any members on {self.url}!')

        def dummy_roster(self):
            return ['Adventurer', 'Master', 'Member', 'Apprentice', 'Staff']