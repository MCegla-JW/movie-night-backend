# MovieNight App

# Description

The Problem:
Have you ever spent ages scrolling through your streaming platform of choice, only to find nothing to watch? Or planned a fun movie night with friends, only to struggle to agree on what to put on?

The Solution:
MovieNight helps users discover movies by browsing a large catalog and adding titles to their personal watchlists. Users can then create watch parties and invite friends to join. When a friend joins a party, one movie from their watchlist is randomly added to the party’s selection. On the day of the event, the group chooses from a curated list of movies—making decision-making easy and fun.

This is my fourth and final project from my three-month intensive bootcamp at General Assembly.

*This app has two repositories: frontend and backend

Code snippets in this ReadMe are from backend, for frontend, please go here - [Frontend ReadMe](https://github.com/MCegla-JW/movie-night-frontend)

# Deployment Link 

🍿The App: [MovieNight](https://movienight-app-project.netlify.app/movies)

# Timeframe & Working Team 

## Timeframe: 9 days (solo project)

| Time | Task 
|:-----| :-----
| Day 1 | Planning (user stories, ERD, Miro wireframe)
| Day 2 | Backend Setup + Models + Admin 
| Day 3 | Authentication + TMDB Integration 
| Day 4 | Watchlist System Creation 
| Day 5 | Voting System + Winner Logic
| Day 6 | Party Creation + Join System
| Day 7 | Frontend Setup + Authentication UI
| Day 8 | Discover + Watchlist UI
| Day 8 | Party UI + Voting Interface
| Day 9 | Polish + Testing + Bug Fixes + Deployment + Presentation

# Technologies Used

## Frontend:

- React
- JavaScript (ES6)
- JSX
- React Router
- Tailwind CSS
- DaisyUI
- Headless UI
- HTML5
- npm
- localStorage

## Backend/ APIs: 

- Python
- Django
- Django REST Framework
- Pipenv
- PostgreSQL (Neon)
- Django Authentication
- JSON Web Tokens (JWT)
- TMDB API
- axios

## Development & Design Tools:

- Miro
- Trello 
- Postman (API testing)
- VSCode

## Deployment: 

- Heroku (server)
- Netlify (client)

## Version Control:

- Git 
- GitHub

## Features 

- User Authentication: Secure sign-up, sign-in and sign-out functionality using a JSON Web Token (JWT)
- TMDB API Integration: Access to The Movie Database for movie discovery and metadata
- CRUD Operations: Create, read, update and delete parties
- Party Join Codes: Unique join codes allow users to join specific parties
- Random Movie Selection: Movies are randomly added to parties from user watchlists
- Responsive Design: Mobile-first, fully responsive UI
- Error Handling & Validation: Server-side and client-side validation to prevent invalid data submission
- Environment Variable Security: Sensitive keys managed through .env files

## Brief

The project requirements included:

- The back-end is built with Django and Python
- The front-end is built with React
- PostgreSQL (Neon) is used as the database management system
- Both the back-end and front-end implement JWT token-based authentication for user sign-up, sign-in, and sign-out
- Authorization is enforced across the application: guest users (not signed in) cannot create, update, or delete data, or access functionality for those actions
- Discover page and cannot add movies to their watchlist until signed in
- The project includes at least two data entities in addition to the User model, with multiple relationships between them
- There is full CRUD functionality on at least one model, implemented on both the front-end and back-end
- The front-end does not store any secret keys. Any public APIs requiring secret keys are accessed via the back-end
- The project is deployed online and accessible to users worldwide

# Planning

Theme: I am a big movie fan and I wanted to make something that I could use myself - I don't use Letterboxd but I wanted to make something similar to manage my watchlist 

Entity Relationship Diagram (ERD): Created an ERD to visualize the relationships between Users, Watchlist, Parties and Movies

Wireframes: Developed wireframes in Miro to establish the basic layout and user flow through the application

Project Document: Created a comprehensive document detailing the user journey alongside the wireframes to help visualize the flow and functionalities

Project Management: Used Trello to organize tasks, track progress, and manage the project timeline effectively

# Build/Code Process

## Movie - Discover View Creation

The Discover page is accessible to both signed-in and guest users. Authenticated users can interact fully with the content, while guest users have read-only access.

The goal of this view was to display popular movies while also providing a search feature to improve user experience. This was achieved by modifying the movie `GET` request and integrating TMDB API.

The 'TMDB_API_KEY' and 'TMDB_BEARER_TOKEN' were securely stored in environment variables. Movie data was fetched conditionally depending on whether a search query was provided, switching between the TMDB popular movies endpoint and the search endpoint.

```python
class MoviesView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        search_query = request.GET.get('search', '')
        API_KEY = settings.TMDB_API_KEY
        TMDB_BEARER_TOKEN = settings.TMDB_BEARER_TOKEN
        base_url = "https://api.themoviedb.org/3/movie/popular?language=en-US&page=1"
        search_url = "https://api.themoviedb.org/3/search/movie"
        headers = {
        "accept": "application/json",
        "Authorization": TMDB_BEARER_TOKEN}
        if search_query:
            url = f'{search_url}?api_key={API_KEY}&query={search_query}'
        else:
            url = f'{base_url}&api_key={API_KEY}'
        response = requests.get(url, headers=headers)
        data = response.json().get('results',[])
        return Response({'movies': data, 'search': search_query}, status=200)
```


## Party – Random Movie Added on Creation

When a party is created, one random movie from the creator’s watchlist is automatically added to the party. This ensures that every party starts with at least one movie and encourages engagement from the moment it’s created.

On creation:
- The party creator is added as the first party member
- A random movie is selected from the creator’s watchlist
- The movie is added to the party if it does not already exist
- Duplicate movie additions are prevented at the database level

```python
def post(self, request):
    creator = request.user
    created_party.members.add(creator)

    movie_to_add = Watchlist.objects.filter(
        user=request.user.id
    ).order_by("?").first()

    if not movie_to_add:
        return Response(
            {'message': 'Watchlist empty. Add movies first'},
            status=400
        )

    if PartyMovie.objects.filter(
        party=created_party,
        movie=movie_to_add.movie
    ).exists():
        return Response(
            {'message': 'Movie already exists in party'},
            status=400
        )

    PartyMovie.objects.get_or_create(
        party=created_party,
        movie=movie_to_add.movie,
        defaults={'added_by_user': creator}
    )

    updated_serializer = PartySerializer(created_party)
    return Response(updated_serializer.data, status=201)
```
## Party - Unique Code Creation

When creating a party, the goal was to automatically generate a unique join code that users could share with friends. The code was unique per party.

This was achieved by modifying the party `POST` request to generate a UUID using Python's built-in 'uuid' module. A 'uuid4' value was generated on party creation and passed into the serializer's 'save()' method, ensuring each party has a secure, collision-safe join code.

```python
def post(self, request): 
        serializer = PartySerializer(data=request.data)
        is_valid = serializer.is_valid(raise_exception=True)
        print(serializer._validated_data)
        # save created party
        created_party = serializer.save(creator = request.user, join_code = uuid.uuid4())

        updated_serializer = PartySerializer(created_party)
        return Response(updated_serializer.data, 201)
```
## Party - Join Logic

When a user joins a party using a unique join code:
- They are automatically added as a party member
- One random movie from their watchlist is added to the party
- Duplicate users and duplicate movies are prevented

This was implemented by modifying the party join `POST` request and using the 'join_code' to ensure correct party is updated. Additional safeguards were added to handle edge cases such as users already in the party or empty watchlist.

```python
def post(self, request, join_code):
        party = get_object_or_404(Party, join_code=join_code)
        user_to_join = request.user
        users_in_party = party.members.filter(id = user_to_join.id).exists()
        if users_in_party == True:
            return Response({'message': 'Party member already exists', 'party_id': party.id})
        party.members.add(user_to_join)
        movie_to_add = Watchlist.objects.filter(user = request.user.id).order_by("?").first()
        if not movie_to_add:
            return Response({'message': 'Watchlist empty. Add movies first', 'party_id': party.id})
        party_movie, created = PartyMovie.objects.get_or_create(party=party, movie=movie_to_add.movie, defaults={'added_by_user': user_to_join})
        if not created:
            return Response({'message': 'Cannot add duplicate movies. Movie already in party', 'party_id': party.id})
        serializer = PartySerializer(party)
        return Response({'message': 'User joined party', 'party_id': party.id})
```

## Planning & Wireframes: 

I designed the user interface and flow using wireframes in Miro, ensuring a clear, intuitive layout before coding

📓[Miro Board](https://miro.com/welcomeonboard/SWhsK2M4SDhKRlZxcWxkNXMwN2FhUVBMdm9HVGVNaTNGZnYrNUs3d2poQkgyZm1vNnVieXM4cVFlaFV3WGx6eFpndVA3MWZMZ2paTm42bk5WcG9pRFBJVkNPUTRUcFhaUkx6dUdXeWFRTTR5allMUUZqbmJjM29kd01UZy8vRUNQdGo1ZEV3bUdPQWRZUHQzSGl6V2NBPT0hdjE=?share_link_id=346039286400)

I also created a planning document containing the user flow, wireframes, data models, routing tables and links to supporting materials.
  
📑[Planning Word Doc](https://docs.google.com/document/d/1JNhUyX-8qCxzBIFX848Q8rcOJbRCzBLj7rZ0Pe1xPSM/edit?tab=t.0)


## Challenges 

- Serializers: Understanding how serializers map models to JSON, control validation, creation and updates within Django REST Framework
- Django Models & Relationships: Designing and managing multiple related models (Users, Watchlists, Parties, Movies) and ensuring data integrity across relationships
- Switching Languages: Adapting from JavaScript to Python and learning Django's conventions, syntax and project structure within a short timeframe
- Data Flow: Handling data from both an external API (TMDB) and the database, and ensuring consistent serialization and rendering

## Wins

- TMDB Integration: I’m very pleased I successfully integrated TMDB into this project, including the search feature, to fetch and display movie data dynamically 
- Making an app that I will use in my personal life 
- This was my first time using Django and Python.  I gained a solid foundation in both, including models, serializers, views, authentication, syntax, project structure among others
- Learned to navigate the Django and Django REST Framework documentation independently under tight time constraints
- Improved my confidence in designing RESTful APIs and handling complex logic on the server side 

## Key Learnings/Takeaways

- Python & Django Fundamentals: I gained hands-on experience building a full REST API using Django and Django REST Framework, including models, serializers, views, permissions, and authentication
- Relational Data Modeling: I learned how to design and manage relational data in PostgreSQL (Neon), including many-to-many relationships, foreign keys, and enforcing data integrity
- Serializers as Core Logic: I developed a solid understanding of Django REST Framework serializers for validation, data transformation, nested relationships, and controlled object creation
- API Design: I improved my ability to design RESTful endpoints that handle real-world business logic, such as party creation, join flows, random movie selection, and duplicate prevention
- External API Integration: I gained experience integrating and securing third-party APIs (TMDB), including conditional data fetching and environment variable management
- Authentication & Authorization: I implemented JWT-based authentication and permission controls to restrict write access while allowing read-only access for guest users
- Planning and Prototyping: I realized that thorough wireframing and prototyping during the planning stage makes frontend development faster and more efficient
- Confidence in Backend Development: I finished the project with greater confidence building scalable backend systems and debugging complex server-side issues independently


## Known Bugs

- When a movie is deleted from watchlist but is in a party, it remains in party 

## Future Improvements 

- Dark/Light mode
- BottomNavBar - icons are highlighted differently to indicate an active tab
- Party members can vote for movies in party and land on one winning one that they can watch on the day
- Solo watcher mode - feature in watchlist where a user can get a movie selected for them at random if they don't know what to watch 
- Users can leave party
- Party creator is notified that a new user joined the party
- Users can manually add a movie to party 
- Users can remove the random movie if they don't like it and another random movie is added 
- Connect to third party API to source weather data in each trip destination and display it for users 
- Users can rate movies

## Installation & Setup

Prerequisites
- Python 3.11+ installed
- PostgreSQL database (or Neon for hosted PostgreSQL)
- pipenv or virtualenv for managing dependencies
- Git

| Step | Action |
|:-----|:------|
| 1. Clone the repo | `git clone https://github.com/MCegla-JW/movie-night-backend.git && cd movie-night-backend` |
| 2. Create and activate a virtual environment (pipenv example) | `pip install pipenv && pipenv shell` |
| 3. Install dependencies | `pipenv install` |
| 4. Create a `.env` file with the following variables | `SECRET_KEY=your_django_secret_key` <br> `DEBUG=True` <br> `DATABASE_URL=postgres://user:password@host:port/dbname` <br> `TMDB_API_KEY=your_tmdb_api_key` <br> `TMDB_BEARER_TOKEN=your_tmdb_bearer_token` |
| 5. Create a superuser (optional, for admin access) | `python manage.py createsuperuser` |
| 6. Start the development server | `python manage.py runserver` |

Note: Replace all `your_...` values with your own credentials.  
Sensitive keys are intentionally not included in the repository.

