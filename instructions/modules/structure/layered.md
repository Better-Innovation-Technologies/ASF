## Internal structure — layered (three-tier)

Every backend module under `{{be_modules_path}}/<domain>/` has three layers, called only downwards:

```
<domain>.router / controller   # HTTP: validation and a service call — thin
<domain>.service               # business logic and orchestration
<domain>.repository            # data access — no query lives outside this file
<domain>.schema / types        # request/response schemas, DTOs, enums
<domain>.test                  # tests
```

- A router never touches the database; a repository never contains business rules.
- Shared utilities go in `{{be_lib_path}}`; no domain code outside its module.
