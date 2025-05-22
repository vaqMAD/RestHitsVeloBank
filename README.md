# 🎵 RestHits – API do zarządzania Hitami Muzycznymi

W tym projekcie wprowadziłem kilka zmian w stosunku do pierwotnej specyfikacj. Wynikają one z moich preferencji
programistycznych, szczególnie w obszarze bezpieczeństwa i zgodności z zasadami REST.

Uważam, że te modyfikacje
mieszczą się w ramach elastyczności, jaką dopuszczały instrukcje w zadaniu. W przypadku konieczności dostosowania do
ścisłej
specyfikacji, jestem gotów przygotować wersję w 100% zgodną z opisem zadania.

### ⚠️ UWAGA !!!

Jeśli korzystają Państwo z automatycznych testów do weryfikacji poprawności aplikacji, możliwe jest, że część z nich
zakończy się błędem z uwagi na wprowadzone modyfikacje. Proszę o zapoznanie się z dokumentacją i uwzględnienie tych
zmian przy ocenie projektu.
O przyczynach wprowadzonych zmian napisałem w dwóch poniższych sekcjach.

---

### 💚Kilka rzeczy od serca

Wprowadziłem kilka funkcjonalności wykraczających poza podstawowe wymagania, które według mnie znacząco poprawiają jakość aplikacji:

* **Kwestie bezpieczeństwa** - opisane niżej.
* **Inteligenty mechanizm cache'owania** - wpływa na szybkość i wydajność aplikacji. Rozwiązanie inspirowane moim głównym projektem [schemat](https://imgur.com/ejYuZhe).
* **Rozszerzone możliwości filtrowania i sortowania widoków** -bo czemu nie umożliwić użytkownikowi dynamicznej pracy z danymi?
* **Ponad 70 testów jednostkowych i integracyjnych z 99% pokryciem kodu.**
* **Endpoint sortujący Hity względem Artysty.**
* **Dokumentacja projektu.**
* **Walidacja logiki biznesowej** - np. unikalność tytułów piosenek danego artysty.
* **Konteneryzacja**

---

### 💡 Usprawnienia: Bezpieczeństwo, Decyzje Techniczne i Uzasadnienie

- **Problem N+1 rozwiązany** — zapytania do bazy danych zostały zoptymalizowane.
- **UUID jako identyfikatory zasobów (zamiast integerów)** — trudniejsze do odgadnięcia, bezpieczniejsze przy współpracy z frontendem.
- **Dynamiczne Generowanie title_url (zamiast pola w bazie):** - nie trzymam go w bazie, tylko obliczam przy serializacji. Mniejszy narzut dla DB, większa elastyczność.
- **Tylko superużytkownicy mogą modyfikować dane (POST/PUT/DELETE)** - zachowanie integralności i bezpieczeństwa systemu.

---

## 🛠️ Instalacja

Aby uruchomić aplikację:
```bash
git clone https://github.com/vaqMAD/RestHitsVeloBank
cd timemate
docker compose up --build
```

---

## 🚀 Quick Start

### 1. Dostęp do Aplikacji

Po zbudowaniu obrazu możemy uruchomić testy: `docker-compose run --rm web python manage.py test`

Kontener należy uruchomić komendą `docker-compose up`

Po uruchomieniu kontenera aplikacja będzie dostępna pod adresem:
`http://127.0.0.1:8000` lub `http://localhost:8000`

### 2. API Dokumentacja

Interaktywna dokumentacja API jest dostępna pod adresem:`http://127.0.0.1:8000/api/schema/swagger-ui/`

### 🔑 Uwierzytelnianie i Autoryzacja

- **Username:** `admin@admin.com`
- **Password:** `1234`
- **Auth Token:** `9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b`

### Poziomy dostępu:
- **Publiczne** (GET) — odczyt danych bez logowania.
- **Chronione** (POST, PUT, DELETE) — wymagane logowanie jako superużytkownik, autoryzacja przez token za pomocą `TokenAuthentication`

### 🔐 Jak się uwierzytelnić?

```http
POST http://127.0.0.1:8000/hits/
Content-Type: application/json
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

### 🌱 Dane testowe

Generowanie danych testowych odbywa się automatycznie przy starcie kontenera. Opcjonalnie można je uruchomić ręcznie:
 `docker-compose run --rm web python manage.py seed_data`

---

## 📡 Nasz pierwszy API Request
📊 **Przeglądanie przykładowych danych**
- `GET http://127.0.0.1:8000/artists/`  
  _Pobierz listę artystów: Odpowiedź (status 200 OK): Lista 20 artystów_

- `GET http://127.0.0.1:8000/hits/`  
  _Pobierz listę hitów: Odpowiedź (status 200 OK): Lista 20 hitów_

⚙️ **Filtrowanie i sortowanie**

Zgodnie z Państwa prośbą dane w endpointcie `http://127.0.0.1:8000/hits/` są posortowane wedle daty utworzenia.

Obsługiwane są dodatkowe parametry filtrowania:
```http
GET http://127.0.0.1:8000/hits/?ordering=-created_at&created_at_before=2025-05-22
```

**🛠 Tworzenie naszych własnych rekordów**

Można również przesyłać własne obiekty. Aplikacja zawiera walidację logiki biznesowej - na przykład dla modułu hit,
jeśli artysta posiada już piosenkę o takiej nazwie, otrzymasz wyraźną odpowiedź o błędzie:

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
