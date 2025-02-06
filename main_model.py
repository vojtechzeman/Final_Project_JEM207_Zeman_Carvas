"""
MODEL HISTORY CHECK, MODEL UPDATE
"""

from src.model_history_checker import HistoryChecker
history_checker = HistoryChecker()
from src.data_processor import DataProcessor
data_processor = DataProcessor()
from src.annuity_processor import AnnuityProcessor
annuity_processor = AnnuityProcessor()
from src.model_builder import Model
model = Model()


if __name__ == "__main__":


    # -----------------------------------------------------------------------
    # DECIDE WHETHER TO 'CHECK MODEL HISTORY' OR 'UPDATE MODEL'
    # DECIDE WHICH DATA YOU WILL PERFORM OPERATION WITH

    operation = 'update_model'    # Choose: 'check_history' | 'update_model'
    data_type = 'rent'            # Choose: 'sale' | 'rent'
    # -----------------------------------------------------------------------


    if operation == 'check_history':
        if data_type == 'sale':
            history_checker.check_model_history(check_sale=True, check_rent=False)
        elif data_type == 'rent':
            history_checker.check_model_history(check_sale=False, check_rent=True)

    if operation == 'update_model':
        check = input("Did you check the model history first? (yes/no): ")
        if data_type == 'sale' and check == "yes":
            # TODO add scraper SALE
            data_processor.process_data(process_sale=True, process_rent=False)
            annuity_processor.process_data_annuity()
            model = model.train_model(process_sale=True, process_rent=False)
        elif data_type == 'rent' and check == "yes":
            # TODO add scraper RENT
            data_processor.process_data(process_sale=False, process_rent=True)
            model = model.train_model(process_sale=False, process_rent=True)
        else:
            print("Please check the model history first.")



    


