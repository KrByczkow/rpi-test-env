#!/bin/bash

shopt -s globstar
shopt -s nullglob

NBD_PREFIX=${1:-/dev/nbd}
NFS_ROOT=${2:-/nfs}
SLAVE_IMG=${3:-/slave.img}
IP_PREFIX=${4:-172.21.18}

modprobe nbd

# Make sure that qemu-nbd executable is present, and that "nfs-kernel-server" can be used to successfully start NFS server
apt install -y qemu-utils nbd nfs-kernel-server

systemctl enable --now nfs-kernel-server

i=0
ip=49
for DIR in "${NFS_ROOT}"/slave*; do
    NBD_DEVICE="${NBD_PREFIX}$i"

    i=$(( i + 1 ))
    ip=$(( ip + 1 ))

    qemu-nbd --snapshot --connect "$NBD_DEVICE" "$SLAVE_IMG"

    mount "${NBD_DEVICE}p2" "$DIR"
    mount "${NBD_DEVICE}p1" "/tftpboot/${IP_PREFIX}.${ip}"

    echo "console=serial0,115200 console=tty1 root=/dev/nfs nfsroot=172.21.18.1:/nfs/slave$i,vers=3 rw ip=dhcp rootwait elevator=deadline" > "/tftpboot/${IP_PREFIX}.${ip}/cmdline.txt"

    index=$(( i - 1 ))
    echo -e "proc /proc proc defaults 0 0\n172.21.18.1:/tftpboot/${IP_PREFIX}.${ip} /boot nfs defaults,vers=3 0 0\n" > "/nfs/slave${index}/etc/fstab"
done

systemctl enable rpcbind
systemctl restart rpcbind nfs-kernel-server