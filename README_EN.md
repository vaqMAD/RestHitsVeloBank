# 🎵 RestHits – API for Managing Music Hits

Some modifications have been made to the project compared to the original specification. These changes reflect my programming preferences, especially regarding security and REST standards. I believe these modifications fall within the flexibility allowed by the specification. If strict compliance with the specification is required, I am ready to deliver a 100% compliant version.

### ⚠️ NOTE!!!

If you use automated tests to verify the application's correctness, the changes I introduced may lead to test failures. Please review the documentation thoroughly and take the modifications into account when evaluating the project.

---

### 💚A Few Things from the Heart

I implemented some additional enhancements and features that go beyond the original project scope, but I believe they are crucial:

* **Security Measures** – see more details in the next section.
* **Smart Caching Mechanism** – to improve app performance and response time. This mechanism is inspired by my main project [diagram](https://imgur.com/ejYuZhe).
* **Extended Filtering and Sorting Options** – why not dynamically filter and sort data? I made it happen!
* **Over 70 unit and integration tests with 99% code coverage.**
* **Endpoint for sorting Hits by Artist.**
* **Project Documentation.**
* **Business Logic Validation** – e.g., verifying the uniqueness of song titles per artist to prevent data inconsistencies.
* **Containerization**

---

### 💡 Improvements: Security, Technical Decisions, and Rationale

* **N+1 Query Problem Solved** – optimized database queries to eliminate N+1 issues.
* **UUIDs for Resource Identifiers (instead of ints)** – UUIDs are harder to guess and more secure, especially when consumed by a frontend.
* **Dynamic Generation of `title_url`** – instead of storing it in the database, it is dynamically generated during API serialization. This reduces DB load and increases flexibility.
* **Superuser Authorization for Data-Modifying Operations** – all data-changing endpoints (`POST`, `PUT/PATCH`, `DELETE`) require superuser authentication to maintain data integrity and security.

---

## 🛠️ Installation

You can install and run the application with:

```bash
git clone https://github.com/vaqMAD/Link
cd timemate
docker compose up --build
```

---

## 🚀 Quick Start

### 1. Application Access

To run the tests: `docker-compose run --rm web python manage.py test`

Start the container with: `docker-compose up`

Once the container is running, the app will be available at:
`http://127.0.0.1:8000` or `http://localhost:8000`

### 2. API Documentation

Interactive API docs available at:
`http://127.0.0.1:8000/api/schema/swagger-ui/`

### 🔑 Authentication and Authorization

* **Username:** `admin@admin.com`
* **Password:** `1234`
* **Auth Token:** `9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b`

API access levels:

* **Public Access (`GET`)**
  All data read operations (e.g., listing hits) are public and **do not require authentication**.

* **Protected Access (Data Modification):**
  Operations like `POST`, `PUT`, and `DELETE` **require superuser authentication**.

### 🔐 How to Authenticate?

```http
POST http://127.0.0.1:8000/hits/
Content-Type: application/json
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

### 🌱 Sample Data

As per the assignment description, test data generation is automated during container startup.

Manual trigger is also available:

```bash
docker-compose run --rm web python manage.py seed_data
```

---

## 📱 First API Request

Start interacting with the API like this:

📊 **Viewing Sample Data**

* `GET http://127.0.0.1:8000/artists/`
  *Get a list of 20 artists*

* `GET http://127.0.0.1:8000/hits/`
  *Get a list of 20 hits*

⚙️ **Filtering and Sorting**

By default, hits at `http://127.0.0.1:8000/hits/` are sorted by creation date.

Extended filtering and sorting options are documented in the API docs.

Example request:

```http
GET http://127.0.0.1:8000/hits/?ordering=-created_at&created_at_before=2025-05-22
```

**🛠 Creating Custom Records**

You can submit your own data. Business logic validation is enforced. For example, if an artist already has a song with the same title, a clear error message will be returned:

```http
POST http://127.0.0.1:8000/hits/
Content-Type: application/json
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

```json
{
  "title": "Billie Jean",
  "artist_id": "ae985c49-278c-4917-91d4-4703950e7bb6"
}
```

**Response:**

```json
{
  "hit": [
    "Hit with title Billie Jean already exists for this artist."
  ]
}
```

---
