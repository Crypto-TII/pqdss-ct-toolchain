#!/bin/bash
set -o errexit

### current state: 2021-09-16, should be compatible with Ubuntu focal, needs Xenial for some older llvm dependencies

#INSTALL_DIR=$(pwd)
INSTALL_DIR=/tmp/pqdss-toolchain
#BOOGIE_DIR="$INSTALL_DIR/boogie"
BAM_DIR="$INSTALL_DIR/bam-bam-boogieman"
#CORRAL_DIR="$INSTALL_DIR/corral"
SMACK_DIR="$INSTALL_DIR/smack"
#CTVERIF_DIR="$INSTALL_DIR/ctverif"
#GEM_HOME="$HOME/.gem"

SMACK_VERSION="1.9.3"
BAM_VERSION="1.0.10"
USER="user"

### if you dislike sudo, you can replace this with pleaser, (OpenBSD) doas, plain old "su - root $CMD" or something else
SUDO_IS="sudo"

DEPENDENCIES="git wget curl build-essential cmake software-properties-common lsb-release apt-transport-https ca-certificates"

function get-platform-codename {
        case $(lsb_release -c | tr -d '[ \t]' | tr 'A-Z' 'a-z' | awk -F: '{print $2;}') in
                "focal")
                        echo "Ubuntu focal"
                        ### although we know it is bionic, we really need additional xenial repos and packages for llvm
                        # CODENAME="xenial"
                        # DISTROTOOLCHAINPART="xenial-"
                        DEPENDENCIES="python-is-python2 ${DEPENDENCIES}"
                        ${SUDO_IS} add-apt-repository -y "deb http://us.archive.ubuntu.com/ubuntu/ xenial main"
                        # need this for libpng12
                        ${SUDO_IS} add-apt-repository -y ppa:linuxuprising/libpng12
                        ;;
                *)
                        echo "Platform not supported, let's see if it works..."
                        ;;
        esac
}



get-platform-codename
${SUDO_IS} apt update && ${SUDO_IS} apt upgrade -y
${SUDO_IS} apt install -y $DEPENDENCIES

 Install SMACK and its dependencies (Boogie, Corral, LLVM and Z3)
wget --no-verbose -O - http://apt.llvm.org/llvm-snapshot.gpg.key | ${SUDO_IS} apt-key add -
git clone https://github.com/smackers/smack.git -b "v$SMACK_VERSION"
# Patch the build script so that it think we are on xenial and doesn't freak out
patch -p1 smack/bin/build.sh < build_smack.patch

#git clone https://github.com/smackers/smack.git
## PATCH smack v2.8.0
## patch -p1 smack/bin/build.sh < build_smack.patch
#echo "+++++++++++++CWD+++++++++++++"
#pwd
#echo "+++++++++++++Content of CWD+++++++++++++"
##ls
cd smack
sudo ./bin/build.sh
cd ..
# echo "source $(pwd)/smack.environment" >> ~/.bashrc
echo "source smack.environment" >> ~/.bashrc

# Patch and install bam-bam-boogiman, using rvm to do it with ruby-2.5.5
curl -sSL https://rvm.io/mpapis.asc | sudo gpg --import -
curl -sSL https://rvm.io/pkuczynski.asc | sudo gpg --import -
curl -sSL https://get.rvm.io | sudo bash -s stable
[[ -f ${HOME}/.rvm/scripts/rvm ]] && rvm_sources="${HOME}/.rvm/scripts/rvm" || rvm_sources="/usr/local/rvm/scripts/rvm"
# source "$rvm_sources"
# source /etc/profile.d/rvm.sh

useradd -m user && \
    echo user:user | chpasswd && \
    cp /etc/sudoers /etc/sudoers.bak && \
    echo 'user  ALL=(root) NOPASSWD: ALL' >> /etc/sudoers


# Add the current directory to `/home/user/smack`
# ADD --chown=user . $PQDSSDIR

echo "source $rvm_sources" >> ~/.bashrc
echo "source /etc/profile.d/rvm.sh" >> ~/.bashrc
sudo usermod -a -G rvm "$USER"

touch "$INSTALL_DIR/.rvm_installed"
echo "Please login again so that the group change takes effect, then run the script again."

echo "Welcome back, let's finish this installation!"
source /etc/profile.d/rvm.sh
rvm install ruby-2.5.5
rvm use ruby-2.5.5
git clone https://www.github.com/michael-emmi/bam-bam-boogieman -b v$BAM_VERSION
patch -p1 bam-bam-boogieman/lib/bpl/passes/security/shadowing.rb < build_bam.patch
cd bam-bam-boogieman/
# NEW ADD
gem install colorize -v 0.8.1
# NEW ADD:  END
gem build ./bam-bam-boogieman.gemspec
gem install ./bam-bam-boogieman-$BAM_VERSION.gem
cd ..

# Install ctverif
sudo apt install -y npm
sudo npm i -g ctverif
git clone https://github.com/michael-emmi/ctverif.git
cp ctverif/resources/include/ctverif.h ~/
rm "$INSTALL_DIR/.rvm_installed"

echo -e "\nInstallation done!\nUse as \n$ctverif --entry-point foo bar.c"
