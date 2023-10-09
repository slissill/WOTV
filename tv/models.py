from django.db import models
from datetime import datetime

import locale

# password for mysql on pythonanywhere : litswd?pa



class Channel(models.Model):
    channel_id = models.CharField(max_length=50, verbose_name="code", primary_key=True)
    display_name = models.CharField(max_length=50, verbose_name="Chaine")
    icon_sc = models.CharField(max_length=500, verbose_name="Icon")
    sort = models.IntegerField(default=0, verbose_name="Tri")    
    class Meta:
        verbose_name = "Chaine"
        verbose_name_plural = "Chaines"
        ordering = ['sort']

    def __str__(self): return self.display_name

    @classmethod
    def create_or_update(cls, **kwargs): return cls.objects.get_or_create(**kwargs)


class Programme(models.Model):
    start_time = models.DateTimeField(verbose_name="Début")    
    stop_time = models.DateTimeField(verbose_name="Fin")
    day = models.DateField(verbose_name="Jour")
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.CharField(max_length=1000, verbose_name="Description")
    category = models.CharField(max_length=100, verbose_name="Catégorie")
    genre = models.CharField(max_length=100, verbose_name="Genre")    
    length = models.IntegerField(default=0, verbose_name="Durée")
    icon_sc = models.CharField(max_length=500, verbose_name="Icon")
    rating = models.CharField(max_length=100, verbose_name="Rating")

    status = models.IntegerField(default=0, verbose_name="Status")
    year = models.IntegerField(default=0, verbose_name="Année")
    actors = models.CharField(max_length=100, default="", verbose_name="Acteurs")
    url_cover = models.CharField(max_length=500, default="", verbose_name="Affiche")

    json_data = models.JSONField(null=True)


    
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='fk_Programme_Channel')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Programme"
        verbose_name_plural = "Programmes"
        constraints = [models.UniqueConstraint(fields=['channel', 'start_time'], name='unique_programme_key')]        
        ordering = ['channel', 'start_time']


    def __str__(self): return self.title

    @classmethod
    def create_or_update(cls, **kwargs): return cls.objects.get_or_create(**kwargs)

    @property
    def note(self):        
        if self.json_data and 'rating' in self.json_data and self.json_data['rating'] != "":
            rating = int(round(float(self.json_data['rating'])) / 2)
            return range(0, rating)
        else: 
            return range(0, 0)

    @property
    def duree(self):
        difference = self.stop_time - self.start_time
        heures, seconds = divmod(difference.seconds, 3600)
        minutes, _ = divmod(seconds, 60)
        duree_formatee = f"{heures:02}h{minutes:02}"
        return duree_formatee[1:]

    @property
    def hdeb(self): return self.start_time.strftime("%H:%M")
    @property
    def hfin(self): return self.stop_time.strftime("%H:%M")
    @property
    def horaire(self): return f"{self.hdeb} - {self.hfin}"
    @property
    def tranche(self):
        if self.hdeb >= "00:00" and self.hdeb <= "05:59" :      return "N"        
        elif self.hdeb >= "06:00" and self.hdeb <= "11:59" :    return "MA"
        elif self.hdeb >= "12:00" and self.hdeb <= "17:59" :    return "AM"
        elif self.hdeb >= "18:00" and self.hdeb <= "20:29" :    return "S1"        
        else :                                                  return "S2"
    @property    
    def display_date(self):
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
        jour_semaine_format = "%a"  # Exemple : "Jeu"
        mois_format = "%b"  # Exemple : "Jul"
        return self.start_time.strftime(f"{jour_semaine_format} %d {mois_format}")


class ProgressModel(models.Model):
    progress = models.IntegerField(default=0)

    def get_progress_percentage(self):
        return self.progress


class Prog(models.Model):
    identifiant = models.IntegerField(default=0)
    start_time = models.DateTimeField(verbose_name="Début")    
    stop_time = models.DateTimeField(verbose_name="Fin")
    day = models.DateField(verbose_name="Jour")
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.CharField(max_length=1000, verbose_name="Description")
    category = models.CharField(max_length=100, verbose_name="Catégorie")
    genre = models.CharField(max_length=100, verbose_name="Genre")        
    visuel = models.CharField(max_length=500, verbose_name="Icon")
    channel = models.CharField(max_length=500, verbose_name="Chaine")

    class Meta:
        managed = False
        verbose_name = "Programme"
        verbose_name_plural = "Programmes"
        ordering = ['channel', 'start_time']


    def __str__(self): return self.title

    @property
    def duree(self):
        difference = self.stop_time - self.start_time
        heures, seconds = divmod(difference.seconds, 3600)
        minutes, _ = divmod(seconds, 60)
        duree_formatee = f"{heures:02}h{minutes:02}"
        return duree_formatee[1:]

    @property
    def day_str(self): return self.day.strftime('%Y%m%d')

    @property
    def hdeb(self): return self.start_time.strftime("%H:%M")
    @property
    def hfin(self): return self.stop_time.strftime("%H:%M")
    @property
    def horaire(self): return f"{self.hdeb} - {self.hfin}"
    @property
    def tranche(self):
        if self.hdeb >= "00:00" and self.hdeb <= "05:59" :      return "N"        
        elif self.hdeb >= "06:00" and self.hdeb <= "11:59" :    return "MA"
        elif self.hdeb >= "12:00" and self.hdeb <= "17:59" :    return "AM"
        elif self.hdeb >= "18:00" and self.hdeb <= "20:29" :    return "S1"        
        else :                                                  return "S2"
    @property    
    def display_date(self):
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
        jour_semaine_format = "%a"  # Exemple : "Jeu"
        mois_format = "%b"  # Exemple : "Jul"
        return self.start_time.strftime(f"{jour_semaine_format} %d {mois_format}")


    #  python manage.py makemigrations tv
    #  python manage.py migrate