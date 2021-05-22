# This script will install the turntable software and any required prerequisites.
cd ~
echo -e ''
echo -e '\033[32mTurntable [Installation Script] \033[0m'
echo -e '\033[32m-------------------------------------------------------------------------- \033[0m'
echo -e ''
echo -e '\033[93mUpdating package repositories... \033[0m'
sudo apt update

echo ''
echo -e '\033[93mInstalling prerequisites... \033[0m'
sudo apt install -y git python3 python3-pip python3-pil python3-numpy ttf-dejavu
sudo pip3 install requests adafruit-circuitpython-motorkit adafruit-circuitpython-rgb-display

echo ''
echo -e '\033[93mInstalling Turntable... \033[0m'
cd ~
sudo rm -Rf ~/turntable
sudo git clone https://github.com/eat-sleep-code/turntable
sudo mkdir -p ~/turntable/logs
sudo chown -R $USER:$USER turntable
cd turntable
sudo chmod +x *.py

echo ''
echo -e '\033[93mCreating Service... \033[0m'
sudo mv turntable.service /etc/systemd/system/turntable.service
sudo chown root:root /etc/systemd/system/turntable.service
sudo chmod +x *.sh 
echo 'Please see the README file for more information on configuring the service.'

cd ~
echo ''
echo -e '\033[93mSetting up alias... \033[0m'
sudo touch ~/.bash_aliases
sudo sed -i '/\b\(function turntable\)\b/d' ~/.bash_aliases
sudo sed -i '$ a function turntable { sudo python3 ~/turntable/turntable.py "$@"; }' ~/.bash_aliases
echo -e 'You may use \e[1mturntable <options>\e[0m to launch the program.'



echo ''
echo -e '\033[32m-------------------------------------------------------------------------- \033[0m'
echo -e '\033[32mInstallation completed. \033[0m'
echo ''
sudo rm install-turntable.sh
bash
