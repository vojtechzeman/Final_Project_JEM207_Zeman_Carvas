import json
import re
import pandas as pd
import os


class AnnuityProcessor:
    def __init__(self) -> None:
        pass

    def process_data_annuity(self) -> None:
        """
        Update prices of non-private items with annuities (information got from item description).

        """


        # Load JSON
        with open("data/processed/sale.json", 'r', encoding='utf-8') as file:
            data = json.load(file)


        # ANNUITY FOR NON PRIVATE APARTMENTS
        def find_sentences_with_anuit(text):
            text = text.replace('\r', ' ').replace('\n', ' ').replace(' : ', ' ')
            sentences = text.split('. ')
            pattern_number = r'\d+'
            anuit_sentences = []
            for sentence in sentences:
                sentence = sentence.strip().lower()
                if re.search(r'anuit|částk|doplat|splát|plat', sentence) and re.search(pattern_number, sentence):
                    anuit_sentences.append(sentence)
            return " ".join(anuit_sentences)

        def find_annuity(text):
            pattern = r'\d+(?:[., ]\d+)*'
            date_pattern = r'\.\d{1,2}\.'
            castky = [match for match in re.findall(pattern, text) if not re.search(date_pattern, match)]
            castky = [castka.replace(' ', '').replace('.', '').replace(',', '').strip() for castka in castky]
            castky = [castka for castka in castky if len(castka) > 3]
            castky = [int(castka) for castka in castky if int(castka)>60000]
            castky = list(set(castky))
            castky = sorted(castky, reverse=True)[:3]
            return castky
            
        def differ_by_one_digit(n1, n2):
            return len(str(n1)) == len(str(n2)) and sum(a != b for a, b in zip(str(n1), str(n2))) <= 1


        print("Processing...")
        for item in data:

            # Anuita search
            if item["ownership_private"] == 0:
                description = item["description"].lower()
                if (
                    re.search(r'anuit|částk|doplat|splát|plat', description)
                    and not any(phrase in description.lower() for phrase in [
                        "anuita splacena", 
                        "anuita splacená",
                        " splacena anuita",
                        " splacená anuita",
                        " splacenou anuitou",
                        "anuita je zcela splacena",
                        "anuita je zcela splacená",
                        "anuita kompletně splacena",
                        "anuita kompletně splacená",
                        "anuita doplacena"
                    ])
                ):
                    item["annuity"] = 1
                else:
                    item["annuity"] = 0
            else:
                item["annuity"] = 0


        print("Processing...")
        for item in data:
            # Application of find_sentences_with_anuit() and find_annuity() functions
            if item["annuity"] == 1:
                sentences = find_sentences_with_anuit(item["description"])
                item["sentences"] = sentences

                amounts = find_annuity(sentences)
                item["amounts"] = amounts

        

        print("Processing...")
        for item in data:

            if item["annuity"] == 1:
                if len(item["amounts"]) == 3:
                    max_val = max(item["amounts"])
                    min_val = min(item["amounts"])
                    middle = sum(item["amounts"]) - max_val - min_val
                    sum_val = min_val + middle
                    if differ_by_one_digit(sum_val, max_val):
                        item["price"] = max_val
                        del item["amounts"]
                        del item["sentences"]
                        item["annuity"] = 0

            if item["annuity"] == 1:
                if len(item["amounts"]) == 3:
                    item["amounts"] = [amount for amount in item["amounts"] if not (amount < 500000 and str(amount).endswith('000'))]

            if item["annuity"] == 1:
                if len(item["amounts"]) == 2:
                    max_val = max(item["amounts"][0], item["amounts"][1], item["price"])
                    min_val = min(item["amounts"][0], item["amounts"][1], item["price"])
                    middle = sum(item["amounts"]) + item["price"] - max_val - min_val
                    sum_val = min_val + middle
                    if differ_by_one_digit(sum_val, max_val):
                        item["price"] = max_val
                        del item["amounts"]
                        del item["sentences"]
                        item["annuity"] = 0

            if item["annuity"] == 1:
                if len(item["amounts"]) == 2:
                    if differ_by_one_digit(item["amounts"][0], item["price"]) or differ_by_one_digit(item["amounts"][1], item["price"]):
                        item["price"] = sum(item["amounts"])
                        del item["amounts"]
                        del item["sentences"]
                        item["annuity"] = 0

            if item["annuity"] == 1:
                if len(item["amounts"]) == 1:
                    item["price"] = item["price"] + item["amounts"][0]
                    del item["amounts"]
                    del item["sentences"]
                    item["annuity"] = 0

            if item["annuity"] == 1:
                if item["sentences"] == "":
                    del item["amounts"]
                    del item["sentences"]
                    item["annuity"] = 0

        

        def find_annuity_2(text):
            pattern = r'\d+(?:[., ]\d+)*(?:\s*(?:mil|tis))?'
            date_pattern = r'\.\d{1,2}\.'
            castky = [match for match in re.findall(pattern, text) if not re.search(date_pattern, match)]
            
            converted_castky = []
            for castka in castky:
                castka = castka.strip()
                try:
                    if 'mil' in castka.lower():
                        # Millions
                        num = castka.lower().replace('mil', '').strip()
                        num = num.replace(' ', '').replace('.', '').replace(',', '').strip()
                        value = float(num) * 1000000
                        converted_castky.append(int(value))
                    elif 'tis' in castka.lower():
                        # Thousands
                        num = castka.lower().replace('tis', '').strip()
                        num = num.replace(' ', '').replace('.', '').replace(',', '').strip()
                        value = float(num) * 1000
                        converted_castky.append(int(value))
                    else:
                        # Common numbers
                        num = castka.replace(' ', '').replace('.', '').replace(',', '').strip()
                        if len(num) > 3:
                            value = int(num)
                            if value > 60000:
                                converted_castky.append(value)
                except (ValueError, TypeError):
                    continue
            
            # Delete duplicates
            converted_castky = list(set(converted_castky))
            converted_castky = sorted(converted_castky, reverse=True)[:3]
            return converted_castky


        print("Processing...")
        for item in data:
            if item["annuity"] == 1:
                # Find amounts in sentences containing "anuit" or "odstup"
                amounts = find_annuity_2(item["sentences"])
                item["amounts"] = amounts


        # Deletion of items with suspicious prices
        data = [item for item in data if not (item["annuity"] == 1 and len(item.get("amounts", [])) > 0)]

        for item in data:
            if item["annuity"] == 1:
                del item["amounts"]
                del item["sentences"]
                item["annuity"] = 0


        KEYS_TO_REMOVE = {"annuity", "description"}
        data = [{k: v for k, v in item.items() if k not in KEYS_TO_REMOVE} for item in data]

        # Deletion of non-private ownership with suspicious prices
        data = [item for item in data if not (item["ownership_private"] == 0 and item["price"] < item["usable_area"] * 85000)]



        # Save result
        df = pd.DataFrame(data)
        desired_order = ['price', 'usable_area']
        other_columns = [col for col in df.columns if col not in desired_order]
        final_order = desired_order + other_columns
        df = df[final_order]
        df.to_csv("data/processed/sale.csv", index=False, encoding='utf-8', sep=";")

        os.remove("data/processed/sale.json")

        print(f"Successfully processed annuity")

