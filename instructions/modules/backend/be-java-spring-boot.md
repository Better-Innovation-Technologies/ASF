## Backend — Java + Spring Boot

| | |
|---|---|
| Language | Java {{java_version}} (LTS) |
| Framework | Spring Boot {{spring_boot_version}} (Spring MVC; WebFlux only where the I/O is reactive end to end) |
| Build | {{build_tool}} with the wrapper committed (`mvnw` / `gradlew`); dependency versions from the Spring Boot BOM |
| ORM / migrations | Spring Data JPA + Hibernate · {{be_migration_tool}} |
| Validation | Jakarta Bean Validation (`@Valid`) at the API boundary |
| Tests | JUnit 5 + AssertJ · Testcontainers for integration |

- Code under `{{be_modules_path}}/`; one package per domain module, holding its controller,
  service, repository, entities and DTOs. `@SpringBootApplication` sits in the root package.
- Controllers are thin: bind and validate a request record, call a service, return a declared
  response record. Business logic lives in `@Service` classes, never in a controller or an entity.
- DTOs are Java `record`s; an entity never crosses the HTTP boundary.
- Constructor injection only (no `@Autowired` on fields); dependencies are `private final`.
- Every relation is mapped (`@ManyToOne(fetch = LAZY)`, `@OneToMany(mappedBy = …)`); a bare `*Id`
  column without its mapping is a blocking violation. `spring.jpa.open-in-view` is `false`; reads
  that need a relation use `JOIN FETCH` or `@EntityGraph`, never a lazy load inside a loop (N+1).
- Transactions are explicit: `@Transactional` on the service method that owns a multi-step
  operation, `readOnly = true` for reads; never on controllers or repositories. Schema changes go
  through {{be_migration_tool}} only — `spring.jpa.hibernate.ddl-auto` is `validate` or `none`.
- Configuration through `@ConfigurationProperties` records annotated `@Validated`, bound from the
  environment; the application refuses to start on a missing value. No `System.getenv()` or
  `@Value` in business code.
- Logging through SLF4J (`LoggerFactory.getLogger`), configured once in `{{be_logger_path}}`; the
  trace id is in the MDC (`traceId`, set by Micrometer Tracing) and in every entry.
  `System.out.println` and `printStackTrace()` only in scripts and tests.
- Exceptions are mapped to HTTP responses in one `@RestControllerAdvice`; a controller never
  catches an exception to build an error response by hand.
- Integration tests run against the real database in Testcontainers (`@ServiceConnection`), never
  against H2 or another substitute; mocks only at the boundaries the service does not own.
