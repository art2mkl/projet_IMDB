import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

def imdb_requests(num_request = [1, 51, 101, 151, 201]):

    titles_name = []
    movies_grade = []
    movies_year = []
    voices_count = []
    movies_director = []
    movies_genre = []
    movies_gross = []
    df1 = pd.DataFrame()
    counter = 16.6666666667

    for i in num_request:
        url = f"https://www.imdb.com/search/title/?groups=top_250&sort=user_rating,desc&start={i}&ref_=adv_nxt"
        response = requests.get(url)
        if response.ok:
            counter += 16.6666666667
            print(f'avancement = {round(counter,2)} %')
            html_parsed = BeautifulSoup(response.text, 'html.parser')
            
            # Cette div comprend tous les éléments à scraper
            div_content = html_parsed.find_all(class_='lister-item-content')
            for div in div_content:
                titles_name.append(div.find(class_='lister-item-header').find('a').text)    
                movies_grade.append(div.find(class_='ratings-bar').find('strong').text)
                movies_genre.append(div.find(class_="genre").text.strip('\n'))
                movies_year.append(div.find(class_="lister-item-year").text.replace('(','').replace(')','').replace('I ', ''))
                voices_count.append(div.find(class_="sort-num_votes-visible").find_all('span')[1].text.replace(',', ''))
                if len(div.find(class_="sort-num_votes-visible").find_all('span')) == 5:
                    movies_gross.append(div.find(class_="sort-num_votes-visible").find_all('span')[4].text.replace('$', '').replace('M', ''))
                else:
                    movies_gross.append(np.nan)
                
                movies_director.append(div.find_all('p')[2].find('a').text)
      
    #ADDING list to DF              
    df1['titles'] = titles_name
    
    #MODIFICATION to float
    df1['grade'] = list(map(float, movies_grade))
     
    df1['genre'] = movies_genre
    
    #MODIFICATION to datetime
    df1['released_year'] = list(map(int, movies_year))
    
    #df1['year'] = [datetime.strptime(date, '%Y').date() for date in movies_year]
    #df1['year'] = df1['year'].apply(lambda year: to_datetime(year))
    
    #MODIFICATION type of votes in integer
    df1['votes'] = list(map(int, voices_count))
    #df1['votes'] = df1['votes'].astype(dtype='int64')
    df1['director'] = movies_director
    df1['gross(M$)'] = list(map(float, movies_gross))
  
    
    return df1