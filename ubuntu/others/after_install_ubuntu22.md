# Autoremove & Firefox

22.04 Ubuntu와 관련해 보고된 이슈를 해결하기 위해 몇가지 명령 수행이 필요

## 1. Autoremove

```bash
    sudo apt autoremove
```

## 2. AppImage: Libfuse installation

```bash
    sudo apt install libfuse2
```

## 3. VPN이 여전히 작동하는지 확인(didn't check)

다양한 응용 프로그램은 Ubuntu 22.04 LTS로 업그레이드한 후 업데이트가 필요할 수 있지만 이러한 작업 중 일부는 다른 것보다 더 쉽습니다.

Linux에 NordVPN을 설치했다면 간단한 프로세스가 아님을 알 수 있습니다. Ubuntu 22.04 LTS로 업그레이드하면 NordVPN을 사용할 수 없게 만드는 디렉토리가 변경됩니다.

이 문제를 해결하려면 터미널을 열고 ln 명령을 사용하여 다음 파일 경로를 연결하십시오.

```bash
    sudo ln -s /usr/bin/resolvectl /usr/bin/systemd-resolve
```

## 4. Firefox

firefox 브라우저의 로드 및 속도가 정상적이지 않음을 확인. snap버전으로 기본 설치된 버전을 제거 필요

```bash
    sudo snap remove --purge firefox
    sudo apt remove firefox 
    sudo apt purge firefox

    sudo add-apt-repository ppa:mozillateam/ppa
    sudo apt install -t 'o=LP-PPA-mozillateam' firefox
```

```sudo vim /etc/apt/preferences.d/mozillateamppa``` 에서 다음 내용 추가

```plaintext
    Package: firefox*
    Pin: release o=LP-PPA-mozillateam
    Pin-Priority: 501
```

```bash
    sudo apt update
```
