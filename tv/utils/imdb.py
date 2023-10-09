import requests
from imdb import IMDb
from ..models import Programme, ProgressModel
#from bs4 import BeautifulSoup


def update_imdb_infos(programmes):
    # excluded_channel_ids = ['CanalPlus.fr', 'CanalPlusCinema.fr', 'CanalPlusSport.fr', 'ParisPremiere.fr', 'PlanetePlus.fr']
    # programmes = Programme.objects.exclude(channel_id__in=excluded_channel_ids).filter(category='Film', status = 0).order_by('title')
    items_count = len(programmes)

    i = 1
    pc = 0
    list_progress = []
    ProgressModel.objects.all().delete()
    new_record = ProgressModel()
    new_record.progress = 0
    new_record.save()

    ia = IMDb()
    for p in programmes[:100]:
        print(p.title)
        get_imdb_film_info(ia, p)

        pc = int((i / items_count) * 100)
        if not pc in list_progress:
                list_progress.append (pc)
                new_record.progress = pc
                new_record.save()
                print (f"xxxxxxxxxxxxxx { pc }%  xxxxxxxxxxxxxxxxx")
        i += 1

    new_record.progress = 0
    new_record.save()


    return True


def get_imdb_infos(programmes):
    ia = IMDb()
    for p in programmes[:3]:
        #if p.status == 0 and p.category == "Film":
        if p.category == "Film" and p.status != 2:
            get_imdb_film_info(ia, p)
    return True


def get_imdb_film_info(ia, programme):

    #ia = IMDb()
    movies = ia.search_movie(programme.title)

    if not movies:
        programme.status = 2
        programme.save()
        return False
    else:
        print (movies)
        id = movies[0].getID()
        movie = ia.get_movie(id)
        #movie.infoset2keys
        print ("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        print (movie.keys)
        print ("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

        year = movie['year'] if 'year' in movie else ""
        cover = movie['cover url'] if 'cover url' in movie else ""         
        rating = movie['rating'] if 'rating' in movie else "" 
        director = movie['director'][0]['name'] if 'director' in movie else "" 
        cast = []
        if 'cast' in movie:
            max_actors = 4
            cast = [
                    {
                        'name':actor['name'],                         
                    }                    
                    for actor in movie['cast'][:max_actors]
                    ] 
        donnees_json = {
            "id": id,
            "year": year,
            "cover": cover,
            "rating": rating,
            "director": director, 
            "cast": cast
        }
        programme.json_data = donnees_json
        programme.status = 1
        programme.save()
        return True






# def get_first_google_image_url(query):
#     # Requête Google Image Search avec la requête de recherche
#     url = f"https://www.google.com/search?tbm=isch&q={query}"
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
#     response = requests.get(url, headers=headers)

#     # Analyser le contenu HTML de la réponse
#     soup = BeautifulSoup(response.content, "html.parser")

#     # Trouver la balise de la première image
#     image_element = soup.find("img")

#     # Récupérer l'URL de la première image
#     if image_element and "src" in image_element.attrs:
#         image_url = image_element["src"]
#         return image_url

#     return None