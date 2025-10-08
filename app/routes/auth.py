from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from app.utils.database import db

router = APIRouter()

# ⚠️ Troque por variável de ambiente depois (segurança)
SECRET_KEY = "chave_super_secreta"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# contexto de hash com bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


# -------------------------------
# Funções auxiliares
# -------------------------------

def verify_password(plain_password: str, hashed_password: str):
    """Verifica a senha truncando a 72 caracteres (limite do bcrypt)."""
    return pwd_context.verify(plain_password[:72], hashed_password)

def get_password_hash(password: str):
    """Gera o hash truncando a 72 caracteres para evitar erro do bcrypt."""
    return pwd_context.hash(password[:72])

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Cria token JWT com expiração."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# -------------------------------
# Rotas
# -------------------------------

@router.post("/auth/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Autenticação: retorna JWT se o login for válido."""
    user = await db["users"].find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")

    token = create_access_token({"sub": user["email"]})
    return {"access_token": token, "token_type": "bearer"}


# -------------------------------
# Dependência de autenticação
# -------------------------------

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token inválido")
        user = await db["users"].find_one({"email": email})
        if not user:
            raise HTTPException(status_code=401, detail="Usuário não encontrado")

        # 🔍 Validação da assinatura
        subscription = user.get("subscription", {})
        if not subscription.get("active"):
            raise HTTPException(status_code=403, detail="Assinatura inativa")

        end_date = subscription.get("end_date")
        if end_date and datetime.utcnow() > datetime.fromisoformat(end_date):
            raise HTTPException(status_code=403, detail="Sua assinatura expirou. Renove para continuar.")

        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
