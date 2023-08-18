from kubernetes import client, config
from artifactory import ArtifactoryPath
from .utils import make_dataframe


class KUBERNETES_CLUSTER:

    def __init__(self):
        # Configs can be set in Configuration class directly or using helper utility
        config.load_kube_config()
        self.v1 = client.CoreV1Api()
        self.images = None

    @property
    def get_running_images(self):
        self.all_pods = self.v1.list_pod_for_all_namespaces(watch=False)

        # set back to list dedupes the list
        self.images = list(set(
            [container.image for i in self.all_pods.items for container in i.spec.containers]))

        self.images.sort()

        df = make_dataframe(self.images)

        return df


class ARTIFACTORY_REPO:
    def __init__(self, auth=None):
        self.auth = auth

    @property
    def get_pipeline_images(self):
        pipeline_tools = []
        if self.auth:
            path = ArtifactoryPath(
                "https://artifactory.cloud.cms.gov/artifactory/batcave-docker/pipeline-tools/",
                auth=self.auth
            )
            pipeline_tools = [
                f"artifactory.cloud.cms.gov/batcave-docker{p.path_in_repo}" for p in path]
        pipeline_tools.sort()
        df = make_dataframe(pipeline_tools)
        return df
