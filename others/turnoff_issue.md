# turn off issue after ubuntu setup

poweroff가 정상 작동하지 않는 현상 발생
다음 [링크](https://askubuntu.com/questions/1467524/shutdown-not-completing-cleanly-on-ubuntu-22-04)의 지침을 따라 해결

## Instruction on above followed link

I solved it by adding acpi=force to the grub configuration.

```bash
    sudo nano /etc/default/grub
    Add acpi=force to the GRUB_CMDLINE_LINUX_DEFAULT line e.g. GRUB_CMDLINE_LINUX_DEFAULT="quiet splash acpi=force"
    sudo update-grub
```

And now it shuts down cleanly!

## Kernel issue

커널이 업데이트 되면서 다시 프리징 현상 발생

- linux image 검색

    ```bash
        (base) sunhokim@sunhokim-Dell-G15-5525:~$ dpkg --list|grep linux-image-*
        rc  linux-image-6.2.0-26-generic                     6.2.0-26.26~22.04.1                     amd64        Signed kernel image generic
        rc  linux-image-6.2.0-34-generic                     6.2.0-34.34~22.04.1                     amd64        Signed kernel image generic
        ii  linux-image-6.2.0-35-generic                     6.2.0-35.35~22.04.1                     amd64        Signed kernel image generic
        ii  linux-image-6.2.0-36-generic                     6.2.0-36.37~22.04.1                     amd64        Signed kernel image generic
        ii  linux-image-generic-hwe-22.04                    6.2.0.36.37~22.04.14                    amd64        Generic Linux kernel image
    ```

걍 다운 그레이드 귀찮아서 안함

## Additional info

<https://askubuntu.com/questions/1481452/ubuntu-22-04-3-lts-wont-power-off>
<https://askubuntu.com/questions/1481221/ubuntu-desktop-disappear-on-reboot-ubuntu-22-04/>

and i followed below instruction

<https://www.reddit.com/r/debian/comments/g46dip/activation_via_systemd_failed_for_unit/>

sudo apt-get remove rtkit