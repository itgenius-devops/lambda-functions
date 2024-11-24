import boto3
import datetime

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    current_day = datetime.datetime.utcnow().weekday() + 1  # 1=Monday, 7=Sunday
    current_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    print(f"Current UTC time: {current_time}, Current UTC day: {current_day}")

    # Describe all instances
    instances = ec2.describe_instances()

    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_name = get_instance_name(instance)
            print(f"Processing instance {instance_id} ({instance_name})")

            # Check for 'backup_policy' tag
            backup_policy_tag = next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'backup_policy'), None)
            if backup_policy_tag:
                print(f"Instance {instance_name} has backup_policy: {backup_policy_tag}")
                if should_backup(backup_policy_tag, current_day):
                    take_instance_snapshots(instance, ec2, backup_policy_tag, instance_name)
                else:
                    print(f"No backup required today for instance {instance_name} (policy: {backup_policy_tag})")
            else:
                print(f"Instance {instance_name} has no 'backup_policy' tag; skipping instance.")

    print("Lambda function execution completed.")


def get_instance_name(instance):
    """
    Retrieve the Name tag of the instance. If not found, return the instance ID.
    """
    tags = instance.get('Tags', [])
    for tag in tags:
        if tag['Key'] == 'Name':
            return tag['Value']
    return instance['InstanceId']  # Default to instance ID if no Name tag is found


def should_backup(backup_policy, current_day):
    """
    Determine if a backup should be taken based on the backup policy and current day.
    """
    if backup_policy == "daily":
        return True
    elif backup_policy == "weekly" and current_day == 1:  # Monday
        return True
    elif backup_policy == "midweekly" and current_day == 3:  # Wednesday
        return True
    return False


def take_instance_snapshots(instance, ec2, backup_policy, instance_name):
    """
    Take snapshots of all volumes attached to the given instance.
    """
    instance_id = instance['InstanceId']
    volumes = instance.get('BlockDeviceMappings', [])
    
    for volume in volumes:
        volume_id = volume.get('Ebs', {}).get('VolumeId')
        if volume_id:
            # Snapshot name includes instance name (or instance ID if no name) and backup_policy
            snapshot_name = f"{instance_name}-{backup_policy}-snapshot"
            print(f"Creating snapshot for volume {volume_id} on instance {instance_name} with name '{snapshot_name}'")
            try:
                snapshot = ec2.create_snapshot(
                    VolumeId=volume_id,
                    Description=f"Snapshot of {volume_id} from instance {instance_name} on {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}",
                    TagSpecifications=[
                        {
                            'ResourceType': 'snapshot',
                            'Tags': [
                                {'Key': 'Name', 'Value': snapshot_name},
                                {'Key': 'InstanceId', 'Value': instance_id},
                                {'Key': 'VolumeId', 'Value': volume_id},
                                {'Key': 'BackupPolicy', 'Value': backup_policy}
                            ]
                        }
                    ]
                )
                print(f"Snapshot {snapshot['SnapshotId']} created for volume {volume_id}")
            except Exception as e:
                print(f"Error creating snapshot for volume {volume_id} on instance {instance_name}: {str(e)}")

