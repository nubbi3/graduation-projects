# ~/.profile: executed by Bourne-compatible login shells.

if [ "$BASH" ]; then
  if [ -f ~/.bashrc ]; then
    . ~/.bashrc
  fi
fi

mesg n 2> /dev/null || true

adddate() {
    while IFS= read -r line; do
        printf '%s %s\n' "$(date)" "$line";
    done
}

/usr/bin/script -fq >( adddate >> /etc/session.log) && exit