---
title: "PEP8과 타입 힌트: 협업을 위한 Python 코드 스타일 가이드"
date: 2025-08-19
categories:
  - python
tags:
  - pep8
  - typing
  - linters
  - code-quality
  - black
  - flake8
  - mypy
---

# PEP8과 타입 힌트: 협업을 위한 Python 코드 스타일 가이드

## 1. PEP8 규칙 (Python Enhancement Proposal 8, Python 공식 스타일 가이드)
- PEP8은 Python 코드의 일관성과 가독성을 위한 공식 스타일 가이드로, 협업시 팀 컨벤션 위반을 방지하기 위해 필수적으로 알고있어야 한다.

### 기본 규칙

|항목|요약|예시|
|----------|----------------|------------------------|
|들여쓰기|4칸 스페이스|def func():⎵⎵⎵⎵pass|
|한 줄 길이|79자 이하 (문서용은 72자 이하)|너무 길면 줄바꿈|
|공백 사용|연산자, 콤마 등에서 과도한 공백 ❌|a = 1, x = (a + b)|
|함수/변수 명|소문자 + 언더스코어 (snake_case)|def get_user_info():|
|클래스 명|PascalCase 사용|class UserManager:|
|상수|모두 대문자 + 언더스코어|MAX_RETRIES = 5|
|불필요한 줄|함수 간 2줄, 메서드는 1줄|가독성 확보 목적|

- 자동 정리는 black, isort, flake8, pylint 등으로 팀내 룰 맞출 수 있다.

## 2. 협업을 위한 실무 스타일 가이드 (팀 내 코드 규칙)
- 📌 구조적 원칙
    - 하나의 함수는 하나의 책임만 갖도록 
    - 각 함수는 5~15줄 이하 유지 (가독성)
    - 클래스/모듈은 파일 300줄, 클래스 100줄 넘지 않도록 제한하는 경우도 있음

- 📌 함수 설계
    - side-effect를 최소화 (순수 함수 지향)
    - None을 반환하는 함수는 명확하게 의미를 주기 (ex: find_user_or_none)
    - 디폴트 값은 None보다 명확한 값 사용

- 📌 모듈 구조
    - import 순서: 표준라이브러리 → 서드파티 → 내부모듈 → 상대경로
    - 정리는 isort로 자동화

## 3. 파이썬다운(파이쏘닉한) 코드 스타일

|비효율 ❌|파이썬다운 코드 ✅|설명|
|---------------|------------------------------|-------------------|
|for i in range(len(list))|for item in list:|직접 순회로 가독성 증가|
|if x == True:|if x:|Truthy/Falsy를 자연스럽게|
|temp = [] for x in y:temp.append(x)|[x for x in y]|리스트 컴프리헨션|
|not x is None|x is not None|표현 순서|
|dict.keys() in loop|for k in dict:|더 간결하고 빠름|
|중첩 조건문|조기 return 활용|불필요한 들여쓰기 제거|
|if x in [1,2,3]|if x in {1,2,3}|set이 더 빠름|


## 4. 추가적으로 신경 쓰면 좋은 부분
| 항목 | 설명 |
|------|------|
| **타입 힌트 적극 사용** | `def get_user(id: int) -> Optional[User]:` |
| **에러 메시지 명확하게** | `raise ValueError("User not found")` |
| **로깅 일관성** | print 대신 `logger.debug/info/warning/error()` |
| **컨텍스트 매니저 적극 활용** | `with open(...) as f:`, DB 연결 등 |
| **의미 있는 변수명** | `data1`, `data2` ❌ → `user_data`, `order_items` ✅ |


## 5. 추천 도구
| 도구 | 역할 |
|------|------|
| `black` | 코드 자동 포매터 (PEP8 기반) |
| `flake8` / `pylint` | 스타일 위반 감지, 린터 |
| `mypy` | 타입 힌트 검증 |
| `isort` | import 정리 도구 |
| `pre-commit` | 커밋 전 자동 검사 적용 |

## cf. 실무에서 사용해본 방식 
- .vscode/settings.json 방식 또는 팀 공유용 Prettier / Linter 설정 파일을 통한 스타일 가이드 자동화
    - 팀 내에서 .vscode/settings.json를 받아, 이를 각 팀원들에게 복사하도록 안내 -> 자동으로 통인된 포맷이 적용되게 함
    - 이 .vscode/settings.json에서는 black, pylint, mypy 등이 적용된 설정이 있었던 것으로 기억 

```text 
Q: 협업시 Python 코드 스타일을 통일시키기 위해 어떤 도구를 사용해보셨나요? 

이전 팀에서는 .vscode/settings.json을 공유해서 black, pylint, mypy 등을 자동 적용하는 방식으로 코드 스타일을 통일했습니다. 저장 시 자동 포맷팅이 되도록 설정해서, 코드 리뷰 효율이 높아졌고 저도 신규 팀원들에게 적용 방법을 안내한 경험이 있습니다.
``` 

---

<details>
<summary>참고 자료</summary>

- 

</details> 



