
if [[ -z "$VERSION" || -z "$USER" ]]; then
    echo "Usage: USER=username VERSION=version-name  prepare_appserver.sh"
    exit 1
fi

# create the main Appserver directory
cd /home/$USER
mkdir appserver-$VERSION
cd appserver-$VERSION

# Clone worker Git
git clone https://github.com/ufal/mtmonkey.git git

# Prepare subdirectories
mkdir -p config logs
ln -s git/appserver/src appserver
ln -s git/scripts scripts

# copy default config
cp git/config-example/{appserver.cfg} config

