# R03 - GNSS/IMU Navigation Integrity Research Report

**Issue:** [R03 / #3](https://github.com/mathissdupont/swarm-rejoin/issues/3)  
**Proposed lead:** Ceren Tolunay (@cerentolunay)  
**Imported:** 2026-10-31. Consolidated research draft; no experimental results.

## Provenance and evidence status

English repository edition of the supplied `R03_GNSS_IMU_Integrity_Research_Report.md`. The English technical core is retained; the Turkish introduction and appendices are rendered in English below. The supplied report describes three survey readings and four pages of handwritten notes. Those PDFs, photographs, and previous conversations were not available for independent verification during this import. Statements about their contents are inherited from the supplied report, not newly completed literature reviews. No paper access date or full-text review is implied by the import date.

Evidence labels: **[S]** source-attributed information in the supplied report; **[N]** researcher interpretation; **[P]** proposed design; **[U]** unverified detail. A source attribution is not independent confirmation.

## Executive summary and researcher notes

A returning UAV should report measurable navigation evidence rather than position alone. The candidate is a loosely coupled error-state EKF with innovation/NIS monitoring. Position covariance, measurement age, and GNSS clock integrity remain separate. The candidate does not prove position, uniquely identify spoofing, or provide device attestation. [P]

The handwritten-note synthesis in the supplied report distinguishes accuracy, availability, reliability, and integrity; random uncertainty, bias, drift, and outliers; and fault detection from protection-level estimation. Its illustrative model is `z_measured = z_true + bias + drift(t) + random_noise`. A defensible protection level cannot be assumed. RAIM/A-RAIM, model/coherence-based fault detection and exclusion, RANSAC, maximum consensus, and robust factor graphs are possible reading directions. Robustness to non-Gaussian or correlated errors is a research question, not an established literature gap. [N]

GNSS supplies an external reference while INS supplies frequent motion propagation with accumulating drift. Loosely, tightly, and deeply coupled architectures differ in their measurement interfaces. Filtering, particle methods, and graph methods offer different estimation and uncertainty representations. UAV attitude and maneuvers prevent direct transfer of ground-vehicle constraints. IMU, GNSS, UWB, and vision may provide complementary evidence, but their errors may be dependent. [N]

The broader researcher question asks how a returning UAV can support independent appraisal of reported position, trajectory, sensor information, and software state. R03 addresses only its navigation part. A signature does not prove a measurement; a nonce does not establish a historical trajectory; UWB and energy/RPM observations do not automatically prove a route. High NIS is not a specific spoofing diagnosis and low NIS does not establish attack absence. UWB, vision, and attestation are extensions rather than implemented R03 capabilities. [N/P]

## 1. Research Question

What navigation evidence can a returning UAV provide, what uncertainty does it express, and when is it insufficient for a mission role?

### Scope

This task investigates how a UAV returning to an autonomous swarm can report its estimated navigation state together with evidence about the consistency, uncertainty, and freshness of that estimate.

The objective is not to prove that the UAV has never experienced a cyber-physical attack. Instead, the objective is to define measurable navigation evidence and identify conditions under which that evidence is insufficient to authorize particular mission roles.

The initial scope covers GNSS/IMU navigation integrity. Cooperative UWB ranging, visual localization, and independent swarm observations are identified as potential extensions, not implemented capabilities.

## 2. Literature Foundation

### 2.1 Localization Integrity

Maharmeh et al. (2025), *A Comprehensive Survey on the Integrity of Localization Systems*, distinguishes localization integrity from accuracy and examines protection levels, fault detection and exclusion, and robust estimation.

The paper identifies four relevant error categories:

- Random uncertainty
- Systematic bias
- Time-dependent drift
- Outliers

It also distinguishes fault detection and exclusion from error-bound estimation. These are complementary rather than interchangeable functions.

**Implication for R03:** A small innovation residual or a low estimated covariance cannot, by itself, establish trustworthy navigation. The system must explicitly represent uncertainty and monitoring limitations.

### 2.2 GNSS/INS Integration

Boguspayev et al. (2023), *A Comprehensive Review of GNSS/INS Integration Techniques for Land and Air Vehicle Applications*, reviews loosely coupled, tightly coupled, and deeply coupled integration architectures.

GNSS provides external navigation measurements, while INS propagates motion estimates using inertial measurements. In the absence of GNSS corrections, accumulated inertial errors can degrade position estimates.

**Implication for R03:** A loosely coupled GNSS/INS estimator is selected as an initial simulation baseline because it allows position/velocity measurements and inertial propagation to be modeled separately.

This selection is a practical hypothesis, not a claim that loosely coupled integration is optimal.

### 2.3 Multi-Sensor Localization

Alipourvarmazabadi and Ebner (2026), *Robot Localization: A Comprehensive Survey from Classical Methods to Intelligent Autonomy*, organizes localization around estimation algorithms, map representations, and sensor modalities.

The survey includes filtering-based, sample-based, graph-based, and learning-augmented approaches, as well as IMU, UWB, camera, LiDAR, and GNSS observations.

**Implication for R03:** The evidence contract should be extensible to independent observations. However, combining multiple sensors does not automatically guarantee independent errors or resistance to malicious measurements.

## 3. Candidate Integrity Monitor

### 3.1 Baseline Architecture

**Proposed estimator:** Loosely coupled error-state Extended Kalman Filter (EKF).

**Proposed sensors:**
- Three-axis accelerometer and gyroscope
- GNSS position and velocity measurements

**Proposed navigation state:**
- 3D position
- 3D velocity
- Orientation
- Accelerometer bias
- Gyroscope bias

The estimator propagates navigation state using inertial measurements and applies GNSS updates when available.

### 3.2 Innovation-Based Consistency Monitoring

For a measurement z_k, the innovation is:

r_k = z_k − h(x̂_k|k−1)

Its covariance is:

S_k = H_k P_k|k−1 H_kᵀ + R_k

The proposed normalized innovation squared statistic is:

NIS_k = r_kᵀ S_k⁻¹ r_k

For a correctly specified linear-Gaussian measurement model, the NIS statistic can be compared against a chi-squared reference distribution with degrees of freedom equal to the innovation dimension.

In the nonlinear UAV setting, threshold behavior must be validated empirically, including model mismatch and temporal correlation.

### 3.3 Monitor Outputs

- Innovation vector and covariance
- NIS statistic and configured threshold
- Monitor decision: PASS, ALERT, or UNKNOWN
- Number of valid measurements
- GNSS availability
- Filter health and numerical validity
- Configuration identifier

**Interpretation limits:**
- ALERT indicates statistical inconsistency, not uniquely spoofing.
- PASS does not prove the absence of a sophisticated attack.
- UNKNOWN must be used when the monitor cannot evaluate its assumptions, including during GNSS measurement absence.
- Estimated covariance is not a guaranteed protection level.

## 4. Explicit Assumptions

### Estimator assumptions
- The EKF model and covariance propagation are implemented correctly.
- Process and measurement noise models are calibrated.
- Filter consistency is evaluated before using NIS thresholds operationally.

### Sensor assumptions
- IMU sampling frequency, noise, bias stability, and saturation limits are documented.
- GNSS position/velocity accuracy assumptions are documented.
- Sensor lever arms, coordinate frames, and synchronization are modeled.
- Sensor errors are not assumed independent without justification.

### Motion assumptions
- The simulated UAV operates in 3D.
- Maximum acceleration, angular velocity, and maneuver profiles are bounded and recorded.
- Stationary-ground-vehicle constraints are not transferred to UAV flight without justification.

### Time assumptions
- Measurement timestamps and receiver-arrival timestamps are distinguished.
- Evidence freshness is evaluated using a trusted or bounded local time reference.
- GNSS time is not the sole trusted clock in scenarios where GNSS manipulation is considered.
- Clock integrity is reported separately from position consistency.

### Threat-model assumptions
The baseline investigates measurement faults, GNSS disturbances, and inconsistent navigation evidence.

Full compromise of the flight controller, falsification of all sensor outputs, or compromise of the evidence producer is outside the baseline guarantee.

## 5. Navigation Evidence Contract

The returning UAV should provide a structured navigation evidence record containing the following fields.

| Group | Required fields | Meaning |
|---|---|---|
| Identity | UAV identifier, evidence version | Identifies the reporting entity and schema |
| State | Position, velocity, orientation, reference frame | Estimated navigation state |
| Uncertainty | State covariance, estimator status | Model-based estimation uncertainty |
| Consistency | NIS, threshold, monitor result, configuration ID | GNSS/INS agreement under model assumptions |
| Freshness | Measurement timestamp, receipt timestamp, age, time-source status | Whether the evidence is sufficiently recent |
| GNSS status | Availability, outage duration, receiver quality flags | Availability and quality context |
| Clock integrity | Status, supporting monitor/reference | Separate assessment of time-source trust |
| Provenance | Sensor identifiers, software/configuration version | Traceability of evidence generation |
| Limitations | Missing fields, unsupported checks, invalid assumptions | Prevents unsupported trust conclusions |

An evidence record may contain unavailable or unknown fields. Missing evidence must not silently be interpreted as successful verification.

The contract represents navigation evidence, not cryptographic proof of physical location.

## 6. Fault and Disturbance Scenarios

| ID | Scenario | Fault injection | Primary evaluation |
|---|---|---|---|
| S0 | Nominal flight | Calibrated benign sensor noise | False alarms and filter consistency |
| S1 | IMU drift | Accelerometer/gyro bias and random walk | Error growth and covariance consistency |
| S2 | GNSS outage | Suppress GNSS updates for controlled durations | Uncertainty growth, monitor UNKNOWN behavior |
| S3 | Step bias | Sudden GNSS position/velocity offset | Detection rate and delay |
| S4 | Ramp bias | Gradually increasing GNSS offset | Sensitivity to slow deviations |
| S5 | Stale evidence | Delay or replay previously valid measurements | Freshness rejection |
| S6 | Correlated faults | Shared or temporally correlated measurement errors | Robustness to violated independence assumptions |
| S7 | GNSS clock anomaly | Introduce time bias/drift or inconsistent timing | Time-source integrity and freshness behavior |

The baseline must also include normal maneuvers that can produce large residuals without malicious activity.

Step and ramp biases are fault models. They may represent aspects of spoofing behavior but must not be equated with a complete physical-layer spoofing simulation.

## 7. Independent Ground Truth

Simulation ground truth must be generated and stored independently from the observations made available to the navigation estimator and admission logic.

Ground truth should include:

- Actual position, velocity, and orientation
- Fault onset and duration
- Injected fault type and magnitude
- Actual measurement age
- Actual navigation error
- Mission-role safety conditions

The evaluator must not use the EKF's own estimate as independent truth.

## 8. Calibration and Validation

### Phase A — Parameter identification

Document or estimate:

- IMU sampling rate and noise density
- Accelerometer and gyro bias characteristics
- GNSS measurement noise and update rate
- Sensor timing uncertainty
- Motion and maneuver bounds
- Initial-state uncertainty
- Process-noise and measurement-noise covariance assumptions

Use sensor specifications, recorded data, and relevant primary literature to justify parameter ranges.

### Phase B — Nominal calibration

1. Generate or collect fault-free trajectories.
2. Calibrate the estimator's process and measurement noise.
3. Evaluate NIS distribution and temporal behavior.
4. Select candidate monitoring thresholds for specified nominal false-alarm targets.
5. Freeze thresholds before final fault evaluation.

### Phase C — Fault validation

Evaluate all defined fault scenarios across multiple trajectories, seeds, magnitudes, durations, and operating conditions.

Separate calibration data from final evaluation data.

### Phase D — Metrics

- False-alarm probability or rate, with its denominator and evaluation window defined
- Missed-detection probability within a specified detection window
- Detection delay
- Position and velocity RMSE
- Covariance consistency and empirical uncertainty coverage
- Fraction of time evidence is unavailable or UNKNOWN
- Evidence freshness violations
- Mission-role false admission and false exclusion, when an admission policy is defined

Results must report the fault model and operating assumptions. No universal detection guarantee is claimed.

## 9. Proposed Mission-Role Evidence Policy

The integrity monitor should not independently decide whether a UAV is safe for every mission role.

A downstream policy may use:

- Current position uncertainty
- Independent consistency observations, when available
- Evidence age
- Monitor validity
- GNSS/clock integrity status
- Role-specific separation and safety requirements

Candidate policy outputs are:

- ISOLATED
- OBSERVATION
- RESTRICTED
- FULL

The exact mapping from evidence to roles remains a separate design and validation task.

A UAV with insufficient evidence may be restricted without being classified as malicious.

## 10. Research Limitations and Open Questions

1. How accurately does a loosely coupled EKF represent UAV uncertainty during aggressive maneuvers?
2. How should correlated GNSS and inertial errors affect consistency monitoring?
3. Can a protection level be constructed with defensible integrity-risk assumptions for this sensor configuration?
4. Which independent observations, such as cooperative ranging or visual localization, are feasible in the swarm?
5. What timing reference is sufficient for freshness validation under GNSS time manipulation?
6. How should unknown or missing navigation evidence influence role authorization?

These are open questions, not established findings.


## 11. Two candidate primary-source reading notes

### 11.1 Tanil et al. (2016)

**Source:** Tanil, C., Khanafseh, S., and Pervan, B. *An INS Monitor Against GNSS Spoofing Attacks During GBAS and SBAS-assisted Aircraft Landing Approaches*. ION GNSS+ 2016. https://doi.org/10.33012/2016.14779  
**Publisher:** https://www.ion.org/publications/abstract.cfm?articleID=14779

**Reading depth/access:** The supplied report relies on an earlier discussion of the publisher abstract. Full text was unavailable among its attachments. No new full-text access is claimed here. [U]

- Source-attributed question: INS/GNSS innovation consistency monitoring and integrity risk under spoofing during GBAS/SBAS aircraft approaches. [S]
- The supplied note describes a loosely coupled candidate; exact estimator architecture, threshold, sensor noise, trial counts, false-alarm definition, and tables still require original-text verification. [U]
- R03 transfer: investigate innovation monitoring, while avoiding direct transfer of aircraft approach dynamics or performance to small UAVs. [P]
- The note motivates a candidate; it establishes neither safe swarm admission nor universal spoofing detection.

### 11.2 Tanil et al. (2018)

**Source:** Tanil, C., Khanafseh, S., Joerger, M., and Pervan, B. *An INS Monitor to Detect GNSS Spoofers Capable of Tracking Vehicle Position*. IEEE Transactions on Aerospace and Electronic Systems, 54(1), 131-143. https://doi.org/10.1109/TAES.2017.2739924  
**Candidate full-text URL supplied by the report:** https://www.aoe.vt.edu/content/dam/aoe_vt_edu/people/faculty/joerger/publications/an_ins_monitor_to_detect_gnss_spoofers_capable_of_tracking_vehicle_position.pdf

**Reading depth/access:** The supplied report references a previous full-text discussion; the PDF and that discussion were not available for independent rechecking. Equation/page numbers, window, thresholds, and experiment parameters remain unverified. [U]

- Source-attributed method: tightly coupled INS/GNSS Kalman filtering, accumulated normalized innovations, noise and Gauss-Markov bias dynamics. [S/U]
- Conceptual accumulated statistic: `q_k = sum_i gamma_i^T S_i^-1 gamma_i`. It is not the single-step NIS test. Degrees of freedom, time dependence, and window definition need separate treatment. [P/U]
- R03 transfer: compare single-step and windowed/cumulative monitors. The specific attacker, approach dynamics, and tightly coupled architecture limit direct transfer to the proposed loosely coupled 3D UAV baseline. [P]
- These papers are from the same research line, not independent replications or end-to-end proofs of swarm admission security.

## 12. Parameter rationale and calibration protocol

### 12.1 Theoretical NIS reference thresholds

For calibrated zero-mean Gaussian innovations with positive-definite covariance, NIS has a chi-square reference distribution with innovation dimension `m`. EKF linearization and model mismatch require empirical checking.

| Single-test upper-tail alpha | m=3: position | m=6: position and velocity |
| --- | ---: | ---: |
| 0.05 | 7.815 | 12.592 |
| 0.01 | 11.345 | 16.812 |
| 0.001 | 16.266 | 22.458 |

For example, `m=3, alpha=0.01` gives approximately 11.345. This is a theoretical single-test threshold, not an hourly false-alarm guarantee. At one test per second, 3,600 nominal tests each with alarm probability 0.01 yield 36 expected alarms. Operational thresholds need a defined window, repeated-testing policy, dependence analysis, and calibration. [P]

### 12.2 Exploratory sensitivity grid

These values are proposed design sweeps, not manufacturer specifications or parameters verified from the primary papers. They do not satisfy hardware-specific parameter justification by themselves. [P]

| Parameter | Proposed points | Purpose |
| --- | --- | --- |
| IMU sampling | 50, 100, 200 Hz | Sampling/computation sensitivity |
| GNSS updates | 1, 5, 10 Hz | Measurement sparsity |
| GNSS position noise per-axis sigma | 0.5, 1, 3, 5 m | Measurement quality |
| GNSS outage | 5, 15, 30, 60, 120 s | Inertial error growth |
| GNSS step bias | 1, 3, 5, 10, 20 m | Abrupt error sensitivity |
| GNSS ramp bias | 0.05, 0.1, 0.5, 1 m/s | Slow error sensitivity |
| Evidence age | 0.1, 0.5, 1, 3, 5 s | Freshness sensitivity |
| Maneuvers | Straight, turn, acceleration, climb | Model mismatch |

Convert noise density to sample variance consistently when changing sampling rates.

### 12.3 Parameters requiring sensor or mission evidence

| Parameter | Required justification | Use |
| --- | --- | --- |
| Accelerometer/gyro noise density | Datasheet, stationary data, Allan deviation | Process covariance Q |
| Bias instability | Long stationary and temperature records | Bias model |
| Bias correlation time | Time-series/model identification | Gauss-Markov dynamics |
| GNSS velocity noise and axis correlations | Receiver documentation and measured errors | Measurement covariance R |
| Synchronization error | Timestamp logs and clock reference | Freshness |
| Acceleration/angular-rate bounds | Platform and flight logs | Motion envelope |
| Clock anomaly threshold | Independent time and risk requirement | Clock integrity |
| Role-specific alarm/protection limits | Mission geometry and acceptable risk | Admission |

An illustrative single-axis constant accelerometer bias gives `position_error(t) ~= 0.5*b*t^2` with zero initial errors. Gyro bias, attitude errors, and gravity projection introduce additional errors; this is not a complete INS error model.

### 12.4 Proposed validation procedure and metric definitions

1. Define platform, sensors, frames, and time sources.
2. Identify noise/bias from stationary IMU and nominal GNSS logs.
3. Fit EKF Q/R on nominal training data.
4. Check innovation whiteness, NIS, and uncertainty coverage on separate calibration data.
5. Specify false-alarm target, test frequency, and window; freeze thresholds.
6. Evaluate S0-S7 on held-out data across seeds, speeds, maneuvers, fault directions, magnitudes, and durations.
7. Keep truth independent of estimator observations and policy inputs.
8. Report metrics with denominators/windows and uncertainty intervals; report model/dependence violations.

`FAR = nominal alarm decisions / nominal decision opportunities`, additionally reporting alarms per hour. `MDR = injected fault events without an alarm in the specified detection window / relevant injected fault events`. Detection delay is first valid alarm time minus fault onset. Position RMSE is `sqrt(mean(||p_hat-p_truth||^2))`. Also report UNKNOWN duration, freshness violations, and confidence coverage. Missing GNSS is UNKNOWN, not NIS PASS. [P]

## 13. Repository alignment and acceptance assessment

The contract expands the navigation-evidence row of [system design](../../docs/04-system-design.md). Its admission states match ISOLATED, OBSERVATION, RESTRICTED, and FULL. Navigation evidence remains separate from software authorization, runtime assurance, and update lifecycle. Unknown essential evidence cannot be offset by utility. This is documentation alignment, not a tested executable interface.

S0-S7 are report-local fault identifiers, not replacements for the joint [scenario catalog](../../experiments/scenarios.json). Role thresholds, units, covariance ordering, clock-domain conversion, session binding, and schema versioning still need agreement under [D01 / #12](https://github.com/mathissdupont/swarm-rejoin/issues/12).

| R03 requirement | Evidence here | Remaining limitation |
| --- | --- | --- |
| Candidate and assumptions | Sections 3-4 | Proposed, not implemented |
| Uncertainty, age, clock separation | Section 5 | Typed schema and role thresholds pending |
| Fault cases and independent truth | Sections 6-7 | Scenarios planned, not run |
| Calibration/FAR/MDR plan | Sections 8 and 12 | Sensor-specific ranges not yet justified |
| Two primary-source notes | Section 11 | Full-text confirmations incomplete |

At the requester's direction, #3 may be administratively closed with this consolidated draft as its artifact. This does not establish full acceptance or scientific validation. Before simulation, complete original-text checks and sensor/mission parameter justification; implementation and empirical calibration remain later work. No universal spoofing-detection guarantee is claimed.

## 14. References inherited from the supplied report

These citations are preserved for provenance. Except for the existing `tanil2016` seed, they are pending screening and metadata/source verification before promotion into the retained source registry, bibliography, and matrix. The import does not increase completed review counts.

1. Maharmeh, E., Alsayed, Z., and Nashashibi, F. (2025). *A Comprehensive Survey on the Integrity of Localization Systems*. Sensors, 25(2), 358. https://doi.org/10.3390/s25020358
2. Boguspayev, N., Akhmedov, D., Raskaliyev, A., Kim, A., and Sukhenko, A. (2023). *A Comprehensive Review of GNSS/INS Integration Techniques for Land and Air Vehicle Applications*. Applied Sciences, 13(8), 4819. https://doi.org/10.3390/app13084819
3. Alipourvarmazabadi, M., and Ebner, M. (2026). *Robot Localization: A Comprehensive Survey from Classical Methods to Intelligent Autonomy*. International Journal of Intelligent Robotics and Applications, 10, 795-817. https://doi.org/10.1007/s41315-026-00528-9
4. Tanil et al. (2016). DOI and reading status in section 11.1.
5. Tanil et al. (2018). DOI and reading status in section 11.2.

Personal-note provenance: the supplied report describes four handwritten pages associated with 2026-10-31. They were not attached to this repository import. Their synthesis is researcher interpretation rather than primary-source evidence.
