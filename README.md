# Foodgram

## Инструкция

### 1. Клонируйте репозиторий

```bash
git clone git@github.com:AraKi-Chragian/foodgram-st.git
cd foodgram-st
```

### 2. Файл `.env` 

Файл `.env` в корне директории `infra/` уже создан. Вот его содержимое (при необходимости изменить):

```env
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=your_password
DB_HOST=db
DB_PORT=5432
USE_SQLITE=False
```

### 3. Соберите и запустите контейнеры

```bash
docker-compose -f infra/docker-compose.yml up -d --build
```


## Доступ

* **Backend:** [http://localhost:8000](http://localhost:8000)
* **Frontend:** [http://localhost/](http://localhost/)
* **Админка:** [http://localhost:8000/admin/](http://localhost:8000/admin/)

---

## Автор

**Ara52, Ararat Chragian**  
