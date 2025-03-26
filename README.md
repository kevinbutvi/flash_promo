# Flash Promos
El siguiente codigo busca ser una especie de POC para dar solucion al problema planteado.
La propuesta consta de 4 servicios principales corriendo en Docker con DockerCompose  
- web (Backend Python + Django REST)
- worker (Celery para manejo de tareas asincronas)
- redis (Redis, para manejo de cache)
- postgresql (Base de datos)
- wdb (utilizado para debugging)  
Dada la falta de tiempo se opto por priorizar la entrega de una solucion en cuanto a funcionalidad e integracion de servicios, dejando de lado calidad de codigo, relaciones de bases de datos, etc para que sean mejoraros en futuras versiones

# Justificacion de deciciones de arquitectura
La arquitectura es una integración bastante básica de DjangoREST, Postgres, Celery y Redis.
Los modelos creados y los endpoints son solo lo escencial para poder probar y mostrar una solución que cumpla con los requisitos y demostrar la capacidad de desarrollar e implementar una solución desde cero, que contemple varios aspectos a nivel arquitectura y creación de la app, aunque sacrificando calidad de código, validaciones, etc etc.por la falta de tiempo.

Las promociones se manejan de la siguiente manera. Hay un endpoint disponible para hacer CRUD de las mismas. Se permiten crear promociones dentro del mismo día y a futuro.
Si el backend recibe una promoción con fecha de inicio del corriente día pero en horario pasado se crea en ese momento una tarea en Celery para disparar los avisos de las mismas. En cambio si una promoción tiene fecha futura, se genera la creación de la tarea para que se ejecute al comienzo de la misma. Se pueden crear promociones como inactivas, las cuales no se ejecutarán.
La “notificación” es simbólica, sólo llama a una función que genera un log, posteriormente a esto vendría alguna integración de tipo websocket o similar para manejar la notificación inmediata de los usuarios, pero se pensó de esta forma para que sea asíncrona y no bloquee el hilo de ejecución.
La segmentación de usuarios se manejó mediante relacionar las segmentaciones con los usuarios y las mismas con las promociones (una promoción tiene relación con una tienda). De esta forma se filtran los usuarios que por segmento puedan acceder a dicha promoción y posteriormente acorde a la distancia que la promoción tiene establecida.

En cuanto al manejo del spam, los clientes en su modelo tienen un campo donde se guarda la fecha y hora de la última notificación que se les envió y a la hora de enviar notificaciones, se filtra por dicho valor para no enviar una nueva.

En cuanto a optimizaciones implementadas para el manejo de lo anteriormente mencionado, se utilizó Redis como caché para los modelos. Se cachean todos los modelos con la librería “cacheops” de forma automática y se implementó cache custom para el manejo de las reservas de promociones. 
Se guarda con una clave generada por combinación de valores las reservas con tiempo de caducidad de 1 minuto y se consultan directamente en caché sin necesidad de hacer consultas a la DB, aunque si se guardan las reservas en la postgres a modo de auditoría.
En cuanto al modelo de arquitectura y los servicios se opto por esta propuesta teniendo en cuenta los siguientes puntos:
Aislamiento y gestión eficiente: Cada servicio corre en un contenedor independiente, evitando conflictos y facilitando despliegues.
Escalabilidad: Se pueden aumentar instancias de Django, Redis o Celery según la carga sin afectar otros servicios.
Optimización de rendimiento: Redis reduce consultas a la base de datos, mejorando tiempos de respuesta.
Procesamiento asincrónico: Celery maneja tareas en segundo plano, evitando bloqueos en el backend.
Facilidad de despliegue y mantenimiento: Docker Compose simplifica la configuración, permite replicar entornos rápidamente y evitar conflictos de compatibilidades.
Alta disponibilidad: Puede integrarse con orquestadores como Kubernetes para mejorar redundancia y tolerancia a fallos.

La solución se pensó más a nivel de infraestructura, pensando en un mecanismo de caché y de tareas asíncronas para no generar cuellos de botella, tanto en backend como en la instancia de base de datos, no tanto así en el desarrollo de las clases y el modelado de datos por una cuestión de tiempos y velocidad de desarrollo.
La idea fue mostrar un poco de todos los aspectos en los cuales tengo experiencia y capacidad de pensar soluciones.

Mejoras localizadas para realizar en próximas versiones:
- Swagger para documentaciones de APIs
- Mejoras en los modelos de datos y relaciones
- Mejoras generales y personalizadas en administración de caché
- Administraciones de permisos y privilegios de usuarios
- Optimización de Endpoints para retornar solo información necesaria
- Reemplazar operaciones bucles "for" por iteradores o chunk para evitar tener en memoria grandes volumenes de datos
- Refactorizar código para tener métodos y funciones más atómicas (principios SOLID)
- Mejorar la tarea de "send_promo_notifications" que quedó con dependencias y con tareas que se podrían desacoplar para mejor funcionamiento y velocidad
- Mejoras y expansión de tests


## Pre-requisitos
- Crear y agregar variables de entorno en un archivo .env a la altura del "docker-compose.yaml"
- Tener instalado Docker
- Poseer conexion a internet

## Inicio de la app
Para levantar la app se requiere abrir una consola a la altura del archivo "docker-compose.yaml" y ejecutar los siguientes comandos
- docker compose up -d
- docker compose exec web python ./flash_promo/manage.py populate_demo_data

### Flujo de la app
La premisa de la solucion es la siguiente:  
Cuando se da de alta una FlashPromotion se avisa a los usuarios dentro del segmento y radio de distancia segun la tienda que tenga relacion con esa promocion. (esto se dispara de manera asincrona si la promocion es del mismo dia y esta en curso o se programa la ejecucion para la fecha de inicio de la promocion).  
Una vez notificados los mismos pueden hacer una reserva de dicha promocion, al hacerla la misma queda bloqueada para ese usuario y otro usuario que este dentro del segmento y distancia no podra reservarla, a menos que pase mas de 1 minuto y se caiga la reserva del primer usuario.  
Si dentro del rango de tiempo de reserva, el usuario completa la misma, la promocion se desactiva para todos lo usuarios.

## Servicios
La propuesta cuenta con un listado de endpoints con las siguientes finalidades  
- Django admin estara disponible en http://localhost:8000/admin y se podra logear con las credenciales declaradas en el .env

### Stores CRUD
Permite realizar CRUD de tiendas  
http://localhost:8000/api/market/stores/

### Products CRUD
Permite realizar CRUD para productos  
http://localhost:8000/api/market/products/

### Promotions
  - FlashPromo CRUD  
    Permite realizar CRUD de las promociones flash  
    http://localhost:8000/api/promotions/flash-promos/ 

    - FlashPromo Elegible (GET / returns the current available promotions of the querying user)  
      Permite obtener el listado de promociones para las cuales un usuario cumple con los requisitos de distancia, segmento y estan corriendo en ese momento  
      http://localhost:8000/api/promotions/flash-promos/eligible/

    - FlashPromo Running (GET / returns the list of running promotions of the querying user)  
      Retorna todas las promociones que estan corriendo en ese momento  
      http://localhost:8000/api/promotions/flash-promos/running/

  - PromoReservation (POST / Reserve a promotion for 1 minute for the querying user sending the promotion_id)  
    Permite hacer una reserva de una promocion  
    http://localhost:8000/api/promotions/promo-reservations/
  
  - PromoReservation/Complete (POST / complete a purchase for the querying user sending the promotion_id)  
    Permite completar la reserva de una promocion  
    http://localhost:8000/api/promotions/promo-reservations/{pk}/complete/

### Users
  - UserSegments (CRUD)  
  Permite realizar CRUD de segmentos de clientes  
  http://localhost:8000/api/users/user-segments/
  
  - ClientProfiles (GET)  
  Permite realizar CRUD de clientes  
  http://localhost:8000/api/users/clients-profiles/


## Tests
Se crearon algunos unittest para algunas apps para probar funcionalidades y endopoints. Para ello hay que ejecutar el siguiente comando y pasar como parametro la app a testear  
Apps con test: utils, market  
docker compose exec web python ./flash_promo/manage.py test NOMBRE_DE_LA_APP
