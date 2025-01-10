"""
MODEL HISTORY CHECK, MODEL UPDATE
"""

from src.modeling_history_check import HistoryChecker
history_checker = HistoryChecker()
from src.modeling_process_data import DataProcessor
data_processor = DataProcessor()
from src.modeling_process_annuity import AnnuityProcessor
annuity_processor = AnnuityProcessor()


if __name__ == "__main__":

    # Do you want to check the history of the model?
    history_checker.check_model_history(check_sale=False, check_rent=False)

    # What type of data do you want to process? sale/rent
    data_type = 'sale'
    if data_type == 'sale':
        data_processor.process_data()
        annuity_processor.process_data_annuity()
    if data_type == 'rent':
        pass




    


