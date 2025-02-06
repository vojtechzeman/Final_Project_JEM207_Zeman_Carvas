"""
IDENTIFICATION OF UNDERVALUED APARTMENTS
"""


from src.data_processor import DataProcessor
data_processor = DataProcessor()
from src.annuity_processor import AnnuityProcessor
annuity_processor = AnnuityProcessor()
from src.searcher import Searcher
searcher = Searcher()
from src.scraper import Scraper
scraper = Scraper()

if __name__ == "__main__":


    # -----------------------------------------------------------------------
    # DECIDE WHETHER YOU WANT TO BUY OR RENT AN APARTMENT

    data_type = 'sale'            # Choose: 'sale' | 'rent'
    # -----------------------------------------------------------------------


    if data_type == 'sale':
        scraper.run(intent="sale")
        data_processor.process_data(process_sale=True, process_rent=False, search = True)
        annuity_processor.process_data_annuity(search = True)
        result_df = searcher.search_apartments(process_sale=True, process_rent=False)
        scraper.get_estimates(estimates=result_df, intent="sale")

    elif data_type == 'rent':
        scraper.run(intent="rent")
        data_processor.process_data(process_sale=False, process_rent=True, search = True)
        result_df = searcher.search_apartments(process_sale=False, process_rent=True)
        scraper.get_estimates(estimates=result_df, intent="rent")




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
