# Social Media Api
Documented api with basic social media functionality

### Features:
1. Users can register with their email and password to create an account
2. Users can login with their credentials and receive a token for authentication
3. Users can logout and invalidate their token.
4. Users can create and update their profile, including profile picture, bio, and other details.
5. Users can to retrieve their own profile and view profiles of other users and search for other users by different criteria
6. User can follow and unfollow another user
7. On his personal page user can see other users who follow him and followed by him
8. Users can create new posts with text content, hashtags and image
9. Users can retrieve their own posts and posts of users they are following.
10. Users can filter posts by hashtags.
11. Users can to like and unlike posts. Users can view the list of posts they have liked. 
12. Users can add comments to posts and view comments on posts.
13. Possibility to schedule Post creation (you can select the time to create the Post before creating of it).

### Permissions:
1. Only authenticated users can perform actions such as creating posts, liking posts, and following/unfollowing users.
2. Users can only update and delete their own posts and comments.
3. Users can only update and delete their own profile.

### Technologies used:
1. Django and Django REST framework for building the API.
2. JWT token for authentication
3. Swagger documentation
4. Postgresql as database
5. Celery + Redis for task scheduling

### How to run:
- Create venv: `python -m venv venv`
- Activate it: `source venv/bin/activate`
- Install requirements: `pip install requirements.txt`
- Create new Postgres DB & User
- copy .env.sample -> .env and populate it
- Run migrations: `python manage.py migrate`
- Run Redis server: `docker run -d -p 6379:6379 redis`
- Run celery worker for tasks handling: `celery -A social_media worker -l INFO`
- Run app: `python manage.py runserver`
