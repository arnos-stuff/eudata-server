import uvicorn

def serve():
    uvicorn.run("eudata_server.api:app", reload=True)

if __name__ == "__main__":
    serve()