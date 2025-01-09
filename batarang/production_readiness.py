from .check_amis import nodes
from .database import check_databases
from .ebs import check_ebs
from .utils import create_client, make_dataframe, Sheet
from .cloudcontrol import CloudControl
from .sechub import SecurityHubQuery


def production_readiness_checks(session, **arguments):
    """Production Readiness - an amalgamation of batarang checks.

    Args:
        session (object): Authenticated AWS Session object
        arguments: Docopt arguments

    Returns:
        _type_: _description_
    """
    if arguments.get("csvoutputfile"):
        outfile = arguments.get("csvoutputfile")
    else:
        if arguments.get("profile"):
            outfile = f"{arguments.get('profile')}.xlsx"
        else:
            outfile = "outfile"

    excel_sheet = {}
    # check volumes
    excel_sheet["volumes"] = check_ebs(session=session)

    # check databases
    excel_sheet["databases"] = check_databases(session=session)

    # check gold image
    excel_sheet["instances"] = nodes(session, **arguments)

    # Get DNS Names, EFS, and S3
    cc = CloudControl(session=session)
    excel_sheet["dns_names"] = cc.dns_names
    excel_sheet["elasticfilesystems"] = cc.efs
    excel_sheet["s3_buckets"] = cc.s3

    # Nessus creates an informational finding with details on configuration. If Nessus isnt configured, this will return empty array.
    securityhub = create_client(session=session, service="securityhub")
    nessus_scan_info = SecurityHubQuery(client=securityhub).get_specific_finding_by_title(title="Nessus Scan Information").get("Findings")
    excel_sheet["nessus_scan_info"] = make_dataframe(nessus_scan_info)

    # Nessus creates an informational finding when Trend is installed.
    antivirus_installed = SecurityHubQuery(client=securityhub).get_specific_finding_by_title(title="Trend Micro Deep Security Agent Installed (Linux)").get("Findings")
    excel_sheet["antivirus_installed"] = make_dataframe(antivirus_installed)

    Sheet(dataframes=excel_sheet, outfile=outfile)

    return f"Wrote file to {outfile}"
