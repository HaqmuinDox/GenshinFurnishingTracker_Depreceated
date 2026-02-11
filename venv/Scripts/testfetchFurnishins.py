import requests
from bs4 import BeautifulSoup
import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('db.db')
cursor = conn.cursor()


# Select all links from the database
cursor.execute('SELECT * FROM Furnishings')
rows = cursor.fetchall()

# Base URL of the wiki
base_url = 'https://genshin-impact.fandom.com'

# Function to extract information from a webpage and store it in the database
# Function to extract information from a webpage and store it in the database
def extract_ingredientsquantities(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Find the specified HTML element
        element = soup.find('div', class_='new_genshin_recipe_body')
        if element:
            # Find all card containers
            card_containers = element.find_all('div', class_='card-container')[:-1]
            for card in card_containers:
                # Extract link, title, and number
                link = card.find('a')['href']
                title = card.find('a')['title']
                number = card.find('span', class_='card-font').text.strip()
                print(link, title, number)
                # Get the ingredient ID
                ingredient_id = get_ingredient_id(link)
                dbfurnishinglink = url.replace('https://genshin-impact.fandom.com','/wiki')
                if ingredient_id:
                    print(ingredient_id, dbfurnishinglink)
                    # Check which ingredient slot is empty and update the Furnishings table accordingly
                    cursor.execute('SELECT ingredient1id, ingredient2id, ingredient3id FROM Furnishings WHERE link = ?', (dbfurnishinglink,))
                    row = cursor.fetchone()
                    if row is not None:
                        print('row is not none')
                        if not ingredient_id==row[0] and not ingredient_id==row[1] and not ingredient_id==row[2]:
                            if row[0] is None:
                                print('row1')
                                cursor.execute('''UPDATE Furnishings 
                                              SET ingredient1id = ?, quantity1 = ? 
                                              WHERE link = ?''', (ingredient_id, number, dbfurnishinglink))
                            elif row[1] is None:
                                print('row2')
                                cursor.execute('''UPDATE Furnishings 
                                              SET ingredient2id = ?, quantity2 = ? 
                                              WHERE link = ?''', (ingredient_id, number, dbfurnishinglink))
                            elif row[2] is None:
                                print('row3')
                                cursor.execute('''UPDATE Furnishings 
                                              SET ingredient3id = ?, quantity3 = ? 
                                              WHERE link = ?''', (ingredient_id, number, dbfurnishinglink))
                        # Commit the changes
                        conn.commit()
                    else:
                        print(f'Row is None for link: {url}')
                else:
                    print(f'Ingredient ID not found for link: {link}')
        else:
            print('Element not found on the webpage.')
    else:
        print(f'Failed to fetch the webpage. Status code: {response.status_code}')

def get_ingredient_id(link):
    cursor.execute('SELECT id FROM Ingredients WHERE link = ?', (link,))
    result = cursor.fetchone()
    if result is not None:
        #print('id returned: ', result[0])
        return result[0]

    else:
        #print('id NOT  returned')
        return None

# Process each row from the database
for row in rows:
    link = row[1]  # The link stored in the database
    # Replace '/wiki/' with the base URL
    full_url = base_url + link.replace('wiki/', '')
    # Extract information from the webpage
    print(f'Processing link: {full_url}')
    extract_ingredientsquantities(full_url)

# Close the connection to the database
conn.close()
