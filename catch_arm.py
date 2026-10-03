"""
Oracle ARM Instance Catcher - FINAL VERSION
"""

import oci
import os
import sys
import time
from datetime import datetime

# ============================================
# CONFIGURATION
# ============================================

COMPARTMENT_ID = os.environ.get("OCI_COMPARTMENT_OCID")

AVAILABILITY_DOMAIN = "AD-1"
SHAPE = "VM.Standard.A1.Flex"
OCPUS = 1
MEMORY_GB = 6

IMAGE_ID = "ocid1.image.oc1.ap-mumbai-1.aaaaaaaam27cs4bad63uypvkxz477ks5ywhyuacgxnkgcrstedgeawym3vyq"

SUBNET_ID = "ocid1.subnet.oc1.ap-mumbai-1.aaaaaaaa6fdhutxidtdfhgrchbhrm3zmqobn5rp5rp3auwjneskquhsj3qxq"

# ============================================


def try_create():
    try:
        config = oci.config.from_file()
        compute = oci.core.ComputeClient(config)

        launch_details = oci.core.models.LaunchInstanceDetails(
            compartment_id=COMPARTMENT_ID,
            availability_domain=AVAILABILITY_DOMAIN,
            shape=SHAPE,
            shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(
                ocpus=OCPUS,
                memory_in_gbs=MEMORY_GB,
            ),
            display_name="forex-vps-caught",
            image_id=IMAGE_ID,
            subnet_id=SUBNET_ID,
        )

        response = compute.launch_instance(launch_details)
        print("SUCCESS! Instance created:")
        print("   OCID:", response.data.id)
        return True

    except oci.exceptions.ServiceError as e:
        print("ServiceError Code:", e.code)
        print("ServiceError Message:", e.message)
        print("ServiceError Status:", e.status)
        if "Out of host capacity" in str(e.message) or "OutOfCapacity" in str(e.code):
            print(datetime.now(), "— Out of capacity. Retrying...")
            return False
        elif "LimitExceeded" in str(e.code):
            print(datetime.now(), "— Limit exceeded. Stopping.")
            sys.exit(0)
        else:
            print("UNHANDLED ServiceError")
            sys.exit(1)
    except Exception as e:
        print("Unexpected error:", str(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    print("Starting Oracle ARM Catcher at", datetime.now())
    print("   Shape:", SHAPE, "|", OCPUS, "OCPU |", MEMORY_GB, "GB RAM")
    print("   AD:", AVAILABILITY_DOMAIN)
    print("   Compartment:", COMPARTMENT_ID)
    print("   Image:", IMAGE_ID[:60])
    print("   Subnet:", SUBNET_ID[:60])
    print()

    for i in range(10):
        print("Attempt", i + 1, "of 10...")
        if try_create():
            print("Done! Instance created.")
            sys.exit(0)

        if i < 9:
            time.sleep(30)

    print("All tries failed — next workflow run in 5 min")
    sys.exit(0)


if __name__ == "__main__":
    main()
