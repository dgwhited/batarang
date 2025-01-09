from .utils import create_client, paginate


def gather_security_hub(session, severity, product_name):
    """Invokes the Security Hub class and gathers findings.

    Args:
        session (_type_): _description_
        severity (list): list of severities in capitals [CRITICAL,HIGH,MEDIUM,LOW,INFORMATIONAL]
        product_name: only required if searching for a specific product name in sechub

    Returns:
        _type_: _description_
    """
    securityhub = create_client(session=session, service="securityhub")
    query = SecurityHubQuery(
        client=securityhub, severity_label_status=severity, product_name=product_name)
    findings = query.get_findings()
    return findings


class SecurityHubQuery:
    """Security Hub Class
    """

    def __init__(self,
                 client,
                 # These defaults are set to only match on "active actual" findings
                 workflow_status=["NEW", "NOTIFIED"],
                 workflow_comparison=["EQUALS"],
                 record_state_status=["ACTIVE"],
                 record_state_comparison=["EQUALS"],
                 compliance_status=["PASSED", "WARNING", "NOT_AVAILABLE"],
                 compliance_comparison=["NOT_EQUALS"],
                 # , "HIGH", "MEDIUM", "LOW"],
                 severity_label_status=["CRITICAL"],
                 severity_label_comparison=["EQUALS"],
                 product_name=None,
                 product_name_comparison="NOT_EQUALS"
                 ) -> None:
        self.client = client
        if not product_name:
            product_name = "Inspector"
        else:
            product_name_comparison = "EQUALS"

        self.args = {
            "Filters": {
                "SeverityLabel": [
                    {"Value": status, "Comparison": comparison} for status in severity_label_status for comparison in severity_label_comparison
                ],
                "WorkflowStatus": [
                    {"Value": status, "Comparison": comparison} for status in workflow_status for comparison in workflow_comparison
                ],
                "RecordState": [
                    {"Value": status, "Comparison": comparison} for status in record_state_status for comparison in record_state_comparison
                ],
                "ComplianceStatus": [
                    {"Value": status, "Comparison": comparison} for status in compliance_status for comparison in compliance_comparison
                ],
                "ProductName": [
                    # CLDSPT-36821 ticket open to remove inspector findings from our account since we are using nessus
                    {"Value": product_name, "Comparison": product_name_comparison}
                ]
            }
        }

    def get_findings(self):
        """Gets Security Hub Findings

        Returns:
            list: Array of Findings returned from the search.
        """
        pages = paginate(service=self.client,
                         method="get_findings", **self.args)
        findings = [
            finding for page in pages for finding in page.get("Findings")]
        return findings


    def get_specific_finding_by_title(self, title):
        """Gets Security Hub findings by title

        Args:
            title (str): The full title to search for

        Returns:
            dict: Response object from AWS Security Hub's GetFindings API
        """
        response = self.client.get_findings(Filters={
            'Title': [
                {
                    'Value': title,
                    'Comparison': 'EQUALS'
                }
            ]
        },
        SortCriteria=[
            {
                'Field': 'LastObservedAt',
                'SortOrder': 'desc'
            }
        ])
        return response
