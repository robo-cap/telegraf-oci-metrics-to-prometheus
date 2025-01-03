
class OCIMetaClient:
    
    # Resource Identifier based on metrics data
    default_resource_identifier = "resourceId"

    resource_identifier_override = {
        "oci_service_connector_hub": "connectorId",
        "oci_objectstorage": "resourceID"
    }
    

    @classmethod
    def get_resource_ocid(cls, namespace, dimensions):
        """
        Function returns the resource identifier based on the namespace and dimensions
        from OCI metrics.
        """

        namespace = dimensions.get("namespace")
        
        if namespace in OCIMetaClient.resource_identifier_override:
            return dimensions.get(OCIMetaClient.resource_identifier_override[namespace])
        
        return dimensions.get(OCIMetaClient.default_resource_identifier)


    def __init__(self, namespace, **kwargs):
        
        if kwargs.get("retry_strategy"):
            self.retry_strategy = kwargs.get("retry_strategy")
        else:
            from oci.retry import DEFAULT_RETRY_STRATEGY
            self.retry_strategy = DEFAULT_RETRY_STRATEGY
        
        if kwargs.get("config"):
            self.config = kwargs.get("config")
        else:
            self.config = {}

        if kwargs.get("signer"):
            self.signer = kwargs.get("signer")
        else:
            self.signer = None

        self.namespace = namespace

        if namespace == "oci_apigateway":
            from oci.apigateway import GatewayClient
            self.gateway_client = GatewayClient(config=self.config, signer=self.signer, retry_strategy=self.retry_strategy)
            return

        if namespace == "oci_bastion":
            from oci.bastion import BastionClient
            self.bastion_client = BastionClient(config=self.config, signer=self.signer, retry_strategy=self.retry_strategy)
            return

        if namespace == "oci_blockstore":
            from oci.core import BlockstorageClient
            self.blockstorage_client = BlockstorageClient(config=self.config, signer=self.signer, retry_strategy=self.retry_strategy)
            return
    
        if namespace in ("oci_compute_infrastructure_health", "oci_compute_instance_health", "oci_computeagent", "oci_compute"):
            from oci.core import ComputeClient
            self.compute_sclient = ComputeClient(config=self.config, signer=self.signer, retry_strategy=self.retry_strategy)
            return

        if namespace == "oci_filestorage":
            from oci.file_storage import FileStorageClient
            self.file_storage_client = FileStorageClient(config=self.config, signer=self.signer, retry_strategy=self.retry_strategy)
            return

        if namespace == "oci_internet_gateway":
            from oci.core import VirtualNetworkClient
            self.virtual_network_client = VirtualNetworkClient(config=self.config, signer=self.signer, retry_strategy=self.retry_strategy)
            return

        if namespace == "oci_lbaas":
            from oci.load_balancer import LoadBalancerClient
            self.load_balancer_client = LoadBalancerClient(config=self.config, signer=self.signer, retry_strategy=self.retry_strategy)
            return

        if namespace == "oci_logging":
            from oci.logging import LoggingManagementClient
            self.logging_management_client = LoggingManagementClient(config=self.config, signer=self.signer, retry_strategy=self.retry_strategy)
            return

        if namespace == "oci_managementagent":
            from oci.management_agent import ManagementAgentClient
            self.management_agent_client = ManagementAgentClient(config=self.config, signer=self.signer, retry_strategy=self.retry_strategy)
            return

        if namespace == "oci_objectstorage":
            from oci.object_storage import ObjectStorageClient
            self.object_storage_client = ObjectStorageClient(config=self.config, signer=self.signer, retry_strategy=self.retry_strategy)
            
            from oci.resource_search import ResourceSearchClient
            self.resource_search_client = ResourceSearchClient(config=self.config, signer=self.signer, retry_strategy=self.retry_strategy)
            return

        if namespace == "oci_oke":
            from oci.container_engine import ContainerEngineClient
            self.container_engine_client = ContainerEngineClient(config=self.config, signer=self.signer, retry_strategy=self.retry_strategy)

            from oci.core import ComputeClient
            self.compute_client = ComputeClient(config=self.config, signer=self.signer, retry_strategy=self.retry_strategy)    
            return
        
        if namespace == "oci_postgresql":
            from oci.psql import PostgresqlClient
            self.postgresql_client = PostgresqlClient(config=self.config, signer=self.signer, retry_strategy=self.retry_strategy)
            return
        
        if namespace == "oci_secrets":
            from oci.vault import VaultsClient
            self.vaults_client = VaultsClient(config=self.config, signer=self.signer, retry_strategy=self.retry_strategy)
            return
        
        if namespace == "oci_service_connector_hub":
            from oci.sch import ServiceConnectorClient
            self.service_connector_client = ServiceConnectorClient(config=self.config, signer=self.signer, retry_strategy=self.retry_strategy)
            return
        
        if namespace == "oci_service_gateway":
            from oci.core import VirtualNetworkClient
            self.virtual_network_client = VirtualNetworkClient(config=self.config, signer=self.signer, retry_strategy=self.retry_strategy)
            return
        
        if namespace == "oci_vcn":
            from oci.core import VirtualNetworkClient
            self.virtual_network_client = VirtualNetworkClient(config=self.config, signer=self.signer, retry_strategy=self.retry_strategy)
            return
        
        if namespace == "oci_vcnip":
            from oci.core import VirtualNetworkClient
            self.virtual_network_client = VirtualNetworkClient(config=self.config, signer=self.signer, retry_strategy=self.retry_strategy)
            return

    def get_resource(self, namespace, dimensions):
        """
        Method used to return resource based on the OCI metric content.
        """

            
        if namespace == "oci_apigateway":
            resource_id = self.get_resource_ocid(namespace, dimensions)
            if "apigateway" in resource_id.split("."):
                response = self.gateway_client.get_gateway(resource_id)
                return response

        if namespace == "oci_bastion":
            resource_id = self.get_resource_ocid(namespace, dimensions)
            if "bastion" in resource_id.split("."):
                response = self.bastion_client.get_bastion(resource_id)
                return response
                
        if namespace == "oci_blockstore":
            resource_id = self.get_resource_ocid(namespace, dimensions)
            if "bootvolume" in resource_id.split("."):
                response = self.blockstorage_client.get_boot_volume(resource_id)
                return response
            if "volume" in resource_id.split("."):
                response = self.blockstorage_client.get_volume(resource_id)
                return response

        if namespace in ("oci_compute_infrastructure_health", "oci_compute_instance_health", "oci_computeagent", "oci_compute"):
            resource_id = self.get_resource_ocid(namespace, dimensions)
            if "instance" in resource_id.split("."):
                response = self.compute_sclient.get_instance(resource_id)
                return response

        if namespace == "oci_filestorage":
            resource_id = self.get_resource_ocid(namespace, dimensions)
            if "mounttarget" in resource_id.split("."):
                response = self.file_storage_client.get_mount_target(resource_id)
                return response

            if "filesystem" in resource_id.split("."):
                response = self.file_storage_client.get_file_system(resource_id)
                return response    

        if namespace == "oci_internet_gateway":
            resource_id = self.get_resource_ocid(namespace, dimensions)
            if "internetgateway" in resource_id.split("."):
                response = self.virtual_network_client.get_internet_gateway(resource_id)
                return response

        if namespace == "oci_lbaas":
            resource_id = self.get_resource_ocid(namespace, dimensions)
            if "loadbalancer" in resource_id.split("."):
                response = self.load_balancer_client.get_load_balancer(resource_id)
                return response

        if namespace == "oci_logging":
            resource_id = self.get_resource_ocid(namespace, dimensions)
            logGroupId = dimensions.get("logGroupId", None)
            if "log" in resource_id.split(".") and logGroupId:
                response = self.logging_management_client.get_log(logGroupId, resource_id)
                return response

        if namespace == "oci_managementagent":
            resource_id = self.get_resource_ocid(namespace, dimensions)
            if "managementagent" in resource_id.split("."):
                response = self.management_agent_client.get_management_agent(resource_id)
                return response

        if namespace == "oci_objectstorage":
            from oci.resource_search.models import StructuredSearchDetails
            resource_id = self.get_resource_ocid(namespace, dimensions)
            if "bucket" in resource_id.split("."):
                # get bucket name
                resource_search_response = self.resource_search_client.search_resources(
                    search_details=StructuredSearchDetails(
                        type="Structured",
                        query=f"query bucket resources where identifier='{resource_id}'"
                    ),
                    limit=1
                )

                if resource_search_response.status == 200 and len(resource_search_response.data.items):
                    bucket_name = resource_search_response.data.items[0].display_name
                
                namespace = self.object_storage_client.get_namespace()

                response = self.object_storage_client.get_bucket(namespace_name=namespace.data, bucket_name=bucket_name)
                return response

        if namespace == "oci_oke":
            resource_id = self.get_resource_ocid(namespace, dimensions)
            if "instance" in resource_id.split("."):
                response = self.compute_client.get_instance(resource_id)
                return response

            if "cluster" in resource_id.split("."):
                response = self.container_engine_client.get_cluster(resource_id)
                return response    

        if namespace == "oci_postgresql":
            resource_id = self.get_resource_ocid(namespace, dimensions)
            if "postgresqldbsystem" in resource_id.split("."):
                response = self.postgresql_client.get_db_system(resource_id)
                return response

        if namespace == "oci_secrets":
            resource_id = self.get_resource_ocid(namespace, dimensions)
            if "vaultsecret" in resource_id.split("."):
                response = self.vaults_client.get_secret(resource_id)
                return response

        if namespace == "oci_service_connector_hub":
            resource_id = self.get_resource_ocid(namespace, dimensions)
            if "serviceconnector" in resource_id.split("."):
                response = self.service_connector_client.get_service_connector(resource_id)
                return response
                
        if namespace == "oci_service_gateway":
            resource_id = self.get_resource_ocid(namespace, dimensions)
            if "servicegateway" in resource_id.split("."):
                response = self.virtual_network_client.get_service_gateway(resource_id)
                return response

        if namespace == "oci_vcn":
            resource_id = self.get_resource_ocid(namespace, dimensions)
            if "vnic" in resource_id.split("."):
                response = self.virtual_network_client.get_vnic(resource_id)
                return response

        if namespace == "oci_vcnip":
            resource_id = self.get_resource_ocid(namespace, dimensions)
            if "subnet" in resource_id.split("."):
                response = self.virtual_network_client.get_subnet(resource_id)
                return response