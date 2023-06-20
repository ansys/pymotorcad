from ansys.motorcad.core.motorcad_methods import _MotorCADCore
import uuid

try:
    import pdl_client
    from pdl_client import AuthenticatedClient
    from pdl_client.helpers import default_cluster_preference as c_pref
    from pdl_client.helpers import pdl_access_token as token
    from pdl_client.api.cluster_preference import post_cluster_preference_set
    from pdl_client.models import ValueSetBatchRequest, ValueSetRequest
    from pdl_client.api.value import post_value_set_batch
    PDL_CLIENT_AVAILABLE = True

except:
    PDL_CLIENT_AVAILABLE = False


class MotorCADaaS(_MotorCADCore):
    """Connect to an existing Motor-CAD instance or open a new instance.

    Parameters
    ----------


    Returns
    -------
    MotorCAD object.

    access token - launch a new one
    url - connect to existing
    """
    def __init__(
        self,
        url="",
        access_token=""
    ):

        if access_token != "":
            if not PDL_CLIENT_AVAILABLE:
                raise Exception("Could not import pdl-client. Please install with pip")

            client = AuthenticatedClient(base_url="https://pdl.test.portal.onscale.com", token=access_token,
                                         verify_ssl=False)

            # Generate notebook instance id (UUID)
            notebookInstanceId = str(uuid.uuid4())

            # Set PDL cluster preference to specify the Notebook's K8s cluster for deployment
            print('set cpref for groupId:' + notebookInstanceId)
            cluster_pref = c_pref.create_cluster_preference_for_dev_hpc(notebookInstanceId)
            post_cluster_preference_set.sync_detailed(client=client, json_body=cluster_pref)

            # Send values to PDL to trigger mapdl deployment on to Notebook's K8s cluster.
            value1 = ValueSetRequest(
                name="notebookInstanceId",
                value=notebookInstanceId,
                group_key="notebookInstanceId",
                group_id=notebookInstanceId
            )

            value2 = ValueSetRequest(
                name="motorcadImageTag",
                value="569061078778.dkr.ecr.us-east-1.amazonaws.com/team1:motor-cad",
                group_key="notebookInstanceId",
                group_id=notebookInstanceId
            )

            value3 = ValueSetRequest(
                name="stage",
                value="test",
                group_key="notebookInstanceId",
                group_id=notebookInstanceId
            )

            value4 = ValueSetRequest(
                name="notebookSolverName",
                value="motor-cad",
                group_key="notebookInstanceId",
                group_id=notebookInstanceId
            )

            value5 = ValueSetRequest(
                name="notebookNamespace",
                value="motor-cad",
                group_key="notebookInstanceId",
                group_id=notebookInstanceId
            )

            value6 = ValueSetRequest(
                name="hpcIngressDomainName",
                value="nginx.dev-hpc-us-east-1-v1-21.hpcs.dev.portal.onscale.com",
                group_key="notebookInstanceId",
                group_id=notebookInstanceId
            )

            values_batch = ValueSetBatchRequest(
                items=[value1, value2, value3, value4, value5, value6]
            )

            response = post_value_set_batch.sync_detailed(
                client=client,
                json_body=values_batch,
                group_id=notebookInstanceId,
                group_key="notebookInstanceId")

            print(response)

            print(notebookInstanceId)

            url = "https://nginx.dev-hpc-us-east-1-v1-21.hpcs.dev.portal.onscale.com/motor-cad-" \
                  + notebookInstanceId + "/"

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

