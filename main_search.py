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





