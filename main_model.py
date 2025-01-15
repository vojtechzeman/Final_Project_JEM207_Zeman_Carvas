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

    # Check the history first before you update the model
    # "sale" / "rent" / "-"
    data_type_1 = '-'

    if data_type_1 == 'sale':
        history_checker.check_model_history(check_sale=True, check_rent=False)
    elif data_type_1 == 'rent':
        history_checker.check_model_history(check_sale=False, check_rent=True)


    # What type of data do you want to process?
    # "sale" / "rent" / "-"
    data_type_2 = 'sale'
    check = input("Did you check the model history? (yes/no): ")
 
    if check == "yes":
        if data_type_2 == 'sale':
            data_processor.process_data(process_sale=True, process_rent=False)
            annuity_processor.process_data_annuity()
            model = model.train_model(process_sale=True, process_rent=False)
        elif data_type_2 == 'rent':
            data_processor.process_data(process_sale=False, process_rent=True)
            model = model.train_model(process_sale=False, process_rent=True)



    


