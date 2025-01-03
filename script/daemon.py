#!/usr/bin/env python3

import json
import logging
import os
import sys
import traceback

from concurrent.futures import ThreadPoolExecutor

import flatdict
from memoization import cached, CachingAlgorithmFlag
from line_protocol_parser import parse_line
from influx_line_protocol import Metric

os.environ["OCI_PYTHON_SDK_NO_SERVICE_IMPORTS"] = "1"

from oci.retry import RetryStrategyBuilder, BACKOFF_FULL_JITTER_EQUAL_ON_THROTTLE_VALUE

from oci_metaclient import OCIMetaClient

root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.INFO)
root.addHandler(handler)

logger =logging.getLogger(__name__)

clients = {}
TAG_DISCOVER_WORKERS = int(os.environ.get("TAG_DISCOVER_WORKERS", "10"))
OCI_CONFIG_PATH = os.environ.get("OCI_CONFIG_PATH", None)


@cached(max_size=128, algorithm=CachingAlgorithmFlag.LFU)  # the cache overwrites items using the LFU algorithm
def fetch_resource_tags(namespace, dimensions):
    global clients
    api_resource_tags = {}
    
    try:
        resource_info = clients[namespace].get_resource(namespace, dimensions)
        if resource_info.status == 200:
            api_resource_tags = dict(flatdict.FlatDict({ **resource_info.data.defined_tags, **resource_info.data.freeform_tags }, delimiter = ".").items())
        else:
            logger.error(f"The API returned an unexpected error code: {resource_info.status}. Response: {resource_info}")
    
    except Exception as e:
        logger.error(f"An unexpected error was returned during the attempt to fetch data for dimensions {dimensions}: {traceback.format_exc()}")

    return api_resource_tags

def metric_to_stdout(fn):
    if fn.done():
        error = fn.exception()
        if error:
            logger.error(f'{fn.arg} cancelled.')
            fn.result()
        else:
            oci_metric, oci_tags = fn.result()
            for datapoint in oci_metric.get("datapoints"):

                metric = Metric(oci_metric["name"])
                metric.with_timestamp(datapoint["timestamp"]*pow(10, 6))
                
                for k, v in datapoint.items():
                    if k != 'timestamp':
                        metric.add_value(k, v)
                
                for k, v in oci_metric["metadata"].items():
                    metric.add_tag(k, v)
                
                for k, v in oci_metric["dimensions"].items():
                    metric.add_tag(k, v)

                for k, v in oci_tags.items():
                    metric.add_tag(k, v)

                logger.debug(f"Constructed metric: {metric}")
                print(metric)
                sys.stdout.flush()


def fetch_resource(oci_metric):
    namespace = oci_metric.get("namespace")
    dimensions = oci_metric.get("dimensions")

    resource_tags = fetch_resource_tags(namespace, dimensions)
    return oci_metric, resource_tags

def main(oci_config, oci_signer):
    global clients
    logger.info("Initializing main loop.")

    oci_retry_strategy = RetryStrategyBuilder(
        max_attempts_check=True,
        max_attempts=3,

        # Wait 3 seconds between attempts
        retry_max_wait_between_calls_seconds=3,

        service_error_check=True,
        service_error_retry_on_any_5xx=True,
        service_error_retry_config={
            429: []
        },

        # Use exponential backoff and retry with full jitter, but on throttles use
        # exponential backoff and retry with equal jitter
        backoff_type=BACKOFF_FULL_JITTER_EQUAL_ON_THROTTLE_VALUE
    ).get_retry_strategy()

    logger.debug("Setting up OCI API clients.")

    logger.debug("Setting up ThreadPoolExecutor.")
    executor = ThreadPoolExecutor(TAG_DISCOVER_WORKERS)

    logger.info("Entering the main loop.")
    while True:
        for entry in sys.stdin:
            try:
                
                data_from_telegraf = parse_line(entry)
                # if 'value' not in data_from_telegraf['fields']:
                #     continue
                data_to_load = data_from_telegraf['fields']['value'].replace(r'\"', '"')
                oci_metric_json = json.loads(data_to_load)
            
                namespace = oci_metric_json.get("namespace")
                
                if namespace not in clients:
                    clients[namespace] = OCIMetaClient(namespace, signer=oci_signer, retry_strategy=oci_retry_strategy, config=oci_config)

                job = executor.submit(fetch_resource, oci_metric_json)
                job.add_done_callback(metric_to_stdout)
            
            except Exception as e:
                logger.error(f"Couldn't process the input {data_from_telegraf}: {traceback.format_exc()}")



if __name__ == "__main__":

    auth = False
    try:
        from oci.config import from_file
        if OCI_CONFIG_PATH:
            logger.info(f"OCI CONFIG PATH: {OCI_CONFIG_PATH}")
            config = from_file(file_location=OCI_CONFIG_PATH, profile_name="DEFAULT")
        else:
            config = from_file(profile_name="DEFAULT")

        from oci import Signer
        signer = Signer.from_config(config)
        auth = True
    except:
        logger.error('Failed to load profile and signer from the OCI config file.')

    if not auth:
        try:
            from oci.auth.signers import InstancePrincipalsSecurityTokenSigner
            config = {}
            signer = InstancePrincipalsSecurityTokenSigner()
        except:
            logger.error("Failed to load instance principal signer. No supported signer found.")
            sys.exit(1)    

    main(config, signer)