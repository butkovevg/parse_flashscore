
## Инструкция по миграции БД
1. Для накатывания миграций, если файла alembic.ini ещё нет, нужно запустить в терминале команду:
```alembic init migrations```
2. В alembic.ini нужно задать адрес базы данных, в которую будем катать миграции.
sqlalchemy.url = postgresql://postgres:password@localhost:5432/postgres
3. В папке с миграциями открываем env.py, там вносим изменения:
``` 
from src.model.tables import Base
target_metadata = Base.metadata
# target_metadata = None 
```
4. Для создания миграции вводим:
```alembic revision --autogenerate -m "my_comment"```
5. ол



