import requests
from bs4 import BeautifulSoup
import sqlite3
import urllib.parse

#loads in Furnihings Sets and Furnishings, loads recipes for Furnishings

# Connect to the SQLite database
conn = sqlite3.connect('db.db')
cursor = conn.cursor()

# Create a table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS FurnishingSets (
                    id INTEGER PRIMARY KEY,
                    link TEXT UNIQUE,
                    name TEXT,
                    obtained INTEGER DEFAULT 0 CHECK (obtained IN (0, 1))
                )''')
cursor.execute('''CREATE TABLE IF NOT EXISTS Furnishings (
                    id INTEGER PRIMARY KEY,
                    link TEXT UNIQUE,
                    name TEXT,
                    ingredient1id INTEGER,
                    ingredient2id INTEGER,
                    ingredient3id INTEGER,
                    quantity1 INTEGER,
                    quantity2 INTEGER,
                    quantity3 INTEGER,
                    obtained INTEGER DEFAULT 0 CHECK (obtained IN (0, 1))
                )''')
cursor.execute('''CREATE TABLE IF NOT EXISTS Ingredients (
                    id INTEGER PRIMARY KEY,
                    link TEXT UNIQUE,
                    name TEXT
                )''')


# URL of the webpage
url = 'https://genshin-impact.fandom.com/wiki/Category:Gift_Sets'

# Send a GET request to the webpage
response = requests.get(url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Get the HTML content of the webpage
    html_content = response.content

    # Parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all links with the class category-page__member-link
    links = soup.find_all('a', class_='category-page__member-link')

    # Extract the href attribute from each link and insert into the database
    for link in links[2:]:  # Skip the first two links
        href = link.get('href')
        # Extract the name from the link
        name = urllib.parse.unquote(href.split('/')[-1]).replace('_', ' ')
        # Check if the link already exists in the database
        cursor.execute('SELECT COUNT(*) FROM FurnishingSets WHERE Name=?', (name,))
        if cursor.fetchone()[0] == 0:
            # Insert the href and name into the database if it doesn't already exist
            cursor.execute('INSERT INTO FurnishingSets (Link, Name) VALUES (?, ?)', (href, name))
            print(f"Inserted: {name}")
        else:
            print(f"Skipped (already existed): {name}")

    # Commit the changes
    conn.commit()
    print("Links inserted into the database successfully.")
else:
    print('Failed to fetch the webpage. Status code:', response.status_code)

# Select all links from the database
cursor.execute('SELECT * FROM FurnishingSets')
rows = cursor.fetchall()



# Base URL of the wiki
base_url = 'https://genshin-impact.fandom.com/wiki'

def insert_furnishing_set_relationship(furnishing_set_id, furnishing_id, quantity=1):
    # Insert the relationship into the FurnishingSet_Furnishing table
    cursor.execute('''INSERT INTO FurnishingSet_Furnishing (furnishingSetID, furnishingID, quantity) 
                      VALUES (?, ?, ?)''', (furnishing_set_id, furnishing_id, quantity))
    conn.commit()


# Function to extract information from a webpage and store it in the database
def extract_furnishings(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Find the specified HTML element
        element = soup.find('div', class_='new_genshin_recipe_body')
        if element:
            # Find all card containers
            card_containers = element.find_all('div', class_='card-container')
            for card in card_containers:
                # Extract link, title, and number
                link = card.find('a')['href']
                title = card.find('a')['title']
                number = card.find('span', class_='card-font').text.strip()
                # Store the extracted information in the database
                cursor.execute('''INSERT OR IGNORE INTO Furnishings (link, name) 
                                  VALUES (?, ?)''', (link, title))
                cursor.execute('SELECT * FROM Furnishings WHERE link = ?', (link,))
                rows1 = cursor.fetchall()
                for row in rows1:
                    link = row[1]  # The link stored in the database
                    # Replace '/wiki/' with the base URL
                    full_url = base_url + link.replace('wiki/', '')
                    # Extract information from the webpage
                    print(f'Processing link: {full_url}')
                    extract_ingredients(full_url)
                # Commit the changes
                conn.commit()
        else:
            print('Element not found on the webpage.')
    else:
        print(f'Failed to fetch the webpage. Status code: {response.status_code}')

def extract_ingredients(url):
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
                cursor.execute('''INSERT OR IGNORE INTO Ingredients (link, name) 
                    VALUES (?, ?)''', (link, title))
                conn.commit()
        else:
            print('Element not found on the webpage.')
    else:
        print(f'Failed to fetch the webpage. Status code: {response.status_code}')

# Process each row from the database
for row in rows:
    link = row[1]  # The link stored in the database
    # Replace '/wiki/' with the base URL
    full_url = base_url + link.replace('wiki/', '')
    # Extract information from the webpage
    print(f'Processing link: {full_url}')
    extract_furnishings(full_url)

# Close the connection to the database
conn.close()

#LOAD Quantities for each ingredient



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
