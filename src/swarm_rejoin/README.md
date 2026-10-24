# Implementation boundary map

This directory intentionally contains no executable simulator or security implementation yet. Start after the team selects a concrete question within GNSS, secure updates, and UAV swarms.

Proposed modules:

| Module | Responsibility | Boundary |
| --- | --- | --- |
| `navigation` | GNSS/IMU observations, consistency evidence, uncertainty and age | Does not grant roles or declare a device uncompromised |
| `updates` | Verified release metadata, staged transfer/activation, permitted recovery | Uses real verification libraries when implemented; does not trust a Boolean self-report |
| `evidence` | Session binding, provenance, freshness, software/navigation appraisal | Exposes appraised evidence to policies; separate from hidden truth |
| `policies` | Baselines and candidate joint decisions under hard constraints | Cannot read evaluator ground truth |
| `simulation` | Agent/mission dynamics, faults, reproducible event scheduling | Defines physical and operational modeling limits |
| `evaluation` | Independent labels, metrics, uncertainty and traces | Does not define safety from the policy's own score |
| `adapters` | A later PX4/companion-service case study | Must not equate a service restart with autopilot firmware flashing |

These names are implementation proposals, not stable APIs. Select packaging and dependencies when executable behavior exists.
