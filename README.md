# tving

티빙 KODI / PLEX 플러그인이다.

블로그에서 먼저 배포. 설명 참조
https://blog.naver.com/cybersol/221198625272

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
##### 0.3.0 (20180709)
만들었던 코드가 웹 로그인을 이용하는데, 웹이 구글캡차를 사용하도록 변경.
모바일을 이용하는 방식으로 고쳐야 하나 안된다는 문의 글이 많아
임시로 토큰을 직접 넣도록 수정.
