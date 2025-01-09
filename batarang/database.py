from .utils import create_client, make_dataframe, paginate


def check_databases(session):
    """Performs Database information gathering

    Args:
        session (obj): Authenticated AWS Session object

    Returns:
        Dataframe: Pandas Dataframe with Database information
    """
    # get database encryption and backup retention
    rds = create_client(session=session, service="rds")
    databases = RDS(client=rds)
    df = make_dataframe(databases.databases)
    return df


class RDS:
    """Gets a list of database instances and then returns a dictionary of relevant information for production readiness.
    """

    def __init__(self, client):
        self.client = client
        self.databases_response = []
        self.get_dbs()
        self.databases = [vars(Database(db)) for db in self.databases_response]

    def get_dbs(self):
        response = paginate(service=self.client,
                            method="describe_db_instances")
        self.databases_response = [
            db for page in response for db in page.get("DBInstances")]


class Database:
    """Database information formatting
    """
    def __init__(self, describe_db_response):
        self.name = describe_db_response.get("DBName")
        self.engine = describe_db_response.get("Engine")
        self.instance = describe_db_response.get("DBInstanceClass")
        self.backup_retention = describe_db_response.get(
            "BackupRetentionPeriod")
        self.multi_az = describe_db_response.get("MultiAZ")
        self.encrypted_at_rest = describe_db_response.get("StorageEncrypted")
        self.backup_target = describe_db_response.get("BackupTarget")
