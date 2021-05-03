#!/bin/bash
echo "Run this after backgrounding a netcat shell with ^Z."
echo
echo "This will not work if the remote process is not running a tty."
echo "You can spawn one using python, then background the netcat shell."
echo "python -c 'import pty;pty.spawn(\"/bin/bash\")'"
echo
echo "Here is the upgrade process:"
echo "First, run \`stty raw -echo\`, then \`fg\`, then press enter again."
echo
echo "Now, copy the following three commands and paste them into your terminal:"
echo "export SHELL=/bin/bash"
echo "export TERM=$TERM"
echo "stty rows $(stty size | cut -d' ' -f1) columns $(stty size | cut -d' ' -f2)"
echo
echo "Your terminal is now fully interactive. You may need to run \`reset\`."
echo "If the shell is closed, run \`reset\` to restore terminal functionality."
