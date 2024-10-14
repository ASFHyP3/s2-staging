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
python
```

```python
from main import fetch_scene
fetch_scene('S2B_MSIL1C_20240216T235509_N0510_R087_T51CWT_20240217T005730', 'myBucket', 'myPrefix/')
```
