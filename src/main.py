from fastapi import FastAPI
from binascii import Error
from src.db import engine, Base
from src.auth.auth_router import app as auth_app
from src.client.client_router import app as client_app


app = FastAPI()

app.include_router(auth_app)
app.include_router(client_app)


@app.get("/init")
async def create_db():
    async with engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.drop_all)
        except Error as e:
            print(e)     
        await  conn.run_sync(Base.metadata.create_all)
    return({"msg":"db creat! =)"})





