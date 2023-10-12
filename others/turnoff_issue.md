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
