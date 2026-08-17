from __future__ import annotations

import argparse

from rbek import GovernedAction, Policy


policy = Policy.allow_if(
    'amount <= 1000 and currency == "EUR" '
    'and recipient_trusted == True'
)

payment = GovernedAction(
    "payment",
    policy=policy,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Framework-neutral RBEK payment governance example."
        )
    )

    parser.add_argument(
        "--amount",
        type=float,
        default=1500.0,
        help="Proposed payment amount.",
    )

    parser.add_argument(
        "--currency",
        default="EUR",
        help="Proposed payment currency.",
    )

    parser.add_argument(
        "--recipient-trusted",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Whether the proposed recipient is trusted.",
    )

    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    result = payment.evaluate(
        amount=args.amount,
        currency=args.currency,
        recipient_trusted=args.recipient_trusted,
    )

    print("status:", result.status)
    print("executed:", result.executed)


if __name__ == "__main__":
    main()
