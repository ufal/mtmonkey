#
# Configuring the remote share (where models & Moses are stored)
# - this may be a local/NFS path or a path on a remote machine
#   (use SSH keys to avoid login prompt!)

export REMOTE=/mnt/share
# export LOGIN=user@host

if [[ -n "$LOGIN" ]]; then
    LOGIN="-e ssh $LOGIN:" # prepare parameter for rsync
fi

