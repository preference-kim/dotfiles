# customization of actions for keycode
- 한글버튼이 동작 안 해서 다음 과정을 통해 해결

1. refer to `/usr/share/X11/xkb/rules`
  - `korean:ralt_hangul` 과 같은 option 확인

2. edit `/etc/default/keyboard`
   ```bash
     sudo vi /etc/default/keyboard
   ```
   ```text
    # KEYBOARD CONFIGURATION FILE
    
    # Consult the keyboard(5) manual page.
    
    XKBMODEL="pc105"
    XKBLAYOUT="us"
    XKBVARIANT=""
    XKBOPTIONS="korean:ralt_hangul"
    
    BACKSPACE="guess"
   ```
