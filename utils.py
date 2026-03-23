import boto3, os
from datetime import datetime

rekognition = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

TABLE_NAME = os.getenv('DDB_TABLE', 'AttendanceLogs')
table = dynamodb.Table(TABLE_NAME)

def list_registered_faces_from_users(bucket_name):
    res = s3.list_objects_v2(Bucket=bucket_name, Prefix='registered_faces/')
    ret = {}
    for obj in res.get('Contents', []):
        key = obj['Key']
        filename = key.split('/')[-1]
        user_id = filename.split('.')[0]
        ret[user_id] = key
    return ret

def compare_and_log_attendance(bucket_name, target_image_key, similarity_threshold=90):
    registered = list_registered_faces_from_users(bucket_name)
    for user_id, ref_key in registered.items():
        try:
            resp = rekognition.compare_faces(
                SourceImage={'S3Object': {'Bucket': bucket_name, 'Name': ref_key}},
                TargetImage={'S3Object': {'Bucket': bucket_name, 'Name': target_image_key}},
                SimilarityThreshold=similarity_threshold
            )
            if resp.get('FaceMatches'):
                timestamp = datetime.utcnow().isoformat()
                item = {
                    'user_id': user_id,
                    'timestamp': timestamp,
                    'status': 'Present',
                    'image_s3_key': target_image_key
                }
                table.put_item(Item=item)
                return user_id
        except Exception as e:
            print("Rekognition error:", e)
    return None

def fetch_attendance_logs(limit=1000):
    resp = table.scan()
    items = resp.get('Items', [])
    items.sort(key=lambda x: x.get('timestamp',''), reverse=True)
    return items