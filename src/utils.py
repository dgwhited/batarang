import boto3
import pandas as pd


def create_session(profile=None, region=None):
    """Creates a boto session

    Args:
        profile (string): AWS profile name

    Returns:
        [object]: Authenticated Boto3 session
    """
    session = boto3.Session(profile_name=profile, region_name=region)
    if(session.region_name == None):
        session = boto3.Session(profile_name=profile, region_name="us-east-1")
    return session


def create_client(session, service):
    """Creates a service client from a boto session

    Args:
        session (object): Authenicated boto3 session
        service (string): service name to create the client for

    Returns:
        [object]: client session for specific aws service (eg. accessanalyzer)
    """
    return session.client(service)


def paginate(service, method, **method_args):

    paginator = service.get_paginator(method)
    results = paginator.paginate(**method_args)
    return results


def make_dataframe(input):
    """Creates a Pandas Dataframe

    Args:
        input (list): List of k,v pairs to make into a Pandas Dataframe

    Returns:
        Dataframe: Pandas Dataframe
    """
    pd.set_option('max_colwidth', 0)
    df = pd.DataFrame(input)
    return df


def make_dataframe_from_dict(input):
    """Creates a Pandas Dataframe from a Dictionary

    Args:
        input (Dict): Dictionary of k,v pairs to make into a Pandas Dataframe

    Returns:
        Dataframe: Pandas Dataframe
    """
    pd.set_option('max_colwidth', 0)
    df = pd.DataFrame.from_dict(input)
    return df


class Sheet:
    def __init__(self,
                 dataframes: dict,
                 outfile="outfile.xlsx"
                 ):
        """Excel writer class

        Args:
            dataframes (list): Dictionary of sheet name(key), and pandas dataframes (value)
            outfile (str): Path to write the xlsx file
        """

        self.writer = pd.ExcelWriter(outfile, engine='xlsxwriter')
        for sheetname,df in dataframes.items():
            try:
                date_columns = df.select_dtypes(include=['datetime64[ns, UTC]']).columns
                for date_column in date_columns:
                    df[date_column] = df[date_column].dt.date
            except AttributeError:
                continue
            df.to_excel(self.writer, sheet_name=sheetname)

        self.writer.close()
