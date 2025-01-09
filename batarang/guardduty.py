from .utils import create_client, paginate


def get_guardduty_findings(session):
    """_summary_

    Args:
        session (_type_): _description_

    Returns:
        _type_: _description_
    """
    gd_client = create_client(session=session, service="guardduty")

    gd = GuardDuty(client=gd_client)
    return gd.get_findings()


class GuardDuty:
    """_summary_
    """

    def __init__(self, client):
        self.client = client
        self.detector = self.client.list_detectors().get("DetectorIds")[0]
        self.findings = self.finding_ids()

    def finding_ids(self):
        """_summary_
        """
        # get_findings can only handle max 50 findings at a time
        args = {"DetectorId": self.detector,
                "PaginationConfig": {'PageSize': 50}}
        response = paginate(service=self.client,
                            method="list_findings", **args)
        findings = [page.get("FindingIds") for page in response]
        return(findings)

    def get_findings(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        finding_details = []
        for grouping in self.findings:
            args = {"DetectorId": self.detector, "FindingIds": grouping}

            # this method cannot paginate
            response = self.client.get_findings(**args)
            f = [item for item in response.get("Findings")]
            finding_details.extend(f)
        return finding_details
