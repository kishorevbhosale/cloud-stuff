import boto3
import time
import logging
from botocore.exceptions import ClientError, BotoCoreError

# ========== CONFIG ==========
REGION = "us-east-1"
AVAILABILITY_ZONE = "us-east-1a"
AMI_ID = "ami-0abcdef1234567890"  # Replace with your AMI
INSTANCE_TYPE = "t3.micro"
KEY_NAME = "my-key-pair"
SECURITY_GROUP_IDS = ["sg-0123456789abcdef0"]  # Replace with your SG
SUBNET_ID = "subnet-0abcdef1234567890"  # Must match AZ
TOTAL_INSTANCES = 50
MAX_BATCH = 10  # AWS EC2 RunInstances API allows max 100, but use lower for control
TAGS = [{'Key': 'Environment', 'Value': 'Production'}, {'Key': 'Project', 'Value': 'EC2-Auto-Deploy'}]
MAX_RETRIES = 5

# ========== SETUP ==========
logging.basicConfig(
    filename='ec2_creation.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)
ec2 = boto3.client('ec2', region_name=REGION)

# ========== FUNCTION ==========
def launch_instances(count, attempt=1):
    try:
        logging.info(f"Launching {count} instances... Attempt {attempt}")
        response = ec2.run_instances(
            ImageId=AMI_ID,
            InstanceType=INSTANCE_TYPE,
            KeyName=KEY_NAME,
            MaxCount=count,
            MinCount=count,
            SubnetId=SUBNET_ID,
            SecurityGroupIds=SECURITY_GROUP_IDS,
            Placement={"AvailabilityZone": AVAILABILITY_ZONE},
            TagSpecifications=[{
                'ResourceType': 'instance',
                'Tags': TAGS
            }]
        )
        instance_ids = [inst['InstanceId'] for inst in response['Instances']]
        logging.info(f"Successfully launched: {instance_ids}")
        return instance_ids

    except ClientError as e:
        error_code = e.response['Error']['Code']
        logging.error(f"ClientError: {error_code} - {str(e)}")

        if error_code in ["InsufficientInstanceCapacity", "InstanceLimitExceeded", "RequestLimitExceeded"]:
            if attempt <= MAX_RETRIES:
                sleep_time = 2 ** attempt
                logging.warning(f"Retrying after {sleep_time}s due to {error_code}")
                time.sleep(sleep_time)
                return launch_instances(count, attempt + 1)
            else:
                logging.error("Max retries reached. Skipping batch.")
        else:
            logging.error("Fatal error occurred. Exiting.")
            raise e
    except BotoCoreError as e:
        logging.error(f"BotoCoreError: {str(e)}")
        raise e
    return []

# ========== MAIN EXECUTION ==========
def main():
    remaining = TOTAL_INSTANCES
    all_instances = []

    while remaining > 0:
        batch = min(remaining, MAX_BATCH)
        instances = launch_instances(batch)
        if not instances:
            logging.warning("No instances launched in this batch. Breaking loop.")
            break
        all_instances.extend(instances)
        remaining -= len(instances)
        time.sleep(1)  # throttle to avoid hitting API rate limits

    logging.info(f"Total launched: {len(all_instances)} out of {TOTAL_INSTANCES}")
    print(f"Provisioning complete. {len(all_instances)} instances launched.")

if __name__ == "__main__":
    main()
