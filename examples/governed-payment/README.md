# Framework-neutral governed payment

This example shows that RBEK can govern a proposed action without an
agent framework.

No agent framework is required.

No LLM is required.

No API key is required.

No payment provider is called.

No money moves.

The example uses the published RBEK Python SDK:

~~~text
rbek==0.3.0a3
~~~

## Business policy

The proposed payment must satisfy:

~~~python
Policy.allow_if(
    'amount <= 1000 and currency == "EUR" '
    'and recipient_trusted == True'
)
~~~

The policy is attached to a normal `GovernedAction`:

~~~python
payment = GovernedAction(
    "payment",
    policy=policy,
)
~~~

There is deliberately no execution binding.

The example only calls:

~~~python
payment.evaluate(...)
~~~

It never calls `payment.execute(...)`.

## DENIED proposal

Run:

~~~bash
python quickstart.py
~~~

The default proposal is:

~~~text
amount=1500
currency=EUR
recipient_trusted=True
~~~

Expected result:

~~~text
status: DENIED
executed: False
~~~

This is a normal business-policy rejection.

It is not a TAMPERED_GATE.

## ALLOWED proposal

Run:

~~~bash
python quickstart.py --amount 500
~~~

Expected result:

~~~text
status: ALLOWED
executed: False
~~~

ALLOWED does not mean executed.

It means the local business policy permits the proposed action.

There is no payment execution binding in this example, so the proposal
does not cross an external execution boundary.

## Why this example exists

LangGraph, CrewAI, and OpenAI Agents SDK can all propose governed actions,
but RBEK itself does not depend on any of those frameworks.

RBEK is independent of the framework that proposed the action.

The application proposes an action.

RBEK evaluates whether the proposal satisfies deterministic business
policy.

External execution remains a separate authority.

## Deliberate non-goals

This example does not implement:

- Stripe
- Adyen
- bank transfers
- card charges
- refunds
- Treasury execution
- any payment provider
- any payment capability
- any real money movement

A future real payment integration would require a separately implemented
and certified execution binding.
