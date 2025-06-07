# listing-app

## Relationships between tables

```
+------------------+     1        *     +-------------------------+
|     Listing      |------------------>| StringPropertyValue     |
|------------------|                   |-------------------------|
| listing_id (PK)  |<------------------| listing_id (FK)         |
| scan_date        |     1        *     | property_id (FK)        |
| is_active        |                   | value (String)          |
| dataset_entity_ids|                  +-------------------------+
| image_hashes     |
|                  |     1        *     +-------------------------+
|                  |------------------>| BoolPropertyValue       |
|                  |<------------------| listing_id (FK)         |
+------------------+                   | property_id (FK)        |
                                       | value (Boolean)         |
                                       +-------------------------+

        ^                                      ^
        |                                      |
        |                                      |
        |            *                         * 
        |          (FK)                       (FK)
+------------------+                   +-------------------------+
|     Property     |<------------------| Property (shared)       |
|------------------|                   +-------------------------+
| property_id (PK) |
| name             |
| type             |
+------------------+

+------------------+
| DatasetEntity    |
|------------------|
| entity_id (PK)   |
| name             |
| data (JSON)      |
+------------------+
```

### Migrations with Alembic
I have used alembic to generate and run migration in the db. This was done through:

1. Initialize alembic
``` bash
alembic init alembic
```

2. Setup models: write models in app.models.schemas

3. Set `env.py` to import your models
``` python
from app.models.schemas import Base
target_metadata = Base.metadata
```

4. Create a new migration
``` bash
alembic revision --autogenerate -m "Add models" # this will autogenerate the obvious migration
```

5. Apply migrations
``` bash
alembic upgrade head
```

<b> New migration </b> <br>
For new models or changes in the schemas, we can generate a new file under versions
or autogenerate the changes. Then we can run the upgrade command to apply the changes.