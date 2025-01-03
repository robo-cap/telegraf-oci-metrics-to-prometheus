# Export OCI Metrics using Telegraf

## Prerequisites

### OCI Metrics -> OCI Streaming

Setup Service Connector Hub to export metrics from OCI Monitoring to OCI Streaming.

1. Create a new stream

Navigate to https://cloud.oracle.com/storage/streaming and create a new stream named `metrics`.

You may select the existing stream pool named, `DefaultPool`, or you can create a new Public one.

2. Configure the Service Connector Hub to export the metrics to OCI Streaming

Navigate to https://cloud.oracle.com/connector-hub/service-connectors and create a new connector.

Source: Monitoring
Configure the desired metric compartment and metric namespaces.

Target: Streaming
Configure the desired stream compartment and stream name.

### Identify connection parameters to OCI Streaming

Get the required information to setup the Telegraf `kafka_consumer` input connection to OCI Streaming.

- Navigate to https://cloud.oracle.com/storage/streaming/streampools and click on the configured StreamPool.

- Click on the `Kafka Connection Settings` link from the right side menu. Here you can find the parameters required to configure the telegraf input.

- Go through [the following steps](https://docs.oracle.com/en-us/iaas/Content/Registry/Tasks/registrygettingauthtoken.htm) to generate an authentication token.

## Build

    docker build -t telegraf:latest .


## Run

Execute the export with the command:

    docker run -itd -p 9273:9273 telegraf 

## Test

    curl localhost:9273/metrics
    # HELP BufferCacheHitRatio Telegraf collected metric
    # TYPE BufferCacheHitRatio untyped
    BufferCacheHitRatio{Oracle_Tags_CreatedBy="oracleidentitycloudservice/test.user@oracle.com",Oracle_Tags_CreatedOn="2024-05-21T12:52:24.647Z",dbInstanceId="379d3543-a719-4dd1dc5196b7",dbInstanceRole="PRIMARY",resourceId="ocid1.postgresqldbsystem.oc1.eu-frankfurt-1.amaaaaaawe6j4fqa6hvp7usdarm2n6pc4svdcu42sxa",resourceName="postgres-demo",resourceType="OCI_OPTIMIZED_STORAGE"} 100
    # HELP BufferCacheHitRatio_count Telegraf collected metric
    # TYPE BufferCacheHitRatio_count untyped
    BufferCacheHitRatio_count{Oracle_Tags_CreatedBy="oracleidentitycloudservice/test.user@oracle.com",Oracle_Tags_CreatedOn="2024-05-21T12:52:24.647Z",dbInstanceId="379d3543-a719-4dd1dc5196b7",dbInstanceRole="PRIMARY",resourceId="ocid1.postgresqldbsystem.oc1.eu-frankfurt-1.amaaaaaawe6j4fqa6hvp7usdarm2n6pc4svdcu42sxa",resourceName="postgres-demo",resourceType="OCI_OPTIMIZED_STORAGE"} 1