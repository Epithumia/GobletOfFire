#!/bin/bash

echo "export LD_LIBRARY_PATH=/home/vagrant/coin-cbc/lib" >> /home/vagrant/.bashrc
echo "#!/bin/bash" > /home/vagrant/run.sh
echo "cd /vagrant/TriWizard" >> /home/vagrant/run.sh
echo "/vagrant/bin/python -W ignore /vagrant/TriWizard/tournament.py -v -s" >> /home/vagrant/run.sh
chmod +x /home/vagrant/run.sh
chown vagrant:vagrant /home/vagrant/run.sh
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install git subversion python-dev libldap2-dev libsasl2-dev libssl-dev python-pip gfortran -y
svn checkout https://projects.coin-or.org/svn/Cbc/releases/2.9.9 coin-cbc
cd /home/vagrant/coin-cbc
./configure -C
make && make install
sudo pip install virtualenv
cd /vagrant/
/usr/local/bin/virtualenv ./ --always-copy
export COIN_INSTALL_DIR=/home/vagrant/coin-cbc/
bin/pip install sqlalchemy zope.sqlalchemy transaction numpy==1.12.1
bin/pip install cylp
