#!/usr/bin/env bash

PROG=$(basename $0)
CWD=$(cd $(dirname $0) && pwd)

# OS globals
#
OS=$(uname -s)
OS_ID=""
OS_ID_Lower=""
OS_Release=""
OS_Release_Major=""
OS_Release_Minor=""
OS_Release_Minor=""

# Return values
typeset -i STATUS_PASSED=0
typeset -i STATUS_FAILED=1
typeset -i STATUS_NA=42
typeset -i STATUS_WARNING=99

# Flags
DEBUG=false
SILENT=false

PRODUCT_NAME="ArcGIS Enterprise on Kubernetes"

fail()
{
  echo ""
  echo "ERROR: $1"
  echo ""
  exit $STATUS_FAILED
}

echo_d()
{
  [ "$DEBUG" = true ] && echo "$1"
}

print_msg()
{
  [ "$SILENT" = true ] && return

  local fmt="$1"
  shift

  printf "$fmt" "$@"
}

set_globals()
{
  OS_ID=$(get_linux_distro)
  OS_ID_Lower=$(echo $OS_ID | tr "[A-Z]" "[a-z]")
  OS_Release=$(get_os_version)
  OS_Release_Major=$(echo $OS_Release | cut -d"." -f1)
  OS_Release_Minor=$(echo $OS_Release | cut -d"." -f2)
  OS_Release_Minor=${OS_Release_Minor:-0}  # default to 0 if no patch level defined
}

get_linux_distro()
{
  #if [ "$HAS_LSB" = "true" ]; then
  #  echo "$(lsb_release -si)"
  #  return
  #fi

  DISTRO="Unknown"

  if [ "$(uname -s)" = "Linux" ]; then
    #
    # CENTOS
    #
    if [ -f /etc/centos-release ]; then
      DISTRO="CentOS"
    #
    # ORACLE
    #
    elif [ -f /etc/oracle-release ]; then
      DISTRO="OracleServer"
    #
    # SCIENTIFIC
    #
    elif [ -f /etc/scientific-release ]; then
      DISTRO="Scientific"
    #
    # ALMALINUX
    #
    elif [ -f /etc/almalinux-release ]; then
      DISTRO="AlmaLinux"
    #
    # ROCKY
    #
    elif [ -f /etc/rocky-release ]; then
      DISTRO="Rocky"
    #
    # REDHAT
    #
    elif [ -f /etc/redhat-release ]; then
      if [ "$(grep -i 'Red Hat' /etc/redhat-release)" != "" ]; then
        DISTRO="RedHatEnterpriseServer"
      elif [ "$(grep -i 'CentOS' /etc/redhat-release)" != "" ]; then
        DISTRO="CentOS"
      elif [ "$(grep -i 'Scientific' /etc/redhat-release)" != "" ]; then
        DISTRO="Scientific"
      elif [ "$(grep -i 'Oracle' /etc/redhat-release)" != "" ]; then
        DISTRO="OracleServer"
      elif [ "$(grep -i 'Rocky' /etc/redhat-release)" != "" ]; then
        DISTRO="Rocky"
      elif [ "$(grep -i 'AlmaLinux' /etc/redhat-release)" != "" ]; then
        DISTRO="AlmaLinux"
      fi
    #
    # SUSE 11
    #
    elif [ -f /etc/SuSE-release ]; then
      DISTRO="SUSE LINUX"
    #
    # UBUNTU & SUSE12+
    #
    elif [ -f /etc/os-release ]; then
      if [ "$(grep -i 'Ubuntu' /etc/os-release)" != "" ]; then
        DISTRO="Ubuntu"
      fi
      if [ "$(grep -i 'SUSE' /etc/os-release)" != "" ]; then
        DISTRO="SUSE LINUX"
      fi
    fi
  else
    echo "Unsupported OS"
    return
  fi

  echo "$DISTRO"
}

get_os_version()
{
  #if [ "$HAS_LSB" = "true" ]; then
  #  echo "$(lsb_release -sr)"
  #  return
  #fi

  VERSION="Unknown"

  if [ "$(uname -s)" = "Linux" ]; then
    #
    # CENTOS
    #
    if [ -f /etc/centos-release ]; then
      VERSION=$(cat /etc/centos-release | sed s/.*release\ // | sed s/\ .*//)
    #
    # ORACLE
    #
    elif [ -f /etc/oracle-release ]; then
      VERSION=$(cat /etc/oracle-release | sed s/.*release\ // | sed s/\ .*//)
    #
    # SCIENTIFIC
    #
    elif [ -f /etc/scientific-release ]; then
      VERSION=$(cat /etc/scientific-release | sed s/.*release\ // | sed s/\ .*//)
    #
    # ALMALINUX
    #
    elif [ -f /etc/almalinux-release ]; then
      VERSION=$(cat /etc/almalinux-release | sed s/.*release\ // | sed s/\ .*//)
    #
    # ROCKY
    #
    elif [ -f /etc/rocky-release ]; then
      VERSION=$(cat /etc/rocky-release | sed s/.*release\ // | sed s/\ .*//)
    #
    # REDHAT
    #
    elif [ -f /etc/redhat-release ]; then
      VERSION=$(cat /etc/redhat-release | sed s/.*release\ // | sed s/\ .*//)
    #
    # SUSE 11
    #
    elif [ -f /etc/SuSE-release ]; then
      VERSION=$(cat /etc/SuSE-release | grep VERSION | awk '{print $NF}')
      hasPatchLevel=$(echo $VERSION | grep "\.")
      if [ -z "$hasPatchLevel" ]; then
        level=$(cat /etc/SuSE-release | grep PATCHLEVEL | awk '{print $NF}')
        VERSION=${VERSION}.${level}
      fi
    #
    # UBUNTU & SUSE 12+
    #
    elif [ -f /etc/os-release ]; then
      VERSION=$(cat /etc/os-release | grep VERSION_ID | cut -d= -f2 | sed 's/\"//g')
    fi
  else
    echo "Unsupported OS"
    return
  fi

  echo "$VERSION"
}


os_warning()
{
  # Unsupported OS Major version
  print_msg "Unsupported %s version detected (%s). Check the %s System Requirements for supported Linux OS versions.\n" "$1" "$OS_Release" "$PRODUCT_NAME"
  exit $STATUS_WARNING
}

os_check()
{
  case ${OS_ID_Lower} in
    centos)
      [ $OS_Release_Major -lt 8 ] && os_warning "CentOS Linux"
      ;;
    almalinux)
      [ $OS_Release_Major -lt 9 ] && os_warning "AlmaLinux"
      ;;
    rocky)
      [ $OS_Release_Major -lt 8 ] && os_warning "Rocky Linux"
      ;;
    oracleserver)
      [ $OS_Release_Major -lt 8 ] && os_warning "Oracle Linux"
      ;;
    scientific)
      [ $OS_Release_Major -lt 8 ] && os_warning "Scientific Linux"
      ;;
    redhatenterprise*)
      [ $OS_Release_Major -lt 8 ] && os_warning "RedHat"
      ;;
    suse*)
      [ $OS_Release_Major -lt 15 ] && os_warning "SuSE"
      ;;
    ubuntu*)
      [ $OS_Release_Major -lt 20 ] && os_warning "Ubuntu"
      ;;
    *)
      print_msg "Unsupported Linux distribution. Check the %s System Requirements for supported Linux distributions.\n" "$PRODUCT_NAME"
      exit $STATUS_WARNING
      ;;
  esac

  exit $STATUS_PASSED
}

platform_check()
{
  if [ "$OS" != "Linux" ]; then
    if [ "$OS" = "Darwin" ]; then
      print_msg "MacOS is not a supported operating system. Check the %s System Requirements for supported platforms.\n" "$PRODUCT_NAME"
    else
      print_msg "Unknown operating system.\n"
    fi
    exit $STATUS_WARNING
  fi
}

process_args()
{
  while getopts "hds?" opt
  do
    case "$opt" in
      h)
        usage
        ;;
      d)
        DEBUG=true
        ;;
      s)
        SILENT=true
        ;;
      *)
        echo "-- What? --"
        usage
        ;;
    esac
  done
}

Main()
{
  process_args "$@"
  platform_check
  set_globals

  echo_d "OS_ID=$OS_ID"
  echo_d "OS_ID_Lower=$OS_ID_Lower"
  echo_d "OS_Release=$OS_Release"
  echo_d "OS_Release_Major=$OS_Release_Major"
  echo_d "OS_Release_Minor=$OS_Release_Minor"

  os_check
}

Main "$@"


