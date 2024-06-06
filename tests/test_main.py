from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert b"Image Resizer" in response.content

def test_resize_image():
    with open("tests/test_image.png", "rb") as img_file:
        response = client.post("/resize", files={"file": img_file}, data={"scale": 0.5})
        assert response.status_code == 200
        assert b"Resized Image Result" in response.content