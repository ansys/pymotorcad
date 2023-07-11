"""Module containing MotorCADaaS class for requesting Motor-CAD instances from OnScale."""
from ansys.motorcad.core.motorcad_methods import _MotorCADCore
import uuid

try:
    from pdl_client import AuthenticatedClient
    from pdl_client.helpers import default_cluster_preference as c_pref
    from pdl_client.api.cluster_preference import post_cluster_preference_set
    from pdl_client.models import ValueSetRequest, ValueSetRequestItemValues, ValueSetRequestItem
    from pdl_client.api.value import post_value_set_batch

    PDL_CLIENT_AVAILABLE = True

except:
    PDL_CLIENT_AVAILABLE = False


class MotorCADaaS(_MotorCADCore):
    """Connect to an existing Motor-CAD instance or open a new instance.

    Parameters
    ----------
    url : string, default: ""
        If Motor-CAD instance is already live then set the url to connect to it.
    access_token : string, default: ""
        If this is set then try to create a new instance of Motor-CAD using the access token.

    Returns
    -------
    MotorCADaaS object.
    """

    def __init__(self, url="", access_token=""):
        """Initiate MotorCADaaS object."""
        # Add some error handling to ensure either url or access token set

        if access_token != "":
            if not PDL_CLIENT_AVAILABLE:
                raise Exception("Could not import pdl-client. Please install with pip")

            client = AuthenticatedClient(base_url="https://pdl.test.portal.onscale.com",
                                         token=access_token,
                                         verify_ssl=False)

            # Generate notebook instance id (UUID)
            simulationId = str(uuid.uuid4())

            # Set PDL cluster preference to specify the Notebook's K8s cluster for deployment
            print("set cpref for groupId:" + simulationId)
            cluster_pref = c_pref.create_cluster_preference_for_dev_hpc(simulationId)
            post_cluster_preference_set.sync_detailed(client=client, json_body=cluster_pref)

            # Send values to PDL to trigger mapdl deployment on to Notebook's K8s cluster.
            values = ValueSetRequestItemValues()
            values["notebookInstanceId"] = simulationId
            #values["simulationId"] = simulationId
            values["motorcadImageTag"] = "569061078778.dkr.ecr.us-east-1.amazonaws.com/team1:motor-cad"
            values["stage"] = "test"
            values["notebookSolverName"] = "motor-cad"
            values["notebookNamespace"] = "motor-cad"
            values["hpcIngressDomainName"] = "nginx.dev-hpc-us-east-1-v1-21.hpcs.dev.portal.onscale.com"

            value_set_request_item = ValueSetRequestItem(
                group_id=simulationId,
                group_key="simulationId",
                values=values
            )
            value_set_request = ValueSetRequest(
                cluster_preference_id=simulationId,
                items=[value_set_request_item],
                dry_run=False
            )

            response = post_value_set_batch.sync_detailed(
                client=client,
                json_body=value_set_request,
            )

            print(response)

            print(simulationId)

            url = (
                "https://nginx.dev-hpc-us-east-1-v1-21.hpcs.dev.portal.onscale.com/motor-cad-"
                + simulationId
                + "/"
            )

        """Initiate MotorCAD object."""
        _MotorCADCore.__init__(
            self,
            port=-1,
            open_new_instance=False,
            enable_exceptions=True,
            enable_success_variable=False,
            reuse_parallel_instances=False,
            url=url,
            timeout=300
        )
