import pandas as pd


def dumpCSV(jsonData, csvPath):
    """Creates a csv output of the passed in jsonData

    Args:
        jsonData (object): jsonData to be normalized and flattened into a csv
        csvPath (string): filename to write the data to

    """
    if isinstance(jsonData, pd.DataFrame):
        df = jsonData
    else:
        df = pd.json_normalize(jsonData)
    df.to_csv(csvPath, index=False, encoding="utf-8")
