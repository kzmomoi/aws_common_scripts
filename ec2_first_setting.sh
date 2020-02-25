#!/bin/sh
# ユーザ作成、sudoの設定、タイムゾーンの設定を行う.

# ユーザ名と公開鍵を入力
echo '### ユーザ作成 ###'
read -p '作成するユーザ名を入力してください: ' U
read -p '作成するユーザの公開鍵を入力してください: ' K
# ユーザ作成
sudo useradd -G wheel $U
sudo mkdir /home/$U/.ssh
sudo touch /home/$U/.ssh/authorized_keys
echo $K | sudo tee /home/$U/.ssh/authorized_keys > /dev/null
sudo chmod 700 /home/$U/.ssh
sudo chmod 600 /home/$U/.ssh/authorized_keys
sudo chown -R $U:$U /home/$U/.ssh
echo 'ユーザを作成しました'
echo '/etc/passwd を確認'
cat /etc/passwd | grep $U
echo -e

# wheelグループの所属のユーザがsudoする時、パスワード入力を不要とする設定
echo '### wheelグループの所属のユーザがsudoする時、パスワード入力を不要とする設定 ###'
sudo touch /etc/sudoers.d/wheel
echo '%wheel ALL=(ALL) NOPASSWD:ALL' | sudo tee /etc/sudoers.d/wheel > /dev/null
sudo cat /etc/sudoers.d/wheel
echo -e

echo '### タイムゾーンをAsia/Tokyoに変更 ###'
sudo timedatectl set-timezone Asia/Tokyo
echo 'タイムゾーン変更結果'
timedatectl