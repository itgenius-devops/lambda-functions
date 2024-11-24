import boto3
import datetime

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    instances = ec2.describe_instances()

    # Get the current UTC time in HHMM format
    current_time = int(datetime.datetime.utcnow().strftime('%H%M'))
    current_day = datetime.datetime.utcnow().weekday() + 1  # 1=Monday, 7=Sunday

    print(f"Current UTC time: {current_time}, Current UTC day: {current_day}")
    
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_state = instance['State']['Name']
            print(f"Checking instance {instance_id} with state '{instance_state}'.")

            # Find the 'schedule' tag
            schedule_tag = next((tag['Value'] for tag in instance['Tags'] if tag['Key'] == 'schedule'), None)
            if schedule_tag:
                schedule_params = parse_schedule(schedule_tag)
                
                # Print parsed schedule details
                print(f"Instance {instance_id} schedule found: {schedule_params}")
                
                # Convert the days into a list and check if today is within the specified days
                days = schedule_params['days'].split('-')
                day_range = list(range(int(days[0]), int(days[1]) + 1))
                print(f"Allowed days for instance {instance_id}: {day_range}")
                
                # Check if today is within the specified days
                if current_day in day_range:
                    # Determine start and stop times
                    start_time = int(schedule_params['start'])
                    stop_time = int(schedule_params['stop'])
                    print(f"Today's schedule for instance {instance_id}: Start at {start_time}, Stop at {stop_time}")
                    
                    # Handle schedules that span (stop < start)
                    if start_time < stop_time:
                        # Regular schedule within the same day
                        if start_time <= current_time < stop_time:
                            # Operational hours: start <= current < stop
                            if instance_state == 'stopped':
                                ec2.start_instances(InstanceIds=[instance_id])
                                print(f"Started instance {instance_id} at {current_time} UTC (operational hours)")
                            else:
                                print(f"Instance {instance_id} is already running during operational hours.")
                        else:
                            # Non-operational hours
                            if instance_state == 'running':
                                ec2.stop_instances(InstanceIds=[instance_id])
                                print(f"Stopped instance {instance_id} at {current_time} UTC (non-operational hours)")
                            else:
                                print(f"Instance {instance_id} is already stopped during non-operational hours.")
                    else:
                        # schedule (stop < start), e.g., start=0950, stop=0940
                        if current_time >= start_time or current_time < stop_time:
                            # Operational hours: current is after start or before stop the next day
                            if instance_state == 'stopped':
                                ec2.start_instances(InstanceIds=[instance_id])
                                print(f"Started instance {instance_id} at {current_time} UTC (operational hours)")
                            else:
                                print(f"Instance {instance_id} is already running during operational hours.")
                        else:
                            # Non-operational hours
                            if instance_state == 'running':
                                ec2.stop_instances(InstanceIds=[instance_id])
                                print(f"Stopped instance {instance_id} at {current_time} UTC (non-operational hours)")
                            else:
                                print(f"Instance {instance_id} is already stopped during non-operational hours.")
                else:
                    print(f"Today (day {current_day}) is not within the scheduled days {day_range} for instance {instance_id}.")
            else:
                print(f"No schedule tag found for instance {instance_id}; skipping instance.")

    print("Lambda function execution completed.")

def parse_schedule(schedule):
    """
    Parse the schedule string into a dictionary of start, stop, and days.
    Example input: "start=0950;stop=0940;days=1-7"
    """
    params = {}
    for part in schedule.split(';'):
        key, value = part.split('=')
        params[key] = value
    return params
