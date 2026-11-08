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
