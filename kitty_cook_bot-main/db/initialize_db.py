import sqlite3
conn = sqlite3.connect('./db/user.db')

c = conn.cursor()

c.execute('''CREATE TABLE info
            (id INTEGER PRIMARY KEY,
            sex CHAR(1), 
            height INTEGER, 
            age INTEGER,
            weight_current INTEGER, 
            weight_desired INTEGER, 
            intensity REAL, 
            deficiency INTEGER)''')

users = [(364271594, 'M', 182, 21, 70, 67, 1.55, 20)
        ]
c.executemany('INSERT INTO info VALUES (?,?,?,?,?,?,?,?)', users)

c.execute(
        '''CREATE TABLE IF NOT EXISTS "calories" 
           ("id"    int,
           "possible" int,
           "eaten" int,
           PRIMARY KEY("id"),
           FOREIGN KEY("id") REFERENCES "info"("id"))''')
calories = [(364271594, 1941, 0)]
c.executemany('INSERT INTO calories VALUES (?,?,?)', calories)

c.execute('''CREATE TABLE recipes
            (id INTEGER PRIMARY KEY,
            recipe_name, 
            image_url)''')

recipes = [
        (56927, 'Delicious Ham and Potato Soup', 'https://images.media-allrecipes.com/userphotos/720x405/962656.jpg'),
        (16066, 'Awesome Slow Cooker Pot Roast', 'https://images.media-allrecipes.com/userphotos/720x405/2287775.jpg'),
        (23600, "World's Best Lasagna", 'https://images.media-allrecipes.com/userphotos/720x405/3359675.jpg'),
        (8941, 'Slow Cooker Chicken and Dumplings', 'https://images.media-allrecipes.com/userphotos/720x405/806223.jpg'),
        (26317, 'Chicken Pot Pie IX', 'https://images.media-allrecipes.com/userphotos/720x405/4535759.jpg'),       
        (15004, 'Award Winning Soft Chocolate Chip Cookies', 'http://images.media-allrecipes.com/userphotos/250x250/693521.jpg'),
        (10549, 'Best Brownies', 'http://images.media-allrecipes.com/userphotos/720x405/1090243.jpg'),
        (12682, 'Apple Pie by Grandma Ople', 'http://images.media-allrecipes.com/userphotos/720x405/736203.jpg'),
        (162760, 'Fluffy Pancakes', 'https://images.media-allrecipes.com/userphotos/720x405/5079227.jpg'),
        (50644, 'Broiled Tilapia Parmesan', 'https://images.media-allrecipes.com/userphotos/720x405/687910.jpg'),  
        (6820, 'Downeast Maine Pumpkin Bread', 'https://images.media-allrecipes.com/userphotos/720x405/4567827.jpg')
        ]
c.executemany('INSERT INTO recipes VALUES (?,?,?)', recipes)

c.execute('''CREATE TABLE rates
            (id_users,
            id_recipes, 
            rate INTEGER DEFAULT NULL,
            FOREIGN KEY(id_users) REFERENCES users(id),
            FOREIGN KEY(id_recipes) REFERENCES recipes(id))''')

c.execute('''CREATE TABLE recommendations
            (id_users,
            id_recipes, 
            FOREIGN KEY(id_users) REFERENCES users(id),
            FOREIGN KEY(id_recipes) REFERENCES recipes(id))''')

conn.commit()
conn.close()