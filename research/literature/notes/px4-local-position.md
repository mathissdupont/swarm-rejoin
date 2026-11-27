# Source note: PX4 estimator evidence fields

- Source: `px4-local-position`, [pinned message definition](../../library/px4-local-position/README.md)
- Checked: 2026-11-27; complete definition inspected, no PX4 adapter or detector validation

The native definition supplies boot-relative timestamps, validity flags, position/velocity reset counters and error estimates. `timestamp` is microseconds since system start. Position-reset counters are `uint8`; they are not persistent security counters, unique boot identifiers or authentication evidence.

R10/T5 must distinguish a companion application's restart from an estimator or flight-controller restart. Restarting the application we update does not imply that a separately running flight-controller estimator resets. For that case, reacquire current estimator output and rebind the communication/application session instead of automatically claiming full-filter reinitialization.

Our proposed contract must also bind producer/boot identity, configuration, reference frame, sample age and source continuity. Equal reset-counter values across boots, stale caches or wraparound cannot establish continuity. Field presence alone does not prove trustworthy transport, sensor accuracy or genuine GNSS position; those remain explicit model/integration assumptions.
