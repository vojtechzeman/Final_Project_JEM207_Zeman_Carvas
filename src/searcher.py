from sklearn.pipeline import Pipeline
import joblib


class Searcher:
    def __init__(self) -> None:
        pass

    def load_model(self, load_sale: bool = False, load_rent: bool = False) -> Pipeline:
        if load_sale:
            model = joblib.load("sale_model.joblib")
        elif load_rent:
            model = joblib.load("rent_model.joblib")

       