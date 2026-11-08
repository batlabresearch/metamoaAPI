# 4개 공간 최대값 자동 생성

`Metamoa Max Online`은 GitHub 서버에서 **7분마다** 산사·온라인 갓바위·코루라이브 객장·
온라인 신당(재회, 연애, 취업)의 최신 `online` 값을 조회하고 최댓값을 선택합니다.
`floor(max_online * 0.9 + random_digit)`를 계산하며, `random_digit`은 0~9입니다.
결과는 루트의 `metamoaAPI.txt`에 숫자 하나로 저장됩니다.

- 반환 주소: https://raw.githubusercontent.com/batlabresearch/metamoaAPI/main/metamoaAPI.txt
- 확인 시각·원본·계산 결과: `data/latest.json`
- 누적 기록: `data/four_spaces.csv` (기존 산사 기록은 `data/sansa.csv`에 보관)

실행기 하나가 5시간 동안 7분 간격으로 갱신하고, 끝나면 저장소의 `GITHUB_TOKEN`으로
다음 실행을 시작합니다. 실행이 교체돼도 마지막 수집 시각에서 7분 뒤에 갱신합니다.
매시 23분의 예약 실행은 중단 시 복구를 돕습니다.
GPT 앱이나 사용자 PC를 켜 둘 필요가 없습니다.
GitHub 장애·실행기 배정 지연 및 raw 캐시로 반영이 늦어질 수 있습니다.

시작: Actions → Metamoa Max Online → Run workflow (기본 300분).
중지: 워크플로를 비활성화한 뒤 진행 중인 실행과 대기 중인 실행을 취소합니다.

# Metamoa 자동 전송

`Send Metamoa visitor count` 워크플로는 매시 07·17·27·37·47·57분에
GitHub Actions에서 실행됩니다. PC나 ChatGPT 앱을 켜 둘 필요가 없습니다.

- 원본: `https://raw.githubusercontent.com/batlabresearch/metamoaAPI/main/metamoaAPI.txt`
- 전송: `POST https://metamoa.com/api/live/batlabresearch-github-io-mw4gjmx2`
- 본문: `{"count": 파일의 현재 정수}`
- 인증키: 저장소의 Actions secret `METAMOA_SPACE_KEY`
- 성공: 실행 로그와 요약의 `HTTP 204`

원본은 0~100000 사이 정수여야 합니다. 파일의 값을 그대로 전달하며,
기존 `metamoa_top5.py`의 값 생성 방식은 바꾸지 않습니다.
Metamoa는 현재 실제 접속자 수를 받는 API이므로 원본의 의미는 별도로 관리해야 합니다.

GitHub 예약 실행은 정확한 시각을 보장하지 않으며 혼잡 시 지연되거나 누락될 수 있습니다.
Metamoa가 너무 잦은 요청으로 HTTP 429를 반환하면 즉시 재시도하지 않고 다음 실행을 기다립니다.
공개 저장소에서 60일간 활동이 없으면 GitHub가 예약 실행을 비활성화할 수 있습니다.

수동 실행: Actions → Send Metamoa visitor count → Run workflow.
전송 없이 원본 검증: `python3 scripts/send_metamoa.py --dry-run`.
키는 소스 코드나 로그에 넣지 말고 GitHub의 Actions secret에서 관리합니다.
