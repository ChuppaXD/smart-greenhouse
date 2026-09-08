Phase 1 — Skeleton questions
Pattern / focus: Course intro and an empty-but-running three-tier skeleton (no GoF pattern this phase).

Read first: Guide 01 · Requirements

How to answer
Use your own wording. Do not paste textbook definitions or teaching-example class names as if they were your greenhouse types.
When a question asks about this application, refer to what you built (or what the lab required): layers, routes, and tooling.
Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
A. Pattern
1. In your own words, what is a design pattern? What is it not?
-A design pattern is a common way of solving a problem that appears many times in software design. It gives a general idea of how classes and objects can work together.

-It is not readymade code that we can just copy into every project. It is more like a useful solution idea and we should use it only when it actually fits the problem.


2. Name the three GoF pattern families. For each family, give one-sentence: what kind of design problem it addresses. Then place Factory Method and Strategy into the correct family.
-The three GoF pattern families are;
i. Creational patterns: They deal with how objects are created.
ii. Structural patterns: They deal with how classes and objects are connected together.
iii. Behavioral patterns: They deal with how objects communicate and how responsibilities are shared.

-Factory Method belongs to the Creational family because it is about creating objects.

-Strategy belongs to the Behavioral family because it is about choosing between different behaviours or algorithms.


3. A teammate wants to add a pattern “because it is on the course list,” even though the feature is small and unlikely to grow. When should you skip a pattern? What risk do you take if you apply one too early?
-I think we should skip a pattern when the problem is still simple and normal code already solves it clearly.

-Using a pattern too early can make the code more complicated than necessary. It can add more classes and relationships and then it becomes harder to understand and maintain. We should have a real reason for using a pattern; not just use it because it is on the course list.


B. This phase of the application
4. Why does Phase 1 ship a vertical slice that does almost no greenhouse business logic? What does “empty but running” prove that a folder of unimplemented classes would not?
-Phase 1 is mainly checking that the basic application structure works before adding the real greenhouse features. In my project, the backend can run, connect to PostgreSQL, answer /health, and show the API documentation.

-“Empty but running” proves that the different parts can actually work together. For e.g. my frontend can call the FastAPI backend and the backend can check the PostgreSQL database. A folder with unfinished classes would not prove that these parts can communicate or that the application can really start.


5. List the four backend layer packages used in this course (domain, application, infrastructure, interfaces/api). For each, state what belongs there and give one example of something that must not live in domain.
i. domain: This is where the main business concepts and business rules should go. For this greenhouse project, later this could contain greenhouse related domain objects and rules.
ii. application: This layer is for the application use cases and coordinates what the system should do. It should connect the business logic with the outside parts without putting infrastructure details into the domain.
iii. infrastructure: This contains technical things needed to run the application, such as database connection and settings. In my project, db.py and settings.py are here
iv. interfaces/api: This is where the API endpoints are exposed. In my project, health.py contains the /health route.

-For e.g. FastAPI-specific code should not live in domain, because the domain should not depend on the web framework.


6. What does GET /health return, and why does it check the database instead of only reporting that the HTTP process is up? Why is API documentation served at /scalar, and why is /docs disabled?
-In my project, GET /health returns:
{"status":"ok","db":"ok"}
when both the API and database are working. When the database is not available, it returns a degraded status and db: fail

-It checks the database because an API process can still be running while the database is broken. The health endpoint therefore gives a more useful picture of whether the application backend is really working.

-The API documentation is served at /scalar because Scalar is the documentation tool chosen for this course. The normal FastAPI /docs page is disabled so the project uses Scalar as its API reference instead.


7. Phase 1 requires Alembic (or equivalent) with a baseline migration and no business tables such as devices. Why introduce the migration toolchain before any product schema? What would go wrong if you created tables by hand in Postgres and only added migrations later?
-The migration tool is introduced early so the project has a proper way to track database changes from the beginning. In my phase 1 database, there is only the migration baseline and no real greenhouse business tables yet.

-If tables were created manually first and migrations were added later, the database and the migration history could become different. Then, it would be harder to know what was actually created; and setting up the same database on another computer could give different results.

C. Compare, contrast, and scenarios
8. Explain dependency direction in this skeleton: which layers may import which? Why must domain code not import FastAPI, SQLAlchemy, or Pydantic models used as HTTP schemas?
-The general idea is that the inner business part should not depend on the technical outer parts.

-The domain should be independent. Infrastructure and API code can depend on the application or domain, but the domain should not depend on FastAPI, SQLAlchemy or API-specific Pydantic models.

-This makes the business logic easier to test and change. For e.g. if we changed FastAPI later, the greenhouse business rules should not need to be rewritten.


9. The frontend cannot show a healthy badge. A classmate blames “the patterns.” What should you check first (stack, CORS/proxy, health JSON), and why is that a Phase 1 concern rather than a later pattern concern?
-I would first check whether all the basic parts are running.

For my project I would check:

Is the frontend running?
Is FastAPI running on port 8000?
Does /health return the expected JSON?
Is the frontend calling the correct API address?
Is CORS configured correctly?

-I would not blame the design patterns first because there are no GoF pattern implementations in phase 1. A health badge is part of the basic connection between the frontend, API and database, so it is a skeleton/setup issue.


10. Course completion is at Phase 12, not Phase 1. What is still missing after a successful skeleton, and how do later phases add behaviour without rewriting the foundations you laid here?
-After Phase 1, the application is mostly just a working skeleton. It does not yet have the full greenhouse business logic, sensor handling, actuators, automation, WebSockets, authentication or the design pattern implementations from later phases.

The idea is that later phases can add these features into the existing layers. For e.g. the domain and application layers can get more real greenhouse behaviour, while the infrastructure and API parts can expose that behaviour. The phase 1 structure gives a foundation so we do not need to throw away the whole project when adding new features.