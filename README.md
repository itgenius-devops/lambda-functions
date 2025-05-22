# 📘 AWS Lambda Function Setup Guide (Learning Purpose)

This guide will walk you through creating two separate AWS Lambda functions using the AWS Console.

> ✅ **NOTE**: For real-world scenarios, NEVER use `AdministratorAccess` on Lambda roles. This is for **learning purposes only**.

---

## 🧾 PREREQUISITES

* An AWS account with access to the AWS Management Console.
* Basic understanding of EC2 instance tags and permissions.

---

# 🔐 STEP 1: Create IAM Role for Lambda

1. Go to the AWS Console and open the **IAM** service.

2. In the left sidebar, click **Roles** > then click **Create role**.

3. Choose:

   * **Trusted entity type**: AWS service
   * **Use case**: Lambda
   * Click **Next**.

4. In **Permissions**, search for and select:
   ✅ `AdministratorAccess` (for learning only)
   Click **Next**.

5. Add tags (optional), then click **Next**.

6. Name the role, e.g., `LambdaAdminRole`, then click **Create role**.

---

# ⚙️ STEP 2A: Create `instance-snapshot-lambda`

This Lambda creates snapshots of EC2 instances based on the `backup_policy` tag.

### 1. Go to the **Lambda** service.

2. Click **Create function**.

3. Choose:

   * Function name: `instance-snapshot-lambda`
   * Runtime: **Python 3.12**
   * Execution role: **Use an existing role**
   * Select: `LambdaAdminRole`
   * Click **Create function**.

4. Scroll to **Function code**, delete all default code, and paste the full script from `instance-snapshot-lambda.py`:

   > 📌 Make sure to copy and paste the correct script from your files.

5. Click **Deploy**.

### ✅ Test the Lambda

1. Click the **Test** tab > Create a new test event.
2. Event name: `TestSnapshot`
3. Leave the event JSON as default (`{}`), click **Save**.
4. Click the **Test** button to trigger the function.
5. View logs in the **Monitor** > **View logs in CloudWatch Logs**.

---

## 🗓️ Want to schedule this Lambda?

Use **EventBridge Scheduler** to run it automatically on a schedule (e.g., daily, weekly).
🔗 [Official AWS Scheduling Guide](https://docs.aws.amazon.com/lambda/latest/dg/with-eventbridge-scheduler.html)

---

# ⚙️ STEP 2B: Create `instance-schedule-lambda`

This Lambda starts and stops EC2 instances based on a `schedule` tag.

### 1. Go to the **Lambda** service again.

2. Click **Create function**.

3. Choose:

   * Function name: `instance-schedule-lambda`
   * Runtime: **Python 3.12**
   * Execution role: **Use an existing role**
   * Select: `LambdaAdminRole`
   * Click **Create function**.

4. Scroll to **Function code**, delete all default code, and paste the full script from `instance-schedule-lambda.py`:

   > 📌 Make sure to copy and paste the correct script from your files.

5. Click **Deploy**.

### ✅ Test the Lambda

1. Click the **Test** tab > Create a new test event.
2. Event name: `TestSchedule`
3. Leave the event JSON as default (`{}`), click **Save**.
4. Click the **Test** button to trigger the function.
5. View logs in the **Monitor** > **View logs in CloudWatch Logs**.

---

## 🗓️ Want to schedule this Lambda?

Use **EventBridge Scheduler** to trigger this function a few times per day and night.
🔗 [Official AWS Scheduling Guide](https://docs.aws.amazon.com/lambda/latest/dg/with-eventbridge-scheduler.html)

---

# 🏷️ TAGGING REQUIREMENTS FOR EC2 INSTANCES

### For Snapshot Lambda:

* Add tag key: `backup_policy`
* Tag values:

  * `daily` → every day
  * `midweekly` → only on Wednesday
  * `weekly` → only on Monday

### For Schedule Lambda:

* Add tag key: `schedule`
* Example value: `start=0800;stop=2000;days=1-5` (Mon–Fri, 8 AM to 8 PM UTC)

---

# ✅ CLEANUP

If you're done testing:

* Stop any started EC2 instances.
* Delete snapshots created during tests.
* Delete Lambda functions and IAM roles if no longer needed.

---
