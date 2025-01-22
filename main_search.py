"""
IDENTIFICATION OF UNDERVALUED APARTMENTS
"""
import pandas as pd
import configparser

""" 
-------------- Url guide for filtering --------------
type of building (1-5): "category_main_cb="
    1=flat, 2=house, 3=plot, 4=commercial, 5=other
number of rooms (2,3,4,5,6,7,8,9,10,11,12,16,47): "category_sub_cb="
    2="1+kk", 3="1+1", 4="2+kk", 5="2+1", 6="3+kk", 7="3+1", 8="4+kk",
    9="4+1", 10="5+kk", 11="5+1", 12="6+", 16="atypical", 47="room"
type of advert (1-2): "category_type_cb="
    1=buy, 2=rent
min. price (CZK): "price_from="
max. price (CZK): "price_to="
age of advert (days): "advert_age_to="
condition of building (1-10)": "building_condition="
    1="very good", 2="good", 3="bad", 4="under construction", 5="project", 6="new building",
    7="for demolition", 8="before reconstruction", 9="after reconstruction", 10="in reconstruction"
ownership (1-3): "ownership="
    1=personal, 2=housing cooperative (družstevní), 3=state/municipal
min. floor (integer): "floor_number_from="
max. floor (integer): "floor_number_to="
keywords (with spaces): = "description_search="
    "Klimatizace Recepce Ateliér Bazén Elektromobil Penthouse Rekuperace Sauna Vana Výhled"
energy efficiency (1-7): "energy_efficiency_rating_cb="
    1=A ... 7=G
building type (1-8): "building_type="
    2=brick, 5=panel, rest=other
min usable area (m2): "usable_area_from="
max usable area (m2): "usable_area_to="
bools (true | false):   "balcony="
                        "loggia="
                        "terrace="
                        "cellar="
                        "garden="
                        "parking_lots="
                        "garage="
                        "easy_access=" (disability accessible)
                        "elevator="
---------------------------------------------------------
"""


def generate_link():
    """
    Makes link from parameters in settings.cfg
    """
    config = configparser.ConfigParser()
    config.read('settings.cfg')
    data = {}
    for section in config.sections():
        if section == "filter":
            for key, value in config.items(section):
                data[key] = value
    settings = pd.Series(data)
    # TODO: make link from cfg


def get_filtered_listings():
    base_url = "https://www.sreality.cz/api/v1/estates/search?"
    pass


if __name__ == "__main__":
    pass

    


