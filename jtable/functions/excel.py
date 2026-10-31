#!/usr/bin/env python3
import pandas as pd
from typing import Any, Dict, List, Union

def excel_to_dict(
    file_path: str,
    sheet_name: Union[int, str, None] = None,
    dict_type: str = "records",
    index_col: Union[int, str, None] = None,
    drop_na_columns: bool = False   # option : enlever les colonnes totalement vides
) -> Union[List[Dict[str, Any]], Dict[str, List[Any]], Dict[Any, Dict[str, Any]]]:
    """
    Convertit un fichier Excel (ou une feuille) en dictionnaire.
    * `drop_na_columns` : si True, supprime les colonnes où **toutes** les valeurs sont NaN.
    * Les clés dont la valeur est NaN sont omises dans chaque dictionnaire (mode 'records').
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # Si read_excel renvoie un dict → prendre la première feuille
    if isinstance(df, dict):
        df = next(iter(df.values()))

    # Optionnel : définir un index explicite
    if index_col is not None:
        df = df.set_index(index_col)

    # 1️⃣  (Optionnel) Supprimer les colonnes totalement vides
    if drop_na_columns:
        df = df.dropna(axis=1, how='all')

    # 2️⃣  Remplacer les NaN par None (pour la sérialisation JSON)
    df = df.where(pd.notna(df), None)

    # 3️⃣  Conversion en dictionnaire
    if dict_type == "records":
        raw = df.to_dict(orient="records")
        # 4️⃣  Nettoyer chaque dictionnaire : enlever les clés avec None
        cleaned = [{k: v for k, v in d.items() if v is not None} for d in raw]
        return cleaned

    elif dict_type == "list":
        raw = df.to_dict(orient="list")
        # 4️⃣  Supprimer les colonnes dont toutes les valeurs sont None
        cleaned = {col: vals for col, vals in raw.items() if not all(v is None for v in vals)}
        return cleaned

    elif dict_type == "index":
        raw = df.to_dict(orient="index")
        # Nettoyer chaque sous‑dict
        cleaned = {k: {ck: cv for ck, cv in v.items() if cv is not None} for k, v in raw.items()}
        return cleaned

    else:
        raise ValueError("dict_type doit être 'records', 'list' ou 'index'")

# --------------------------------------------------------------------
# Exemple d’utilisation
# --------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    file = sys.argv[1]

    # 1. Liste de dictionnaires (une ligne par entrée), sans clés NaN
    data_records = excel_to_dict(file, dict_type="records")
    print("Records :", data_records[:2])

    # 2. Dictionnaire de colonnes → listes, sans colonnes entièrement vides
    data_columns = excel_to_dict(file, dict_type="list", drop_na_columns=True)
    print("\nColonnes :", data_columns)
