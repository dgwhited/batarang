from .utils import create_client, make_dataframe, paginate


def check_ebs(session):
    """Creates a Dataframe of currently attached EBS objects that hold data in a cluster.

    Args:
        session (object): Authenticated AWS session object

    Returns:
        Dataframe: Pandas Dataframe of EBS volume information
    """
    ec2 = create_client(session=session, service="ec2")
    volumes_formatted = EBS(client=ec2).volumes_formatted
    df = make_dataframe(volumes_formatted)
    return df


class EBS:
    """Gets a list of EBS volumes and checks if they have a snapshot
    """

    def __init__(self, client):
        self.client = client
        self.all_volumes_over_size = []
        self.get_volumes()
        self.get_snapshots_for_volumes()
        self.volumes_formatted = [vars(vol)
                                  for vol in self.all_volumes_over_size]

    def get_volumes(self):
        """Gets all volumes that have the specific kubernetes created pvc tag
        """
        args = [{
            'Name': 'tag-key',
            'Values': ['kubernetes.io/created-for/pvc/name']
        }]
        response = paginate(service=self.client,
                            method="describe_volumes", Filters=args)
        # 50gb was chosen because root volumes are 8/10gb. Most ADOs have at least a 300gb EBS volume attached to their nodes.
        self.all_volumes_over_size = [Volume(volume) for page in response for volume in page.get(
            "Volumes") if volume.get("State") == "in-use"]

    def get_snapshots_for_volumes(self):
        """Gets all snapshots and then retrieves the latest snapshot from the list.
        """
        for volume in self.all_volumes_over_size:
            response = self.client.describe_snapshots(Filters=[
                {
                    'Name': 'volume-id',
                    'Values': [
                        volume.volume_id
                    ]
                }
            ])
            sorted_snapshots = sorted(response.get("Snapshots"),
                                      key=lambda d: d['StartTime'])
            if sorted_snapshots:
                volume.latest_snapshot_id = sorted_snapshots[-1].get(
                    "SnapshotId")
                volume.latest_snapshot_date = sorted_snapshots[-1].get(
                    "StartTime")


class Volume:
    """Class for formatting purposes.
    """
    def __init__(self, describe_volume_response):
        self.instance_id = describe_volume_response.get("Attachments")[0].get("InstanceId")
        self.volume_id = describe_volume_response.get("VolumeId")
        self.encrypted_at_rest = describe_volume_response.get("Encrypted")
        self.size = describe_volume_response.get("Size")
        self.state = describe_volume_response.get("State")
        self.latest_snapshot_id = None
        self.latest_snapshot_date = None
