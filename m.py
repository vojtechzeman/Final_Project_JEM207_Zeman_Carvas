import json
from collections import defaultdict

def count_materials(json_file_path):
    """
    Projde JSON soubor a spočítá součty všech hodnot podle typu materiálu.
    
    Args:
        json_file_path (str): Cesta k JSON souboru
        
    Returns:
        dict: Slovník s součty podle typu materiálu
    """
    # Použijeme defaultdict pro automatické vytváření nulových hodnot
    material_counts = defaultdict(int)
    
    try:
        # Otevřeme a načteme JSON soubor
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        def process_item(item):
            """Rekurzivně prochází strukturu a hledá klíč 'material'"""
            if isinstance(item, dict):
                # Pokud najdeme klíč 'material', přičteme jeho hodnotu
                if "energy_efficiency_rating_cb" in item:
                    material_type = item["energy_efficiency_rating_cb"]
                    # Pokud je hodnota číslo, přičteme ji
                    value = 1  # Výchozí hodnota, pokud není specifikováno
                    if "quantity" in item:
                        try:
                            value = float(item["quantity"])
                        except (ValueError, TypeError):
                            pass
                    material_counts[material_type] += value
                
                # Rekurzivně procházíme všechny hodnoty v dictionary
                for value in item.values():
                    process_item(value)
                    
            elif isinstance(item, list):
                # Rekurzivně procházíme všechny položky v listu
                for element in item:
                    process_item(element)
        
        # Začneme zpracování od kořene JSON struktury
        process_item(data)
        
        # Převedeme defaultdict na běžný dictionary pro výstup
        return dict(material_counts)
    
    except FileNotFoundError:
        print(f"Soubor {json_file_path} nebyl nalezen.")
        return {}
    except json.JSONDecodeError:
        print(f"Soubor {json_file_path} není validní JSON.")
        return {}
    except Exception as e:
        print(f"Nastala neočekávaná chyba: {str(e)}")
        return {}

# Příklad použití:
if __name__ == "__main__":
    # Změňte cestu k vašemu JSON souboru
    file_path = "data/processed/sale2.json"
    results = count_materials(file_path)
    
    # Výpis výsledků
    print("\nSoučty podle typu materiálu:")
    for material, count in sorted(results.items()):
        print(f"{material}: {count}")