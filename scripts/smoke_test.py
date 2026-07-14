from app.app import create_app
app=create_app()
client=app.test_client()
print('GET / ->', client.get('/').status_code)
print('GET /admin ->', client.get('/admin').status_code)
print("/static/css/style.css ->", client.get('/static/css/style.css').status_code)
