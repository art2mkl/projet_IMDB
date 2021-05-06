import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np


# à intégrer dans le fichier .py
class Dbase:
    def connect_IMDB(self,i):
        url = f"https://www.imdb.com/search/title/?groups=top_250&sort=user_rating,desc&start={i}&ref_=adv_nxt"
        response = requests.get(url)
        html_parsed = BeautifulSoup(response.text, 'html.parser')
        return html_parsed.find_all(class_='lister-item-content')
    
    def imdb_requests(self):
        tabG = self.get_elements()
        return self.createDf(tabG)

    def get_elements(self):
        num_requests = [1, 51, 101, 151, 201]
        titles_name = []
        movies_grade = []
        movies_year = []
        voices_count = []
        movies_director = []
        movies_genre = []
        movies_gross = []

        for i in num_requests:
            # recupération des données à scraper
            div_content = self.connect_IMDB(i)
            for div in div_content:
            # APPEND values to lists
                titles_name.append(div.find(class_='lister-item-header').find('a').text)    
                movies_grade.append(div.find(class_='ratings-bar').find('strong').text)
                movies_genre.append((div.find(class_="genre").text.strip('\n').strip()).split(','))
                movies_year.append(div.find(class_="lister-item-year").text.replace('(','').replace(')','').replace('I ', ''))
                voices_count.append(div.find(class_="sort-num_votes-visible").find_all('span')[1].text.replace(',', ''))
                
                # SELECT gross and transform missing values to Nan
                if len(div.find(class_="sort-num_votes-visible").find_all('span')) == 5:
                    movies_gross.append(div.find(class_="sort-num_votes-visible").find_all('span')[4].text.replace('$', '').replace('M', ''))
                else:
                    movies_gross.append(np.nan)
                
                # ITERATE on multiple directors
                all_p = div.find_all('p')[2]
                first_director = []
                for i in all_p:
                    if '<a' in str(i):
                        first_director.append(i.text)
                    elif '<span' in str(i):
                        break
                movies_director.append(first_director)
            
        # CREATION of 3 lists
        director_1 = []
        director_2 = []
        director_3 = []
        nb_directors = []

        # ITERATE on each list 
        for i in movies_director:
            nb_directors.append(len(i))
            if len(i) == 1:
                director_1.append(i[0])
                director_2.append(i[0])
                director_3.append(i[0])
            elif len(i) == 2:
                director_1.append(i[0])
                director_2.append(i[1])
                director_3.append(i[1])
            elif len(i) == 3:
                director_1.append(i[0])
                director_2.append(i[1])
                director_3.append(i[2]) 

        #CREATION of 3 lists
        genre_1 = []
        genre_2 = []
        genre_3 = []
        nb_genres = []

        #ITERATE on each list 
        for i in movies_genre:
            nb_genres.append(len(i))
            if len(i) == 1:
                genre_1.append(i[0])
                genre_2.append(i[0])
                genre_3.append(i[0])
            elif len(i) == 2:
                genre_1.append(i[0])
                genre_2.append(i[1])
                genre_3.append(i[1])
            elif len(i) == 3:
                genre_1.append(i[0])
                genre_2.append(i[1])
                genre_3.append(i[2]) 

        return [titles_name,genre_1,genre_2,genre_3,nb_genres,movies_year,director_1,director_2,director_3,nb_directors,movies_grade,voices_count,movies_gross]  

    def createDf(self,tabG):
        df1 = pd.DataFrame()

        #ADDING titles list to DF              
        df1['titles'] = tabG[0]

        #ADDING genre lists to DF        
        #CREATION of 3 columns on the DF
        df1['genre1'] = tabG[1]
        df1['genre2'] = tabG[2]
        df1['genre3'] = tabG[3]
        df1['nb_genres'] = tabG[4]

        #MODIFICATION type to datetime
        df1['released_year'] = list(map(int, tabG[5]))

        #CREATION of 3 columns on the DF
        df1['director1'] = tabG[6]
        df1['director2'] = tabG[7]
        df1['director3'] = tabG[8]
        df1['nb_directors'] = tabG[9]

        #MODIFICATION to float
        df1['grade'] = list(map(float, tabG[10]))

        #MODIFICATION type of votes in integer
        df1['votes'] = list(map(int, tabG[11]))
        #df1['votes'] = df1['votes'].astype(dtype='int64')

        #MODIFICATION type of gross in float
        df1['gross(M$)'] = list(map(float, tabG[12]))

        #AJOUT DES VALEURS MANQUANTES
        return self.add_values(df1)

    def add_values(self,df1):
        df2 = df1.copy()
        for i in range(1920,2021):
        #si la date en i ne contient pas que des NAN
            if df2['gross(M$)'][df2['released_year'] == i].notnull().sum() != 0:
                df2['gross(M$)'][df2['released_year'] == i] = df2['gross(M$)'][df2['released_year'] == i].fillna(df2['gross(M$)'][df2['released_year'] == i].mean())

        #si la date en i-1 ne contient pas que des NAN
            elif df2['gross(M$)'][df2['released_year'] == i-1].notnull().sum() != 0:
                df2['gross(M$)'][df2['released_year'] == i] = df2['gross(M$)'][df2['released_year'] == i].fillna(df2['gross(M$)'][df2['released_year'] == i-1].mean())

        #sinon utilise le mean() de i-2
            else:
                df2['gross(M$)'][df2['released_year'] == i] = df2['gross(M$)'][df2['released_year'] == i].fillna(df2['gross(M$)'][df2['released_year'] == i-2].mean())
        return df2


