# Phase 6 — Strategy questions

**Pattern / focus:** Strategy.

**Read first:** [Guide 06](../../materials/guides/06-strategy.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example shipping quotes) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to irrigation (or lighting) policies, location context, and the automation API from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Strategy in plain language. How does the **context** use a strategy, and why must “choose which algorithm” stay separate from “run the algorithm”?

> [!NOTE]
> ***Your Answer***
>
> _(The strategy pattern lets us choose between different algorithms without changing the main context. The context gives the selected strategy the needed data and calls decide(). Choosing which strategy to use should stay separate from running it because the same context can work with different strategies.)_

2. Name the participants (**strategy**, **concrete strategies**, **context**, **client**). What goes wrong when all policies live as `if/elif` inside the context (or inside an HTTP router)?

> [!NOTE]
> ***Your Answer***
>
> _(The strategy is the common interface, the concrete strategies are the different algorithms, the context contains the data given to the strategy and the client chooses which strategy to use. If everything is put into if/elif statements, the context or API becomes full of different rules and gets harder to maintain. Adding another strategy would also mean changing the existing code.)_

3. When should you use Strategy, and when should you skip it (one algorithm only; or the variation is a **lifecycle mode** rather than a chosen policy)?

> [!NOTE]
> ***Your Answer***
>
> _(Strategy is useful when we have several different algorithms or policies that can be selected. We do not really need it when there is only one algorithm and no variation. It is also not the best choice when the changes are about an object's lifecycle or state, because that is more suitable for the state pattern.)_

## B. This phase of the application

4. In this lab, what does a strategy’s `decide(context)` return (action + reason)? Give a concrete difference you implemented (or were required to implement) between **conservative** and **aggressive** on the **same** moisture reading and zone thresholds.

> [!NOTE]
> ***Your Answer***
>
> _(decide(context) returns a recommendation with an action and a reason. For e.g. with moisture 0.40, low threshold 0.25 and high threshold 0.45, the conservative strategy returns wait because the moisture is inside the normal range. The aggressive strategy returns irrigate because it reacts when moisture is below the high threshold.)_

5. Where do the numbers in `LocationAutomationContext` (or your equivalent) come from? Latest moisture may already be in `sensor_readings` from a manual read, the simulation sampler, or MQTT translation — why does this phase not add a scheduler or a broker? Why must strategies receive a plain context object, not SQLAlchemy rows or FastAPI types? Why are thresholds read from **zones**, not hardcoded in the strategy class?

> [!NOTE]
> ***Your Answer***
>
> _(The moisture value comes from the latest reading in sensor_readings for a sensor assigned to that zone. The low and high values come from that zone's stored thresholds. This phase does not add another scheduler or MQTT broker because phase 5 already handles readings and this phase only uses the data. The strategy gets a plain context object so it does not depend on SQLAlchemy or FastAPI. The thresholds come from the zones because different zones can have different settings.)_

6. The active `strategy_key` is **persisted** per `location_id` (for example in `automation_rules`). Why must `POST .../automation/evaluate` use the **saved** key rather than a key the client sends only in that request? What happens on the next evaluate after the operator changes strategy but moisture stays the same?

> [!NOTE]
> ***Your Answer***
>
> _(The saved key makes the selected strategy the actual configuration of that location instead of something temporary from one request. When the operator changes the strategy, the new key is stored in the database. The next evaluate reads that new key, so the same moisture reading can produce a different recommendation.)_

7. Strategy **recommends** (irrigate / wait). It should not itself start a pump. Why keep **decide** separate from **execute**? Which later pattern is meant to carry out the action?

> [!NOTE]
> ***Your Answer***
>
> _(The strategy should only decide what should happen, not control the hardware itself. Keeping decide separate from execution makes the strategy easier to test and change without depending on real devices. The later actuator flow, including the phase 9 Decorator work around ActuatorPort, is where execution side behaviour can be added.)_

## C. Compare, contrast, and scenarios

8. Contrast Strategy with **State** (Phase 8). Both delegate to an object with the same shape. Who typically **changes** the active object, and is the variation a **policy** or a **lifecycle**?

> [!NOTE]
> ***Your Answer***
>
> _(Strategy is usually changed by the client or application when we want a different policy or algorithm. State is usually changed because the object's own lifecycle changes. So strategy is mainly about choosing a policy, while state is about what condition or state the object is currently in.)_

9. Contrast Strategy with **Adapter** (Phase 5) and with **Builder** (Phase 4). Which one translates a foreign API, which one assembles a valid aggregate, and which one swaps an algorithm?

> [!NOTE]
> ***Your Answer***
>
> _(Adapter translates a different or foreign interface into the format our application expects. Builder creates a complete and valid object step by step, like the location configuration with its zones. Strategy lets us swap between different algorithms, such as conservative and aggressive irrigation decisions.)_

10. A classmate writes one “mega-strategy” that still contains `if conservative` / `if aggressive` inside a single class. Another strategy class calls the actuator adapter to water immediately. Explain why each is a trap.

> [!NOTE]
> ***Your Answer***
>
> _(The mega-strategy is a problem because the different algorithms are still mixed together instead of being separate strategy classes. Adding another strategy would make that class bigger again. The second class is also a problem because the strategy should only make the recommendation. Starting the pump is execution logic and should stay outside the strategy.)_