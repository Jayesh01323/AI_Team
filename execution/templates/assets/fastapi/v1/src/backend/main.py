from fastapi import FastAPI  # type: ignore[import-not-found]

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello World"}
