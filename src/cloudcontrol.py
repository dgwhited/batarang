from .utils import create_client, make_dataframe_from_dict
import json

class CloudControl:
    def __init__(self, session):
        """Cloudcontrol and R53 class

        Args:
            session (boto session object): authenticated AWS session
        """
        self.client = create_client(session=session, service="cloudcontrol")
        self.paginator = self.client.get_paginator('list_resources')

        # EFS
        # might need to make this a full function if more resource types are added
        raw_efs = self.list_resource(resource_type="AWS::EFS::FileSystem")
        for filesystem in raw_efs:
            for property,value in json.loads(filesystem.get("Properties")).items():
                filesystem[property] = value
            filesystem.pop("Properties")
        self.efs = make_dataframe_from_dict(raw_efs)

        # S3
        self.s3 = make_dataframe_from_dict(
            self.list_resource(resource_type="AWS::S3::Bucket"))

        # Route 53
        self.r53 = self.list_resource(resource_type="AWS::Route53::HostedZone")

        self.r53_client = create_client(session=session, service="route53")
        self.r53_paginator = self.r53_client.get_paginator(
            'list_resource_record_sets')
        self.r53_records = [item for hosted_zone in self.r53 for page in self.r53_paginator.paginate(
            HostedZoneId=hosted_zone.get("Identifier")) for item in page.get("ResourceRecordSets")]
        self.dns_names = make_dataframe_from_dict(self.r53_records)


    def list_resource(self, resource_type, aggregate_key="ResourceDescriptions"):
        """Paginated list_resource cloud control command 

        Args:
            resource_type (str): Supported cloud control resource type. e.g. AWS::S3::Bucket
            aggregate_key (str, optional): Dict key to return values . Defaults to "ResourceDescriptions".

        Returns:
            list: list of resource dictionaries
        """
        iterator = self.paginator.paginate(TypeName=resource_type)
        results = [
            item for page in iterator for item in page.get(aggregate_key)]

        return results
