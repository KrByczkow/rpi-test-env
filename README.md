# rpi-test-env
A test environment made for Raspberry Pi's

## Master Image Build Process
The build process for the Master Image is simple, yet also straightforward. The Raspberry Pi Imager will be needed for this case.
Using the Imager, you select the Raspberry Pi 4 Series, use the "Raspberry Pi OS Lite (64-bit)" by going into "Raspberry Pi OS (other)"
menu, and selecting the drive. Clicking on "Next", you configure the OS. Within the General tab, the hostname is "rpi0", the username
should "pi", and the user-chosen password.

Within the "Services" tab, you enable SSH, and make sure that `authorized_keys` is pre-filled. If not, then run `ssh-keygen` to create a
pair of `id_rsa` and `id_rsa.pub`.

By applying the settings, you flash the OS by clicking on "Yes". A prompt will appear to enter the superuser password. Shortly afterwards,
the installation will begin.