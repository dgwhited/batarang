from .utils import create_client, make_dataframe, paginate
from datetime import datetime


def get_latest_ami(ec2, version):

    images = ec2.describe_images(
        Owners=["743302140042"],
        Filters=[
            {
                'Name': 'name',
                'Values': [
                    f"amzn2-eks-{version}*",
                ]
            },
        ]
    )
    sorted_images = sorted(images.get("Images"),
                           key=lambda d: d['CreationDate'])
    most_recent_image = sorted_images[len(sorted_images) - 1]
    return most_recent_image


def nodes(session, **arguments):
    ec2 = create_client(session=session, service="ec2")
    order_by = arguments.get("order-by", "ImageCreationDate")

    latest_image = get_latest_ami(
        ec2, arguments.get("eksversion")).get("CreationDate")

    images = paginate(ec2, "describe_instances")

    instances = [
        {
            "InstanceId": instance.get("InstanceId"),
            "ImageId": instance.get("ImageId"),
            "ImageCreationDate": ec2.describe_images(ImageIds=[instance.get("ImageId")]).get("Images")[0].get("CreationDate"),
            "Name": [
                tags for tags in instance.get("Tags")
                for k, v in tags.items() if v == "Name"
            ],
            "InstanceType": instance.get("InstanceType")
        }
        for page in images
        for group in page.get("Reservations")
        for instance in group.get("Instances")
    ]
    for i in instances:
        i["Name"] = i.get("Name")[0].get("Value")
        if i.get("ImageCreationDate") == latest_image:
            i["AgeOfAMI"] = "Current"
        else:
            i["AgeOfAMI"] = datetime.strptime(latest_image, '%Y-%m-%dT%H:%M:%S.%fZ') - datetime.strptime(
                i.get("ImageCreationDate"), '%Y-%m-%dT%H:%M:%S.%fZ')

    if len(instances) > 0:
        df = make_dataframe(instances).sort_values(order_by)
    else:
        df = f"No instances in this region [{session.region_name}]"
    return df
