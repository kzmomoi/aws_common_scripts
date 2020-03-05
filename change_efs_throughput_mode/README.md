# change_efs_throughput_mode

## Summary

EFSのスループットモードを自動で切り替えるスクリプト。  
AWS Lambdaでの実行を想定。

## Description

1. BurstCreditBalanceの残量を取得
2. EFSの現在のスループットモードを取得
3. 1,2の結果からスループットモードの切り替える
    * バーストモードかつ、クレジット残量がLOWER_THRESHOLD未満の時、スループットモードに切り替え
    * スループットモードかつ、クレジット残量がUPPER_THRESHOLDを超えた時、バーストモードに切り替え

## Usage

1. FILESYSTEM_IDに対象のEFSのIDを記載する
2. LOWER_THRESHOLD,UPPER_THRESHOLDに閾値を記載する
3. AWSのLambda関数を作成し、Cloudwatch Eventなどで定期実行されるよう設定する

## Requirements

Python 3.7