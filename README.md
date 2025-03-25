# flash_promo
Market Flash Promotions


## Run Project
  - docker compose up
  - docker compose exec web python ./flash_promo/manage.py populate_demo_data


## Services

### Stores CRUD
http://localhost:8000/api/market/stores/

### Products CRUD
http://localhost:8000/api/market/products/

### Promotions
  - FlashPromo CRUD
    http://localhost:8000/api/promotions/flash-promos/ 

    - FlashPromo Execute Promotion (POST / execute now a list of available future promotions sending a list of promotion_id)
      http://localhost:8000/api/promotions/flash-promos/execute_promotion/

    - FlashPromo Elegible (GET / returns the current available promotions of the querying user)
      http://localhost:8000/api/promotions/flash-promos/eligible/

    - FlashPromo Running (GET / returns the list of running promotions of the querying user)
      http://localhost:8000/api/promotions/flash-promos/running/

  - PromoReservation (POST / Reserve a promotion for 1 minute for the querying user sending the promotion_id)
    http://localhost:8000/api/promotions/promo-reservations/
  
  - PromoReservation/Complete (POST / complete a purchase for the querying user sending the promotion_id)
    http://localhost:8000/api/promotions/promo-reservations/{pk}/complete/

### Users
  - UserSegments (CRUD)
  http://localhost:8000/api/users/user-segments/
  
  - ClientProfiles (GET)
  http://localhost:8000/api/users/clients-profiles/


## Tests
- TODO