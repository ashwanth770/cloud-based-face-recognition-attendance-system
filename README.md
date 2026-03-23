# cloud-based-face-recognition-attendance-system

## Overview
A cloud-native attendance management system that uses facial recognition to 
automatically mark students/employees as **Present**, **Absent**, or 
**Not Registered** — eliminating proxy attendance and manual effort.

## Architecture
User Webcam → EC2 (Flask API) → AWS Rekognition → DynamoDB (logs) → Amazon S3 (registered faces + frames)

## AWS Services Used
| Service | Role |
|---|---|
| EC2 | Hosts Flask backend (port 5000) |
| S3 | Stores registered face images & attendance frames |
| Rekognition | Face detection & comparison |
| DynamoDB | Attendance log storage |
| IAM | Secure service-to-service access |

## Features
- Face registration via web dashboard
- Real-time webcam attendance marking
- Three-state classification: Present / Absent / Not Registered
- Admin panel with date filtering and CSV export
- Secure IAM role-based access (no hardcoded credentials)

## Setup & Deployment

### Prerequisites
- AWS Account with EC2, S3, Rekognition, DynamoDB access
- IAM Role attached to EC2 with required permissions
- Python 3.x

### Local → EC2 Deployment
```bash
# 1. Clone the repo
git clone https://github.com/yourusername/face-attendance-aws.git

# 2. Transfer to EC2
scp -i your-key.pem -r ./face-attendance-aws ubuntu@<ec2-ip>:~/

# 3. SSH into EC2
ssh -i your-key.pem ubuntu@<ec2-ip>

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set environment variables
export AWS_REGION=ap-south-1
export S3_BUCKET=your-bucket-name
export DDB_TABLE=your-table-name

# 6. Run the app
python3 app.py
```

### Access
- Dashboard: `http://<ec2-public-ip>:5000`
- Register users: `/register`
- Admin panel: `/admin`

## S3 Bucket Structure
```
your-bucket/
├── registered_faces/      # Known user images
├── attendance_frames/     # Captured webcam frames
└── archived_attendance/   # CSV backups
```

## DynamoDB Schema
| Field | Type | Description |
|---|---|---|
| user_id | String | Registered user identifier |
| timestamp | String | UTC timestamp of entry |
| status | String | Present / Not Registered / Invalid |
| image_s3_key | String | Reference to frame in S3 |

## Future Scope
- AWS SageMaker for custom model training
- AWS SNS for real-time alerts
- Mobile app with offline sync
- Multi-tenant SaaS deployment
- Analytics dashboard with attendance trends

```

---

### `.gitignore` (add this too)
```
__pycache__/
*.pem
*.env
.env
venv/
*.pyc
