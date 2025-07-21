# 🛠️ Setting up Amazon CloudWatch Agent on EC2 Instances

This guide explains how to install and configure the **Amazon CloudWatch Agent** to monitor **memory**, **disk**, and **custom metrics** on both **Linux** and **Windows** EC2 instances.

---

## ✅ Steps Overview

| Step | Task                                                                 |
|------|----------------------------------------------------------------------|
| 1    | Create IAM Role with `CloudWatchAgentServerPolicy`                  |
| 2    | Install CloudWatch Agent (Linux or Windows)                         |
| 3    | Run `amazon-cloudwatch-agent-config-wizard`                         |
| 4    | Start the agent using `amazon-cloudwatch-agent-ctl`                 |
| 5    | Use metrics in CloudWatch to create alarms, dashboards              |

---

## 🪪 Step 1: Create IAM Role with CloudWatchAgentServerPolicy

Attach the following AWS managed policy to an **EC2 instance role**:

- **Policy Name**: `CloudWatchAgentServerPolicy`

This allows the agent to push metrics and logs to CloudWatch.

### IAM Role - sample

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:PutMetricData",
        "ec2:DescribeVolumes",
        "logs:PutLogEvents",
        "logs:CreateLogGroup",
        "logs:CreateLogStream"
      ],
      "Resource": "*"
    }
  ]
}

```

---

## 💻 Step 2: Install the CloudWatch Agent

### On Amazon Linux / Amazon Linux 2 / Ubuntu:
```bash
sudo yum install amazon-cloudwatch-agent -y
# or for Ubuntu:
# sudo apt-get install amazon-cloudwatch-agent -y
```
## ⚙️ Step 3: Run Configuration Wizard
```
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
```

## Sample config.json

```
{
  "agent": {
    "metrics_collection_interval": 60,
    "run_as_user": "root",
    "region": "us-east-1"
  },
  "metrics": {
    "namespace": "Custom/EC2",
    "append_dimensions": {
      "InstanceId": "${aws:InstanceId}",
      "InstanceType": "${aws:InstanceType}"
    },
    "aggregation_dimensions": [["InstanceId"]],
    "metrics_collected": {
      "mem": {
        "measurement": [
          "mem_used_percent",
          "mem_available",
          "mem_total"
        ],
        "metrics_collection_interval": 60
      },
      "swap": {
        "measurement": [
          "swap_used_percent"
        ],
        "metrics_collection_interval": 60
      },
      "disk": {
        "measurement": [
          "disk_used_percent",
          "disk_free",
          "disk_total"
        ],
        "metrics_collection_interval": 60,
        "resources": [
          "/"
        ]
      },
      "diskio": {
        "measurement": [
          "io_time",
          "read_bytes",
          "write_bytes"
        ],
        "metrics_collection_interval": 60
      }
    }
  }
}
```

### Step 4: Start the CloudWatch Agent

```
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
-a fetch-config \
-m ec2 \
-c file:/opt/aws/amazon-cloudwatch-agent/bin/config.json \
-s
```

Sample CloudWatch Metrics Data (Custom/EC2)

This is an example of metrics collected by the **Amazon CloudWatch Agent** from an EC2 instance after proper configuration.

---

## ✅ Metric Samples

| Metric Name             | Instance ID         | Value    | Unit      | Timestamp           |
|-------------------------|---------------------|----------|-----------|---------------------|
| `mem_used_percent`      | i-0abcd1234efgh5678 | 72.3     | Percent   | 2025-07-21T14:20Z   |
| `mem_available`         | i-0abcd1234efgh5678 | 1.8      | Gigabytes | 2025-07-21T14:20Z   |
| `disk_used_percent`     | i-0abcd1234efgh5678 | 83.6     | Percent   | 2025-07-21T14:20Z   |
| `disk_free`             | i-0abcd1234efgh5678 | 5.2      | Gigabytes | 2025-07-21T14:20Z   |
| `swap_used_percent`     | i-0abcd1234efgh5678 | 35.0     | Percent   | 2025-07-21T14:20Z   |
| `cpu_usage_idle`        | i-0abcd1234efgh5678 | 22.4     | Percent   | 2025-07-21T14:20Z   |
| `cpu_usage_user`        | i-0abcd1234efgh5678 | 55.1     | Percent   | 2025-07-21T14:20Z   |
| `diskio_read_bytes`     | i-0abcd1234efgh5678 | 1,048,576| Bytes     | 2025-07-21T14:20Z   |
| `diskio_write_bytes`    | i-0abcd1234efgh5678 | 2,097,152| Bytes     | 2025-07-21T14:20Z   |

---
