# lucid_test


## How to start

Use `docker compose up` to spin up a database. All credentials are hardcoded in `docker-compose.yaml` and 
`app/config.py`. It is eough for desktop testing

`poetry run shell`
`python app/main.py`

## How to use

`curl -X POST http://127.0.0.1:8000/Signup -d '{"email": "user@example.com", "password": "newpassword"}'`

`curl -X POST http://127.0.0.1:8000/Login -d '{"email": "user@example.com", "password": "newpassword"}'`

`Signup` and `Login` outputs token. Pass them to next methods

`curl -X POST http://127.0.0.1:8000/AddPost -H "Authorization: Bearer <your_token>" -H "Content-Type: application/json" -d '{"text": "This is a sample post content"}'`

`curl -X DELETE http://127.0.0.1:8000/DeletePost -H "Authorization: Bearer <your_token>" -H "Content-Type: application/json" -d '{"postID": 1}'`

`curl -X GET http://127.0.0.1:8000/GetPosts -H "Authorization: Bearer <your_token>"`



