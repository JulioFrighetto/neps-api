from fastapi.testclient import TestClient
from app.main import app

# Override auth dependency to return an admin-like object
class DummyUser:
    def __init__(self):
        self.role = 'admin'
        self.education_institute_id = None

from app.core import deps
app.dependency_overrides[deps.get_current_user] = lambda: DummyUser()

c = TestClient(app)
resp = c.post('/api/v1/periods/detail', json={'period_id':1,'include':'students'})
print('status', resp.status_code)
print('body', resp.text)
