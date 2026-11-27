# Swarmada rollout API and controller source snapshot

Complete snapshots of three named files, not the complete project. Apache-2.0; see accompanying unchanged license. Reading and execution status remain separate.

Pinned commit: `8415495eff904b5d03c47ffdb263d895c0ed752a`.

## api/v1/rollout_types.go

Source URL: https://raw.githubusercontent.com/swarmada/swarmada/8415495eff904b5d03c47ffdb263d895c0ed752a/api/v1/rollout_types.go

````go
/*
Copyright 2026 The Swarmada Authors.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package v1

import metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"

// RolloutPhase is common to both FirmwareRollout and ModelRollout.
// +kubebuilder:validation:Enum=Pending;InProgress;Paused;Succeeded;Failed
type RolloutPhase string

// RolloutPhase values shared by FirmwareRollout and ModelRollout (RFC-0001 #firmwarerollout, #modelrollout).
const (
	RolloutPhasePending    RolloutPhase = "Pending"
	RolloutPhaseInProgress RolloutPhase = "InProgress"
	RolloutPhasePaused     RolloutPhase = "Paused"
	RolloutPhaseSucceeded  RolloutPhase = "Succeeded"
	RolloutPhaseFailed     RolloutPhase = "Failed"
)

// RolloutDesiredState is the operator's declarative intent for an in-flight
// rollout, common to FirmwareRollout and ModelRollout. It is the operator's half
// of a lifecycle whose other half the controller owns.
//
// LEVEL-TRIGGERED, like FleetAction/FleetTask spec.desiredState (ADR-0047): a
// write persists and re-converges after a disconnect, and re-writing the same
// value is idempotent, so a dropped edge is never a lost command.
//
// IT CAN ONLY ADD A HOLD, NEVER RELEASE ONE IT DID NOT PLACE. `Paused` withholds
// dispatch; `Running` withdraws that hold and nothing else. A rollout halted by
// pauseOnError stays halted under `Running`, because the exit from that halt is
// the rollout-resume verb, which decides what happens to the robots that failed
// (ADR-0041). The two holds compose: a rollout resumes when neither is in force.
// This is what lets the operator's intent be symmetric — writing Running lifts an
// operator hold — without giving an operator a spec field that could undo a safety
// halt, which is the asymmetry ADR-0045 had to impose on FleetAction, where the two
// sources of Paused were indistinguishable.
// +kubebuilder:validation:Enum=Running;Paused
type RolloutDesiredState string

// RolloutDesiredState values.
const (
	// RolloutDesiredStateRunning — dispatch as the strategy allows (default).
	RolloutDesiredStateRunning RolloutDesiredState = "Running"
	// RolloutDesiredStatePaused — an operator hold: no FURTHER robot enters a
	// batch. In-flight installs are NOT interrupted; a robot mid-install is
	// physically committed and cancelling it is what would leave a robot on an
	// indeterminate version.
	RolloutDesiredStatePaused RolloutDesiredState = "Paused"
)

// RolloutStrategyType selects the rollout strategy. Only RollingUpdate at v0.1.
// +kubebuilder:validation:Enum=RollingUpdate
type RolloutStrategyType string

// RolloutStrategyType values.
const (
	// StrategyRollingUpdate is the batched rolling-update strategy.
	StrategyRollingUpdate RolloutStrategyType = "RollingUpdate"
)

// RolloutStrategy selects a rollout strategy and carries its parameters, mirroring
// the Kubernetes Deployment shape (spec.strategy.type + a strategy-named sub-object).
// Only RollingUpdate is defined at v0.1.
type RolloutStrategy struct {
	// Type selects the rollout strategy. Only RollingUpdate is supported at v0.1.
	// +kubebuilder:validation:Enum=RollingUpdate
	// +kubebuilder:default=RollingUpdate
	Type RolloutStrategyType `json:"type,omitempty"`

	// RollingUpdate holds the RollingUpdate strategy's parameters (applies when
	// type is RollingUpdate). When omitted, the documented defaults apply
	// (see RollingUpdateOrDefault).
	// +optional
	RollingUpdate *RollingUpdateStrategy `json:"rollingUpdate,omitempty"`
}

// RollingUpdateOrDefault returns the RollingUpdate parameters, substituting the
// documented defaults ("10%", pauseOnError=true) when the block is omitted.
func (s RolloutStrategy) RollingUpdateOrDefault() RollingUpdateStrategy {
	if s.RollingUpdate != nil {
		return *s.RollingUpdate
	}
	pause := true
	return RollingUpdateStrategy{MaxUnavailable: "10%", PauseOnError: &pause}
}

// RollingUpdateStrategy mirrors the K8s RollingUpdate pattern adapted for
// physical robot constraints. It is nested under RolloutStrategy.rollingUpdate.
type RollingUpdateStrategy struct {
	// MaxUnavailable is the maximum number or percentage of robots that may
	// simultaneously be in the updating state.
	// Examples: "10%" or "5".
	// +kubebuilder:default="10%"
	MaxUnavailable string `json:"maxUnavailable,omitempty"`

	// PauseOnError halts the rollout if any robot fails to update: no further robot
	// enters the batch while a failure stands, though in-flight updaters continue.
	//
	// The operator resumes with `swarmctl rollout resume`, which is gated on the
	// rollout-resume custom verb (RFC-0001 #security-permission-matrix) and writes the swarmada.io/rollout-resume
	// annotation the controller consumes. Resume EXCLUDES the robots that failed from
	// further attempts by this rollout rather than retrying them (ADR-0041); a fixed
	// artifact needs a fresh rollout. Excluded robots are named in
	// status.excludedRobots and count as settled, so the rollout can reach a terminal
	// phase and its record becomes deletable.
	// +kubebuilder:default=true
	// +optional
	PauseOnError *bool `json:"pauseOnError,omitempty"`
}

// RolloutSafetyConstraints are physical safety guards applied during updates.
type RolloutSafetyConstraints struct {
	// MinBatteryPct: do not update robots below this battery level.
	// +kubebuilder:validation:Minimum=0
	// +kubebuilder:validation:Maximum=100
	// +kubebuilder:default=30
	MinBatteryPct int32 `json:"minBatteryPct,omitempty"`

	// RequireIdleState: only update robots in Idle phase. Set false to allow updating a
	// robot that is executing an action; unset means true.
	// +kubebuilder:default=true
	// +optional
	RequireIdleState *bool `json:"requireIdleState,omitempty"`

	// MaintenanceWindowOnly: only update robots during their configured
	// MaintenanceWindow. Slowest but least disruptive.
	// +kubebuilder:default=false
	MaintenanceWindowOnly bool `json:"maintenanceWindowOnly,omitempty"`
}

// RolloutTargetKind selects the kind of object a ModelRollout's targetSelector is
// resolved against. It is a discriminator, not a filter: a rollout targets exactly
// one kind, and the status family for the other kind is left at zero.
//
// Robot is the default, so every ModelRollout authored before this field existed
// keeps its meaning unchanged.
// +kubebuilder:validation:Enum=Robot;EdgeNode
type RolloutTargetKind string

// RolloutTargetKind values.
const (
	// RolloutTargetRobot resolves targetSelector against Robot labels.
	RolloutTargetRobot RolloutTargetKind = "Robot"
	// RolloutTargetEdgeNode resolves targetSelector against EdgeNode labels — an
	// edge or zone-controller box the control plane can push to, not an endpoint
	// executor (see EdgeNode's type comment).
	RolloutTargetEdgeNode RolloutTargetKind = "EdgeNode"
)

// RolloutRobotResult records the failure outcome for a single robot.
type RolloutRobotResult struct {
	RobotName string `json:"robotName"`
	// +optional
	Namespace string `json:"namespace,omitempty"`
	// +optional
	PreviousVersion string `json:"previousVersion,omitempty"`
	// +optional
	FailedAt *metav1.Time `json:"failedAt,omitempty"`
	// +optional
	Reason string `json:"reason,omitempty"`
}

// RolloutBatchRobot is a per-robot entry in a rollout's active update batch. Its
// updatePhase reflects the robot's most recently reported intra-update progress
// (the adapter's advisory UpdateProgress, §9.2); when the adapter reports none it
// stays at the initial phase the controller set when the robot entered the batch.
// The phase enum differs by rollout kind (see UpdatePhase), so the field is a
// string validated by the control plane rather than a single CRD enum.
type RolloutBatchRobot struct {
	// RobotName is the robot currently in the active update batch.
	RobotName string `json:"robotName"`
	// Namespace is the robot's namespace.
	// +optional
	Namespace string `json:"namespace,omitempty"`
	// UpdateStartedAt is when the robot entered the active update batch. Preserved
	// across reconciles for the current attempt.
	// +optional
	UpdateStartedAt *metav1.Time `json:"updateStartedAt,omitempty"`
	// PreviousVersion is the robot's firmware version before this update. Filled
	// on a FirmwareRollout only; a ModelRollout leaves it empty at v0.4 and records
	// the previous model version in status.rollbackVersions instead.
	// +optional
	PreviousVersion string `json:"previousVersion,omitempty"`
	// UpdatePhase is the robot's current intra-update phase. Firmware:
	// Pulling / Installing / Verifying / Rebooting. Model:
	// Downloading / Verifying / Installing / HealthChecking. Advisory — sourced from
	// the adapter's UpdateProgress, else the controller's initial phase.
	// +optional
	UpdatePhase string `json:"updatePhase,omitempty"`
	// CapabilitiesSuspendedAt is when this robot's affected capabilities were
	// suspended for the update (ModelRollout only), stamped per attempt at batch
	// entry.
	// +optional
	CapabilitiesSuspendedAt *metav1.Time `json:"capabilitiesSuspendedAt,omitempty"`
}

// RolloutBatchNode is a per-node entry in a ModelRollout's active update batch when
// spec.targetKind is EdgeNode. It mirrors RolloutBatchRobot field for field, keyed
// by nodeName rather than robotName.
//
// It is a separate type rather than an optional nodeName on RolloutBatchRobot
// because the existing field is named for robots and is required; widening it would
// leave every reader guessing which of two names carries the subject. Two lists,
// each with one meaning, is the additive change (see ModelRolloutStatus).
type RolloutBatchNode struct {
	// NodeName is the EdgeNode currently in the active update batch.
	NodeName string `json:"nodeName"`
	// Namespace is the node's namespace.
	// +optional
	Namespace string `json:"namespace,omitempty"`
	// UpdateStartedAt is when the node entered the active update batch.
	// +optional
	UpdateStartedAt *metav1.Time `json:"updateStartedAt,omitempty"`
	// PreviousVersion is the node's model version before this update.
	// +optional
	PreviousVersion string `json:"previousVersion,omitempty"`
	// UpdatePhase is the node's current intra-update phase:
	// Downloading / Verifying / Installing / HealthChecking. Advisory.
	// +optional
	UpdatePhase string `json:"updatePhase,omitempty"`
	// CapabilitiesSuspendedAt is when this node's affected capabilities were
	// suspended for the update, stamped per attempt at batch entry. Only the
	// capabilities in spec.grantsCapabilities are suspended; a node's zone-control
	// and emergency-stop authority is never suspended by a rollout
	// (EdgeNode.status.zoneControlAvailable).
	// +optional
	CapabilitiesSuspendedAt *metav1.Time `json:"capabilitiesSuspendedAt,omitempty"`
}

// RolloutNodeResult records the failure outcome for a single EdgeNode.
type RolloutNodeResult struct {
	NodeName string `json:"nodeName"`
	// +optional
	Namespace string `json:"namespace,omitempty"`
	// +optional
	PreviousVersion string `json:"previousVersion,omitempty"`
	// +optional
	FailedAt *metav1.Time `json:"failedAt,omitempty"`
	// +optional
	Reason string `json:"reason,omitempty"`
}

// ─────────────────────────────────────────────────────────────────────────────
// FirmwareRollout
// ─────────────────────────────────────────────────────────────────────────────

// FirmwareDeliveryMechanism controls how firmware reaches the robot.
// +kubebuilder:validation:Enum=PullOnIdle;PushImmediate
type FirmwareDeliveryMechanism string

const (
	// FirmwareDeliveryPullOnIdle — robot pulls firmware when it next becomes Idle.
	FirmwareDeliveryPullOnIdle FirmwareDeliveryMechanism = "PullOnIdle"
	// FirmwareDeliveryPushImmediate — control plane pushes firmware now (respects safety constraints).
	FirmwareDeliveryPushImmediate FirmwareDeliveryMechanism = "PushImmediate"
)

// FirmwareRollbackPolicy defines rollback behaviour on failure.
// +kubebuilder:validation:Enum=Manual;Auto
type FirmwareRollbackPolicy string

const (
	// FirmwareRollbackManual — operator must explicitly run swarmctl undo rollout.
	FirmwareRollbackManual FirmwareRollbackPolicy = "Manual"
	// FirmwareRollbackAuto — revert to previous version automatically on failure.
	FirmwareRollbackAuto FirmwareRollbackPolicy = "Auto"
)

// FirmwareRolloutSpec defines the desired state of a FirmwareRollout.
type FirmwareRolloutSpec struct {
	// TargetSelector selects which robots receive this firmware update. It is
	// re-resolved on every reconcile, so a robot relabelled mid-rollout joins or
	// leaves the rollout.
	// +kubebuilder:validation:Required
	TargetSelector metav1.LabelSelector `json:"targetSelector"`

	// NewVersion is the target firmware version string.
	//
	// Swarmada treats it as OPAQUE: it is never parsed, ordered or compared. Batch
	// classification is by EQUALITY only — a robot is "done" when
	// Status.FirmwareVersion == NewVersion and "updating" when its pending-firmware
	// annotation == NewVersion; the eligible set is sorted by NAME, not by version.
	// Vendor firmware strings are frequently not semver ("2.5.0-rc1", "v2.5.0",
	// "2026.06"), so constraining the form here would reject valid targets while
	// protecting nothing.
	//
	// ModelRollout.NewVersion IS pattern-constrained to bare major.minor.patch,
	// because that controller refuses downgrades via versionIsNewer and therefore
	// needs a parseable order. The asymmetry is deliberate.
	// +kubebuilder:validation:Required
	// +kubebuilder:validation:MinLength=1
	NewVersion string `json:"newVersion"`

	// FirmwareURI is the download URL for the firmware artifact.
	// +kubebuilder:validation:Required
	FirmwareURI string `json:"firmwareUri"`

	// FirmwareChecksum is the SHA-256 digest of the firmware artifact, as
	// "sha256:<64 hex>". The detached signature is verified over this value; the
	// robot re-verifies the downloaded bytes against it before install (RFC-0001 #firmwarerollout-schema).
	// +kubebuilder:validation:Required
	// +kubebuilder:validation:Pattern=`^sha256:[a-f0-9]{64}$`
	FirmwareChecksum string `json:"firmwareChecksum"`

	// FirmwareSignatureRef references the detached signature for the artifact,
	// verified against SwarmadaConfig.spec.signing.trustRoots before any dispatch.
	// When requireSignatureVerification is true this MUST be set; omitting it fails
	// the rollout closed (RFC-0001 #firmwarerollout-schema, #fleet-adapter-protocol-fleet-adapter-compliance-checklist). Supported forms: an
	// oci:// ref (digest- or tag-addressed, including a cosign signature tag), an
	// https:// URL, or an inline "bundle:<base64>" raw signature. Any other scheme,
	// s3:// included, fails the rollout closed while signing is enforced.
	// +optional
	FirmwareSignatureRef string `json:"firmwareSignatureRef,omitempty"`

	// Strategy controls how the rollout progresses.
	// +optional
	Strategy RolloutStrategy `json:"strategy,omitempty"`

	// DesiredState is the operator's level-triggered intent for this rollout.
	// Writing `Paused` withholds dispatch of any further robot; writing `Running`
	// withdraws that hold. It does NOT release a pauseOnError halt — see
	// RolloutDesiredState and ADR-0041 — so an operator cannot use it to push a
	// rollout past a failure the halt exists to surface.
	// +optional
	// +kubebuilder:validation:Enum=Running;Paused
	// +kubebuilder:default=Running
	DesiredState RolloutDesiredState `json:"desiredState,omitempty"`

	// SafetyConstraints restricts when updates may be applied.
	// +optional
	SafetyConstraints RolloutSafetyConstraints `json:"safetyConstraints,omitempty"`

	// Delivery is specified to control whether the robot pulls or is pushed the
	// update. No controller reads it at this version: every FirmwareRollout is
	// delivered as PullOnIdle, and PushImmediate pushes nothing.
	// +kubebuilder:default=PullOnIdle
	Delivery FirmwareDeliveryMechanism `json:"deliveryMechanism,omitempty"`

	// RollbackPolicy is specified to control what happens on failure. No controller
	// reads it on a FirmwareRollout at this version: neither value changes what
	// happens on failure, and Auto rolls nothing back.
	// +kubebuilder:default=Manual
	RollbackPolicy FirmwareRollbackPolicy `json:"rollbackPolicy,omitempty"`
}

// FirmwareRolloutStatus defines the observed state of a FirmwareRollout.
type FirmwareRolloutStatus struct {
	Phase         RolloutPhase `json:"phase,omitempty"`
	RobotsTotal   int32        `json:"robotsTotal,omitempty"`
	RobotsUpdated int32        `json:"robotsUpdated,omitempty"`
	RobotsPending int32        `json:"robotsPending,omitempty"`
	RobotsFailed  int32        `json:"robotsFailed,omitempty"`
	// RobotsSkipped is an informational sub-count of RobotsPending: robots failing a
	// safety constraint this cycle, re-evaluated next cycle. Not a disjoint total term.
	// +optional
	RobotsSkipped int32 `json:"robotsSkipped,omitempty"`
	// StartedAt/CompletedAt/PausedAt are top-level rollout timing stamps. At v0.4
	// only PausedAt is written (on the transition into Paused, dropped on leaving
	// it); StartedAt and CompletedAt are written by no controller and stay empty.
	// +optional
	StartedAt *metav1.Time `json:"startedAt,omitempty"`
	// +optional
	CompletedAt *metav1.Time `json:"completedAt,omitempty"`
	// +optional
	PausedAt *metav1.Time `json:"pausedAt,omitempty"`
	// CurrentBatch is the per-robot active update batch (RFC-0001 #firmwarerollout-schema). Each entry carries
	// the robot's live updatePhase, sourced from adapter UpdateProgress.
	// +optional
	// +listType=atomic
	CurrentBatch []RolloutBatchRobot  `json:"currentBatch,omitempty"`
	FailedRobots []RolloutRobotResult `json:"failedRobots,omitempty"`

	// ExcludedRobots names the robots an operator resume removed from this rollout
	// (ADR-0041). They failed, the operator resumed past them, and this rollout will
	// not attempt them again — retrying a failed artifact is what a FRESH rollout is
	// for. They are excluded from every progress bucket, so they neither re-pause the
	// rollout nor hold it short of a terminal phase; a non-empty list surfaces that the
	// fleet did not fully converge on this version.
	// +optional
	ExcludedRobots []string `json:"excludedRobots,omitempty"`
	// +optional
	// +listType=map
	// +listMapKey=type
	Conditions []metav1.Condition `json:"conditions,omitempty"`
}

// FirmwareRollout is the Schema for the firmwarerollouts API.
//
// +kubebuilder:object:root=true
// +kubebuilder:subresource:status
// +kubebuilder:resource:scope=Namespaced,shortName=fwr
// +kubebuilder:printcolumn:name="Version",type="string",JSONPath=".spec.newVersion"
// +kubebuilder:printcolumn:name="Phase",type="string",JSONPath=".status.phase"
// +kubebuilder:printcolumn:name="Updated",type="integer",JSONPath=".status.robotsUpdated"
// +kubebuilder:printcolumn:name="Total",type="integer",JSONPath=".status.robotsTotal"
type FirmwareRollout struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`
	Spec              FirmwareRolloutSpec   `json:"spec,omitempty"`
	Status            FirmwareRolloutStatus `json:"status,omitempty"`
}

// FirmwareRolloutList contains a list of FirmwareRollout resources.
// +kubebuilder:object:root=true
type FirmwareRolloutList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []FirmwareRollout `json:"items"`
}

// ─────────────────────────────────────────────────────────────────────────────
// ModelRollout
// ─────────────────────────────────────────────────────────────────────────────

// ModelRollbackPolicy is identical semantics to FirmwareRollbackPolicy.
// Manual is strongly recommended — silent rollbacks create fleet version
// inconsistency and may restore a silently-incorrect model.
// +kubebuilder:validation:Enum=Manual;Auto
type ModelRollbackPolicy string

// ModelRollbackPolicy values (§6.7): Manual leaves a failed model rollout for an operator to roll
// back, Auto reactivates the robot-retained previous version without re-downloading it.
const (
	ModelRollbackManual ModelRollbackPolicy = "Manual"
	ModelRollbackAuto   ModelRollbackPolicy = "Auto"
)

// ModelRolloutSpec defines the desired state of a ModelRollout.
//
// A capability may not be both granted and revoked by one rollout. The two lists drive
// opposite edges of the §6.10 capability derivation, so an overlap has no coherent meaning:
// whichever list the controller happened to apply second would decide, making the outcome an
// artefact of iteration order rather than of the declaration. Rejecting at admission is the
// only place the operator still has the context to say which they meant.
// +kubebuilder:validation:XValidation:rule="!has(self.grantsCapabilities) || !has(self.revokesCapabilities) || !self.grantsCapabilities.exists(c, c in self.revokesCapabilities)",message="a capability must not appear in both grantsCapabilities and revokesCapabilities"
//
// The two eligibility axes are kind-exclusive. requiredHardware enumerates ROBOT
// hardware types (Lidar, Gripper, LoadPlatform…), none of which describes an edge
// box, so it is rejected on an EdgeNode-targeted rollout rather than silently
// ignored; requiredNodeCapabilities is the edge axis and is rejected on a
// robot-targeted one. Stating each as a rule keeps a mis-set field an admission
// error instead of a rollout that quietly selects the wrong set.
// +kubebuilder:validation:XValidation:rule="!has(self.targetKind) || self.targetKind != 'EdgeNode' || !has(self.requiredHardware)",message="requiredHardware enumerates robot hardware types and is not meaningful for targetKind: EdgeNode — use requiredNodeCapabilities"
// +kubebuilder:validation:XValidation:rule="!has(self.requiredNodeCapabilities) || (has(self.targetKind) && self.targetKind == 'EdgeNode')",message="requiredNodeCapabilities applies only to targetKind: EdgeNode — use requiredHardware for robots"
type ModelRolloutSpec struct {
	// TargetKind selects the kind of object TargetSelector is resolved against.
	// Defaults to Robot, so an existing ModelRollout that omits it keeps exactly
	// the behaviour it had before this field existed. EdgeNode targeting is specified but not implemented at this version:
	// the ModelRollout controller refuses a rollout with targetKind EdgeNode (a
	// TargetKindNotImplemented Warning event) and updates no node.
	// +optional
	// +kubebuilder:default=Robot
	TargetKind RolloutTargetKind `json:"targetKind,omitempty"`

	// TargetSelector selects which objects of TargetKind receive this model
	// update: Robot labels by default, EdgeNode labels when TargetKind is
	// EdgeNode. The selector itself is kind-neutral — only what it is matched
	// against changes — so robot targeting is unchanged and no second selector
	// field exists to keep in sync. It is re-resolved on every reconcile, so a
	// robot relabelled mid-rollout joins or leaves the rollout.
	// +kubebuilder:validation:Required
	TargetSelector metav1.LabelSelector `json:"targetSelector"`

	// ModelName is the logical model name (not version-specific).
	// Must match InstalledModel.name on target robots.
	// +kubebuilder:validation:Required
	// +kubebuilder:validation:MinLength=1
	ModelName string `json:"modelName"`

	// NewVersion is the target model version string (semver).
	// +kubebuilder:validation:Required
	// +kubebuilder:validation:Pattern=`^\d+\.\d+\.\d+$`
	NewVersion string `json:"newVersion"`

	// ModelURI is the OCI registry URI or HTTPS URL of the model artifact.
	// +kubebuilder:validation:Required
	// +kubebuilder:validation:Pattern=`^(oci|s3|https)://`
	ModelURI string `json:"modelUri"`

	// ModelChecksum is the SHA-256 digest of the model artifact, as
	// "sha256:<64 hex>". It is carried to the adapter in the model_update Command so
	// the robot re-verifies the downloaded bytes before install (RFC-0001 #fleet-adapter-protocol-fleet-adapter-compliance-checklist), and the
	// adapter verifies the detached signature over this value. Unlike
	// FirmwareRollout, the ModelRollout control plane verifies no signature before
	// dispatch at v0.4 (ADR-0020).
	// +kubebuilder:validation:Required
	// +kubebuilder:validation:Pattern=`^sha256:[a-f0-9]{64}$`
	ModelChecksum string `json:"modelChecksum"`

	// ModelSignatureRef references the detached signature or sigstore bundle for the
	// model artifact. It is carried to the adapter in the model_update Command, and
	// the Fleet Adapter verifies it against the trust roots before install; the
	// ModelRollout control plane does not fetch or verify it at v0.4. When
	// requireSignatureVerification is true (or the namespace has no SwarmadaConfig)
	// the ModelRollout admission webhook refuses a create or update that leaves it
	// empty (ADR-0020, RFC-0001 #modelrollout-schema).
	// +optional
	ModelSignatureRef string `json:"modelSignatureRef,omitempty"`

	// AttestationRef optionally references a signed {modelDigest, metrics}
	// attestation produced by the evaluation job, specified to bind the
	// quality-gate metrics to the artifact being shipped (ADR-0020). Specified, not
	// implemented at v0.4: no controller resolves or verifies it.
	// +optional
	AttestationRef string `json:"attestationRef,omitempty"`

	// RequiredHardware lists hardware component TYPES (not names) that must be
	// present and Healthy for a robot to receive this model.
	// Robots in targetSelector without the required hardware are never dispatched;
	// at v0.4 they are counted in RobotsTotal and remain in RobotsPending, not in
	// RobotsIneligible.
	// Valid only when TargetKind is Robot (see the type-level CEL rules).
	// +optional
	RequiredHardware []HardwareComponentType `json:"requiredHardware,omitempty"`

	// RequiredNodeCapabilities is the EdgeNode eligibility axis: each name listed
	// here MUST appear in EdgeNode.status.capabilities[] with status Active for the
	// node to enter a batch. It replaces RequiredHardware for edge targets because
	// an edge box's fitness to run a model is a capability question (does it offer
	// inference on an accelerator this model needs) and not a robot-hardware-type
	// question. A node matched by the selector that lacks one is counted in
	// NodesIneligible, never in NodesFailed.
	//
	// MaxItems bounds CEL cost (see GrantsCapabilities below).
	// Valid only when TargetKind is EdgeNode (see the type-level CEL rules).
	// +optional
	// +listType=set
	// +kubebuilder:validation:MaxItems=32
	RequiredNodeCapabilities []string `json:"requiredNodeCapabilities,omitempty"`

	// GrantsCapabilities lists capabilities that become Active when this model
	// is Active. During the update nothing writes an Unavailable status: while a
	// robot's copy of the model is Updating, the capability derivation reports each
	// model-driven capability that model provides as Inactive (reason "providing
	// model rolling out").
	//
	// MaxItems bounds CEL cost (see Robot.spec.hardware's comment): the disjointness rule on
	// this type cross-products the two lists, and the API server refuses to install a CRD
	// whose estimated rule cost is unbounded. Matches RobotClass's MaxItems=32 on the same
	// concept, and 32 capabilities granted by a single model is already far past plausible.
	// +optional
	// +kubebuilder:validation:MaxItems=32
	GrantsCapabilities []string `json:"grantsCapabilities,omitempty"`

	// RevokesCapabilities lists capabilities removed when this model replaces
	// a previous model with a different capability set. ("Capability set" is the
	// northbound seam of ADR-0037; the southbound axis is a "protocol profile".
	// This comment said "capability profile", which is neither.)
	// MaxItems bounds CEL cost (see GrantsCapabilities above).
	// +optional
	// +kubebuilder:validation:MaxItems=32
	RevokesCapabilities []string `json:"revokesCapabilities,omitempty"`

	// Strategy controls how the rollout progresses.
	// +optional
	Strategy RolloutStrategy `json:"strategy,omitempty"`

	// DesiredState is the operator's level-triggered intent for this rollout.
	// Writing `Paused` withholds dispatch of any further robot; writing `Running`
	// withdraws that hold. It does NOT release a pauseOnError halt — see
	// RolloutDesiredState and ADR-0041 — so an operator cannot use it to push a
	// rollout past a failure the halt exists to surface.
	// +optional
	// +kubebuilder:validation:Enum=Running;Paused
	// +kubebuilder:default=Running
	DesiredState RolloutDesiredState `json:"desiredState,omitempty"`

	// SafetyConstraints restricts when updates may be applied.
	// +optional
	SafetyConstraints RolloutSafetyConstraints `json:"safetyConstraints,omitempty"`

	// MaxDownloadTimeMinutes: specified so that if a model download exceeds this
	// duration on a given robot, that robot's update is marked Failed.
	// 0 means no limit. Specified, not implemented at v0.4: no controller reads
	// this field or times a download against it.
	// +kubebuilder:validation:Minimum=0
	// +kubebuilder:validation:Maximum=480
	// +kubebuilder:default=30
	MaxDownloadTimeMinutes int32 `json:"maxDownloadTimeMinutes,omitempty"`

	// RollbackPolicy controls what happens on failure.
	// +kubebuilder:default=Manual
	RollbackPolicy ModelRollbackPolicy `json:"rollbackPolicy,omitempty"`
}

// ModelRolloutStatus defines the observed state of a ModelRollout.
//
// The status carries two parallel progress families, one per RolloutTargetKind:
// the robots* fields and the nodes* fields. A rollout targets exactly one kind, so
// one family is populated and the other left at zero. At this version only the
// robots* family is ever populated: EdgeNode targeting is not implemented. They
// are parallel rather than renamed-and-shared because renaming robotsTotal would
// change the meaning of a field readers already consume, which is a breaking change
// (docs/api-principles.md, "Versioning and compatibility"); adding fields is not.
type ModelRolloutStatus struct {
	Phase                   RolloutPhase `json:"phase,omitempty"`
	RobotsTotal             int32        `json:"robotsTotal,omitempty"`
	RobotsUpdated           int32        `json:"robotsUpdated,omitempty"`
	RobotsPending           int32        `json:"robotsPending,omitempty"`
	RobotsFailed            int32        `json:"robotsFailed,omitempty"`
	CapabilitiesSuspendedOn int32        `json:"capabilitiesSuspendedOn,omitempty"`
	// RobotsIneligible counts selector-matched robots excluded from the rollout.
	// At v0.4 it counts only robots refused as a downgrade (already running a newer
	// version of modelName); a robot lacking a required hardware type is not
	// counted here.
	// +optional
	RobotsIneligible int32 `json:"robotsIneligible,omitempty"`
	// StartedAt/CompletedAt/PausedAt are top-level rollout timing stamps. At v0.4
	// only PausedAt is written (on the transition into Paused, dropped on leaving
	// it); StartedAt and CompletedAt are written by no controller and stay empty.
	// +optional
	StartedAt *metav1.Time `json:"startedAt,omitempty"`
	// +optional
	CompletedAt *metav1.Time `json:"completedAt,omitempty"`
	// +optional
	PausedAt *metav1.Time `json:"pausedAt,omitempty"`
	// CurrentBatch is the per-robot active update batch (RFC-0001 #modelrollout-schema); each entry carries
	// the robot's live updatePhase, sourced from adapter UpdateProgress.
	// +optional
	// +listType=atomic
	CurrentBatch []RolloutBatchRobot  `json:"currentBatch,omitempty"`
	FailedRobots []RolloutRobotResult `json:"failedRobots,omitempty"`

	// RobotsRolledBack counts robots this rollout auto-reverted to their previous
	// model version (rollbackPolicy=Auto, §6.7). A non-zero value surfaces fleet
	// version fragmentation: these robots are back in service but NOT on newVersion.
	// +optional
	RobotsRolledBack int32 `json:"robotsRolledBack,omitempty"`

	// RolledBackRobots names the robots this rollout has auto-reverted. They are
	// excluded from further update attempts by this rollout (a fixed model needs a
	// fresh rollout), so a reverted robot is never pushed back into an update loop.
	// +optional
	RolledBackRobots []string `json:"rolledBackRobots,omitempty"`

	// ExcludedRobots names the robots an operator resume removed from this rollout
	// (ADR-0041). They failed, the operator resumed past them, and this rollout will
	// not attempt them again — retrying a failed artifact is what a FRESH rollout is
	// for. They are excluded from every progress bucket, so they neither re-pause the
	// rollout nor hold it short of a terminal phase; a non-empty list surfaces that the
	// fleet did not fully converge on this version.
	// +optional
	ExcludedRobots []string `json:"excludedRobots,omitempty"`

	// RollbackVersions records, per robot, the model version it was running when it
	// entered this rollout's batch — the revert target for an Auto rollback. It is
	// captured at batch entry (before the robot leaves that version) and carried
	// forward across reconciles; it is the only place the previous version survives
	// once the robot reports newVersion.
	//
	// It is keyed by TARGET OBJECT NAME, so it serves both target kinds: a rollout
	// resolves one kind, and no robot and EdgeNode contend for the same key within
	// one rollout.
	// +optional
	RollbackVersions map[string]string `json:"rollbackVersions,omitempty"`

	// ── EdgeNode target family (spec.targetKind: EdgeNode) ────────────────────
	// Specified to be populated only when the rollout targets EdgeNodes. EdgeNode
	// targeting is not implemented at this version, so every field below stays zero.
	// Each field mirrors its robots* sibling above against a different kind.

	// NodesTotal is specified as the number of EdgeNodes matched by the selector AND
	// eligible (every name in spec.requiredNodeCapabilities Active). Always 0 at this
	// version: edgeNode targeting is specified but not implemented at this version.
	// +optional
	NodesTotal int32 `json:"nodesTotal,omitempty"`
	// NodesUpdated is the number running newVersion with capabilities restored.
	// +optional
	NodesUpdated int32 `json:"nodesUpdated,omitempty"`
	// NodesPending is the number matched and eligible but not yet batched.
	// +optional
	NodesPending int32 `json:"nodesPending,omitempty"`
	// NodesFailed is the number whose update failed.
	// +optional
	NodesFailed int32 `json:"nodesFailed,omitempty"`
	// NodesIneligible counts selector-matched nodes excluded from the rollout for
	// lacking a required node capability.
	// +optional
	NodesIneligible int32 `json:"nodesIneligible,omitempty"`

	// CapabilitiesSuspendedOnNodes is specified as the number of EdgeNodes whose
	// granted capabilities are suspended for this rollout (on a ZoneController, the
	// zone-detection blast radius of the current batch). Always 0 at this version:
	// edgeNode targeting is specified but not implemented at this version.
	// +optional
	CapabilitiesSuspendedOnNodes int32 `json:"capabilitiesSuspendedOnNodes,omitempty"`

	// CurrentNodeBatch is the per-node active update batch.
	// +optional
	// +listType=atomic
	CurrentNodeBatch []RolloutBatchNode `json:"currentNodeBatch,omitempty"`

	// FailedNodes records the failure outcome per EdgeNode.
	// +optional
	// +listType=atomic
	FailedNodes []RolloutNodeResult `json:"failedNodes,omitempty"`

	// NodesRolledBack counts EdgeNodes this rollout auto-reverted to their previous
	// model version (rollbackPolicy=Auto).
	// +optional
	NodesRolledBack int32 `json:"nodesRolledBack,omitempty"`

	// RolledBackNodes names the EdgeNodes this rollout has auto-reverted. They are
	// excluded from further attempts by this rollout.
	// +optional
	// +listType=set
	RolledBackNodes []string `json:"rolledBackNodes,omitempty"`

	// ExcludedNodes names the EdgeNodes an operator resume removed from this
	// rollout (ADR-0041), on the same terms as ExcludedRobots.
	// +optional
	// +listType=set
	ExcludedNodes []string `json:"excludedNodes,omitempty"`

	// +optional
	// +listType=map
	// +listMapKey=type
	Conditions []metav1.Condition `json:"conditions,omitempty"`
}

// ModelRollout is the Schema for the modelrollouts API.
//
// Key difference from FirmwareRollout: while a robot's copy of the model is
// Updating, the model-driven capabilities it provides are derived Inactive (reason
// "providing model rolling out") until the robot reports the model Active again.
//
// A rollout targets Robots. spec.targetKind EdgeNode (an edge or zone-controller
// box) is specified but not implemented at this version: the controller refuses such
// a rollout and updates no node. A rollout never targets an
// endpoint executor: a ComputeEndpoint has no ControlStream, so a ModelUpdate has
// no way to reach it, and endpoint model policy is a version requirement plus a
// scheduling gate and result provenance instead (ADR-0006).
//
// +kubebuilder:object:root=true
// +kubebuilder:subresource:status
// +kubebuilder:resource:scope=Namespaced,shortName=mr
// +kubebuilder:printcolumn:name="Model",type="string",JSONPath=".spec.modelName"
// +kubebuilder:printcolumn:name="Target",type="string",JSONPath=".spec.targetKind"
// +kubebuilder:printcolumn:name="Version",type="string",JSONPath=".spec.newVersion"
// +kubebuilder:printcolumn:name="Phase",type="string",JSONPath=".status.phase"
// +kubebuilder:printcolumn:name="Updated",type="integer",JSONPath=".status.robotsUpdated"
// +kubebuilder:printcolumn:name="Suspended",type="integer",JSONPath=".status.capabilitiesSuspendedOn"
type ModelRollout struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`
	Spec              ModelRolloutSpec   `json:"spec,omitempty"`
	Status            ModelRolloutStatus `json:"status,omitempty"`
}

// ModelRolloutList contains a list of ModelRollout resources.
// +kubebuilder:object:root=true
type ModelRolloutList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []ModelRollout `json:"items"`
}

func init() {
	SchemeBuilder.Register(&FirmwareRollout{}, &FirmwareRolloutList{})
	SchemeBuilder.Register(&ModelRollout{}, &ModelRolloutList{})
}

// PausesOnError reports whether a failed robot halts the rollout.
//
// nil resolves to TRUE because the field carries +kubebuilder:default=true: the API server
// materializes an omitted key as true, and an accessor that disagreed with the schema
// default would answer differently from the API server about the same object.
func (r RollingUpdateStrategy) PausesOnError() bool {
	return r.PauseOnError == nil || *r.PauseOnError
}

// RequiresIdleState reports whether a rollout may only touch robots in the Idle phase.
// nil resolves to TRUE, matching the schema default.
func (c RolloutSafetyConstraints) RequiresIdleState() bool {
	return c.RequireIdleState == nil || *c.RequireIdleState
}
````

## internal/controller/firmwarerollout_controller.go

Source URL: https://raw.githubusercontent.com/swarmada/swarmada/8415495eff904b5d03c47ffdb263d895c0ed752a/internal/controller/firmwarerollout_controller.go

````go
/*
Copyright 2026 The Swarmada Authors.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package controller

import (
	"context"
	"crypto"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"fmt"
	"net/url"
	"sort"
	"strconv"
	"strings"
	"time"

	corev1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/api/equality"
	apierrors "k8s.io/apimachinery/pkg/api/errors"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/types"
	"k8s.io/client-go/tools/record"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/handler"
	"sigs.k8s.io/controller-runtime/pkg/log"
	"sigs.k8s.io/controller-runtime/pkg/reconcile"

	fleetv1 "github.com/swarmada/swarmada/api/v1"
	"github.com/swarmada/swarmada/internal/artifact"
	"github.com/swarmada/swarmada/internal/audit"
	"github.com/swarmada/swarmada/internal/registry"
	"github.com/swarmada/swarmada/internal/rekor"
	"github.com/swarmada/swarmada/internal/signing"
)

// Pending-firmware annotations drive the PullOnIdle delivery mechanism (RFC-0001 #firmwarerollout-delivery-mechanisms):
// the Robot Agent polls these on each Idle transition and applies the update.
const (
	annPendingFirmwareVersion  = "swarmada.io/pending-firmware-version"
	annPendingFirmwareURI      = "swarmada.io/pending-firmware-uri"
	annPendingFirmwareChecksum = "swarmada.io/pending-firmware-checksum"

	// conditionSignatureVerified records the artifact verification outcome.
	conditionSignatureVerified = "SignatureVerified"

	// conditionOperatorHold reports whether spec.desiredState: Paused is in force,
	// and is shared by both rollout kinds. It exists because `phase: Paused` alone
	// cannot answer the question an operator actually has — "will this move on its
	// own, or is it waiting for me?" — now that two independent holds produce it.
	// True means the operator's own hold; writing `Running` lifts it. False under
	// `phase: Paused` means the pauseOnError halt, whose exit is the rollout-resume
	// verb. This is the discriminator ADR-0045 lacked on FleetAction, and having it
	// is why the operator's intent here can be symmetric.
	conditionOperatorHold = "OperatorHold"
)

// FirmwareRolloutReconciler drives FirmwareRollout (RFC-0001 #firmwarerollout). Before ANY robot is
// dispatched, it verifies the artifact's signature over its checksum against the
// SwarmadaConfig trust roots and fails closed on any problem — an unverified
// artifact is never annotated onto a robot, even temporarily (RFC-0001 #firmwarerollout).
type FirmwareRolloutReconciler struct {
	client.Client
	Scheme   *runtime.Scheme
	Recorder record.EventRecorder
	// Fetcher retrieves a detached signature from a non-inline signatureRef (an
	// https:// URL). Nil defaults to the production https fetcher; tests inject a
	// fake. What it returns is trusted only after signing.Verify succeeds.
	Fetcher artifact.Fetcher
	// OCIFetcher retrieves a detached signature stored as an OCI blob (an oci://
	// digest-addressed ref). Nil defaults to the production registry client.
	OCIFetcher OCIBlobFetcher
	// Rekor checks the transparency log when signing.rekorUrl is set. Nil defaults
	// to the production Rekor client.
	Rekor rekor.Checker
	// Audit records FIRMWARE_ROLLOUT_CREATED into the RFC-0001 #security-audit-logging chain the first time a
	// verified rollout enters its lifecycle. Nil disables audit recording.
	Audit audit.Recorder

	// notes keeps the FirmwareUpdateUnderWayUnderStop Event to one per held robot.
	notes heldNotes
}

// OCIBlobFetcher fetches OCI artifact material — a content-addressed blob and a
// manifest's layer list. [github.com/swarmada/swarmada/internal/registry.Client]
// satisfies it.
type OCIBlobFetcher interface {
	Blob(ctx context.Context, reg, repo, digest string, cred *registry.Credential) ([]byte, error)
	Layers(ctx context.Context, reg, repo, ref string, cred *registry.Credential) ([]registry.Layer, error)
}

// registryCredentialsSecret is the conventional per-namespace Secret the fetcher
// reads registry/artifact credentials from (keys: token, or username+password; and
// registries, the hosts they may be presented to). Absent means anonymous fetch. There is no api field for this yet (RFC-0001 #security-model-and-firmware-registry-credentials).
const registryCredentialsSecret = "swarmada-registry-credentials"

// +kubebuilder:rbac:groups=swarmada.io,resources=firmwarerollouts,verbs=get;list;watch;patch
// +kubebuilder:rbac:groups=swarmada.io,resources=firmwarerollouts/status,verbs=get;update;patch
// +kubebuilder:rbac:groups=swarmada.io,resources=robots,verbs=get;list;watch;update;patch
// +kubebuilder:rbac:groups=swarmada.io,resources=swarmadaconfigs,verbs=get;list;watch
// +kubebuilder:rbac:groups=swarmada.io,resources=fleetzones,verbs=get;list;watch
// +kubebuilder:rbac:groups="",resources=secrets,verbs=get;list;watch

// Reconcile drives one FirmwareRollout.
func (r *FirmwareRolloutReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	logger := log.FromContext(ctx).WithValues("firmwarerollout", req.NamespacedName)

	rollout := &fleetv1.FirmwareRollout{}
	if err := r.Get(ctx, req.NamespacedName, rollout); err != nil {
		return ctrl.Result{}, client.IgnoreNotFound(err)
	}

	// A rollout already Failed by verification stays failed — a bad signature is
	// not retried into a dispatch. Matched on the reason: SignatureVerified is also False
	// (VerificationDisabled) on a rollout that was never verified, and that one may fail at install.
	if rollout.Status.Phase == fleetv1.RolloutPhaseFailed && conditionIsFalseWithReason(rollout.Status.Conditions, conditionSignatureVerified, "VerificationFailed") {
		return ctrl.Result{}, nil
	}

	// ── Verification gate (fail closed, BEFORE any dispatch) ───────────────────
	signer, verifyErr := r.verifyArtifact(ctx, rollout, rollout.Spec.FirmwareChecksum, rollout.Spec.FirmwareSignatureRef)
	if verifyErr != nil {
		return r.failVerification(ctx, rollout, verifyErr)
	}

	// ── Dispatch (only reached once the artifact is verified) ──────────────────
	var robots fleetv1.RobotList
	sel, err := metav1.LabelSelectorAsSelector(&rollout.Spec.TargetSelector)
	if err != nil {
		return ctrl.Result{}, fmt.Errorf("invalid targetSelector: %w", err)
	}
	if err := r.List(ctx, &robots, client.InNamespace(req.Namespace),
		client.MatchingLabelsSelector{Selector: sel}); err != nil {
		return ctrl.Result{}, fmt.Errorf("listing target robots: %w", err)
	}

	// An operator resume converts the robots that are currently failed into this rollout's
	// excluded set (ADR-0041), so the pause cannot re-latch off the same robots on the very
	// next reconcile. Applied BEFORE classification so this pass already sees them excluded.
	if resumed, err := r.applyResume(ctx, rollout); err != nil {
		return ctrl.Result{}, err
	} else if resumed {
		return ctrl.Result{Requeue: true}, nil
	}
	excludedSet := make(map[string]bool, len(rollout.Status.ExcludedRobots))
	for _, n := range rollout.Status.ExcludedRobots {
		excludedSet[n] = true
	}
	holds, err := readRolloutHolds(ctx, r.Client, req.Namespace)
	if err != nil {
		return ctrl.Result{}, err
	}

	now := time.Now()
	windowOnly := rollout.Spec.SafetyConstraints.MaintenanceWindowOnly
	var done, updating, eligible, failed, skipped, excluded []*fleetv1.Robot
	for i := range robots.Items {
		rob := &robots.Items[i]
		if excludedSet[rob.Name] {
			// An operator resumed past this robot: out of every bucket, so it neither
			// re-pauses the rollout nor is re-dispatched to, and it counts as settled so
			// the rollout can still reach a terminal phase.
			excluded = append(excluded, rob)
			continue
		}
		entry := batchEntryFor(rollout.Status.CurrentBatch, rob.Name)
		held := holds.why(rob)
		if held == "" {
			r.notes.forget(heldNoteKey(rollout, rob.Name, "under-way"))
		}
		pending := rob.Annotations[annPendingFirmwareVersion] == rollout.Spec.NewVersion
		switch {
		case rob.Status.FirmwareVersion == rollout.Spec.NewVersion:
			done = append(done, rob)
			// Completed only if it was in the batch we are still carrying: a robot that
			// already ran this version before the rollout started never installed anything.
			if entry != nil {
				r.recordFirmwareInstalled(ctx, rollout, rob, entry)
			}
			// The install is over, so the PullOnIdle dispatch markers must not outlive it.
			r.clearPendingFirmware(ctx, rob)
		// Checked BEFORE the pending-annotation case below. A failed robot keeps that
		// annotation — nothing clears it — so without this it would classify as forever
		// "updating", which is precisely how a failed install used to wedge a rollout.
		//
		// The second half is what makes the failure STICK. A robot leaves status.currentBatch
		// on the very pass it is recorded failed (the batch is rebuilt from the updating
		// robots), so installFailedForRollout — which keys on the batch entry to establish
		// that the failure belongs to THIS rollout's dispatch — stopped recognising it one
		// reconcile later. The rollout then re-classified it as a phantom updater on its own
		// leftover annotation, `paused` is derived from len(failed), and the halt released
		// itself. status.failedRobots[] is this rollout's own record of an already-attributed
		// failure, so reading it back re-establishes the same fact without re-deciding it.
		case installFailedForRollout(rob, entry) || wasAlreadyFailed(rollout.Status.FailedRobots, rob.Name):
			failed = append(failed, rob)
			r.recordFirmwareInstallFailed(ctx, rollout, rob)
		// A robot a stop holds after it was told to pull: the pull is withdrawn while the
		// install has not begun, so the instruction is not left standing on a stopped robot
		// for the Robot Agent to act on at its next Idle transition. It is held back like any
		// robot a safety constraint holds back, and offered again once nothing holds it.
		case pending && held != "" && !firmwareInstallBegun(rob, entry, rollout.Spec.NewVersion):
			if err := r.withdrawPendingFirmware(ctx, rollout, rob, held); err != nil {
				return ctrl.Result{}, err
			}
			skipped = append(skipped, rob)
		case pending:
			// An install the robot has reported under way is not withdrawn: the agent already
			// holds the artifact, and nothing on the wire aborts an install.
			if held != "" && r.notes.first(heldNoteKey(rollout, rob.Name, "under-way")) && r.Recorder != nil {
				r.Recorder.Event(rollout, corev1.EventTypeWarning, "FirmwareUpdateUnderWayUnderStop",
					fmt.Sprintf("robot %s is under an emergency stop (%s) while its install of firmware %s is under way; "+
						"the control plane has no means to abort an install the robot has begun", rob.Name, held,
						rollout.Spec.NewVersion))
			}
			updating = append(updating, rob)
		case held == "" && eligibleForFirmwareUpdate(rob, rollout) && withinRolloutWindow(rob, windowOnly, now):
			eligible = append(eligible, rob)
		default:
			// Held back this cycle by a safety constraint — battery, idle state or the
			// maintenance window. Still awaiting its update and re-evaluated next cycle, so
			// it stays inside robotsPending; robotsSkipped surfaces it as a sub-count.
			skipped = append(skipped, rob)
		}
	}

	total := len(robots.Items)

	// ── pauseOnError (RFC-0001 #firmwarerollout-rollback-policy) ────────────────────────────────────────────────
	// A failed install halts the rollout: no FURTHER robot enters the batch while the
	// failure stands, though in-flight updaters continue. This is the guard that stops a
	// bad image reaching the whole fleet one batch at a time — firmware has no
	// rollbackPolicy: Auto, so it is the only guard on this path.
	//
	// Derived per reconcile rather than latched, matching ModelRollout: the rollout
	// un-pauses when nothing is failed any more, which happens when an operator resumes
	// (the failed robots move to status.excludedRobots) or repairs them out of band.
	pausedOnError := len(failed) > 0 && rollout.Spec.Strategy.RollingUpdateOrDefault().PausesOnError()

	// The OPERATOR hold, composed with — never substituted for — the error halt.
	// spec.desiredState: Paused withholds dispatch of any further robot. The two
	// holds are independent and the rollout dispatches only when NEITHER is in
	// force, which is the property that makes the operator's field safe: writing
	// `Running` withdraws the operator's own hold and cannot touch a pauseOnError
	// halt, whose exit is the rollout-resume verb because that verb also decides
	// what happens to the robots that failed (ADR-0041). An operator therefore
	// cannot use a spec field to push a rollout past a failure the halt exists to
	// surface.
	//
	// In-flight installs are NOT interrupted. A robot mid-install is physically
	// committed; cancelling it is what would leave a robot on an indeterminate
	// version. A hold stops the NEXT robot, exactly as pauseOnError does.
	heldByOperator := rollout.Spec.DesiredState == fleetv1.RolloutDesiredStatePaused
	paused := pausedOnError || heldByOperator

	if !paused {
		slots := maxUnavailable(rollout.Spec.Strategy.RollingUpdateOrDefault().MaxUnavailable, total) - len(updating)
		sort.Slice(eligible, func(i, j int) bool { return eligible[i].Name < eligible[j].Name })
		for _, rob := range eligible {
			if slots <= 0 {
				break
			}
			if err := r.dispatch(ctx, rob, rollout); err != nil {
				return ctrl.Result{}, err
			}
			updating = append(updating, rob)
			slots--
		}
	}

	// Was this rollout already verified on a previous pass? The condition is re-asserted
	// every reconcile, so the entry has to hang off the edge, not the assertion.
	prevVerified := conditionIsTrue(rollout.Status.Conditions, conditionSignatureVerified)

	newStatus := computeFirmwareStatus(total, len(done), updating, failed, skipped, excluded, paused,
		rollout.Status.CurrentBatch, rollout.Status.FailedRobots)
	// Conditions start from the stored ones, so a condition whose status did not change
	// keeps its lastTransitionTime and an unchanged pass compares equal and writes nothing
	// (RA-1).
	newStatus.Conditions = rollout.Status.DeepCopy().Conditions
	if heldByOperator {
		upsertCondition(&newStatus.Conditions, conditionOperatorHold, metav1.ConditionTrue,
			"OperatorPaused", "spec.desiredState is Paused: no further robot enters a batch until it is set back to Running")
	} else {
		upsertCondition(&newStatus.Conditions, conditionOperatorHold, metav1.ConditionFalse,
			"NoOperatorHold", "spec.desiredState is Running; any Paused phase is the pauseOnError halt, exited with the rollout-resume verb")
	}
	// SignatureVerified is True only when a signature verified against a trust root. With
	// signing not enforced nothing is checked, so the condition says so and nothing is sealed,
	// whether or not the rollout names a signature reference.
	if signer == "" {
		upsertCondition(&newStatus.Conditions, conditionSignatureVerified, metav1.ConditionFalse,
			fleetv1.ReasonVerificationDisabled, notEnforcedMessage(rollout.Spec.FirmwareSignatureRef))
	} else {
		upsertCondition(&newStatus.Conditions, conditionSignatureVerified, metav1.ConditionTrue,
			"Verified", "signature verified by trust root "+signer)
	}
	if signer != "" && !prevVerified {
		r.sealFirmwareEvent(ctx, rollout, audit.EventFirmwareSignatureVerified, "verify", audit.OutcomeAllowed,
			map[string]string{
				"firmware_uri":    rollout.Spec.FirmwareURI,
				"artifact_digest": rollout.Spec.FirmwareChecksum,
				"verified_signer": signer,
			})
	}
	// PausedAt anchors the halt for an operator and for the audit entry. Stamped on the EDGE
	// into Paused so it records when the rollout stopped, not when it was last reconciled
	// while stopped — and so it rides the material-change patch below.
	if newStatus.Phase == fleetv1.RolloutPhasePaused {
		if rollout.Status.PausedAt != nil {
			newStatus.PausedAt = rollout.Status.PausedAt
		} else {
			pausedAt := metav1.Now()
			newStatus.PausedAt = &pausedAt
		}
	}
	pauseEdge := newStatus.Phase == fleetv1.RolloutPhasePaused && rollout.Status.Phase != fleetv1.RolloutPhasePaused
	if !equality.Semantic.DeepEqual(rollout.Status, newStatus) {
		base := rollout.DeepCopy()
		rollout.Status = newStatus
		if err := r.Status().Patch(ctx, rollout, client.MergeFrom(base)); err != nil {
			return ctrl.Result{}, fmt.Errorf("patching rollout status: %w", err)
		}
		logger.V(1).Info("firmware rollout progress", "phase", newStatus.Phase, "updated", newStatus.RobotsUpdated)
		// RFC-0001 #security-audit-logging requires FIRMWARE_ROLLOUT_PAUSED. Until pauseOnError was implemented the
		// transition could not occur, so the required event had no reachable writer.
		// Sealed on the edge: a rollout sitting Paused seals one entry, not one per pass.
		if pauseEdge {
			failedNames := make([]string, 0, len(newStatus.FailedRobots))
			for _, f := range newStatus.FailedRobots {
				failedNames = append(failedNames, f.RobotName)
			}
			r.sealFirmwareEvent(ctx, rollout, audit.EventFirmwareRolloutPaused, "pause", audit.OutcomeError,
				map[string]string{
					"version":       rollout.Spec.NewVersion,
					"failed_robots": strings.Join(failedNames, ","),
				})
		}
		// The first time the phase leaves empty is the first (verified) processing of
		// a newly-created rollout — record it once. Tied to the successful patch so a
		// mid-reconcile error never records a phantom creation.
		if base.Status.Phase == "" && newStatus.Phase != "" {
			r.recordRolloutCreated(ctx, rollout)
		}
	}
	return ctrl.Result{}, nil
}

// applyResume consumes a pending swarmada.io/rollout-resume annotation (ADR-0041).
//
// It moves the robots this rollout records as failed into status.excludedRobots and clears
// status.pausedAt, so `paused` — derived per reconcile from len(failed), not latched — cannot
// immediately re-latch off the same robots, and the rollout can reach a terminal phase and
// become deletable.
//
// Returns resumed=true when it wrote status; the caller ends the reconcile and the write
// requeues. Idempotent, and a rollout that is NOT paused still records the request as
// processed so a stale annotation cannot silently resume a FUTURE pause.
func (r *FirmwareRolloutReconciler) applyResume(ctx context.Context, rollout *fleetv1.FirmwareRollout) (bool, error) {
	req, pending := pendingResume(rollout.Annotations)
	if !pending {
		return false, nil
	}

	resumed := false
	if rollout.Status.Phase == fleetv1.RolloutPhasePaused {
		newlyExcluded := make([]string, 0, len(rollout.Status.FailedRobots))
		for _, f := range rollout.Status.FailedRobots {
			newlyExcluded = append(newlyExcluded, f.RobotName)
		}

		base := rollout.DeepCopy()
		rollout.Status.ExcludedRobots = mergeExcluded(rollout.Status.ExcludedRobots, newlyExcluded)
		// The failure list is what re-derives `paused`; leaving it would re-pause on the very
		// next reconcile and make the resume look like it did nothing.
		rollout.Status.FailedRobots = nil
		rollout.Status.PausedAt = nil
		// Written and sealed only when it changes status. A pass that applied this request
		// but could not record it as processed finds the status already resumed on its retry:
		// it writes nothing, seals nothing, and goes on to the marker (RA-1).
		if !equality.Semantic.DeepEqual(base.Status, rollout.Status) {
			if err := r.Status().Patch(ctx, rollout, client.MergeFrom(base)); err != nil {
				return false, fmt.Errorf("resuming firmware rollout: %w", err)
			}
			// The operator who wrote the resume annotation, stamped at admission (ADR-0046).
			// The identity rides the envelope's Actor — never the Detail map, which must not
			// duplicate envelope-carried identity (the specification's _ENVELOPE_FIELDS rule).
			r.sealFirmwareEventAs(ctx, rollout,
				estopActor(rollout.Annotations, "firmwarerollout-controller"),
				audit.EventRolloutResumed, "resume", audit.OutcomeAllowed,
				map[string]string{
					"reason":          req,
					"excluded_robots": strings.Join(newlyExcluded, ","),
				})
			resumed = true
		}
	}

	if err := markResumeProcessed(ctx, r.Client, rollout, req); err != nil {
		return false, err
	}
	return resumed, nil
}

// sealFirmwareEvent appends one RFC-0001 #safety-required-events entry about a firmware rollout. Best-effort and
// nil-safe: verification and dispatch decisions are made before this is called, and an
// audit sink must never be able to stop a rollout being blocked — least of all the
// signature-failure path, where refusing to dispatch is the safety-relevant behaviour.
func (r *FirmwareRolloutReconciler) sealFirmwareEvent(ctx context.Context, rollout *fleetv1.FirmwareRollout,
	eventType, action string, outcome audit.Outcome, detail map[string]string) {
	r.sealFirmwareEventAs(ctx, rollout,
		audit.Actor{Type: audit.ActorServiceAccount, Identity: "firmwarerollout-controller"},
		eventType, action, outcome, detail)
}

// sealFirmwareEventAs is sealFirmwareEvent with an explicit actor. Only the operator-driven
// events use it: ROLLOUT_RESUMED is an intent a person expressed (ADR-0041's resume
// annotation), so it carries the person (ADR-0046). Everything else this controller seals —
// install outcomes, the pause edge — is genuinely the controller's own act and keeps the
// service-account actor, because claiming a user there would be a false attribution.
func (r *FirmwareRolloutReconciler) sealFirmwareEventAs(ctx context.Context, rollout *fleetv1.FirmwareRollout,
	actor audit.Actor, eventType, action string, outcome audit.Outcome, detail map[string]string) {
	if r.Audit == nil {
		return
	}
	if _, err := r.Audit.Record(audit.Entry{
		EventType: eventType,
		Namespace: rollout.Namespace,
		Actor:     actor,
		Resource:  audit.Resource{Kind: "FirmwareRollout", Namespace: rollout.Namespace, Name: rollout.Name},
		Action:    action,
		Outcome:   outcome,
		Detail:    detail,
	}); err != nil {
		log.FromContext(ctx).Error(err, "recording audit entry", "event", eventType, "rollout", rollout.Name)
	}
}

// recordFirmwareInstalled seals FIRMWARE_INSTALL_SUCCEEDED when a robot that was in this
// rollout's batch reports the target version.
//
// duration_seconds is measured from the batch entry's UpdateStartedAt — the moment the
// robot was dispatched — because that is the span an operator is asking about when a
// rollout looks slow. It is omitted rather than zeroed when the stamp is missing: a
// recorded 0 would assert an instantaneous install.
func (r *FirmwareRolloutReconciler) recordFirmwareInstalled(ctx context.Context, rollout *fleetv1.FirmwareRollout,
	rob *fleetv1.Robot, entry *fleetv1.RolloutBatchRobot) {
	detail := map[string]string{
		"new_version": rollout.Spec.NewVersion,
		"robot":       rob.Name,
	}
	if entry.UpdateStartedAt != nil {
		detail["duration_seconds"] = strconv.Itoa(int(time.Since(entry.UpdateStartedAt.Time).Seconds()))
	}
	r.sealFirmwareEvent(ctx, rollout, audit.EventFirmwareInstallSucceeded, "install", audit.OutcomeAllowed, detail)
}

// batchEntryFor returns the batch record for a robot, or nil when it is not in the batch.
func batchEntryFor(batch []fleetv1.RolloutBatchRobot, robotName string) *fleetv1.RolloutBatchRobot {
	for i := range batch {
		if batch[i].RobotName == robotName {
			return &batch[i]
		}
	}
	return nil
}

// conditionIsTrue reports whether a named condition is present and True.
func conditionIsTrue(conds []metav1.Condition, condType string) bool {
	for i := range conds {
		if conds[i].Type == condType {
			return conds[i].Status == metav1.ConditionTrue
		}
	}
	return false
}

// recordRolloutCreated seals a FIRMWARE_ROLLOUT_CREATED entry into the RFC-0001 #security-audit-logging
// chain. Best-effort: a record failure is logged, never blocking the rollout.
// recordFirmwareInstallFailed seals FIRMWARE_INSTALL_FAILED (RFC-0001 #safety-required-events) on the edge into
// failure, once per robot per rollout.
//
// Sealed ONLY on a confirmed report from the robot. A rollout that abandons an unresponsive
// robot records that on the rollout as unconfirmed and reaches this not at all: never
// hearing is not evidence of failing, and the chain admits only confirmed facts.
func (r *FirmwareRolloutReconciler) recordFirmwareInstallFailed(ctx context.Context,
	rollout *fleetv1.FirmwareRollout, rob *fleetv1.Robot,
) {
	// The edge: a failed robot stays failed across reconciles, so without this the chain
	// would gain an entry per reconcile per robot and bury the incident it records.
	if wasAlreadyFailed(rollout.Status.FailedRobots, rob.Name) {
		return
	}
	fi := rob.Status.FirmwareInstall
	detail := map[string]string{
		"reason":       "no reason reported by the adapter",
		"new_version":  rollout.Spec.NewVersion,
		"rollout_name": rollout.Name,
	}
	if fi != nil {
		if fi.FailureReason != "" {
			detail["reason"] = fi.FailureReason
		}
		// The version the robot is left on. Reported, never assumed — a failed install may
		// leave it on the old version, a recovery image, or elsewhere, and this is the field
		// an operator acts on when deciding whether the robot is safe to keep running.
		detail["robot_remains_on_version"] = fi.RunningVersion
	}
	r.sealFirmwareEvent(ctx, rollout, audit.EventFirmwareInstallFailed, "install", audit.OutcomeError, detail)
}

func (r *FirmwareRolloutReconciler) recordRolloutCreated(ctx context.Context, rollout *fleetv1.FirmwareRollout) {
	if r.Audit == nil {
		return
	}
	if _, err := r.Audit.Record(audit.Entry{
		EventType: audit.EventFirmwareRolloutCreat,
		Namespace: rollout.Namespace,
		Actor:     audit.Actor{Type: audit.ActorServiceAccount, Identity: "firmwarerollout-controller"},
		Resource:  audit.Resource{Kind: "FirmwareRollout", Namespace: rollout.Namespace, Name: rollout.Name},
		Action:    "create",
		Outcome:   audit.OutcomeAllowed,
		Detail:    map[string]string{"version": rollout.Spec.NewVersion},
	}); err != nil {
		log.FromContext(ctx).Error(err, "recording FIRMWARE_ROLLOUT_CREATED audit entry", "rollout", rollout.Name)
	}
}

// verifyArtifact fails closed: it returns an error unless the artifact's checksum
// is well-formed and (when signing is enforced) its signature verifies against a
// configured trust root. A nil error means the rollout may dispatch.
func (r *FirmwareRolloutReconciler) verifyArtifact(ctx context.Context, rollout *fleetv1.FirmwareRollout, checksum, sigRef string) (string, error) {
	namespace := rollout.Namespace
	if !signing.ValidChecksum(checksum) {
		return "", fmt.Errorf("malformed firmwareChecksum %q (want sha256:<64 hex>)", checksum)
	}

	cfg, err := r.namespaceSigningConfig(ctx, namespace)
	if err != nil {
		return "", err
	}
	if !cfg.SignatureVerificationRequired() {
		return "", nil // signing not enforced; checksum format already validated
	}

	if sigRef == "" {
		return "", fmt.Errorf("firmwareSignatureRef is required when signing is enforced; refusing to dispatch unsigned artifact")
	}
	sig, inline := signing.ParseInlineSignature(sigRef)
	var cosignPayload []byte
	if !inline {
		// A non-inline ref is fetched. https and oci:// are wired; anything else fails closed with
		// an honest message — an artifact we cannot fetch is never dispatched.
		fetched, ferr := r.fetchSignature(ctx, rollout, sigRef)
		if ferr != nil {
			return "", ferr
		}
		sig, cosignPayload = fetched.Sig, fetched.Payload
	}

	roots, err := r.loadTrustRoots(ctx, namespace, cfg.TrustRoots)
	if err != nil {
		return "", err
	}

	// Two signature forms, verified over different payloads.
	//
	//   native  — the signature is over the artifact checksum string directly.
	//   cosign  — the signature is over a simplesigning PAYLOAD, which in turn names the digest it
	//             attests. Verifying the signature alone would prove only that SOME payload is
	//             authentic; the binding check below is what ties it to THIS artifact. Without it a
	//             genuine cosign signature for a different image would satisfy the gate.
	verifyOver := []byte(checksum)
	if cosignPayload != nil {
		verifyOver = cosignPayload
	}
	signer, err := signing.Verify(verifyOver, sig, roots)
	if err != nil {
		return "", err
	}
	if cosignPayload != nil {
		attested, perr := cosignPayloadDigest(cosignPayload)
		if perr != nil {
			return "", fmt.Errorf("cosign signature verified but its payload is unusable: %w", perr)
		}
		if attested != checksum {
			return "", fmt.Errorf("cosign signature attests artifact %s but this rollout dispatches %s; refusing to dispatch", attested, checksum)
		}
	}

	// Transparency-log requirement (§9.1.12): when rekorUrl is configured, the
	// artifact's entry MUST appear in the log — an additional fail-closed gate on
	// top of the trust-root signature check.
	if cfg.RekorURL != "" {
		// RFC-0001 #firmwarerollout. With a pinned log key this verifies the entry's inclusion proof AND
		// signed-entry-timestamp; without one it degrades to index presence and SAYS SO, because
		// an operator must be able to tell a cryptographically verified entry from a server that
		// merely answered "yes".
		logKey, kerr := r.rekorLogKey(ctx, namespace, cfg)
		if kerr != nil {
			return "", fmt.Errorf("transparency-log key unavailable (fail closed): %w", kerr)
		}
		note, rerr := r.rekor().VerifyEntry(ctx, cfg.RekorURL, checksum, logKey)
		if rerr != nil {
			return "", fmt.Errorf("transparency-log verification failed for %s at %s; refusing to dispatch: %w",
				checksum, cfg.RekorURL, rerr)
		}
		log.FromContext(ctx).V(1).Info("transparency log checked", "artifact", checksum, "result", note)
	}
	return signer, nil
}

// rekorLogKey loads the operator-pinned transparency-log public key. A nil key with no error means
// none is configured — the caller then runs the degraded presence-only check. A configured but
// unreadable or unparseable key is an ERROR: a key that was meant to be enforced must never
// silently downgrade the gate.
func (r *FirmwareRolloutReconciler) rekorLogKey(ctx context.Context, namespace string, cfg fleetv1.SwarmadaSigningConfig) (crypto.PublicKey, error) {
	ref := cfg.RekorPublicKey
	if ref == nil {
		return nil, nil
	}
	secret := &corev1.Secret{}
	if err := r.Get(ctx, types.NamespacedName{Name: ref.Name, Namespace: namespace}, secret); err != nil {
		return nil, fmt.Errorf("loading rekorPublicKey secret %q: %w", ref.Name, err)
	}
	pemBytes, ok := secret.Data[ref.Key]
	if !ok {
		return nil, fmt.Errorf("rekorPublicKey: key %q absent from secret %q", ref.Key, ref.Name)
	}
	root, err := signing.ParseTrustRoot("rekor-log", pemBytes)
	if err != nil {
		return nil, fmt.Errorf("parsing rekorPublicKey: %w", err)
	}
	return root.PublicKey, nil
}

func (r *FirmwareRolloutReconciler) rekor() rekor.Checker {
	if r.Rekor != nil {
		return r.Rekor
	}
	return rekor.New()
}

// fetchSignature resolves a non-inline signatureRef to its raw detached-signature
// bytes — an oci:// ref through fetchOCISignature, any other through the https
// fetcher — applying the namespace's optional registry credentials to both, when
// they list the ref's host. The returned bytes are untrusted transport output — the
// caller verifies them against a trust root before use. A ref with any other scheme
// fails closed with an unsupported-scheme error.
func (r *FirmwareRolloutReconciler) fetchSignature(ctx context.Context, rollout *fleetv1.FirmwareRollout, sigRef string) (fetchedSignature, error) {
	cred, err := readRegistryCredential(ctx, r.Client, rollout.Namespace)
	if err != nil {
		return fetchedSignature{}, err
	}
	cred = boundRegistryCredential(ctx, &r.notes, r.Recorder, rollout, cred, signatureRefHost(sigRef))
	if strings.HasPrefix(sigRef, "oci://") {
		return r.fetchOCISignature(ctx, sigRef, cred)
	}
	sig, err := r.fetcher().Fetch(ctx, sigRef, cred)
	if err != nil {
		if errors.Is(err, artifact.ErrUnsupportedScheme) {
			return fetchedSignature{}, fmt.Errorf("signatureRef %q: unsupported scheme (only https:// and oci://<registry>/<repo>[@sha256:<digest>|:<tag>] are wired); refusing to dispatch unverified artifact", sigRef)
		}
		return fetchedSignature{}, fmt.Errorf("fetching signature %q: %w", sigRef, err)
	}
	return fetchedSignature{Sig: sig}, nil
}

// fetchedSignature is a detached signature and, for a cosign artifact, the simplesigning payload it
// was made over. Payload nil means the NATIVE form: the signature is over the artifact checksum
// directly. Payload non-nil means the caller must verify over the payload and then BIND it to the
// artifact — see cosign.go.
type fetchedSignature struct {
	Sig     []byte
	Payload []byte
}

// fetchOCISignature retrieves a detached signature stored as a digest-addressed
// OCI blob (oci://<registry>/<repo>@sha256:<digest>). It verifies the fetched
// bytes hash to the requested digest (content-address integrity — a registry
// serving wrong bytes fails here) BEFORE they reach signing.Verify. The bytes are
// still untrusted transport: only signing.Verify against a trust root makes them
// authoritative.
func (r *FirmwareRolloutReconciler) fetchOCISignature(ctx context.Context, sigRef string, cred *artifact.Credential) (fetchedSignature, error) {
	reg, repo, ref, isDigest, err := parseOCIRef(sigRef)
	if err != nil {
		return fetchedSignature{}, err
	}
	rc := toRegistryCred(cred)

	// Resolve the signature blob's digest. Digest-addressed refs carry it directly;
	// a tag-addressed ref resolves the tag's manifest and requires exactly one layer
	// (the signature blob) — the deterministic, unambiguous case.
	digest := ref
	var cosignSig []byte
	if !isDigest {
		layers, lerr := r.ociFetcher().Layers(ctx, reg, repo, ref, rc)
		if lerr != nil {
			return fetchedSignature{}, fmt.Errorf("resolving oci signature manifest %q: %w", sigRef, lerr)
		}
		// Cosign convention (the `sha256-<digest>.sig` tag): the signature is in a layer
		// ANNOTATION and the blob is the payload it was made over. Detected first, because such a
		// manifest legitimately carries layers the native single-layer rule would reject.
		cl, isCosign, cerr := selectCosignLayer(layers)
		if cerr != nil {
			return fetchedSignature{}, fmt.Errorf("oci signatureRef %q: %w", sigRef, cerr)
		}
		switch {
		case isCosign:
			digest, cosignSig = cl.Digest, cl.Signature
		case len(layers) == 1:
			digest = layers[0].Digest // native form: the blob IS the signature
		default:
			return fetchedSignature{}, fmt.Errorf("oci signatureRef %q: expected one signature layer or a cosign signature layer, got %d layers and no cosign annotation (use a digest-addressed ref)", sigRef, len(layers))
		}
	}

	blob, err := r.ociFetcher().Blob(ctx, reg, repo, digest, rc)
	if err != nil {
		return fetchedSignature{}, fmt.Errorf("fetching oci signature %q: %w", sigRef, err)
	}
	// Content-verify the fetched bytes against the (manifest-declared or ref-pinned) digest — a
	// registry serving wrong bytes fails closed HERE, before anything cryptographic runs. This
	// holds for the cosign payload too: the payload is what the signature covers, so serving a
	// different payload would break the binding check silently otherwise.
	sum := sha256.Sum256(blob)
	if got := "sha256:" + hex.EncodeToString(sum[:]); got != digest {
		return fetchedSignature{}, fmt.Errorf("oci signature %q content digest mismatch: got %s, want %s (refusing to dispatch)", sigRef, got, digest)
	}
	if cosignSig != nil {
		return fetchedSignature{Sig: cosignSig, Payload: blob}, nil
	}
	return fetchedSignature{Sig: blob}, nil
}

func (r *FirmwareRolloutReconciler) ociFetcher() OCIBlobFetcher {
	if r.OCIFetcher != nil {
		return r.OCIFetcher
	}
	return registry.New()
}

// parseOCIRef parses an OCI signature reference in either form:
//
//	oci://<registry>/<repo>@sha256:<digest>   (digest-addressed, isDigest=true)
//	oci://<registry>/<repo>:<tag>             (tag-addressed,    isDigest=false)
//
// ref is the digest or the tag accordingly. The registry may carry a port
// (reg:5000) — the tag separator is only sought AFTER the first '/', so the port
// colon is never mistaken for a tag.
func parseOCIRef(ociRef string) (reg, repo, ref string, isDigest bool, err error) {
	rest := strings.TrimPrefix(ociRef, "oci://")

	// Digest form: split on '@'.
	if at := strings.LastIndex(rest, "@"); at >= 0 {
		digest := rest[at+1:]
		reg, repo, ok := splitRegistryRepo(rest[:at])
		if !ok || !strings.HasPrefix(digest, "sha256:") || len(digest) != len("sha256:")+64 {
			return "", "", "", false, fmt.Errorf("malformed digest-addressed oci signatureRef %q", ociRef)
		}
		return reg, repo, digest, true, nil
	}

	// Tag form: the tag is after the last ':' that follows the first '/'.
	reg, rof, ok := splitRegistryRepo(rest) // rof = "<repo>[:tag]"
	if !ok {
		return "", "", "", false, fmt.Errorf("oci signatureRef %q missing repository path", ociRef)
	}
	colon := strings.LastIndex(rof, ":")
	if colon < 0 {
		return "", "", "", false, fmt.Errorf("oci signatureRef %q needs a tag or @digest", ociRef)
	}
	repo, tag := rof[:colon], rof[colon+1:]
	if repo == "" || tag == "" {
		return "", "", "", false, fmt.Errorf("malformed tag-addressed oci signatureRef %q", ociRef)
	}
	return reg, repo, tag, false, nil
}

// splitRegistryRepo splits "<registry>/<repo...>" at the first '/'.
func splitRegistryRepo(s string) (reg, repo string, ok bool) {
	slash := strings.IndexByte(s, '/')
	if slash < 0 {
		return "", "", false
	}
	reg, repo = s[:slash], s[slash+1:]
	return reg, repo, reg != "" && repo != ""
}

// toRegistryCred adapts the shared artifact Credential to the registry client's,
// keeping the hosts it is bound to.
func toRegistryCred(c *artifact.Credential) *registry.Credential {
	if c == nil {
		return nil
	}
	return &registry.Credential{BearerToken: c.BearerToken, Username: c.Username, Password: c.Password,
		Hosts: c.Registries}
}

func (r *FirmwareRolloutReconciler) fetcher() artifact.Fetcher {
	if r.Fetcher != nil {
		return r.Fetcher
	}
	return artifact.DefaultFetcher()
}

// readRegistryCredential reads the conventional per-namespace credentials Secret, for
// both the firmware fetch and the ModelPolicy registry watch. A missing Secret means an
// anonymous fetch (nil); a present one supplies a bearer token (key "token") or basic auth
// (keys "username"/"password"), and the hosts they may be presented to (key "registries").
func readRegistryCredential(ctx context.Context, c client.Reader, namespace string) (*artifact.Credential, error) {
	secret := &corev1.Secret{}
	err := c.Get(ctx, types.NamespacedName{Namespace: namespace, Name: registryCredentialsSecret}, secret)
	if apierrors.IsNotFound(err) {
		return nil, nil // anonymous
	}
	if err != nil {
		return nil, fmt.Errorf("reading registry credentials: %w", err)
	}
	cred := &artifact.Credential{
		BearerToken: string(secret.Data["token"]),
		Username:    string(secret.Data["username"]),
		Password:    string(secret.Data["password"]),
		Registries:  artifact.ParseRegistries(string(secret.Data[artifact.RegistriesKey])),
	}
	if cred.BearerToken == "" && cred.Username == "" && cred.Password == "" {
		return nil, nil
	}
	return cred, nil
}

// reasonRegistryCredentialsUnbound is the Warning Event reason for a credentials Secret
// that lists no host.
const reasonRegistryCredentialsUnbound = "RegistryCredentialsUnbound"

// reasonRegistryCredentialsHostIsURL is the Warning Event reason for a credentials Secret
// whose `registries` key has an entry written as a URL, which matches no host.
const reasonRegistryCredentialsHostIsURL = "RegistryCredentialsHostIsURL"

// boundRegistryCredential returns the credential to present to host for obj's fetch, or
// nil for an anonymous one. A credential that lists no host is presented to none: the
// fetch goes anonymous and one Warning Event on obj says why, once per object until the
// Secret lists a host.
func boundRegistryCredential(ctx context.Context, notes *heldNotes, rec record.EventRecorder,
	obj client.Object, cred *artifact.Credential, host string) *artifact.Credential {
	if cred == nil {
		return nil
	}
	key := string(obj.GetUID()) + "/" + obj.GetName() + "/registry-credentials-unbound"
	if !cred.Bound() {
		if notes.first(key) && rec != nil {
			rec.Event(obj, corev1.EventTypeWarning, reasonRegistryCredentialsUnbound,
				fmt.Sprintf("Secret %s has no %q key, so its credentials are presented to no host and "+
					"this fetch is anonymous; list the registry hosts the credentials are for in %q",
					registryCredentialsSecret, artifact.RegistriesKey, artifact.RegistriesKey))
		}
		return nil
	}
	notes.forget(key)
	urlKey := string(obj.GetUID()) + "/" + obj.GetName() + "/registry-credentials-url-entry"
	if n := len(artifact.URLShapedEntries(cred.Registries)); n > 0 {
		if notes.first(urlKey) && rec != nil {
			rec.Event(obj, corev1.EventTypeWarning, reasonRegistryCredentialsHostIsURL,
				fmt.Sprintf("Secret %s key %q has %d entries written as a URL; an entry is host[:port] "+
					"and is matched exactly, so a URL matches no host and fetches from it are anonymous",
					registryCredentialsSecret, artifact.RegistriesKey, n))
		}
	} else {
		notes.forget(urlKey)
	}
	bound := cred.For(host)
	if bound == nil {
		log.FromContext(ctx).V(1).Info("registry credentials not presented: host not listed",
			"host", host, "secret", registryCredentialsSecret)
	}
	return bound
}

// signatureRefHost is the host a signature reference is fetched from: the registry of
// an oci:// ref, the URL host of any other. Empty when it cannot be parsed, which no
// credential lists.
func signatureRefHost(sigRef string) string {
	if strings.HasPrefix(sigRef, "oci://") {
		reg, _, ok := splitRegistryRepo(strings.TrimPrefix(sigRef, "oci://"))
		if !ok {
			return ""
		}
		return reg
	}
	u, err := url.Parse(sigRef)
	if err != nil {
		return ""
	}
	return u.Host
}

// namespaceSigningConfig returns the signing config from the namespace's
// SwarmadaConfig. If none exists, it fails closed: signature verification is
// required but unconfigurable, so no artifact may be dispatched.
func (r *FirmwareRolloutReconciler) namespaceSigningConfig(ctx context.Context, namespace string) (fleetv1.SwarmadaSigningConfig, error) {
	var configs fleetv1.SwarmadaConfigList
	if err := r.List(ctx, &configs, client.InNamespace(namespace)); err != nil {
		return fleetv1.SwarmadaSigningConfig{}, fmt.Errorf("listing SwarmadaConfig: %w", err)
	}
	if len(configs.Items) == 0 {
		return fleetv1.SwarmadaSigningConfig{}, fmt.Errorf("no SwarmadaConfig in namespace %q; cannot determine signing policy (fail closed)", namespace)
	}
	return configs.Items[0].Spec.Signing, nil
}

func (r *FirmwareRolloutReconciler) loadTrustRoots(ctx context.Context, namespace string, refs []fleetv1.SigningTrustRoot) ([]signing.TrustRoot, error) {
	var roots []signing.TrustRoot
	for _, ref := range refs {
		secret := &corev1.Secret{}
		if err := r.Get(ctx, types.NamespacedName{Name: ref.SecretRef.Name, Namespace: namespace}, secret); err != nil {
			return nil, fmt.Errorf("loading trust root %q secret: %w", ref.Name, err)
		}
		pemBytes, ok := secret.Data[ref.SecretRef.Key]
		if !ok {
			return nil, fmt.Errorf("trust root %q: key %q absent from secret %q", ref.Name, ref.SecretRef.Key, ref.SecretRef.Name)
		}
		root, err := signing.ParseTrustRoot(ref.Name, pemBytes)
		if err != nil {
			return nil, err
		}
		roots = append(roots, root)
	}
	if len(roots) == 0 {
		return nil, fmt.Errorf("signature verification required but no trust roots are configured")
	}
	return roots, nil
}

// failVerification records a fail-closed verification result: the rollout goes
// Failed with SignatureVerified=False, a FIRMWARE_SIGNATURE_FAILED audit event is
// emitted, and NO robot is dispatched.
func (r *FirmwareRolloutReconciler) failVerification(ctx context.Context, rollout *fleetv1.FirmwareRollout, cause error) (ctrl.Result, error) {
	base := rollout.DeepCopy()
	rollout.Status.Phase = fleetv1.RolloutPhaseFailed
	upsertCondition(&rollout.Status.Conditions, conditionSignatureVerified, metav1.ConditionFalse,
		"VerificationFailed", cause.Error())
	if r.Recorder != nil {
		r.Recorder.Event(rollout, corev1.EventTypeWarning, "FIRMWARE_SIGNATURE_FAILED",
			fmt.Sprintf("artifact verification failed; rollout blocked: %v", cause))
	}
	// Also seal into the tamper-evident chain. The Kubernetes Event above stays — it is
	// what an operator sees in `kubectl describe` — but an Event is subject to namespace
	// retention and is NOT covered by the hash chain, so on its own it cannot evidence
	// that unverified firmware was refused. That gap is the reason this row existed.
	r.sealFirmwareEvent(ctx, rollout, audit.EventFirmwareSignatureFailed, "verify", audit.OutcomeDenied,
		map[string]string{
			"firmware_uri":    rollout.Spec.FirmwareURI,
			"artifact_digest": rollout.Spec.FirmwareChecksum,
			"reason":          cause.Error(),
		})
	if err := r.Status().Patch(ctx, rollout, client.MergeFrom(base)); err != nil {
		return ctrl.Result{}, fmt.Errorf("recording verification failure: %w", err)
	}
	log.FromContext(ctx).Info("firmware rollout blocked by verification (fail closed)", "reason", cause.Error())
	return ctrl.Result{}, nil // terminal; do not requeue a bad signature into a dispatch
}

// clearPendingFirmware removes the PullOnIdle dispatch annotations from a robot that now
// reports the target version running.
//
// Nothing cleared them before. The consequence is not cosmetic: the annotation is also the
// "updating" classifier above, so a stale marker makes a finished robot indistinguishable
// from one still installing, and a later rollout to the same version reads a leftover
// dispatch as its own. Failures deliberately keep their annotation -- installFailedForRollout
// is what reads it -- so only the success edge clears.
//
// Best-effort: a failure here is logged, not returned. The robot is already classified done
// on this pass, and the next reconcile retries the clear.
func (r *FirmwareRolloutReconciler) clearPendingFirmware(ctx context.Context, rob *fleetv1.Robot) {
	if rob.Annotations[annPendingFirmwareVersion] == "" {
		return
	}
	base := rob.DeepCopy()
	delete(rob.Annotations, annPendingFirmwareVersion)
	delete(rob.Annotations, annPendingFirmwareURI)
	delete(rob.Annotations, annPendingFirmwareChecksum)
	if err := r.Patch(ctx, rob, client.MergeFrom(base)); err != nil {
		log.FromContext(ctx).Error(err, "clearing pending-firmware annotations", "robot", rob.Name)
	}
}

// withdrawPendingFirmware removes the PullOnIdle dispatch annotations from a robot a stop
// holds before its install began. Unlike clearPendingFirmware it is not best-effort: a
// failed patch fails the pass, which is retried, so the instruction is never left standing
// on the robot unnoticed.
func (r *FirmwareRolloutReconciler) withdrawPendingFirmware(ctx context.Context, rollout *fleetv1.FirmwareRollout,
	rob *fleetv1.Robot, held string) error {
	base := rob.DeepCopy()
	delete(rob.Annotations, annPendingFirmwareVersion)
	delete(rob.Annotations, annPendingFirmwareURI)
	delete(rob.Annotations, annPendingFirmwareChecksum)
	if err := r.Patch(ctx, rob, client.MergeFrom(base)); err != nil {
		return fmt.Errorf("withdrawing pending firmware from %s: %w", rob.Name, err)
	}
	log.FromContext(ctx).Info("pending firmware withdrawn from a robot under an emergency stop",
		"robot", rob.Name, "version", rollout.Spec.NewVersion, "held", held)
	if r.Recorder != nil {
		r.Recorder.Event(rollout, corev1.EventTypeWarning, "FirmwareUpdateWithheld",
			fmt.Sprintf("robot %s is under an emergency stop (%s): its pending firmware %s was withdrawn before its "+
				"install began; it is offered again once nothing holds the robot", rob.Name, held, rollout.Spec.NewVersion))
	}
	return nil
}

// firmwareInstallBegun reports whether the robot has reported that its install of version
// is under way since this rollout's dispatch: its install state reads Updating for that
// version, reported no earlier than the batch entry, or its adapter reports a phase past
// the download (Installing, Verifying, Rebooting). A download alone (Pulling) has not
// begun the install. Without a report that orders after the dispatch, the install is
// taken as not begun, so a held robot's pull is withdrawn rather than left standing.
func firmwareInstallBegun(rob *fleetv1.Robot, entry *fleetv1.RolloutBatchRobot, version string) bool {
	if entry == nil {
		return false
	}
	switch entry.UpdatePhase {
	case "Installing", "Verifying", "Rebooting":
		return true
	}
	fi := rob.Status.FirmwareInstall
	if fi == nil || fi.Status != fleetv1.FirmwareInstallUpdating {
		return false
	}
	if fi.AttemptedVersion != "" && fi.AttemptedVersion != version {
		return false
	}
	if fi.ReportedAt == nil || entry.UpdateStartedAt == nil {
		return false
	}
	return !fi.ReportedAt.Time.Before(entry.UpdateStartedAt.Time)
}

// dispatch annotates a robot with the pending-firmware update (PullOnIdle).
func (r *FirmwareRolloutReconciler) dispatch(ctx context.Context, rob *fleetv1.Robot, rollout *fleetv1.FirmwareRollout) error {
	base := rob.DeepCopy()
	if rob.Annotations == nil {
		rob.Annotations = map[string]string{}
	}
	rob.Annotations[annPendingFirmwareVersion] = rollout.Spec.NewVersion
	rob.Annotations[annPendingFirmwareURI] = rollout.Spec.FirmwareURI
	rob.Annotations[annPendingFirmwareChecksum] = rollout.Spec.FirmwareChecksum
	if err := r.Patch(ctx, rob, client.MergeFrom(base)); err != nil {
		return fmt.Errorf("annotating pending firmware on %s: %w", rob.Name, err)
	}
	if r.Recorder != nil {
		r.Recorder.Event(rollout, corev1.EventTypeNormal, "FirmwareRolloutBatchStarted",
			fmt.Sprintf("robot %s scheduled for firmware %s", rob.Name, rollout.Spec.NewVersion))
	}
	// Sealed after the annotation patch lands: the install has begun only once the robot
	// carries the pending-firmware annotation, and the same annotation is what stops this
	// robot being dispatched again, so the entry cannot repeat.
	r.sealFirmwareEvent(ctx, rollout, audit.EventFirmwareInstallStarted, "install", audit.OutcomeAllowed,
		map[string]string{
			"old_version": rob.Status.FirmwareVersion,
			"new_version": rollout.Spec.NewVersion,
			"robot":       rob.Name,
		})
	return nil
}

// ── Pure helpers ──────────────────────────────────────────────────────────────

// heldFromUpdate reports whether a robot takes no firmware or model update because of an
// emergency stop: a stop is in force on it (robotUnderEstop: Stopping, Stopped or Failed,
// its own trigger, or a zone's or the namespace's stop it records), or it is in the
// post-clear window (Resuming), not yet released by an operator. An update attempt is gated
// on the robot's live physical state, and a robot receiving an emergency stop is not in a
// state to be updated (RFC-0001 #firmwarerollout). It is held back like any robot a safety
// constraint holds back, and re-evaluated on the next pass.
func heldFromUpdate(rob *fleetv1.Robot) bool {
	return robotUnderEstop(rob) || rob.Status.EstopState == fleetv1.RobotEstopResuming
}

func eligibleForFirmwareUpdate(rob *fleetv1.Robot, rollout *fleetv1.FirmwareRollout) bool {
	if heldFromUpdate(rob) {
		return false
	}
	sc := rollout.Spec.SafetyConstraints
	if sc.RequiresIdleState() && rob.Status.Phase != fleetv1.RobotPhaseIdle {
		return false
	}
	if rob.Status.BatteryPercent == nil || *rob.Status.BatteryPercent < sc.MinBatteryPct {
		return false
	}
	return true
}

// computeFirmwareStatus projects the classified buckets onto the rollout status.
//
// The count identity it maintains, and the one crds/firmwarerollout.md publishes:
//
//	robotsTotal = robotsUpdated + robotsPending + robotsFailed + len(excludedRobots)
//
// currentBatch is not a term in it. A robot mid-install has neither completed nor failed nor
// been excluded, so it is counted in robotsPending: len(currentBatch) is a SUB-COUNT of
// robotsPending, not a sibling of it. robotsSkipped is a sub-count on the same footing — a
// robot held back by a safety constraint is still awaiting its update.
func computeFirmwareStatus(total, done int, updating, failed, skipped, excluded []*fleetv1.Robot, paused bool,
	prior []fleetv1.RolloutBatchRobot, priorFailed []fleetv1.RolloutRobotResult) fleetv1.FirmwareRolloutStatus {
	st := fleetv1.FirmwareRolloutStatus{
		//nolint:gosec // small fleet counts
		RobotsTotal: int32(total),
		//nolint:gosec // small fleet counts
		RobotsUpdated: int32(done),
		// Failed robots are NOT pending: a rollout that keeps counting them as outstanding
		// never settles, and an operator reading "3 pending" cannot tell work still to do
		// from work that has already gone wrong.
		//nolint:gosec // small fleet counts
		RobotsPending: int32(total - done - len(failed) - len(excluded)),
		//nolint:gosec // small fleet counts
		RobotsFailed: int32(len(failed)),
		//nolint:gosec // small fleet counts
		RobotsSkipped: int32(len(skipped)),
		CurrentBatch:  buildRolloutBatch(updating, prior, firmwareInitialPhase, firmwarePrevVersion, false),
		FailedRobots:  firmwareFailedResults(failed, prior, priorFailed),
	}
	if len(excluded) > 0 {
		names := make([]string, 0, len(excluded))
		for _, r := range excluded {
			names = append(names, r.Name)
		}
		sort.Strings(names)
		st.ExcludedRobots = names
	}
	switch {
	// Excluded robots count as settled, so a resumed rollout can still reach a terminal
	// phase — which is what makes its record deletable (ADR-0041).
	case total > 0 && done+len(excluded) == total:
		st.Phase = fleetv1.RolloutPhaseSucceeded
	// Paused is checked BEFORE Failed and is deliberately not terminal: pauseOnError halted
	// the rollout so an operator could decide, and `swarmctl rollout resume` is the exit
	// (ADR-0041). Calling that Failed would take the decision away and delete the state the
	// operator needs to make it.
	case paused:
		st.Phase = fleetv1.RolloutPhasePaused
	// Terminal failure. Every targeted robot has settled — updated, failed, or excluded by a
	// resume — and at least one settled as a failure that was neither repaired nor excluded.
	// There is no further work this rollout can do and no configuration under which it will
	// do any, so saying so is the only honest answer; Succeeded would claim a convergence
	// that did not happen, and the InProgress this used to report was a rollout stranded
	// live, undeletable by a delete guard it could never satisfy.
	//
	// Reachable only with pauseOnError: false, since `paused` above claims every other
	// failure. Derived per reconcile rather than latched, like `paused`: a robot repaired out
	// of band classifies as done again and the rollout resumes converging.
	case total > 0 && len(failed) > 0 && done+len(failed)+len(excluded) == total:
		st.Phase = fleetv1.RolloutPhaseFailed
	case len(updating) > 0 || done > 0 || len(failed) > 0:
		st.Phase = fleetv1.RolloutPhaseInProgress
	default:
		st.Phase = fleetv1.RolloutPhasePending
	}
	return st
}

// installFailedForRollout reports whether a robot's own firmware report is a CONFIRMED
// failure belonging to THIS rollout's dispatch.
//
// Both halves matter. The robot must be in the batch (so the failure concerns work this
// rollout started), and the report must be no older than the dispatch — otherwise a robot
// still carrying a Failed state from an EARLIER rollout would be counted as having failed
// this one the moment it was dispatched, before it had done anything at all.
func installFailedForRollout(rob *fleetv1.Robot, entry *fleetv1.RolloutBatchRobot) bool {
	fi := rob.Status.FirmwareInstall
	if fi == nil || fi.Status != fleetv1.FirmwareInstallFailed || entry == nil {
		return false
	}
	if fi.ReportedAt == nil || entry.UpdateStartedAt == nil {
		return false // cannot establish order; refuse to attribute rather than guess
	}
	return !fi.ReportedAt.Time.Before(entry.UpdateStartedAt.Time)
}

// firmwareFailedResults projects the failed robots onto the status list.
//
// previousVersion has two sources because the batch entry it is captured from does not outlive
// the pass on which the robot fails: prefer the live batch entry, and fall back to the value
// already recorded against this robot. Without the fallback the version an operator needs — the
// one the robot is being rolled back from — is dropped one reconcile after the failure.
func firmwareFailedResults(failed []*fleetv1.Robot, prior []fleetv1.RolloutBatchRobot,
	priorFailed []fleetv1.RolloutRobotResult) []fleetv1.RolloutRobotResult {
	if len(failed) == 0 {
		return nil
	}
	out := make([]fleetv1.RolloutRobotResult, 0, len(failed))
	for _, rob := range failed {
		res := fleetv1.RolloutRobotResult{RobotName: rob.Name, Namespace: rob.Namespace}
		if fi := rob.Status.FirmwareInstall; fi != nil {
			res.Reason = fi.FailureReason
			res.FailedAt = fi.ReportedAt
		}
		switch e, p := batchEntryFor(prior, rob.Name), failedResultFor(priorFailed, rob.Name); {
		case e != nil:
			res.PreviousVersion = e.PreviousVersion
		case p != nil:
			res.PreviousVersion = p.PreviousVersion
		}
		out = append(out, res)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].RobotName < out[j].RobotName })
	return out
}

const (
	// firmwareInitialPhase is the updatePhase a robot enters the firmware batch at,
	// before the adapter reports finer progress via UpdateProgress (RFC-0001 #firmwarerollout-schema).
	firmwareInitialPhase = "Pulling"
	// modelInitialPhase is the equivalent entry phase for a model rollout (RFC-0001 #modelrollout-schema).
	modelInitialPhase = "Downloading"
)

// firmwarePrevVersion is the version a robot is on before a firmware update — its
// currently-running firmware.
func firmwarePrevVersion(r *fleetv1.Robot) string { return r.Status.FirmwareVersion }

// buildRolloutBatch builds the structured active-update batch. It PRESERVES each
// robot's reported updatePhase / updateStartedAt / previousVersion across reconciles
// (only new entrants are initialized to initialPhase and now), so an adapter's
// UpdateProgress is never clobbered when the controller recomputes rollout status —
// the two writers cooperate. Entries are sorted by robot name for a stable diff.
//
// stampSuspended marks the model-rollout path (ADR-0023): a model update suspends
// the robot's model-driven capabilities at batch entry (the model is marked
// Updating), so a NEW entrant records CapabilitiesSuspendedAt at that instant.
// Because a continuing entrant is preserved by name, the stamp is stable for the
// life of an attempt; a robot that left the batch and re-enters (e.g. Auto
// rollback → Updating) is a fresh entrant and gets a fresh stamp — the per-attempt
// semantics come for free. Firmware rollouts suspend nothing and pass false.
func buildRolloutBatch(updating []*fleetv1.Robot, prior []fleetv1.RolloutBatchRobot, initialPhase string, prevVersion func(*fleetv1.Robot) string, stampSuspended bool) []fleetv1.RolloutBatchRobot {
	priorByName := make(map[string]fleetv1.RolloutBatchRobot, len(prior))
	for _, b := range prior {
		priorByName[b.RobotName] = b
	}
	out := make([]fleetv1.RolloutBatchRobot, 0, len(updating))
	for _, r := range updating {
		if p, ok := priorByName[r.Name]; ok {
			out = append(out, p) // preserve reported phase / startedAt / previousVersion
			continue
		}
		now := metav1.Now()
		entry := fleetv1.RolloutBatchRobot{
			RobotName:       r.Name,
			Namespace:       r.Namespace,
			UpdateStartedAt: &now,
			PreviousVersion: prevVersion(r),
			UpdatePhase:     initialPhase,
		}
		if stampSuspended {
			suspendedAt := now
			entry.CapabilitiesSuspendedAt = &suspendedAt
		}
		out = append(out, entry)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].RobotName < out[j].RobotName })
	return out
}

// setCondition upserts a metav1.Condition in a slice.
func upsertCondition(conds *[]metav1.Condition, condType string, status metav1.ConditionStatus, reason, msg string) {
	now := metav1.Now()
	for i := range *conds {
		if (*conds)[i].Type == condType {
			if (*conds)[i].Status != status {
				(*conds)[i].LastTransitionTime = now
			}
			(*conds)[i].Status = status
			(*conds)[i].Reason = reason
			(*conds)[i].Message = msg
			return
		}
	}
	*conds = append(*conds, metav1.Condition{
		Type: condType, Status: status, Reason: reason, Message: msg, LastTransitionTime: now,
	})
}

func conditionIsFalse(conds []metav1.Condition, condType string) bool {
	for _, c := range conds {
		if c.Type == condType {
			return c.Status == metav1.ConditionFalse
		}
	}
	return false
}

func conditionIsFalseWithReason(conds []metav1.Condition, condType, reason string) bool {
	for _, c := range conds {
		if c.Type == condType {
			return c.Status == metav1.ConditionFalse && c.Reason == reason
		}
	}
	return false
}

// notEnforcedMessage is the SignatureVerified message when SwarmadaConfig does not enforce
// signing: the checksum format was checked, and no signature was.
func notEnforcedMessage(sigRef string) string {
	if sigRef == "" {
		return "signature verification is not enforced (SwarmadaConfig spec.signing); the checksum format was checked, no signature was"
	}
	return "signature verification is not enforced (SwarmadaConfig spec.signing); firmwareSignatureRef is set but was not verified"
}

// SetupWithManager registers the FirmwareRollout controller.
func (r *FirmwareRolloutReconciler) SetupWithManager(mgr ctrl.Manager) error {
	robotToRollouts := handler.EnqueueRequestsFromMapFunc(func(ctx context.Context, obj client.Object) []reconcile.Request {
		var rollouts fleetv1.FirmwareRolloutList
		if err := r.List(ctx, &rollouts, client.InNamespace(obj.GetNamespace())); err != nil {
			return nil
		}
		reqs := make([]reconcile.Request, 0, len(rollouts.Items))
		for i := range rollouts.Items {
			reqs = append(reqs, reconcile.Request{NamespacedName: types.NamespacedName{
				Name: rollouts.Items[i].Name, Namespace: rollouts.Items[i].Namespace,
			}})
		}
		return reqs
	})

	inNamespace := handler.EnqueueRequestsFromMapFunc(func(ctx context.Context, obj client.Object) []reconcile.Request {
		return rolloutsOfNamespace(ctx, r, &fleetv1.FirmwareRolloutList{}, obj)
	})

	return ctrl.NewControllerManagedBy(mgr).
		For(&fleetv1.FirmwareRollout{}).
		Watches(&fleetv1.Robot{}, robotToRollouts).
		Watches(&fleetv1.FleetZone{}, inNamespace).
		Watches(&fleetv1.SwarmadaConfig{}, inNamespace).
		Complete(r)
}
````

## internal/controller/modelrollout_controller.go

Source URL: https://raw.githubusercontent.com/swarmada/swarmada/8415495eff904b5d03c47ffdb263d895c0ed752a/internal/controller/modelrollout_controller.go

````go
/*
Copyright 2026 The Swarmada Authors.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package controller

import (
	"context"
	"fmt"
	"sort"
	"strconv"
	"strings"
	"time"

	corev1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/api/equality"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/types"
	"k8s.io/client-go/tools/record"
	"k8s.io/client-go/util/retry"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/handler"
	"sigs.k8s.io/controller-runtime/pkg/log"
	"sigs.k8s.io/controller-runtime/pkg/reconcile"

	fleetv1 "github.com/swarmada/swarmada/api/v1"
	"github.com/swarmada/swarmada/internal/audit"
	"github.com/swarmada/swarmada/internal/command"
)

// ModelRolloutReconciler is the OTA/Model Update Manager for ModelRollout
// (RFC-0001 #control-plane-ota-model-update-manager). It selects target robots by safety constraints, marks the
// model Updating on batch entry (which suspends the model-driven capabilities the
// Capability Controller derives — the effective model-update-manager suspension without writing
// status.capabilities directly), and projects the granted capabilities into
// Robot.status.modelGrantedCapabilities[] once a robot reports the model Active at
// the new version. It never writes Robot.spec.
//
// The model_update Command push, the adapter-side artifact signature/checksum
// verification (RFC-0001 #fleet-adapter-protocol-fleet-adapter-compliance-checklist), and the Active/Failed report via telemetry ride the
// ControlStream wire (the push through Pusher, below); this drives the
// control-plane state machine over the observable Robot status.
type ModelRolloutReconciler struct {
	client.Client
	Scheme   *runtime.Scheme
	Recorder record.EventRecorder
	// Audit seals the RFC-0001 #safety-required-events model-update and artifact-verification entries into the
	// tamper-evident chain. Nil disables recording; the rollout is unaffected.
	Audit audit.Recorder
	// Pusher pushes the model_update Command to a robot's adapter over ControlStream
	// (RFC-0001 #control-plane-ota-model-update-manager). When set, batch entry is gated on the adapter acknowledging the
	// update, so capabilities are never suspended for an update that cannot be
	// delivered. Nil (ControlStream disabled) falls back to observe-only: the model
	// is marked Updating and the controller awaits the adapter-reported Active.
	Pusher command.ModelUpdatePusher
	// APIReader reads the API server directly, bypassing the manager's cache. The rollout
	// is re-read through it before a step that must not repeat — a model_update push, and
	// the audit entry for the pause — because a Robot event can queue a reconcile that
	// reads a cached rollout from before this controller's last status write, and would
	// push an artifact already refused or seal the same pause again. Nil falls back to
	// Client.
	APIReader client.Reader
	// Acks records each acknowledged model_update for the UpdateProgress ingestor, which
	// shares it, so a failure the robot reports after acknowledging is recorded even before
	// the batch is written (ModelAckLedger). Nil records nothing.
	Acks *ModelAckLedger

	// notes keeps the ModelRollbackWithheld Event to one per held robot.
	notes heldNotes
}

// +kubebuilder:rbac:groups=swarmada.io,resources=modelrollouts,verbs=get;list;watch;patch
// +kubebuilder:rbac:groups=swarmada.io,resources=modelrollouts/status,verbs=get;update;patch
// +kubebuilder:rbac:groups=swarmada.io,resources=robots,verbs=get;list;watch
// +kubebuilder:rbac:groups=swarmada.io,resources=robots/status,verbs=get;update;patch
// +kubebuilder:rbac:groups=swarmada.io,resources=fleetzones,verbs=get;list;watch
// +kubebuilder:rbac:groups=swarmada.io,resources=swarmadaconfigs,verbs=get;list;watch

type modelState int

const (
	modelPending modelState = iota
	modelUpdating
	modelDone
	modelFailed
	// modelNewer — the robot already runs a version STRICTLY NEWER than the target. It is
	// not a rollout candidate: dispatching would downgrade it. Distinct from modelDone,
	// which means "already at the target", because the two need different reporting — an
	// operator reading `robotsUpdated` should not be told a downgrade-refusal succeeded.
	modelNewer
)

// Reconcile drives one ModelRollout.
func (r *ModelRolloutReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	logger := log.FromContext(ctx).WithValues("modelrollout", req.NamespacedName)

	rollout := &fleetv1.ModelRollout{}
	if err := r.Get(ctx, req.NamespacedName, rollout); err != nil {
		return ctrl.Result{}, client.IgnoreNotFound(err)
	}

	// An EdgeNode-targeted rollout is SPECIFIED but NOT IMPLEMENTED at v0.4: no
	// controller resolves targetSelector against EdgeNodes and no ModelUpdate is
	// dispatched over an edge node's uplink session. Refuse it explicitly rather
	// than fall through — the code below resolves the selector against ROBOTS, so
	// falling through would push an edge model onto whatever robots happen to carry
	// the node labels. Silence is the failure mode worth spending an event on.
	if rollout.Spec.TargetKind == fleetv1.RolloutTargetEdgeNode {
		if r.Recorder != nil {
			r.Recorder.Eventf(rollout, corev1.EventTypeWarning, "TargetKindNotImplemented",
				"spec.targetKind: EdgeNode is specified but not implemented at v0.4; no node is updated by this rollout")
		}
		logger.Info("skipping EdgeNode-targeted ModelRollout: not implemented at v0.4")
		return ctrl.Result{}, nil
	}

	sel, err := metav1.LabelSelectorAsSelector(&rollout.Spec.TargetSelector)
	if err != nil {
		return ctrl.Result{}, fmt.Errorf("invalid targetSelector: %w", err)
	}
	var robots fleetv1.RobotList
	if err := r.List(ctx, &robots, client.InNamespace(req.Namespace),
		client.MatchingLabelsSelector{Selector: sel}); err != nil {
		return ctrl.Result{}, fmt.Errorf("listing target robots: %w", err)
	}

	holds, err := readRolloutHolds(ctx, r.Client, req.Namespace)
	if err != nil {
		return ctrl.Result{}, err
	}

	now := time.Now()
	windowOnly := rollout.Spec.SafetyConstraints.MaintenanceWindowOnly

	// Carry forward the rollback bookkeeping — the previous version survives ONLY
	// here (once a robot reports newVersion, its running version is the new one), and
	// a robot this rollout already reverted must never be pulled back into an update
	// loop. Both are seeded from the persisted status and mutated below.
	rollbackVersions := copyStringMap(rollout.Status.RollbackVersions)
	rolledBackSet := make(map[string]bool, len(rollout.Status.RolledBackRobots))
	for _, n := range rollout.Status.RolledBackRobots {
		rolledBackSet[n] = true
	}

	// An operator resume converts the robots that are currently failed into this
	// rollout's excluded set (ADR-0041), so the pause cannot re-latch off the same
	// robots on the very next reconcile. Applied BEFORE classification so this pass
	// already sees them excluded.
	if done, err := r.applyResume(ctx, rollout); err != nil {
		return ctrl.Result{}, err
	} else if done {
		return ctrl.Result{Requeue: true}, nil
	}
	excludedSet := make(map[string]bool, len(rollout.Status.ExcludedRobots))
	for _, n := range rollout.Status.ExcludedRobots {
		excludedSet[n] = true
	}
	// Robots whose adapter refused this rollout's artifact on its signature. The refusal
	// leaves no trace on the Robot (nothing was installed), so status.failedRobots is where
	// it is kept, and it is what stops the refused artifact from being pushed again.
	refused := signatureRefusals(rollout.Status.FailedRobots)

	var done, updating, failed, eligible, rolledBack, reverting, revertFailed, newer, excluded []*fleetv1.Robot
	for i := range robots.Items {
		rob := &robots.Items[i]
		if rolledBackSet[rob.Name] {
			// This rollout has pushed a rollback to this robot, so it is never re-updated —
			// a fixed model needs a fresh rollout. Whether it has SETTLED is a separate
			// question, and answering it with the acknowledgement was the defect: an ack is
			// a promise to revert, and only the robot reporting the previous version Active
			// is evidence that it did. Until then the model entry is still Updating and the
			// capabilities it grants are still suspended, so counting it settled let the
			// rollout report Succeeded over robots that had lost their capabilities.
			//
			// An empty revert target means the revert has already been observed (the target
			// is dropped when it lands) or that the entry predates this tracking, so the
			// robot is taken as settled rather than stranded reverting for ever.
			switch target := rollbackVersions[rob.Name]; {
			case target == "" || modelActiveAt(rob, rollout.Spec.ModelName, target):
				rolledBack = append(rolledBack, rob)
				delete(rollbackVersions, rob.Name)
			case classifyModel(rob, rollout.Spec.ModelName, target) == modelFailed:
				// The revert itself failed. Counted failed, not reverting: it is the one
				// classification that reaches an operator (or terminates the rollout under
				// pauseOnError: false) instead of waiting for a report that is not coming.
				// Merged into `failed` AFTER the rollback pass below, so this robot is never
				// pushed a second rollback.
				revertFailed = append(revertFailed, rob)
			default:
				reverting = append(reverting, rob)
			}
			continue
		}
		if excludedSet[rob.Name] {
			// An operator resumed past this robot. Same treatment as a rolled-back one:
			// out of every bucket, so it neither re-pauses the rollout (it is no longer
			// in `failed`) nor is re-dispatched to (it is no longer in `eligible`) nor
			// holds the rollout short of terminal (it counts as settled below).
			excluded = append(excluded, rob)
			continue
		}
		switch classifyModel(rob, rollout.Spec.ModelName, rollout.Spec.NewVersion) {
		case modelDone:
			done = append(done, rob)
			// Succeeded only for a robot this rollout actually updated: one already running
			// the target version before the rollout started installed nothing.
			if batchEntryFor(rollout.Status.CurrentBatch, rob.Name) != nil {
				r.sealModelEvent(ctx, rollout, rob.Name, audit.EventModelUpdateSucceeded, "update",
					audit.OutcomeAllowed, map[string]string{
						"model_name":  rollout.Spec.ModelName,
						"new_version": rollout.Spec.NewVersion,
					})
			}
		case modelUpdating:
			updating = append(updating, rob)
		case modelFailed:
			failed = append(failed, rob)
			// A failed model STAYS failed across reconciles, so the edge is the first
			// appearance: a robot not already recorded in status.failedRobots.
			if !wasAlreadyFailed(rollout.Status.FailedRobots, rob.Name) {
				reason := modelFailureReason(rob, rollout.Spec.ModelName)
				r.sealModelEvent(ctx, rollout, rob.Name, audit.EventModelUpdateFailed, "update",
					audit.OutcomeError, map[string]string{
						"model_name": rollout.Spec.ModelName,
						"reason":     reason,
					})
			}
		case modelNewer:
			newer = append(newer, rob)
		default:
			if _, ok := refused[rob.Name]; ok {
				failed = append(failed, rob)
				continue
			}
			if holds.why(rob) == "" && eligibleForModelUpdate(rob, rollout) && withinRolloutWindow(rob, windowOnly, now) {
				eligible = append(eligible, rob)
			}
		}
	}

	total := len(robots.Items)
	deferred := false

	// ── Auto rollback (§6.7) ─────────────────────────────────────────────────────
	// Under rollbackPolicy=Auto, a failed robot with a known previous version is
	// reverted (the adapter reactivates the retained model) instead of pausing the
	// rollout. A robot we cannot safely revert — unknown previous version, or an
	// undeliverable rollback push — stays failed (fail-safe, surfaced), matching
	// Manual. Manual (the default) reverts nothing and pauses on failure.
	if rollout.Spec.RollbackPolicy == fleetv1.ModelRollbackAuto {
		var stillFailed []*fleetv1.Robot
		sort.Slice(failed, func(i, j int) bool { return failed[i].Name < failed[j].Name })
		for _, rob := range failed {
			prev := rollbackVersions[rob.Name]
			if prev == "" {
				stillFailed = append(stillFailed, rob) // nothing to revert to
				continue
			}
			// A rollback is a model push like any other: a robot a stop holds is not pushed
			// one. It stays failed and is retried, as an undeliverable rollback push is.
			held := holds.why(rob)
			if held == "" && r.Pusher != nil {
				held = heldNow(ctx, r.liveReader(), rob)
			}
			if held != "" {
				if r.notes.first(heldNoteKey(rollout, rob.Name, "rollback")) {
					r.event(rollout, corev1.EventTypeWarning, "ModelRollbackWithheld",
						fmt.Sprintf("robot %s is under an emergency stop (%s): its rollback to %s is not pushed while "+
							"the stop holds it, and is retried once nothing holds the robot", rob.Name, held, prev))
				}
				stillFailed = append(stillFailed, rob)
				deferred = true
				continue
			}
			r.notes.forget(heldNoteKey(rollout, rob.Name, "rollback"))
			reverted, err := r.rollbackRobot(ctx, rob, rollout, prev)
			if err != nil {
				return ctrl.Result{}, err
			}
			if !reverted {
				stillFailed = append(stillFailed, rob) // push not delivered — retry
				deferred = true
				continue
			}
			// The revert target is deliberately NOT dropped here: it is what recognises the
			// revert when the robot reports it, and dropping it on the push left nothing
			// able to tell a completed revert from an outstanding one.
			rolledBackSet[rob.Name] = true
			reverting = append(reverting, rob)
		}
		failed = stillFailed
	}
	// A failed revert joins the failed set only now, past the rollback pass, so it cannot be
	// pushed a second rollback on the same reconcile.
	failed = append(failed, revertFailed...)
	sort.Slice(failed, func(i, j int) bool { return failed[i].Name < failed[j].Name })

	// A revert is an error for pauseOnError. Under rollbackPolicy Auto a robot whose update
	// failed is reverted, and the rollback pass above takes it out of `failed`, so judging the
	// halt on `failed` alone let a model that fails on every robot be pushed to every robot in
	// turn. The model failed on the reverted robot; the revert only repaired it. So a reverted
	// robot halts the rollout after the batch in which it happened, until an operator resume
	// acknowledges it by adding it to status.excludedRobots, exactly as a resume past a failed
	// robot does (ADR-0041). What a revert counts toward is unchanged: a landed revert is
	// settled toward Succeeded, so the terminal phase is the same as before.
	var unackedReverts, ackedReverts []string
	for _, group := range [][]*fleetv1.Robot{rolledBack, reverting} {
		for _, rob := range group {
			if excludedSet[rob.Name] {
				ackedReverts = append(ackedReverts, rob.Name)
			} else {
				unackedReverts = append(unackedReverts, rob.Name)
			}
		}
	}
	sort.Strings(unackedReverts)
	pausedOnError := (len(failed) > 0 || len(unackedReverts) > 0) &&
		rollout.Spec.Strategy.RollingUpdateOrDefault().PausesOnError()

	// The OPERATOR hold, composed with — never substituted for — the error halt.
	// spec.desiredState: Paused withholds dispatch of any further robot. The two
	// holds are independent and the rollout dispatches only when NEITHER is in
	// force, which is the property that makes the operator's field safe: writing
	// `Running` withdraws the operator's own hold and cannot touch a pauseOnError
	// halt, whose exit is the rollout-resume verb because that verb also decides
	// what happens to the robots that failed (ADR-0041). An operator therefore
	// cannot use a spec field to push a rollout past a failure the halt exists to
	// surface.
	//
	// In-flight updaters are NOT interrupted, and on this kind that matters more
	// than on firmware: a robot in the batch has its models marked Updating, which
	// suspends every capability those models grant, and the rollout's own status is
	// what un-suspends them. Yanking a robot out of the batch mid-update would
	// strand exactly those capabilities. A hold stops the NEXT robot.
	heldByOperator := rollout.Spec.DesiredState == fleetv1.RolloutDesiredStatePaused
	paused := pausedOnError || heldByOperator

	// current is set once this pass has confirmed, uncached, that it is not working from a
	// stale rollout (see APIReader).
	current := false

	// ── Batch entry ────────────────────────────────────────────────────────────
	// Fill up to maxUnavailable (updaters already in the batch count against it).
	// A Paused rollout starts no new robots; in-progress updaters continue (RFC-0001 #control-plane-ota-model-update-manager).
	if !paused {
		slots := maxUnavailable(rollout.Spec.Strategy.RollingUpdateOrDefault().MaxUnavailable, total) - len(updating)
		if r.Pusher != nil && slots > 0 && len(eligible) > 0 {
			if stale, err := r.staleRollout(ctx, rollout); err != nil {
				return ctrl.Result{}, err
			} else if stale {
				return ctrl.Result{Requeue: true}, nil
			}
			current = true
		}
		sort.Slice(eligible, func(i, j int) bool { return eligible[i].Name < eligible[j].Name })
		for _, rob := range eligible {
			if slots <= 0 {
				break
			}
			entered, prev, refusal, err := r.enterBatch(ctx, rob, rollout)
			if err != nil {
				return ctrl.Result{}, err
			}
			if refusal != "" {
				// Refused on its signature: the robot fails in this rollout, and under
				// pauseOnError the next robot is not pushed an artifact already refused.
				refused[rob.Name] = refusal
				failed = append(failed, rob)
				if rollout.Spec.Strategy.RollingUpdateOrDefault().PausesOnError() {
					paused = true
					break
				}
				continue
			}
			if !entered {
				// Undeliverable model_update push: the robot did not enter the batch
				// and must NOT consume a slot; retry it on the next reconcile.
				deferred = true
				continue
			}
			// Capture the version the robot was on — the Auto rollback revert target
			// if this update later fails.
			if prev != "" {
				rollbackVersions[rob.Name] = prev
			}
			updating = append(updating, rob)
			slots--
		}
	}

	// ── Projection: grant capabilities for robots that finished successfully ────
	for _, rob := range done {
		if err := r.projectGrant(ctx, rob, rollout); err != nil {
			return ctrl.Result{}, err
		}
	}

	// ── Rollout status ─────────────────────────────────────────────────────────
	newStatus := computeRolloutStatus(rollout.Spec.ModelName, total,
		done, updating, failed, rolledBack, reverting, newer, excluded, paused, rollbackVersions,
		rollout.Status.CurrentBatch)
	// Conditions start from the stored ones, so a condition whose status did not change
	// keeps its lastTransitionTime and an unchanged pass compares equal and writes nothing
	// (RA-1).
	newStatus.Conditions = rollout.Status.DeepCopy().Conditions
	for i := range newStatus.FailedRobots {
		if reason, ok := refused[newStatus.FailedRobots[i].RobotName]; ok && newStatus.FailedRobots[i].Reason == "" {
			newStatus.FailedRobots[i].Reason = reason
		}
	}
	// A reverted robot a resume acknowledged stays acknowledged. It is classified as rolled
	// back, not excluded, so computeRolloutStatus does not carry it in excludedRobots, and
	// dropping it there would re-latch the pause on the next pass.
	if len(ackedReverts) > 0 {
		newStatus.ExcludedRobots = mergeExcluded(newStatus.ExcludedRobots, ackedReverts)
	}

	// Which hold is in force — see conditionOperatorHold. `phase: Paused` alone
	// cannot answer "will this move on its own, or is it waiting for me?" now that
	// an operator hold and the pauseOnError halt both produce it.
	if heldByOperator {
		upsertCondition(&newStatus.Conditions, conditionOperatorHold, metav1.ConditionTrue,
			"OperatorPaused", "spec.desiredState is Paused: no further robot enters a batch until it is set back to Running")
	} else {
		upsertCondition(&newStatus.Conditions, conditionOperatorHold, metav1.ConditionFalse,
			"NoOperatorHold", "spec.desiredState is Running; any Paused phase is the pauseOnError halt, exited with the rollout-resume verb")
	}

	// Announce the refusal once per reconcile rather than per robot: on a large fleet a
	// per-robot event would bury the signal it exists to give. A silent skip is what makes
	// "the rollout did nothing" indistinguishable from "there was nothing to do".
	if len(newer) > 0 && !equality.Semantic.DeepEqual(rollout.Status.RobotsIneligible, newStatus.RobotsIneligible) {
		names := make([]string, 0, len(newer))
		for _, rob := range newer {
			names = append(names, rob.Name)
		}
		sort.Strings(names)
		r.event(rollout, corev1.EventTypeWarning, "ModelDowngradeRefused", fmt.Sprintf(
			"%d robot(s) already run a newer %s than %s and were not updated: %s",
			len(newer), rollout.Spec.ModelName, rollout.Spec.NewVersion, strings.Join(names, ", ")))
	}
	// PausedAt anchors the halt for an operator and for the audit entry. Stamped on the
	// EDGE into Paused so it records when the rollout stopped, not when it was last
	// reconciled while stopped — and so it rides the material-change patch below.
	if newStatus.Phase == fleetv1.RolloutPhasePaused {
		if rollout.Status.PausedAt != nil {
			newStatus.PausedAt = rollout.Status.PausedAt
		} else {
			pausedAt := metav1.Now()
			newStatus.PausedAt = &pausedAt
		}
	}
	pauseEdge := newStatus.Phase == fleetv1.RolloutPhasePaused && rollout.Status.Phase != fleetv1.RolloutPhasePaused
	if pauseEdge && !current {
		if stale, err := r.staleRollout(ctx, rollout); err != nil {
			return ctrl.Result{}, err
		} else if stale {
			return ctrl.Result{Requeue: true}, nil
		}
	}
	if !equality.Semantic.DeepEqual(rollout.Status, newStatus) {
		orig := rollout.DeepCopy()
		rollout.Status = newStatus
		if err := r.Status().Patch(ctx, rollout, client.MergeFrom(orig)); err != nil {
			return ctrl.Result{}, fmt.Errorf("patching rollout status: %w", err)
		}
		logger.V(1).Info("model rollout progress", "phase", newStatus.Phase,
			"updated", newStatus.RobotsUpdated, "total", newStatus.RobotsTotal)
		// RFC-0001 #security-audit-logging requires MODEL_ROLLOUT_PAUSED. Sealed on the edge, so a rollout that sits
		// Paused across many reconciles seals one entry rather than one per pass.
		if pauseEdge {
			failedNames := make([]string, 0, len(newStatus.FailedRobots))
			for _, f := range newStatus.FailedRobots {
				failedNames = append(failedNames, f.RobotName)
			}
			detail := map[string]string{
				"model_name":    rollout.Spec.ModelName,
				"failed_robots": strings.Join(failedNames, ","),
			}
			if len(unackedReverts) > 0 {
				detail["rolled_back_robots"] = strings.Join(unackedReverts, ",")
			}
			r.sealModelEvent(ctx, rollout, "", audit.EventModelRolloutPaused, "pause", audit.OutcomeError, detail)
		}
	}

	// While updaters are outstanding, requeue to pick up the adapter-reported
	// Active transition (telemetry-driven). Also requeue when a robot's model_update
	// push was deferred (adapter not yet reachable) so it is retried.
	if newStatus.Phase == fleetv1.RolloutPhaseInProgress || deferred || len(reverting) > 0 {
		return ctrl.Result{RequeueAfter: 15 * time.Second}, nil
	}
	return ctrl.Result{}, nil
}

// enterBatch tries to bring a robot into the update batch (RFC-0001 #control-plane-ota-model-update-manager). When a Pusher
// is configured it PUSHES the model_update Command FIRST and only enters the robot
// (marking the model Updating, which suspends model-driven capabilities) once the
// adapter ACKNOWLEDGES — so an undeliverable update never suspends capabilities.
// A push that is unreachable/timed-out/un-acked returns entered=false (the robot
// stays Pending and is retried), NOT an error. With no Pusher (ControlStream
// disabled) it falls back to observe-only: mark Updating and await the reported
// Active. Returns (entered, err); err is only for a real control-plane failure.
// enterBatch returns (entered, previousVersion, refusal, err). previousVersion is the model
// version the robot was running at entry — captured BEFORE the model is marked
// Updating, since it is the Auto rollback revert target if this update later fails.
// refusal is non-empty only when the adapter refused the artifact on its signature: the
// failure reason the caller records for the robot.
func (r *ModelRolloutReconciler) enterBatch(ctx context.Context, rob *fleetv1.Robot, rollout *fleetv1.ModelRollout) (bool, string, string, error) {
	var prevVersion string
	if e := modelEntry(rob, rollout.Spec.ModelName); e != nil {
		prevVersion = e.RunningVersion
	}
	if r.Pusher != nil {
		// The robot was found eligible on the copy this pass listed from the cache. A push
		// cannot be taken back, so a stop that reached the robot since is read first.
		if held := heldNow(ctx, r.liveReader(), rob); held != "" {
			log.FromContext(ctx).Info("model_update not pushed: the robot is under an emergency stop",
				"robot", rob.Name, "held", held)
			return false, "", "", nil
		}
		r.Acks.forget(rollout.Namespace, rob.Name, rollout.Spec.ModelName)
		outcome, err := r.Pusher.PushModelUpdate(ctx, rollout.Namespace, rob.Name, modelUpdatePayload(rob, rollout))
		if err != nil {
			r.event(rollout, corev1.EventTypeWarning, "ModelRolloutPushDeferred",
				fmt.Sprintf("robot %s: model_update not delivered (%v); will retry", rob.Name, err))
			return false, "", "", nil
		}
		if !outcome.Acknowledged {
			if isSignatureFailure(outcome.Message) {
				r.event(rollout, corev1.EventTypeWarning, "ModelRolloutPushDeclined",
					fmt.Sprintf("robot %s: adapter refused the model's signature: %s; the robot is failed in this rollout and the model is not pushed to it again",
						rob.Name, outcome.Message))
			} else {
				r.event(rollout, corev1.EventTypeWarning, "ModelRolloutPushDeclined",
					fmt.Sprintf("robot %s: adapter did not acknowledge model_update: %s", rob.Name, outcome.Message))
			}
			// Only a decline the adapter attributes to signature verification is sealed as
			// MODEL_SIGNATURE_FAILED. RFC-0001 #fleet-adapter-protocol-fleet-adapter-compliance-checklist mandates that exact reason for that case, so
			// matching it follows the contract rather than guessing; a decline for any
			// other cause is a delivery problem, already surfaced by the event above, and
			// recording it as a signature failure would put a false rejection in the chain.
			// A signature refusal is sealed once: the caller records the robot failed, and a
			// failed robot is never pushed again by this rollout.
			if isSignatureFailure(outcome.Message) {
				r.sealModelEvent(ctx, rollout, rob.Name, audit.EventModelSignatureFailed, "verify",
					audit.OutcomeDenied, map[string]string{
						"model_name":      rollout.Spec.ModelName,
						"artifact_digest": rollout.Spec.ModelChecksum,
						"reason":          outcome.Message,
					})
				return false, "", signatureRefusalPrefix + outcome.Message, nil
			}
			return false, "", "", nil
		}
		r.Acks.ack(rollout.Namespace, rob.Name, rollout.Spec.ModelName)
		// Acknowledged means the adapter verified the artifact before installing it
		// (RFC-0001 #fleet-adapter-protocol-fleet-adapter-compliance-checklist). verified_signer is the adapter's attestation of which trust root it
		// checked against — the robot-side counterpart of the control plane's own
		// FIRMWARE_SIGNATURE_VERIFIED, and the only evidence available for a model, whose
		// bytes this process never sees.
		r.sealModelEvent(ctx, rollout, rob.Name, audit.EventModelSignatureVerified, "verify",
			audit.OutcomeAllowed, map[string]string{
				"model_name":      rollout.Spec.ModelName,
				"artifact_digest": rollout.Spec.ModelChecksum,
				"verified_signer": outcome.VerifiedSigner,
			})
	}

	// Re-read before marking. `rob` is the copy listed at the top of this reconcile, from
	// BEFORE the push — and the push above blocked on an acknowledgement that the reference
	// adapter sends AFTER its terminal install outcome. So by the time we get
	// here the robot may already have reported the install finished, and marking Updating
	// off the stale copy would overwrite that report and pin the robot mid-update for ever:
	// classifyModel would read Updating on every subsequent reconcile and the rollout would
	// never complete. Re-reading costs one Get on a path that has just done a network round
	// trip to a robot.
	//
	// Already settled for THIS target version — the install outcome beat the ack. Enter the
	// batch (so the success is attributed to this rollout and MODEL_UPDATE_SUCCEEDED is
	// sealed on the next pass) but write no status: there is nothing to suspend, and the
	// robot has already told us what it is running.
	settled, err := r.markModelUpdating(ctx, rob, rollout.Spec.ModelName, func(fresh *fleetv1.Robot) bool {
		st := classifyModel(fresh, rollout.Spec.ModelName, rollout.Spec.NewVersion)
		return st == modelDone || st == modelFailed
	})
	if err != nil {
		return false, "", "", fmt.Errorf("marking model updating on %s: %w", rob.Name, err)
	}
	if settled {
		return true, prevVersion, "", nil
	}
	r.event(rollout, corev1.EventTypeNormal, "ModelRolloutBatchStarted",
		fmt.Sprintf("robot %s entered ModelRollout batch for %s@%s", rob.Name, rollout.Spec.ModelName, rollout.Spec.NewVersion))
	// After the mark, not before: the update has begun only once the model is Updating,
	// and that status is what keeps the robot out of a later batch — so this cannot repeat.
	r.sealModelEvent(ctx, rollout, rob.Name, audit.EventModelUpdateStarted, "update",
		audit.OutcomeAllowed, map[string]string{
			"model_name":  rollout.Spec.ModelName,
			"old_version": prevVersion,
			"new_version": rollout.Spec.NewVersion,
		})
	return true, prevVersion, "", nil
}

// rollbackRobot performs an Auto rollback (§6.7) for a robot whose update failed:
// it pushes a rollback model_update (the adapter reactivates the retained
// prevVersion — no download) and, on acknowledgement, marks the model Updating
// (reverting; capabilities stay suspended until the adapter reports the previous
// model Active). Push-then-mark: an undeliverable/declined rollback returns
// (false, nil) so the robot stays failed and is retried — it never silently drops.
func (r *ModelRolloutReconciler) rollbackRobot(ctx context.Context, rob *fleetv1.Robot, rollout *fleetv1.ModelRollout, prevVersion string) (bool, error) {
	failedVersion := rollout.Spec.NewVersion
	if r.Pusher != nil {
		r.Acks.forget(rollout.Namespace, rob.Name, rollout.Spec.ModelName)
		outcome, err := r.Pusher.PushModelUpdate(ctx, rollout.Namespace, rob.Name, command.ModelUpdate{
			ModelName:  rollout.Spec.ModelName,
			OldVersion: failedVersion,
			NewVersion: prevVersion,
			Rollback:   true,
		})
		if err != nil {
			r.event(rollout, corev1.EventTypeWarning, "ModelRollbackDeferred",
				fmt.Sprintf("robot %s: rollback to %s not delivered (%v); will retry", rob.Name, prevVersion, err))
			return false, nil
		}
		if !outcome.Acknowledged {
			r.event(rollout, corev1.EventTypeWarning, "ModelRollbackDeclined",
				fmt.Sprintf("robot %s: adapter did not acknowledge rollback: %s", rob.Name, outcome.Message))
			return false, nil
		}
		r.Acks.ack(rollout.Namespace, rob.Name, rollout.Spec.ModelName)
	}

	// Re-read before marking, for the SAME reason enterBatch does — and this path needs it
	// more, because it is the path that GIVES CAPABILITIES BACK. `rob` is the copy listed at
	// the top of this reconcile, from before the push; the push blocked on an acknowledgement
	// the reference adapter sends AFTER both its terminal outcome and its ADR-0033
	// CapabilitiesSnapshot. So by the time we get here the robot has usually already reported
	// the revert landed, and marking Updating off the stale copy overwrites that report.
	//
	// Nothing repairs it afterwards. The forward path is rescued by the snapshot the adapter
	// re-sends on its next install transition; a reverted robot has no next transition — the
	// revert WAS the last one — so the overwrite is permanent. Reproduced on a live
	// three-robot cluster: every robot pinned at the previous version with status Updating,
	// the model-driven capability suspended and the rollout stuck InProgress, while all
	// three were in fact running that version and had reported it.
	//
	// The revert already landed and the robot is back on the retained version. Report it
	// rolled back and write no status: there is nothing left to suspend, and marking
	// Updating here would take the capability away again after the robot restored it.
	//
	// A revert the robot has already reported FAILED is settled too, and must not be marked
	// over either: the next pass counts it failed (revertFailed). The entry was Failed before
	// this push as well, from the update that failed, so only an entry that changed since the
	// pre-push copy is the robot's report of this revert.
	var reportedFailed bool
	settled, err := r.markModelUpdating(ctx, rob, rollout.Spec.ModelName, func(fresh *fleetv1.Robot) bool {
		if modelActiveAt(fresh, rollout.Spec.ModelName, prevVersion) {
			return true
		}
		reportedFailed = revertReportedFailed(rob, fresh, rollout.Spec.ModelName)
		return reportedFailed
	})
	if err != nil {
		return false, fmt.Errorf("marking model reverting on %s: %w", rob.Name, err)
	}
	if settled && reportedFailed {
		r.event(rollout, corev1.EventTypeWarning, "ModelRollbackFailed",
			fmt.Sprintf("robot %s: model %s revert to %s was reported failed", rob.Name, rollout.Spec.ModelName, prevVersion))
		return true, nil
	}
	if settled {
		r.event(rollout, corev1.EventTypeWarning, "ModelRolledBack",
			fmt.Sprintf("robot %s: model %s update to %s failed — auto-reverted to %s (§6.7); fleet now version-fragmented",
				rob.Name, rollout.Spec.ModelName, failedVersion, prevVersion))
		return true, nil
	}
	r.event(rollout, corev1.EventTypeWarning, "ModelRolledBack",
		fmt.Sprintf("robot %s: model %s update to %s failed — auto-reverting to %s (§6.7); fleet now version-fragmented",
			rob.Name, rollout.Spec.ModelName, failedVersion, prevVersion))
	return true, nil
}

// markModelUpdating re-reads the robot after a push and marks the model Updating on it,
// unless settled reports that the robot has already said how the push ended; it returns
// true, having written nothing, in that case.
//
// The re-read covers a report that arrives before the acknowledgement. A report can also
// arrive after the acknowledgement and before the mark is written, and a plain merge patch
// computed from the re-read copy would then replace installedModels with that copy and
// erase the report; nothing reports again, so the robot would read Updating for ever. So
// the mark carries the re-read's resourceVersion: a report written in between makes the
// patch conflict, and the robot is read and judged again.
func (r *ModelRolloutReconciler) markModelUpdating(ctx context.Context, rob *fleetv1.Robot, modelName string, settled func(*fleetv1.Robot) bool) (bool, error) {
	var reader client.Reader = r.Client
	if r.APIReader != nil {
		reader = r.APIReader
	}
	already := false
	err := retry.RetryOnConflict(retry.DefaultRetry, func() error {
		fresh := &fleetv1.Robot{}
		if err := reader.Get(ctx, client.ObjectKeyFromObject(rob), fresh); err != nil {
			return fmt.Errorf("re-reading %s after push: %w", rob.Name, err)
		}
		if settled(fresh) {
			already = true
			return nil
		}
		orig := fresh.DeepCopy()
		upsertModelStatus(fresh, modelName, fleetv1.ModelStatusUpdating)
		return r.Status().Patch(ctx, fresh, client.MergeFromWithOptions(orig, client.MergeFromWithOptimisticLock{}))
	})
	return already, err
}

// revertReportedFailed reports whether fresh carries a Failed entry for modelName that
// differs from the entry in before, the copy read before the rollback push: a failure the
// robot reported for the revert, not the failure the revert answers.
func revertReportedFailed(before, fresh *fleetv1.Robot, modelName string) bool {
	now := modelEntry(fresh, modelName)
	if now == nil || now.Status != fleetv1.ModelStatusFailed {
		return false
	}
	was := modelEntry(before, modelName)
	return was == nil || was.Status != now.Status || was.RunningVersion != now.RunningVersion ||
		was.FailureReason != now.FailureReason
}

// copyStringMap returns a shallow copy so the persisted status map is not mutated
// in place while the reconcile accumulates rollback bookkeeping.
func copyStringMap(m map[string]string) map[string]string {
	out := make(map[string]string, len(m))
	for k, v := range m {
		out[k] = v
	}
	return out
}

// modelUpdatePayload builds the model_update Command payload from the rollout spec
// and the robot's currently-installed version. modelChecksum and modelSignatureRef
// travel to the adapter so the robot re-verifies the downloaded bytes and the
// detached signature against the checksum before install (RFC-0001 #fleet-adapter-protocol-fleet-adapter-compliance-checklist, ADR-0020).
func modelUpdatePayload(rob *fleetv1.Robot, rollout *fleetv1.ModelRollout) command.ModelUpdate {
	var oldVersion string
	if e := modelEntry(rob, rollout.Spec.ModelName); e != nil {
		oldVersion = e.RunningVersion
	}
	return command.ModelUpdate{
		ModelName:         rollout.Spec.ModelName,
		OldVersion:        oldVersion,
		NewVersion:        rollout.Spec.NewVersion,
		ModelURI:          rollout.Spec.ModelURI,
		ModelChecksum:     rollout.Spec.ModelChecksum,
		ModelSignatureRef: rollout.Spec.ModelSignatureRef,
	}
}

// projectGrant upserts the model's granted capabilities into
// status.modelGrantedCapabilities[] (grants − revokes, RFC-0001 #control-plane-ota-model-update-manager). Idempotent.
func (r *ModelRolloutReconciler) projectGrant(ctx context.Context, rob *fleetv1.Robot, rollout *fleetv1.ModelRollout) error {
	grants := subtractCaps(rollout.Spec.GrantsCapabilities, rollout.Spec.RevokesCapabilities)
	if modelGrantMatches(rob, rollout.Spec.ModelName, rollout.Name, grants) {
		return nil // already projected; no-op write avoided
	}
	orig := rob.DeepCopy()
	upsertModelGrant(rob, rollout.Spec.ModelName, rollout.Name, grants)
	if err := r.Status().Patch(ctx, rob, client.MergeFrom(orig)); err != nil {
		return fmt.Errorf("projecting model grant on %s: %w", rob.Name, err)
	}
	r.event(rollout, corev1.EventTypeNormal, "CapabilitiesRestored",
		fmt.Sprintf("robot %s: model %s@%s active; granted %v", rob.Name, rollout.Spec.ModelName, rollout.Spec.NewVersion, grants))
	return nil
}

func (r *ModelRolloutReconciler) event(obj client.Object, eventType, reason, msg string) {
	if r.Recorder != nil {
		r.Recorder.Event(obj, eventType, reason, msg)
	}
}

// ── Pure helpers ──────────────────────────────────────────────────────────────

// classifyModel reports a robot's state for the rolled-out model.
func classifyModel(rob *fleetv1.Robot, modelName, newVersion string) modelState {
	e := modelEntry(rob, modelName)
	if e == nil {
		return modelPending
	}
	switch e.Status {
	case fleetv1.ModelStatusActive:
		if e.RunningVersion == newVersion {
			return modelDone
		}
		// "Not equal" is not "older". Before this check, a rollout naming an older version
		// silently downgraded every robot already past it — the controller compared for
		// equality only, so a newer robot looked exactly like a stale one.
		//
		// Refuse only on PROOF: both versions must parse and the installed one must be
		// strictly greater. An unparseable RunningVersion (it is reported by the adapter,
		// so it is whatever the vendor sends) is NOT evidence of a downgrade, and treating
		// it as one would silently empty the batch — the failure mode where a rollout that
		// did nothing reads exactly like a rollout with nothing to do.
		if newer, ok := versionIsNewer(e.RunningVersion, newVersion); ok && newer {
			return modelNewer
		}
		return modelPending // active but on an older/unorderable version → still needs updating
	case fleetv1.ModelStatusUpdating:
		return modelUpdating
	case fleetv1.ModelStatusFailed:
		return modelFailed
	default:
		return modelPending
	}
}

// sealModelEvent appends one RFC-0001 #safety-required-events entry about a model rollout. Best-effort and
// nil-safe: the push, the mark and the classification have all already happened, and an
// audit sink must never be able to hold up a model update or a rollback.
// applyResume consumes a pending swarmada.io/rollout-resume annotation (ADR-0041).
//
// It moves the robots this rollout currently records as failed, and the robots it has reverted,
// into status.excludedRobots and clears status.pausedAt. `paused` is derived per reconcile from
// the failed robots and the reverted robots not yet excluded, not latched, so it cannot
// immediately re-latch off the same robots, and the rollout can reach a terminal phase and
// become deletable.
//
// Returns done=true when it wrote status; the caller ends the reconcile and the write requeues.
// Idempotent: a request already applied writes nothing (RA-1). A rollout that is NOT paused
// still records the request as processed, so a stale annotation cannot silently resume a
// FUTURE pause.
func (r *ModelRolloutReconciler) applyResume(ctx context.Context, rollout *fleetv1.ModelRollout) (bool, error) {
	req, pending := pendingResume(rollout.Annotations)
	if !pending {
		return false, nil
	}

	resumed := false
	if rollout.Status.Phase == fleetv1.RolloutPhasePaused {
		newlyExcluded := make([]string, 0, len(rollout.Status.FailedRobots)+len(rollout.Status.RolledBackRobots))
		for _, f := range rollout.Status.FailedRobots {
			newlyExcluded = append(newlyExcluded, f.RobotName)
		}
		// A reverted robot halts the rollout as a failed one does, and is acknowledged the
		// same way; it stays rolled back, so this changes only what holds the rollout.
		excluded := make(map[string]bool, len(rollout.Status.ExcludedRobots))
		for _, n := range rollout.Status.ExcludedRobots {
			excluded[n] = true
		}
		for _, n := range rollout.Status.RolledBackRobots {
			if !excluded[n] {
				newlyExcluded = append(newlyExcluded, n)
			}
		}

		base := rollout.DeepCopy()
		rollout.Status.ExcludedRobots = mergeExcluded(rollout.Status.ExcludedRobots, newlyExcluded)
		// The failure list is what re-derives `paused`; leaving it would re-pause on the very
		// next reconcile and make the resume look like it did nothing — the same trap
		// policy-reset avoids by zeroing ConsecutiveRejections.
		rollout.Status.FailedRobots = nil
		rollout.Status.PausedAt = nil
		// Written and sealed only when it changes status. A pass that applied this request
		// but could not record it as processed finds the status already resumed on its retry:
		// it writes nothing, seals nothing, and goes on to the marker (RA-1).
		if !equality.Semantic.DeepEqual(base.Status, rollout.Status) {
			if err := r.Status().Patch(ctx, rollout, client.MergeFrom(base)); err != nil {
				return false, fmt.Errorf("resuming model rollout: %w", err)
			}
			r.sealModelEventAs(ctx, rollout,
				estopActor(rollout.Annotations, "modelrollout-controller"),
				"", audit.EventRolloutResumed, "resume", audit.OutcomeAllowed,
				map[string]string{
					"reason":          req,
					"excluded_robots": strings.Join(newlyExcluded, ","),
				})
			resumed = true
		}
	}

	if err := markResumeProcessed(ctx, r.Client, rollout, req); err != nil {
		return false, err
	}
	return resumed, nil
}

func (r *ModelRolloutReconciler) sealModelEvent(ctx context.Context, rollout *fleetv1.ModelRollout,
	robotName, eventType, action string, outcome audit.Outcome, detail map[string]string) {
	r.sealModelEventAs(ctx, rollout,
		audit.Actor{Type: audit.ActorServiceAccount, Identity: "modelrollout-controller"},
		robotName, eventType, action, outcome, detail)
}

// sealModelEventAs is sealModelEvent with an explicit actor — see the FirmwareRollout twin
// for why only ROLLOUT_RESUMED uses it (ADR-0046).
func (r *ModelRolloutReconciler) sealModelEventAs(ctx context.Context, rollout *fleetv1.ModelRollout,
	actor audit.Actor, robotName, eventType, action string, outcome audit.Outcome, detail map[string]string) {
	if r.Audit == nil {
		return
	}
	if detail == nil {
		detail = map[string]string{}
	}
	// Rollout-scope events (pause, resume) concern the whole rollout, not one robot;
	// an empty "robot" key would claim a subject that does not exist.
	if robotName != "" {
		detail["robot"] = robotName
	}
	if _, err := r.Audit.Record(audit.Entry{
		EventType: eventType,
		Namespace: rollout.Namespace,
		Actor:     actor,
		Resource:  audit.Resource{Kind: "ModelRollout", Namespace: rollout.Namespace, Name: rollout.Name},
		Action:    action,
		Outcome:   outcome,
		Detail:    detail,
	}); err != nil {
		log.FromContext(ctx).Error(err, "recording audit entry", "event", eventType, "rollout", rollout.Name)
	}
}

// isSignatureFailure reports whether an adapter's decline names signature verification as
// the cause. RFC-0001 #fleet-adapter-protocol-fleet-adapter-compliance-checklist requires exactly this reason for a fail-closed signature refusal
// ("SignatureVerificationFailed"), so matching it reads the contract rather than guessing;
// the check is case-insensitive and substring-based because the reason is carried in a
// free-text message field alongside whatever context the adapter adds.
func isSignatureFailure(message string) bool {
	return strings.Contains(strings.ToLower(message), "signature")
}

// staleRollout reports whether the cached rollout this pass read is older than the stored
// one. A stale pass is abandoned and requeued: the newer rollout's own event follows.
func (r *ModelRolloutReconciler) staleRollout(ctx context.Context, rollout *fleetv1.ModelRollout) (bool, error) {
	var reader client.Reader = r.Client
	if r.APIReader != nil {
		reader = r.APIReader
	}
	stored := &fleetv1.ModelRollout{}
	if err := reader.Get(ctx, client.ObjectKeyFromObject(rollout), stored); err != nil {
		return false, fmt.Errorf("re-reading rollout: %w", err)
	}
	return stored.ResourceVersion != rollout.ResourceVersion, nil
}

// signatureRefusalPrefix begins the status.failedRobots reason of a robot whose adapter
// refused the rollout's artifact on its signature. It is how a later reconcile tells that
// failure, which leaves nothing on the Robot, from one the robot reported itself.
const signatureRefusalPrefix = "adapter refused the model's signature: "

// signatureRefusals returns the robots recorded failed on a signature refusal, with the
// recorded reason.
func signatureRefusals(failed []fleetv1.RolloutRobotResult) map[string]string {
	out := map[string]string{}
	for _, f := range failed {
		if strings.HasPrefix(f.Reason, signatureRefusalPrefix) {
			out[f.RobotName] = f.Reason
		}
	}
	return out
}

// wasAlreadyFailed reports whether a robot is already recorded in the rollout's failed set.
// The failure classification persists across reconciles, so this is what turns it into an
// edge — without it the chain would gain one MODEL_UPDATE_FAILED per reconcile per robot.
// On the firmware path it does more: it is what carries the failure across the pass on which
// the robot leaves status.currentBatch.
func wasAlreadyFailed(failed []fleetv1.RolloutRobotResult, robotName string) bool {
	return failedResultFor(failed, robotName) != nil
}

// failedResultFor returns a robot's recorded failure result, or nil when it has none.
func failedResultFor(failed []fleetv1.RolloutRobotResult, robotName string) *fleetv1.RolloutRobotResult {
	for i := range failed {
		if failed[i].RobotName == robotName {
			return &failed[i]
		}
	}
	return nil
}

// modelFailureReason pulls the adapter's reported reason for a failed model, falling back
// to a plain statement of the fact. An empty reason is recorded as such rather than left
// blank: "the adapter reported no reason" is itself worth knowing in a review.
func modelFailureReason(rob *fleetv1.Robot, modelName string) string {
	if e := modelEntry(rob, modelName); e != nil && e.FailureReason != "" {
		return e.FailureReason
	}
	return "adapter reported the model Failed with no reason"
}

// versionIsNewer reports whether `have` is strictly greater than `want`, and whether the
// comparison could be made at all. Both must be plain major.minor.patch — the same shape
// ModelRollout.spec.newVersion is constrained to at admission, and the same exclusion of
// prerelease/build metadata the contract-version parser makes (RFC-0001 §9.2.2): ordering
// those would require this controller to define their precedence, and it does not.
//
// ok=false means "cannot be ordered", which callers must treat as "unknown", never as
// "not newer" — the distinction between a negative answer and no answer is the whole point.
func versionIsNewer(have, want string) (newer, ok bool) {
	h, hok := parseSemver(have)
	w, wok := parseSemver(want)
	if !hok || !wok {
		return false, false
	}
	for i := range h {
		if h[i] != w[i] {
			return h[i] > w[i], true
		}
	}
	return false, true // equal
}

func parseSemver(v string) ([3]int, bool) {
	var out [3]int
	parts := strings.Split(v, ".")
	if len(parts) != 3 {
		return out, false
	}
	for i, p := range parts {
		if p == "" {
			return out, false
		}
		n, err := strconv.Atoi(p)
		if err != nil || n < 0 {
			return out, false
		}
		out[i] = n
	}
	return out, true
}

func modelEntry(rob *fleetv1.Robot, modelName string) *fleetv1.InstalledModelStatusEntry {
	for i := range rob.Status.InstalledModels {
		if rob.Status.InstalledModels[i].Name == modelName {
			return &rob.Status.InstalledModels[i]
		}
	}
	return nil
}

// eligibleForModelUpdate checks the model-update-manager safety constraints before batch
// entry; a robot under an emergency stop, or Resuming, is held back (heldFromUpdate).
func eligibleForModelUpdate(rob *fleetv1.Robot, rollout *fleetv1.ModelRollout) bool {
	if heldFromUpdate(rob) {
		return false
	}
	sc := rollout.Spec.SafetyConstraints
	if sc.RequiresIdleState() && rob.Status.Phase != fleetv1.RobotPhaseIdle {
		return false
	}
	// Battery must be known and at/above the floor — an unknown battery is not a
	// safe basis for starting an update.
	if rob.Status.BatteryPercent == nil || *rob.Status.BatteryPercent < sc.MinBatteryPct {
		return false
	}
	for _, reqType := range rollout.Spec.RequiredHardware {
		if !hasHealthyHardwareType(rob, reqType) {
			return false
		}
	}
	return true
}

// hasHealthyHardwareType reports whether the robot has at least one hardware
// component of the given type reporting Healthy.
func hasHealthyHardwareType(rob *fleetv1.Robot, t fleetv1.HardwareComponentType) bool {
	statusByName := make(map[string]fleetv1.HardwareStatus, len(rob.Status.Hardware))
	for _, h := range rob.Status.Hardware {
		statusByName[h.Name] = h.Status
	}
	for i := range rob.Spec.Hardware {
		hw := &rob.Spec.Hardware[i]
		if hw.Type == t && statusByName[hw.Name] == fleetv1.HardwareHealthy {
			return true
		}
	}
	return false
}

func upsertModelStatus(rob *fleetv1.Robot, modelName string, status fleetv1.ModelStatus) {
	for i := range rob.Status.InstalledModels {
		if rob.Status.InstalledModels[i].Name == modelName {
			rob.Status.InstalledModels[i].Status = status
			return
		}
	}
	rob.Status.InstalledModels = append(rob.Status.InstalledModels,
		fleetv1.InstalledModelStatusEntry{Name: modelName, Status: status})
}

func upsertModelGrant(rob *fleetv1.Robot, modelName, grantedBy string, caps []string) {
	for i := range rob.Status.ModelGrantedCapabilities {
		if rob.Status.ModelGrantedCapabilities[i].ModelName == modelName {
			rob.Status.ModelGrantedCapabilities[i].GrantedBy = grantedBy
			rob.Status.ModelGrantedCapabilities[i].Capabilities = caps
			return
		}
	}
	rob.Status.ModelGrantedCapabilities = append(rob.Status.ModelGrantedCapabilities,
		fleetv1.ModelGrantedCapabilityEntry{ModelName: modelName, GrantedBy: grantedBy, Capabilities: caps})
}

func modelGrantMatches(rob *fleetv1.Robot, modelName, grantedBy string, caps []string) bool {
	for i := range rob.Status.ModelGrantedCapabilities {
		e := &rob.Status.ModelGrantedCapabilities[i]
		if e.ModelName == modelName {
			return e.GrantedBy == grantedBy && equalStringSets(e.Capabilities, caps)
		}
	}
	return false
}

// subtractCaps returns grants with any name in revokes removed, sorted.
func subtractCaps(grants, revokes []string) []string {
	rev := make(map[string]bool, len(revokes))
	for _, r := range revokes {
		rev[r] = true
	}
	out := make([]string, 0, len(grants))
	for _, g := range grants {
		if !rev[g] {
			out = append(out, g)
		}
	}
	sort.Strings(out)
	return out
}

func equalStringSets(a, b []string) bool {
	if len(a) != len(b) {
		return false
	}
	as := append([]string(nil), a...)
	bs := append([]string(nil), b...)
	sort.Strings(as)
	sort.Strings(bs)
	for i := range as {
		if as[i] != bs[i] {
			return false
		}
	}
	return true
}

// maxUnavailable resolves the strategy value ("10%" or "5") to an absolute count,
// bounded below by 1.
func maxUnavailable(spec string, total int) int {
	if spec == "" {
		spec = "10%"
	}
	if strings.HasSuffix(spec, "%") {
		pct, err := strconv.Atoi(strings.TrimSuffix(spec, "%"))
		if err != nil || pct <= 0 {
			return 1
		}
		n := total * pct / 100
		if n < 1 {
			return 1
		}
		return n
	}
	n, err := strconv.Atoi(spec)
	if err != nil || n < 1 {
		return 1
	}
	return n
}

func computeRolloutStatus(modelName string, total int, done, updating, failed, rolledBack, reverting, newer, excluded []*fleetv1.Robot, paused bool, rollbackVersions map[string]string, prior []fleetv1.RolloutBatchRobot) fleetv1.ModelRolloutStatus {
	batch := buildRolloutBatch(updating, prior, modelInitialPhase, func(*fleetv1.Robot) string { return "" }, true)

	failedResults := make([]fleetv1.RolloutRobotResult, 0, len(failed))
	for _, r := range failed {
		reason := ""
		if e := modelEntry(r, modelName); e != nil {
			reason = e.FailureReason
		}
		failedResults = append(failedResults, fleetv1.RolloutRobotResult{RobotName: r.Name, Namespace: r.Namespace, Reason: reason})
	}
	sort.Slice(failedResults, func(i, j int) bool { return failedResults[i].RobotName < failedResults[j].RobotName })

	// Every robot this rollout has pushed a rollback to, settled or not. This list is what
	// seeds the exclusion set on the next reconcile, so a robot still reverting MUST appear
	// in it — dropping it would push the failed model onto the robot a second time.
	// status.robotsRolledBack, below, counts only the reverts actually observed to land.
	rolledBackNames := make([]string, 0, len(rolledBack)+len(reverting))
	for _, r := range rolledBack {
		rolledBackNames = append(rolledBackNames, r.Name)
	}
	for _, r := range reverting {
		rolledBackNames = append(rolledBackNames, r.Name)
	}
	sort.Strings(rolledBackNames)

	// Persist revert targets only for robots that could still need one — those updating now,
	// currently failed, or reverting. A reverting robot needs its target most of all: it is
	// the version the controller compares the robot's next report against to decide the
	// revert has landed. done/settled/pending robots need none, keeping the map bounded.
	keep := make(map[string]bool, len(updating)+len(failed)+len(reverting))
	for _, r := range updating {
		keep[r.Name] = true
	}
	for _, r := range failed {
		keep[r.Name] = true
	}
	for _, r := range reverting {
		keep[r.Name] = true
	}
	prunedVersions := map[string]string{}
	for name, ver := range rollbackVersions {
		if keep[name] {
			prunedVersions[name] = ver
		}
	}
	if len(prunedVersions) == 0 {
		prunedVersions = nil
	}

	st := fleetv1.ModelRolloutStatus{
		//nolint:gosec // small fleet counts
		RobotsTotal: int32(total),
		//nolint:gosec // small fleet counts
		RobotsUpdated: int32(len(done)),
		//nolint:gosec // small fleet counts
		RobotsFailed: int32(len(failed)),
		// Reverts OBSERVED to land. A robot whose rollback was acknowledged but not yet
		// reported back is not counted here: it has not returned to service on the previous
		// version, and its granted capabilities are still suspended. It is counted in
		// robotsPending and in capabilitiesSuspendedOn instead, which is what stops a
		// rollout from reading as settled over robots that have lost their capabilities.
		//nolint:gosec // small fleet counts
		RobotsRolledBack: int32(len(rolledBack)),
		//nolint:gosec // small fleet counts
		// A downgrade-refused robot is not pending: it will never enter a batch, and
		// counting it as pending would leave the rollout reporting work outstanding that
		// it has already decided not to do — a progress bar that can never reach the end.
		RobotsPending: int32(total - len(done) - len(failed) - len(rolledBack) - len(newer)),
		// Robots refused as a downgrade only. A robot lacking a required hardware type is
		// never dispatched either, but it is not counted here: it stays in robotsPending
		// (RequiredHardware, api/v1/rollout_types.go). Counting the downgrade refusals is
		// what stops "did nothing" from being indistinguishable from "had nothing to do".
		//nolint:gosec // small fleet counts
		RobotsIneligible: int32(len(newer)),
		// Reverting robots are included: their model entry is Updating while the adapter
		// reactivates the retained version, so the capabilities that model grants are
		// suspended on exactly the same terms as a forward update's.
		//nolint:gosec // small fleet counts
		CapabilitiesSuspendedOn: int32(len(updating) + len(reverting)),
		CurrentBatch:            batch,
		FailedRobots:            failedResults,
		RollbackVersions:        prunedVersions,
	}
	if len(rolledBackNames) > 0 {
		st.RolledBackRobots = rolledBackNames
	}
	if len(excluded) > 0 {
		excludedNames := make([]string, 0, len(excluded))
		for _, r := range excluded {
			excludedNames = append(excludedNames, r.Name)
		}
		sort.Strings(excludedNames)
		st.ExcludedRobots = excludedNames
	}
	settled := len(done) + len(rolledBack) + len(newer) + len(excluded)
	switch {
	case settled == total && total > 0:
		// Every robot is on newVersion, was reverted AND observed back on the previous
		// version, was refused as a downgrade, or was excluded by an operator resume.
		// Succeeded, but a non-zero RobotsRolledBack / ExcludedRobots surfaces the version
		// fragmentation (§6.7, ADR-0041). Counting excluded robots as settled is what lets a
		// resumed rollout reach a terminal phase at all — without it the record could never
		// be deleted, which is the other half of the wedge resume fixes. A robot still
		// reverting is deliberately NOT settled: its capabilities are suspended and the
		// rollout still owns the state that restores them.
		st.Phase = fleetv1.RolloutPhaseSucceeded
	// Paused is checked before Failed and is not terminal: pauseOnError halted the rollout so
	// an operator could decide, and `swarmctl rollout resume` is the exit (ADR-0041).
	case paused:
		st.Phase = fleetv1.RolloutPhasePaused
	// Terminal failure. Every robot has settled or failed, and at least one failed without
	// being reverted, repaired or excluded — so there is no further work this rollout can do.
	// Before this branch existed such a rollout sat InProgress for ever and could never be
	// deleted, which on this kind means model-granted capabilities left suspended with no
	// owner to restore them. Reachable only with pauseOnError: false; derived per reconcile
	// rather than latched, like `paused`.
	case total > 0 && len(failed) > 0 && settled+len(failed) == total:
		st.Phase = fleetv1.RolloutPhaseFailed
	case len(updating) > 0 || len(done) > 0 || len(failed) > 0 || len(rolledBack) > 0 || len(reverting) > 0:
		st.Phase = fleetv1.RolloutPhaseInProgress
	default:
		st.Phase = fleetv1.RolloutPhasePending
	}
	return st
}

// modelActiveAt reports whether a robot is running the named model, Active, at version want.
// It is the evidence a rollback has actually landed — as opposed to the adapter having
// acknowledged that it would.
func modelActiveAt(rob *fleetv1.Robot, modelName, want string) bool {
	e := modelEntry(rob, modelName)
	return e != nil && e.Status == fleetv1.ModelStatusActive && e.RunningVersion == want
}

// SetupWithManager registers the ModelRollout controller and re-reconciles a
// namespace's rollouts when any Robot in it changes (its model progress may have
// advanced).
func (r *ModelRolloutReconciler) SetupWithManager(mgr ctrl.Manager) error {
	robotToRollouts := handler.EnqueueRequestsFromMapFunc(func(ctx context.Context, obj client.Object) []reconcile.Request {
		var rollouts fleetv1.ModelRolloutList
		if err := r.List(ctx, &rollouts, client.InNamespace(obj.GetNamespace())); err != nil {
			return nil
		}
		reqs := make([]reconcile.Request, 0, len(rollouts.Items))
		for i := range rollouts.Items {
			reqs = append(reqs, reconcile.Request{NamespacedName: types.NamespacedName{
				Name: rollouts.Items[i].Name, Namespace: rollouts.Items[i].Namespace,
			}})
		}
		return reqs
	})

	inNamespace := handler.EnqueueRequestsFromMapFunc(func(ctx context.Context, obj client.Object) []reconcile.Request {
		return rolloutsOfNamespace(ctx, r, &fleetv1.ModelRolloutList{}, obj)
	})

	return ctrl.NewControllerManagedBy(mgr).
		For(&fleetv1.ModelRollout{}).
		Watches(&fleetv1.Robot{}, robotToRollouts).
		Watches(&fleetv1.FleetZone{}, inNamespace).
		Watches(&fleetv1.SwarmadaConfig{}, inNamespace).
		Complete(r)
}
````
