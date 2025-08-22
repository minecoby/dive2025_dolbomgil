# dive2025_dolbomgil

## FCM 푸시 알림 설정

### 1. Firebase 프로젝트 설정
1. Firebase Console에서 새 프로젝트 생성
2. Cloud Messaging 활성화
3. 서비스 계정 키 생성 및 다운로드
4. `serviceAccountKey.json` 파일을 프로젝트 루트에 배치

### 2. 환경 변수 설정
```bash
# .env 파일에 추가
FIREBASE_SERVICE_ACCOUNT_PATH=serviceAccountKey.json
```

### 3. API 엔드포인트

#### FCM 토큰 관리
- `POST /api/fcm-token/` - FCM 토큰 등록
- `GET /api/fcm-token/my-tokens` - 내 FCM 토큰 목록 조회
- `PUT /api/fcm-token/{fcm_token}` - FCM 토큰 업데이트
- `DELETE /api/fcm-token/{fcm_token}` - FCM 토큰 삭제
- `POST /api/fcm-token/{fcm_token}/deactivate` - FCM 토큰 비활성화

#### 자동 알림
- **안전구역 이탈**: 피보호자가 안전구역을 벗어날 때 자동으로 보호자에게 푸시 알림
- **배터리 부족**: 피보호자 워치 배터리가 20% 이하일 때 자동으로 보호자에게 푸시 알림

### 4. 사용 방법
1. 클라이언트에서 FCM 토큰을 서버에 등록
2. 피보호자 위치 업데이트 시 자동으로 알림 조건 확인
3. 조건 충족 시 보호자에게 푸시 알림 전송

### 5. 보안 주의사항
- `serviceAccountKey.json`은 절대 Git에 커밋하지 마세요
- 프로덕션 환경에서는 환경 변수나 시크릿 관리 시스템 사용