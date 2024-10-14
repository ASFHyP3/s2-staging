# s2-staging
Small app for copying Sentinel-2 B08.jp2 files from Google Cloud Storage to AWS S3

For example, for scene `S2A_MSIL1C_20231213T235751_N0510_R087_T51CWT_20231214T003659`:
- https://storage.googleapis.com/gcp-public-data-sentinel-2/tiles/51/C/WT/S2A_MSIL1C_20231213T235751_N0510_R087_T51CWT_20231214T003659.SAFE/./GRANULE/L1C_T51CWT_A044271_20231213T235749/IMG_DATA/T51CWT_20231213T235751_B08.jp2

is copied to:
- `s3://myBucket/myPrefix/S2A_MSIL1C_20231213T235751_N0510_R087_T51CWT_20231214T003659_B08.jp2`

## Local Usage

Requires AWS credentials with `s3:PutObject` permissions for `arn:aws:s3:::myBucket/myPrefix/*`.

```commandline
git clone git@github.com:ASFHyP3/s2-staging.git
cd s2-staging
mamba env create -f environment.yml
mamba activate s2-staging
cd src
python
```

```python
from main import fetch_scene
fetch_scene('S2B_MSIL1C_20240216T235509_N0510_R087_T51CWT_20240217T005730',
            'myBucket', 'myPrefix/')
```

## AWS Usage

Requires AWS credentials with permission to deploy the CloudFormation stack into JPL-managed AWS.

```
git clone git@github.com:ASFHyP3/s2-staging.git
cd s2-staging
mamba env create -f environment.yml
mamba activate s2-staging

python -m pip install -r requirements.txt -t src/
aws cloudformation package \
  --template-file cloudformation.yml \
  --s3-bucket myBucket \
  --s3-prefix myPrefix \
  --output-template-file packaged.yml
aws cloudformation deploy \
  --template-file packaged.yml \
  --stack-name s2-staging \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides BucketName=its-live-project BucketPrefix=s2-cache/

aws sqs send-message \
  --queue-url https://sqs.us-west-2.amazonaws.com/123456789012/s2-staging-Queue-MxuL1mLZVvUO \
  --message-body S2A_MSIL1C_20231213T235751_N0510_R087_T51CWT_20231214T003659
```

See [batch_sqs_submit.py](batch_sqs_submit.py) for an example of submitting many scenes using [sqs.send_message_batch](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs/client/send_message_batch.html).
