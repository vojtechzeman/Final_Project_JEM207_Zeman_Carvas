# MODEL HISTORY CHECK, MODEL UPDATE

from src.modeling_history_check import HistoryChecker
history_checker = HistoryChecker()

if __name__ == "__main__":
    history_checker.check_model_history(check_sale=True, check_rent=False)


    


