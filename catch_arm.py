"""
Oracle ARM Instance Catcher for GitHub Actions
"""
import oci
import os
import sys
import time
from datetime import datetime

# --- CONFIGURATION (તમારે આ બદલવાનું છે) ---
COMPARTMENT_ID = os.environ.get("OCI_COMPARTMENT_OCID")
AVAILABILITY_DOMAIN = "AD-1"     # AD-1, AD-2, કે AD-3 માંથી એક
SHAPE = "VM.Standard.A1.Flex"
OCPUS = 1                        # 1 OCPU = capacity મળવાની શક્યતા વધુ
MEMORY_GB = 6                    # 6 GB RAM

# આ OCID તમારા Oracle Account મુજબ બદલવો પડશે (નીચે સમજાવ્યું છે)
IMAGE_ID = "ocid1.image.oc1.ap-mumbai-1.aaaaaaa..."   # Ubuntu ARM Image
SUBNET_ID = "ocid1.subnet.oc1.ap-mumbai-1.aaaaaaa..." # Public Subnet

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
        print(f"✅ SUCCESS! Instance created: {response.data.id}")
        return True

    except oci.exceptions.ServiceError as e:
        if "Out of host capacity" in str(e.message):
            print(f"⚠️ {datetime.now()} — Out of capacity. Retrying...")
            return False
        else:
            print(f"❌ Error: {e.code} — {e.message}")
            sys.exit(1)  # બીજી કોઈ ભૂલ હોય તો અટકી જાઓ

def main():
    print(f"🎯 Starting Oracle ARM Catcher at {datetime.now()}")
    print(f"   Shape: {SHAPE} | {OCPUS} OCPU | {MEMORY_GB} GB RAM")
    
    for i in range(10):   # 10 વાર પ્રયત્ન કરો
        if try_create():
            sys.exit(0)
        if i < 9:
            time.sleep(30) # 30 સેકન્ડ રાહ જુઓ
    
    print("⏳ All tries failed. Next run in 5 minutes.")

if __name__ == "__main__":
    main()
