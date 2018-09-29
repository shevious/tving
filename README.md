# tving

티빙 KODI / PLEX 플러그인이다.

~~블로그에서 먼저 배포. 설명 참조~~
~~https://blog.naver.com/cybersol/221198625272~~

[KODI용 ZIP](https://github.com/soju6jan/soju6jan.github.io/tree/master/kodi_plugin)

문의사항은 ISSUE에 로그파일을 같이 올려주세요

----
#### 폴더구조
#####  ```tving.py``` 파일은 공용파일이다. 직접 파일을 복사한 후 설치 해야한다.
  - KODI
  ```
    - plugin.video.tving
        resoureces
          language
            Korean
            English
          lib  (lib 폴더 생성 후 tving.py 복사)
  ```

  - PLEX
  ```
    - Tving.bundle
        Contents
          Code ( code 폴더에 tving.py 복사)
          esources
            English
  ```


----
#### ChangeLog
##### 0.4.0 (20180929)
- 로그인 정보를 저장할 수 없는 OS가 있는 것 같으며 그럴 경우 URL을 가져오기전 매번 로그인.

##### 0.3.3 (20180910)
SSL관련 로그인 안되는 문제 수정

##### 0.3.2 (20180729)
다시 계정정보 입력하도록 변경

##### 0.3.0 (20180709)
만들었던 코드가 웹 로그인을 이용하는데, 웹이 구글캡차를 사용하도록 변경.
모바일을 이용하는 방식으로 고쳐야 하나 안된다는 문의 글이 많아
임시로 토큰을 직접 넣도록 수정.
