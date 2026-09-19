# CompliNet implementation process

This note records the working approach for stabilizing and extending the project without drifting into unnecessary platform complexity.

## 1. Stabilize the compliance engine first

The first task was to remove the unresolved merge artifacts in the compliance service and align the rule set with the actual FRR lab environment instead of the older Cisco mock setup.

Key conclusions:
- the project must evaluate the current FRR lab rules (`SYS-*` and `OSPF-*`)
- generated config output should be compared against a real baseline
- drift and compliance are different concepts and must be tracked separately

## 2. Keep the rule model explainable

Rule results should not only say PASS or FAIL. They should also include the details required to support human review:
- expected
- actual
- reason
- remediation

This makes the system suitable for the Detect -> Analyse -> Explain -> Remediate flow without requiring a dashboard rewrite first.

## 3. Separate collection by `source`

The project should not conflate the collection strategies for lab and production systems. The explicit collector split is:

- `containerlab` -> `ContainerlabCollector`
- `netmiko` -> `NetmikoCollector`

The selection logic is handled by the `collectors` package so each device type follows the appropriate path.

## 4. Preserve the lab, but keep future expansion open

The lab continues to use Containerlab and FRR. The Netmiko path remains available for real devices without abandoning the current research platform. This keeps the architectural direction clear without introducing a large premature abstraction layer.

## 5. Validate before extending further

Once the analyzer and collector logic are stable, the next tasks should be:
- explainable findings in the dashboard
- Linux controller health metrics
- human-approved remediation flow
- audit trail and post-remediation verification

This keeps the implementation incremental and avoids building unnecessary services before the core research question is fully proven.
