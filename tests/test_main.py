from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_read_hello():
    response = client.get("/api/v1/students/")
    print("Status Code:", response.status_code)
    print("Response Body:", response.text)
    assert response.status_code == 200
