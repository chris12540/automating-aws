import boto3
import click

session = boto3.Session(profile_name="pythonAutomation")
s3 = session.resource('s3')


@click.group()
def cli():
    "Webotron deploys websites to AWS"
    pass


@cli.command('list-buckets')
def list_buckets():
    "List all s3 buckets"
    for bucket in s3.buckets.all():
        print(bucket)


@cli.command('list-bucket-objects')
@click.argument('bucket')
def list_bucket_objects(bucket):
    "List all objects in a bucket"
    for obj in s3.Bucket(bucket).objects.all():
        print(obj)


@cli.command('bucket-upload')
@click.argument('bucket')
@click.argument('file')
@click.argument('key')
def bucket_upload(bucket, file, key):
    "Upload object to bucket"
    s3.Bucket(bucket).upload_file(file, key)


@cli.command('setup-bucket')
@click.argument('bucket')
def setup_bucket(bucket):
    "Create and configure bucket"
    s3_bucket = None
    if session.region_name == 'us-east-1':
        s3_bucket = s3.create_bucket(Bucket=bucket)
    else:
        s3_bucket = s3.create_bucket(
            Bucket=bucket, CreateBucketConfiguration={'LocationContraint': session.region_name})
    policy = """
    {
    "Version":"2012-10-17",
    "Statement":[{
    "Sid":"PublicReadGetObject",
    "Effect":"Allow",
    "Principal": "*",
        "Action":["s3:GetObject"],
        "Resource":["arn:aws:s3:::%s/*"]
        }
    ]}
    """ % s3_bucket.name
    policy = policy.strip()

    pol = s3_bucket.Policy()
    pol.put(Policy=policy)
    ws = s3_bucket.Website()

    ws.put(WebsiteConfiguration={
        'ErrorDocument': {
            'Key': 'error.html'
        },
        'IndexDocument': {
            'Suffix': 'index.html'
        }})

    print(s3_bucket)
    print(policy)
    print(pol)
    print(ws)

    return


if __name__ == '__main__':
    cli()
