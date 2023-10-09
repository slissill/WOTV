import requests
import xml.etree.ElementTree as ET
from ..models import Channel , Programme, ProgressModel, Prog
from datetime import datetime, date


def read_progs():
        cnt = 1
        url = "https://xmltvfr.fr/xmltv/xmltv_tnt.xml"
        response = requests.get(url)
        xml_content = response.content
        root = ET.fromstring(xml_content)

        channels_to_ignore = [
                "CanalPlus.fr", 
                "ParisPremiere.fr", 
                "CanalPlusCinema.fr",         
                ]

        channels = {}
        xpath_query = ".//channel"
        for item in root.findall(xpath_query):
                id_channel = item.get('id')
                if not id_channel in channels_to_ignore:
                        channels[id_channel] =  get_xml_text(item, "display-name") 



        
        programmes = []
        progs = []
        xpath_query = ".//programme[category='Film']"
        for item in root.findall(xpath_query):
                id_channel = item.get('channel')
                if id_channel in channels:

                        categories_list = ["", ""] 
                        get_xml_categories(item, categories_list)
                        programme = {
                                "channel"       : channels[id_channel],
                                "start_time"    : get_xml_date(item.get('start')),
                                "stop_time"     : get_xml_date(item.get('stop')), 
                                "duree"         : get_duree (get_xml_date(item.get('start')), get_xml_date(item.get('stop'))),        
                                "day"           : get_xml_date(item.get('start')).date(), 
                                "title"         : get_xml_text(item, "title"), 
                                "description"   : get_xml_text(item, "desc"),              
                                "category"      : categories_list[0],
                                "genre"         : categories_list[1],
                                "visuel"        : get_xml_text(item, "icon", "src"),
                        }
                        programmes.append(programme)

                        prog = Prog()
                        prog.identifiant = cnt
                        prog.channel = channels[id_channel]
                        prog.start_time = get_xml_date(item.get('start'))
                        prog.stop_time = get_xml_date(item.get('stop'))
                        prog.day = prog.start_time.date()
                        prog.title = get_xml_text(item, "title")
                        prog.description = get_xml_text(item, "desc")
                        prog.category = categories_list[0]
                        prog.genre = categories_list[1]
                        prog.visuel = get_xml_text(item, "icon", "src")
                        progs.append (prog)
                        cnt += 1  
                        if cnt > 50 : break

        return progs

def get_duree(start_time, stop_time):        
        difference = stop_time - start_time        
        heures, seconds = divmod(difference.seconds, 3600)
        minutes, _ = divmod(seconds, 60)
        duree_formatee = f"{heures:02}h{minutes:02}"
        return duree_formatee[1:]        

def maj_programmes():
        url = "https://xmltv.ch/xmltv/xmltv-tnt.xml"
        url = "https://xmltvfr.fr/xmltv/xmltv_tnt.xml"        
        response = requests.get(url)
        xml_content = response.content
        root = ET.fromstring(xml_content)

        idx = 0
        for item in root.findall('.//channel'):
                idx = idx + 1
                channel_db, created = Channel.create_or_update(
                        channel_id = item.get('id'), 
                        display_name = get_xml_text(item, "display-name"), 
                        icon_sc = get_xml_text(item, "icon", "src"), 
                        sort = idx
                        )
        idx = 1
        

        i = 1
        pc = 0
        list_progress = []
        ProgressModel.objects.all().delete()
        new_record = ProgressModel()
        new_record.progress = 0
        new_record.save()

        idx = 0
        items = root.findall('.//programme')
        items_count = len(items)
        for item in items:
                length = get_xml_text(item, "length")
                if length == "": length = "0"
                categories_list = ["", ""] 
                get_xml_categories(item, categories_list)

                programme_db, created = Programme.create_or_update(
                        channel         = Channel.objects.get(pk = item.get('channel')), 
                        start_time      = get_xml_date(item.get('start')), 
                        defaults = {
                                'stop_time'     : get_xml_date(item.get('stop')), 
                                'day'           : get_xml_date(item.get('start')).date(), 
                                'title'         : get_xml_text(item, "title"), 
                                'description'   : get_xml_text(item, "desc"),                                
                                'category'      : categories_list[0],
                                'genre'         : categories_list[1],
                                'length'        : length,  
                                'icon_sc'       : get_xml_text(item, "icon", "src"),
                                'rating'        : get_xml_text(item, "rating/value"),
                                }
                        ) 

                
                pc = int((i / items_count) * 100)
                if not pc in list_progress:
                        list_progress.append (pc)
                        new_record.progress = pc
                        new_record.save()
                        print (f"xxxxxxxxxxxxxx { pc }%  xxxxxxxxxxxxxxxxx")
                i += 1

                idx = idx + 1
                if idx > 10000 : break


        new_record.progress = 0
        new_record.save()

        return True

     
def get_xml_categories(item, categories):
        ctg_idx = 0                
        for category in item.findall('category'):
                if ctg_idx < 2:
                        categories[ctg_idx] = category.text
                        ctg_idx += 1
                else:
                        break

def get_xml_text(item, balise_name, arg = None):
        node = item.find(balise_name)
        if node is None:
                return ""
        else :
                return node.text if arg is None else node.get(arg)


def get_xml_date(s):
        year    = int(s[0:4])
        month   = int(s[4:6])
        day     = int(s[6:8])
        hour    = int(s[8:10])
        minute  = int(s[10:12])

        return datetime(year, month, day, hour, minute)   

def raz():
        Programme.objects.all().delete()
        Channel.objects.all().delete()
        return True
