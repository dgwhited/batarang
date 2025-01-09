"""batarang
Usage:
    batarang [--help] [--version]
    batarang nodes  [--order-by order]
                    [--profile PROFILE] [--region REGION] [--csvoutputfile CSV_OUT]
    batarang latest [--eksversion eksversion]
                    [--profile PROFILE] [--region REGION] [--csvoutputfile CSV_OUT]
    batarang sechub [--severity severity]
                    [--profile PROFILE] [--region REGION] [--csvoutputfile CSV_OUT] [--productname productname]
    batarang guardduty
                    [--profile PROFILE] [--region REGION] [--csvoutputfile CSV_OUT]
    batarang k8s    [--csvoutputfile CSV_OUT]
    batarang artifactory [--csvoutputfile CSV_OUT]
    batarang databases [--profile PROFILE] [--region REGION] [--csvoutputfile CSV_OUT]
    batarang ebs [--profile PROFILE] [--region REGION] [--csvoutputfile CSV_OUT]
    batarang productionreadiness [--profile PROFILE] [--region REGION] [--csvoutputfile CSV_OUT]

Options:
    --help                          Show this screen.
    --version                       Show version.
    --profile profile               AWS Profile [None]
    --region region                 AWS Region [None]
    --csvoutputfile csvoutputfile   Name of file to dump output to
    --eksversion eksversion         EKS version to use when searching AMIs [Default: 1.29]
    --severity severity             Security Hub Severity [Default: CRITICAL,HIGH,MEDIUM,LOW]
    --order-by order                Sort the tabular output [Default: ImageCreationDate]
    --productname productname       Name of product name to search for [None]
"""

from docopt import docopt
from .utils import create_client, create_session
from .check_amis import get_latest_ami, nodes
from .sechub import gather_security_hub
from .guardduty import get_guardduty_findings
from .dump_csv import dumpCSV
from .k8s import KUBERNETES_CLUSTER
from .database import check_databases
from .ebs import check_ebs
from .production_readiness import production_readiness_checks
from getpass import getpass


def main():
    arguments = {
        k.lstrip('-'): v for k, v in docopt(__doc__, version='batCAVE batarang v2.1.0').items()
    }
    run(**arguments)


def run(**arguments):
    """_summary_
    """
    session = create_session(profile=arguments.get(
        "profile"), region=arguments.get("region"))

    if arguments.get("productionreadiness"):
        response = production_readiness_checks(session=session, **arguments)
    else:
        if arguments.get("nodes"):
            response = nodes(session=session, **arguments)
        elif arguments.get("latest"):
            ec2 = create_client(session=session, service="ec2")
            response = get_latest_ami(ec2=ec2, version=arguments.get("eksversion"))
        elif arguments.get("sechub"):
            if arguments.get("severity"):
                arguments["severity"] = arguments['severity'].rsplit(sep=',')
            response = gather_security_hub(
                session=session, severity=arguments.get("severity"), product_name=arguments.get("productname"))
        elif arguments.get("guardduty"):
            response = get_guardduty_findings(session=session)
        elif arguments.get("k8s"):
            cluster = KUBERNETES_CLUSTER()
            # only one kubernetes command right now more if statements when we add more features
            response = cluster.get_running_images
        # elif arguments.get("artifactory"):
        #     un = getpass(prompt="EID:")
        #     pw = getpass(prompt="Password:", stream=None)
        #     auth = (un, pw)
        #     af = ARTIFACTORY_REPO(auth=auth)
        #     response = af.get_pipeline_images
        elif arguments.get("databases"):
            response = check_databases(session=session)
        elif arguments.get("ebs"):
            response = check_ebs(session=session)

        if arguments.get("csvoutputfile"):
            dumpCSV(response, csvPath=arguments.get("csvoutputfile"))
        else:
            print(response)

if __name__ == '__main__':
    main()
