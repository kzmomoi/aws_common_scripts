import datetime
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

REGION = 'ap-northeast-1'
FILESYSTEM_ID = 'FILESYSTEM_ID'   # fs-XXXXXXXX
LOWER_THRESHOLD = 500000000000.0
UPPER_THRESHOLD = 2300000000000.0
EFS_CLIENT = boto3.client('efs', region_name=REGION)


def lambda_handler(event, context):
    try:
        logger.info('start lambda_handler')

        # BurstCreditBaranceの残量を取得する
        burst_credit_balance = fetch_burst_credit_balance()
        logger.info(f'burst_credit_balance: {burst_credit_balance}')

        # EFSのスループットモードの状態を取得する（Burst or Provisioned）
        throughput_mode = fetch_efs_throughput_mode()
        logger.info(f'throughput_mode: {throughput_mode}')

        # スループットモードの切り替え
        change_throughput_mode(burst_credit_balance, throughput_mode)

    except Exception as e:
        if e.response['Error']['Code'] == 'TooManyRequests':
            # スループットモードの前回の変更から24時間経たないと変更できない。
            # この時TooManyRequestsエラーになるが、問題ないためINFOとして扱う
            logger.info('Can not be changed until 24 hours have passed since the last change')
        else:
            logger.error(e)
    finally:
        logger.info('end lambda_handler')


def fetch_burst_credit_balance():
    """CloudWatchからBurstCreditBalanceの残量を取得する

    Returns:
        str: バーストクレジットの残量
    """

    client = boto3.client('cloudwatch', region_name=REGION)

    response = client.get_metric_statistics(
        Namespace='AWS/EFS',
        MetricName='BurstCreditBalance',
        Dimensions=[
            {
                'Name': 'FileSystemId',
                'Value': FILESYSTEM_ID
            }
        ],
        StartTime=datetime.datetime.now() - datetime.timedelta(seconds=300),
        EndTime=datetime.datetime.now(),
        Period=300,
        Statistics=['Average'],
    )

    return response['Datapoints'][0]['Average']


def fetch_efs_throughput_mode():
    """EFSのスループットモードを取得する（bursting か provisioned）

    Returns:
        str: EFSのスループットモード
    """

    response = EFS_CLIENT.describe_file_systems(
        FileSystemId=FILESYSTEM_ID
    )
    return response['FileSystems'][0]['ThroughputMode']


def change_throughput_mode(burst_credit_balance, throughput_mode):
    """現在のスループットモードとバーストクレジットの条件によってスループットモードを切り替える

    Args:
        burst_credit_balance (float): バーストクレジットの残量
        throughput_mode (str): EFSのスループットモード
    """
    # スループットモードをバーストからプロビジョンドに切り替える
    if throughput_mode == 'bursting' and burst_credit_balance < LOWER_THRESHOLD:
        logger.info('changemode_burst_to_provisioned')
        EFS_CLIENT.update_file_system(
            FileSystemId=FILESYSTEM_ID,
            ThroughputMode='provisioned',
            ProvisionedThroughputInMibps=100
        )
    # スループットモードをプロビジョンドからバーストに切り替える
    elif throughput_mode == 'provisioned' and burst_credit_balance > UPPER_THRESHOLD:
        logger.info('changemode_provisioned_to_burst')
        EFS_CLIENT.update_file_system(
            FileSystemId=FILESYSTEM_ID,
            ThroughputMode='bursting'
        )
