# Directory Updater

Objective for this program was to create a script that could listen for incoming emails on microsoft exchange email platform and make file system changes that would update digital signage display media.

The file system and access to it on a raspberry-pi-based digital signage platform I installed for a former employer was not very user friendly. To circumvent this problem I wrote this python script to listen for specifically labeled emails to a specific address and update the files on the machine with the files in the emails attachment. Users would simply email whatever files they wanted to update with the parameters they wanted, the system would respond to the user with formatting instructions or clarifications if they did not format the file names or email correctly.
