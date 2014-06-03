#!/bin/bash -ex

ADMIN_EMAIL=uckelman@nomic.net
HOSTNAME=nym
DOMAIN=dmnes.org

FILES_SRC=/root/files

chown -R root.root $FILES_SRC

# get current
yum install -y yum-plugin-fastestmirror
yum update -y

# packages needed to make system use bearable
yum install -y screen vim htop iotop iftop mlocate rpmreaper

# install etckeeper
yum install -y etckeeper
etckeeper init
git config --global user.email root@dmnes.org
git config --global user.name root
etckeeper commit 'Initial commit.'

sed -i -e '/^#AVOID_DAILY_AUTOCOMMITS=1/{s/^#//}' /etc/etckeeper/etckeeper.conf
sed -i -e '/^#AVOID_COMMIT_BEFORE_INSTALL=1/{s/^#//}' /etc/etckeeper/etckeeper.conf
etckeeper commit 'Never autocommit with etckeeper.'

# set up a user account for me
useradd uckelman
etckeeper commit 'Added uckelman user account.' 

# set up root
cp $FILES_SRC/root/{.vimrc,.bashrc} /root

# set up regular static IP networking
yum install -y system-config-network
sed -i -e '/NM_CONTROLLED/d' /etc/sysconfig/network-scripts/ifcfg-eth0
systemctl enable network.service
etckeeper commit 'Enabled networking.'

# set hostname
echo $HOSTNAME >/etc/hostname
etckeeper commit 'Set hostname.'

# set up ntp
yum install -y chrony
systemctl enable chronyd.service
systemctl start chronyd.service
etckeeper commit 'Set up NTP.'

# set timezone to UTC
timedatectl set-timezone UTC
etckeeper commit 'Set timezone to UTC.'

# set up sshd
cp $FILES_SRC/etc/ssh/* /etc/ssh
systemctl reload sshd.service
etckeeper commit 'Disabled password login via ssh.'

# remove crap we don't need
yum remove -y irda-utils nfs-utils pcsc-lite rpcbind wpa_supplicant NetworkManager NetworkManager-glib ntfsprogs ntfs-3g ModemManager-glib fprintd mdadm PackageKit realmd pam_krb5 avahi-autoipd smartmontools firewalld ssmtp

# set up firewall
yum install -y system-config-firewall-tui
cp $FILES_SRC/etc/sysconfig/{iptables,ip6tables,system-config-firewall} /etc/sysconfig
systemctl enable iptables.service
systemctl enable ip6tables.service
etckeeper commit 'Enabled iptables firewall.'

# turn on process accounting
systemctl enable psacct.service
etckeeper commit 'Enabled psacct.'

# install misc things
yum install -y logwatch setroubleshoot-server

# install postfix
yum install -y postfix postgrey
cp $FILES_SRC/etc/postfix/main.cf /etc/postfix
sed -i -e "/^myhostname =/{s/.*/myhostname = $HOSTNAME.$DOMAIN/}" /etc/postfix/main.cf
echo "root: $ADMIN_EMAIL" >>/etc/aliases
postalias /etc/aliases
systemctl enable postfix.service
systemctl enable postgrey.service
etckeeper commit 'Set up postfix.'

# install apache
yum install -y httpd mod_ssl python3-mod_wsgi
echo '
# Load vhost files in the "/etc/httpd/vhost.d" directory, if any.
IncludeOptional vhost.d/*.conf' >>/etc/httpd/conf/httpd.conf
mkdir /etc/httpd/vhost.d
cp $FILES_SRC/etc/httpd/vhost.d/* /etc/httpd/vhost.d
cp $FILES_SRC/etc/httpd/conf.d/* /etc/httpd/conf.d/
systemctl enable httpd.service
etckeeper commit 'Set up apache.'

# install packages needed by dmnes editor
yum install -y python3-flask python3-lxml

useradd -s /sbin/nologin editor 
sudo -u editor ssh-keygen -t rsa -N "" -f /home/editor/.ssh/id_rsa

chmod a+x /home/editor

# TODO: copy editor files to /home/editor here

chown -R editor.editor /home/editor

# cleanup
restorecon -r -v /etc
/etc/cron.daily/mlocate
echo 'Remember:

  * Reboot: shutdown -r now
  * Install editor public SSH key as deploy key on GitHub.
  * SSH to GitHub once as editor user: sudo -u editor ssh git@github.com
'
