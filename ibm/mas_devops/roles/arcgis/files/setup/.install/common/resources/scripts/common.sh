
# common.sh
#
# This script should not be run.  It is sourced by the setup
# scripts to provide common functions shared by these scripts
#
SCRIPT_VERSION="0.1.5"

# Base 10
ONE_KB=1000
ONE_MB=$(( $ONE_KB * $ONE_KB ))
ONE_GB=$(( $ONE_MB * $ONE_KB ))
ONE_TB=$(( $ONE_GB * $ONE_KB ))

# Base 2
ONE_KIB=1024
ONE_MIB=$(( $ONE_KIB * $ONE_KIB ))
ONE_GIB=$(( $ONE_MIB * $ONE_KIB ))
ONE_TIB=$(( $ONE_GIB * $ONE_KIB ))

# For checking if the terminal supports color and ANSI escape sequences
HAS_TTY=true
tty -s || HAS_TTY=false

# --------------------------------------------------------------
# GUI Stuff
# --------------------------------------------------------------

BLACK=0
RED=1
GREEN=2
YELLOW=3
BLUE=4
MAGENTA=5
CYAN=6
WHITE=7
GREY=8

if [ "$HAS_TTY" = true ]; then
  fg_black=$(tput setaf $BLACK)
  fg_red=$(tput setaf $RED)
  fg_green=$(tput setaf $GREEN)
  fg_yellow=$(tput setaf $YELLOW)
  fg_blue=$(tput setaf $BLUE)
  fg_magenta=$(tput setaf $MAGENTA)
  fg_cyan=$(tput setaf $CYAN)
  fg_white=$(tput setaf $WHITE)
  fg_grey=$(tput setaf $GREY)
  fg_bold=$(tput bold)
  txt_reset=$(tput sgr0)
else
  fg_black=""
  fg_red=""
  fg_green=""
  fg_yellow=""
  fg_blue=""
  fg_magenta=""
  fg_cyan=""
  fg_white=""
  fg_grey=""
  fg_bold=""
  txt_reset=""
fi

HAS_SYMBOLS=true

loc=$(echo "$LANG" | tr '[A-Z]' '[a-z]')
[[ $loc =~ utf-8 ]] || HAS_SYMBOLS=false

BULLET_SMALL="\xe2\x88\x99"
BULLET_LARGE="\xe2\x97\x8f"
CHECK_NORMAL="\xe2\x9c\x93"
CHECK_BOLD="\xe2\x9c\x94"
FAILED_NORMAL="\xe2\x9c\x95"
FAILED_BOLD="\xe2\x9c\x96"

if [ "$HAS_SYMBOLS" = false ]; then
  BULLET_SMALL="*"
  BULLET_LARGE="*"
  CHECK_NORMAL="OK"
  CHECK_BOLD="OK"
  FAILED_NORMAL="FAILED"
  FAILED_BOLD="FAILED"
fi

has_tty()
{
  [ "$HAS_TTY" = true ]
}

fg()
{
  [ "$HAS_TTY" = true ] && tput setaf $1
}
bg()
{
  [ "$HAS_TTY" = true ] && tput setab $1
}

bullet()
{
  echo -en "$BULLET_SMALL"
}
bullet_large()
{
  echo -en "$BULLET_LARGE"
}

check()
{
  echo -en "$CHECK_NORMAL"
}
check_bold()
{
  echo -en "$CHECK_BOLD"
}

failed()
{
  echo -en "$FAILED_NORMAL"
}
failed_bold()
{
  echo -en "$FAILED_BOLD"
}

draw_line()
{
  local _HLINE="─"

  if [ "$HAS_TTY" = true ]; then
    for i in $(seq 1 79) ; do echo -ne $_HLINE; done
    echo ""
  else
    printf -v line "%*s" 79 && echo "${line// /-}"
  fi
}

draw_ellipses()
{
  local width=$1
  printf -v line "%*s" $width && printf "${line// /.}"
}

print_center()
{
  local text="$1"
  local max_width="$2"

  [ -z "$2" ] && max_width="79"

  local width=${#text}
  local start_col=$(( ($max_width - $width) / 2 ))

  printf "%${start_col}s%s\n" '' "$text"
}

text_bold()
{
  $(has_tty) && tput bold
}

text_reverse()
{
  $(has_tty) && tput rev
}

text_normal()
{
  $(has_tty) && tput sgr0
}

header()
{
  draw_line
  text_bold
  echo "$1"
  text_normal
  draw_line
}

success()
{
  $(has_tty) && {
    echo "[${fg_green}SUCCESS${txt_reset}]"
  } || {
    echo "SUCCESS"
  }
}

note()
{
  echo ""
  $(has_tty) && {
    printf "${fg_cyan}NOTE:${txt_reset}"
  } || {
    printf "NOTE:"
  }
  printf " %s\n" "$1" | fmt -w 79
  echo ""
}

warning()
{
  echo ""
  $(has_tty) && {
    printf "${fg_yellow}WARNING:${txt_reset}"
  } || {
    printf "WARNING:"
  }
  printf " %s\n" "$1" | fmt -w 79
  echo ""
}

alert()
{
  echo ""
  $(has_tty) && {
    printf "${fg_magenta}ALERT:${txt_reset}"
  } || {
    printf "ALERT:"
  }
  printf " %s\n" "$1" | fmt -w 79
  echo ""
}

ccat()
{
  cat "$1" | grep -Ev "^#|^$" # Cat file and strip blanks and comments
}

# --------------------------------------------------------------
# User question prompts
# --------------------------------------------------------------
error_msg()
{
  local msg="$1"
  $(has_tty) && {
    printf "    - ${fg_red}%s${txt_reset}" "$msg"
  } || {
    printf "    - %s" "$msg"
  }
  printf "\n"
  sleep 1
}

warning_msg()
{
  local msg="$1"
  $(has_tty) && {
    printf "    - ${fg_yellow}%s${txt_reset}" "$msg"
  } || {
    printf "    - %s" "$msg"
  }
  printf "\n"
  sleep 1
}

error_prompt()
{
  local msg="$1"
  $(has_tty) && {
    printf "    - ${fg_red}%s${txt_reset}" "$msg"
  } || {
    printf "    - %s" "$msg"
  }
}

section_header()
{
  local msg="$1"
  local color="${fg_blue}"

  [ -n "$2" ] && color="$2"

  echo ""
  draw_line
  text_bold
  printf "${color}%s${txt_reset}\n" "$msg"
  text_normal
}

section_description()
{
  local msg="$1"

  echo ""
  text_normal
  printf "%s" "$msg" | fmt -w 79
  draw_line  
}

section_prompt()
{
  local msg="$1"

  echo ""
  echo "$msg" | fmt | sed 's/^/    /g'
  echo ""
}

prompt()
{
  local msg="$1"
  local default="$2"

  if [ -n "$default" ]; then
    printf "    - %s (default=${fg_bold}%s${txt_reset}) : " "$msg" "$default"
  else
    printf "    - %s : " "$msg"
  fi
}


# --------------------------------------------------------------
# Misc
# --------------------------------------------------------------
echo_dbg()
{
  [ "$DEBUG" = true ] && echo "$1"
}

file_exists()
{
  [ -f "$1" ]
}

is_yes()
{
  local answer=$(echo $1 | tr '[A-Z]' '[a-z]')
  case "$answer" in
    y|yes|ok|true|1) true ;;
    *) false ;;
  esac
}

is_no()
{
  local answer=$(echo $1 | tr '[A-Z]' '[a-z]')
  case "$answer" in
    n|no|nope|false|0) true ;;
    *) false ;;
  esac
}

str_contains()
{
  local string="$1"
  local tofind="$2"

  [[ -n "$tofind" ]] && [[ $string =~ $tofind ]]
}

has_spaces()
{
  local string="$1"

  local re="[[:space:]]+"
  [[ $string =~ $re ]]
}

has_digits()
{
  local num="$1"
  [[ $num =~ [[:digit:]] ]]
}

has_digits_only()
{
  local num="$1"
  [[ $num =~ ^[0-9]+$ ]]
}

starts_with()
{
  local string="$1"
  local match="$2"

  [[ $string == $match* ]]
}

clear_line()
{
  # Erase prompt in tty mode
  $(has_tty) && {
    tput cuu1
    tput el
    echo -e "\r"
  }
}

press_a_key()
{
  [ "$INTERACTIVE" = false ] && return
  echo ""
  echo -n "$1"
  read -s -n 1 key

  clear_line
}

edit_in_file()
{
  local sed_string="$1"
  local file="$2"

  [ ! -f "$file" ] && return

  # MacOSX's version of sed's -i flag requires a backup extension
  # argument so just supply an empty string.
  #
  if [ "$(uname -s)" = "Darwin" ]; then
    sed -i '' "$sed_string" "${file}"
  else
    sed -i "$sed_string" "${file}"
  fi
}

# Handle base64 -d flag on MacOS
decode64()
{
  local decode_flag="-d"

  [ "$(uname -s)" = "Darwin" ] && decode_flag="-D"

  echo -n "$1" | base64 $decode_flag
}

# Preserve sudo user's ownership during file operations (bash-only)
safe_touch()
{
  touch "$1"
  res=$?
  if [ $res -eq 0 ]; then
    [ -n "${SUDO_USER}" ] && chown "${SUDO_USER}:${SUDO_GID}" "$1"
  fi
  return $res
}

safe_mkdir()
{
  mkdir "$@"
  res=$?
  if [ $res -eq 0 ]; then
    [ -n "${SUDO_USER}" ] && chown -R "${SUDO_USER}:${SUDO_GID}" "${@: -1}"
  fi
  return $res
}

safe_cp()
{
  cp "$@"
  res=$?
  if [ $res -eq 0 ]; then
    [ -n "${SUDO_USER}" ] && chown -R "${SUDO_USER}:${SUDO_GID}" "${@: -1}"
  fi
  return $res
}

safe_ln()
{
  ln "$@"
  res=$?
  if [ $res -eq 0 ]; then
    [ -n "${SUDO_USER}" ] && chown -R "${SUDO_USER}:${SUDO_GID}" "${@: -1}"
  fi
  return $res
}


# Number conversions
kb_to_gb()
{
  local kb="$1"

  ret=$(awk -v k="$kb" -v m="$ONE_MB" 'BEGIN { printf "%.1fG", k / m }')
  echo "$ret"
}

secs_to_min_sec()
{
  local secs="$1"
  printf "%02dm:%02ds" "$(($secs%3600/60))" "$(($secs%60))"
}

secs_to_hour_min_sec()
{
  local secs="$1"
  printf "%02dh:%02dm:%02ds" "$(($secs/3600))" "$(($secs%3600/60))" "$(($secs%60))"
}

# https://www.linuxjournal.com/content/validating-ip-address-bash-script
is_valid_ip()
{
    local  ip=$1
    local  stat=1

    if [[ $ip =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        OIFS=$IFS
        IFS='.'
        ip=($ip)
        IFS=$OIFS
        [[ ${ip[0]} -le 255 && ${ip[1]} -le 255 \
            && ${ip[2]} -le 255 && ${ip[3]} -le 255 ]]
        stat=$?
    fi
    return $stat
}

# https://stackoverflow.com/a/26850032
is_valid_fqdn()
{
  local fqdn="$1"
  local res=""

  # strip any port number
  fqdn=$(echo ${fqdn} | cut -d: -f1)

  if [ "$(uname -s)" = "Darwin" ]; then
    res=$(echo $fqdn | perl -lne 'print $1 if /(?=^.{4,253}$)(^(?:[a-zA-Z0-9](?:(?:[a-zA-Z0-9\-]){0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$)/')
  else
    res=$(echo $fqdn | grep -P '(?=^.{4,253}$)(^(?:[a-zA-Z0-9](?:(?:[a-zA-Z0-9\-]){0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$)')
  fi
  [ -n "$res" ]
}

is_internal_deployment()
{
  [[ $1 =~ esri.com ]]
}

mask()
{
  mask_command "$@"
}

mask_command()
{
  local command="$1"
  local mask="$2"

  if [ -z "$mask" ]; then
    echo "${command}"
    return
  fi

  echo "${command}" | sed "s^${mask}^\*\*\*\*\*\*^g"
}

encode_base64()
{
  local str="$1"

  if [ "$(uname -s)" = "Darwin" ]; then
    echo -n "$str" | base64
  else
    echo -n "$str" | base64 --wrap=0
  fi
}

decode_base64()
{
  local str="$1"
  local res=""

  if [ "$(uname -s)" = "Darwin" ]; then
    res=$(echo -n "$str" | base64 -D)
  else
    res=$(echo -n "$str" | base64 -d)
  fi
  echo -n "$res"
}

can_encrypt_aes256_string()
{
  local str="$1"
  local keyfile="$2"

  echo -n "$str" | openssl enc -A -e -aes256 -pbkdf2 -pass file:"${keyfile}" -base64 > /dev/null 2>&1
  [ $? -eq 0 ]
}

can_decrypt_aes256_string()
{
  local str="$1"
  local keyfile="$2"

  echo "$str" | openssl enc -A -d -aes256 -pbkdf2 -pass file:"${keyfile}" -base64 > /dev/null 2>&1
  [ $? -eq 0 ]
}

get_encrypted_aes256_string()
{
  local str="$1"
  local keyfile="$2"
  local res=""

  res=$(echo -n "$str" | openssl enc -A -e -aes256 -pbkdf2 -pass file:"${keyfile}" -base64)
  echo -n "$res"
}

get_decrypted_aes256_string()
{
  local str="$1"
  local keyfile="$2"
  local res=""

  res=$(echo "$str" | openssl enc -A -d -aes256 -pbkdf2 -pass file:"${keyfile}" -base64)
  echo -n "$res"
}

adjust_repo_for_tag_internal()
{
  local tag="$1"
  local repo=""

  # If the tag is all digits use endeavour-daily
  if [[ $tag =~ ^[0-9]+$ ]]; then
    repo="endeavour-daily"
  # Version tag like 10.9.0 or 10.9.0-beta or any dotted version number
  elif [[ $tag =~ ^([[:alnum:]]+\.){1,} ]]; then
    repo="endeavour-release"
  else
    # Other common internal tags
    case "$tag" in
      *main*)
        repo="endeavour-ci"
        ;;
      dev-stable*)
        repo="endeavour-stable"
        ;;
      *alpha|*beta|*pre-release|*final)
        repo="endeavour-release"
        ;;
    esac
  fi

  echo "$repo"
}

get_root_cert_dir()
{
  local cert_dir=""
  local cert_dirs=(
    "/etc/ssl/certs"                 # Debian, Ubuntu, Arch, Gentoo, openSuSE
    "/etc/pki/tls/certs"             # CentOS, Fedora, RHEL6
    "/etc/pki/ca-trust/extracted"    # RHEL7
    "/system/etc/security/cacerts"   # Android
  )

  for dir in ${cert_dirs[@]}
  do
    if [ -d "$dir" ]; then
      local found=""

      found="$(find $dir -maxdepth 1 -type f -o -type l)"

      if [ -n "$found" ]; then
        cert_dir="$dir"
        break
      fi
    fi
  done

  echo "$cert_dir"
}

get_root_cert_file()
{
  local cert_file=""
  local cert_files=(
    "/etc/ssl/certs/ca-certificates.crt"                   # Debian/Ubuntu/Gentoo etc.
    "/etc/pki/tls/certs/ca-bundle.crt"                     # Fedora/RHEL 6
    "/etc/ssl/ca-bundle.pem"                               # OpenSUSE
    "/etc/pki/tls/cacert.pem"                              # OpenELEC
    "/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem"    # CentOS/RHEL 7
    "/etc/ssl/cert.pem"                                    # Alpine Linux
  )

  for f in ${cert_files[@]}
  do
    if [ -f "$f" ]; then
      cert_file="$f"
      break
    fi
  done

  echo "$cert_file"
}

