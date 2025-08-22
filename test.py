from functools import wraps
from typing import Callable, Any
import jwt
from datetime import datetime, timedelta
import traceback
SECRET_KEY = "secret"

def require_auth(required_roles: list = None):
    """인증 및 권한 체크 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            token = kwargs.get('token') or (args[0] if args else None)

            if not token:
                raise ValueError("인증 토큰이 필요합니다")

            try:
                # JWT 토큰 검증
                payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                user_id = payload.get('user_id')
                user_roles = payload.get('roles', [])

                # 권한 체크
                if required_roles and not any(role in user_roles for role in required_roles):
                    raise PermissionError(f"필요한 권한: {required_roles}, 현재 권한: {user_roles}")

                # 원본 함수에 사용자 정보 추가
                kwargs['user_id'] = user_id
                kwargs['user_roles'] = user_roles

                return func(*args, **kwargs)

            except jwt.ExpiredSignatureError:
                raise ValueError("토큰이 만료되었습니다")
            except jwt.InvalidTokenError:
                raise ValueError("유효하지 않은 토큰입니다")

        return wrapper
    return decorator

# 사용 예시
@require_auth(required_roles=["admin"])
def delete_user(user_id: int, token: str = None, **kwargs) -> dict:
    """사용자 삭제 함수 - admin 권한 필요"""
    return {
        "message": f"사용자 {user_id} 삭제 완료",
        "deleted_by": kwargs.get('user_id'),
        "roles": kwargs.get('user_roles')
    }

# 테스트용 토큰 생성
def create_test_token(user_id: int, roles: list):
    payload = {
        'user_id': user_id,
        'roles': roles,
        'exp': datetime.now() + timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    # PyJWT 2.x 이상에서는 str로 변환 필요
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token

# 테스트 실행
if __name__ == "__main__":
    admin_token = create_test_token(1, ["admin", "user"])
    user_token = create_test_token(2, ["user"])

    try:
        # ✅ admin 권한 → 성공
        result = delete_user(user_id=123, token=admin_token)
        print("✅ admin_token 실행 결과:", result)

        # ❌ user 권한만 → 실패
        result = delete_user(user_id=123, token=user_token)
        print("❌ user_token 실행 결과:", result)
    except Exception as e:
        # print(traceback.format_exc())
        print(f"🚫 예외 발생: {e}")