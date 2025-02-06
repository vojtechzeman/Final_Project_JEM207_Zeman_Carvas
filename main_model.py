"""
MODEL HISTORY CHECK, MODEL UPDATE
"""

from src.modeling_history_check import HistoryChecker
history_checker = HistoryChecker()
from src.modeling_process_data import DataProcessor
data_processor = DataProcessor()
from src.modeling_process_annuity import AnnuityProcessor
annuity_processor = AnnuityProcessor()
from src.modeling import Model
model = Model()


if __name__ == "__main__":


    # -----------------------------------------------------------------------
    # DECIDE WHETHER TO 'CHECK MODEL HISTORY' OR 'UPDATE MODEL'
    # DECIDE WHICH DATA YOU WILL PERFORM OPERATION WITH

    operation = 'update_model'    # Choose: 'check_history' | 'update_model'
    data_type = 'sale'            # Choose: 'sale' | 'rent'
    # -----------------------------------------------------------------------


    if operation == 'check_history':
        if data_type == 'sale':
            history_checker.check_model_history(check_sale=True, check_rent=False)
        elif data_type == 'rent':
            history_checker.check_model_history(check_sale=False, check_rent=True)

    if operation == 'update_model':
        check = input("Did you check the model history first? (yes/no): ")
        if data_type == 'sale' and check == "yes":
            data_processor.process_data(process_sale=True, process_rent=False)
            annuity_processor.process_data_annuity()
            # model = model.train_model(process_sale=True, process_rent=False)
        elif data_type == 'rent' and check == "yes":
            data_processor.process_data(process_sale=False, process_rent=True)
            # model = model.train_model(process_sale=False, process_rent=True)
        else:
            print("Please check the model history first.")



    


