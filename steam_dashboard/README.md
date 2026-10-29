# Steam indie insight — Streamlit Community Cloud 배포

이 폴더를 GitHub 저장소의 `steam_dashboard/` 위치에 올려 배포합니다. 기존 화면·데이터·계산식을 그대로 사용하는 배포 구성입니다.

## 배포 설정

Streamlit Community Cloud에서 `Create app`을 선택하고 아래 값을 입력합니다.

| 항목 | 값 |
| --- | --- |
| Repository | `ohseho/mystreamlittest` |
| Branch | `main` |
| Main file path | `steam_dashboard/steam_dashboard_redesign.py` |
| Advanced settings → Python version | `3.12` |
| Secrets | 필요 없음 |

설정 후 `Deploy`를 누릅니다. 생성된 `streamlit.app` 주소를 공유하면 다른 사람이 브라우저에서 대시보드를 볼 수 있습니다. 앱 공개 범위는 Streamlit의 공유 설정에서 확인하세요.

`launch_dashboard.py`나 `.bat` 파일은 로컬 실행용이므로 Cloud 실행 파일로 지정하지 않습니다.

## 포함 파일

- `steam_dashboard_redesign.py`: Cloud 실행 파일
- `requirements.txt`: 검증한 Python 패키지 버전
- `.streamlit/config.toml`: 기존 화면 테마
- `steam_insight/`: 데이터·분석·차트·화면 모듈
- `data/`: 앱이 사용하는 CSV 세 파일
- `assets/steam_insight_v2/`: 배너·KPI 이미지와 제작 정보

ZIP 파일 하나만 GitHub에 올리면 앱 소스로 사용할 수 없습니다. 위 폴더와 파일을 압축 해제한 상태로 올려야 합니다. `.streamlit` 폴더도 포함하세요.

## 로컬 확인

저장소 루트에서 실행합니다.

```powershell
python -m pip install -r steam_dashboard/requirements.txt
python -m streamlit run steam_dashboard/steam_dashboard_redesign.py
```

원본 CSV는 앱 폴더의 `data/`에서 자동으로 읽습니다. 별도 API 키나 Windows 전용 프로그램이 필요하지 않습니다.

공식 안내: [배포](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy), [파일 구성](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization), [의존성](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies).
