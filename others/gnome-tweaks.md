# Abstract

- 전원과 관련한 세부 옵션 설정을 위해 `gnome-tweaks`를 사용
- 어플리케이션 실행 후 오류가 발생됨을 확인하여 관련 해결법을 아래 기록함


## ModuleNotFoundError: No module named 'gi'
Reference: <https://jeeu147.tistory.com/38>

- Follow those commands in order
  """bash
  python --version #파이썬 3.6 이상 버전에서 다운로드 가능
  sudo apt install libcairo2-dev
  sudo apt install libxt-dev
  sudo apt install libgirepository1.0-dev
  pip install pycairo
  pip install PyGObject
  """
