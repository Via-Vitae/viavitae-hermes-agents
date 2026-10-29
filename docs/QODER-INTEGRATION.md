# Via-Vitae: Qoder integration decision and implementation guide

Date: 29 October 2026. Status: proposed architecture, not a deployed integration or compliance approval.

## 1. Decision

Start with a supervised developer CLI pilot over approved source code and synthetic fixtures. Do not install every Qoder product. Do not embed a remote runtime in Hermes or send pastoral records to a vendor before resolving the existing data-boundary requirements.

This decision follows the current code: Hermes has a no-egress design, no generic MCP discovery, inert drafts, and mandatory human review. The API requires EU-resident integrations and an architectural decision plus processing agreement for an outbound integration outside the EEA. The proposed pilot is separate from the runtime serving customers.

| Component | Recommendation now | Reason and later trigger |
| --- | --- | --- |
| CLI | Candidate for supervised developer pilot | Useful for source review and bounded changes; no production credentials or customer records. |
| Agent SDK | Defer runtime dependency | Adopt only for a defined backend agent task with an approved data flow and isolated worker. |
| Cloud Agents | Defer | Consider for asynchronous work only after vendor, region, retention, identity and cost controls are verified. |
| Mobile & Web | Optional operator interface later | Does not replace authentication, authorization or backend enforcement in Via-Vitae. |
| QoderWake | Defer unattended work | A manual, repeatable, low-risk workflow must pass acceptance tests first. |
| Organization OpenAPI | Optional administration integration | Use for a concrete membership or usage-reporting need, separately from task execution. |
| Enterprise workflow guidance | Adopt delivery discipline | Requirements, design, implementation and independent verification can improve the existing process without adding a vendor runtime. |
| Enterprise AI platform | Defer a new portal | Build only if several approved internal use cases require a common entry point. |

The CLI is a developer-facing coding tool. The Agent SDK starts a local `qodercli` process, but that process calls a model service: local process execution does not imply local-only data processing. [CLI overview](https://docs.qoder.com/cli/overview), [SDK architecture](https://docs.qoder.com/cli/sdk/how-it-works).

Cloud Agents provides managed execution. Its documentation describes agents, environments, sessions and streamed events. That does not establish Via-Vitae's contractual data residency or deletion guarantees. Obtain those separately for the exact purchased service. [Cloud Agents overview](https://docs.qoder.com/cloud-agents/overview).

Qoder's organization OpenAPI covers organization administration and usage. Its organization API key is a different credential purpose from an agent session token; do not share either with a browser. [OpenAPI overview](https://docs.qoder.com/account/teams/openapi).

## 2. Step one — define a single useful task

1. Name the task: for example, “review a proposed Python change and produce a patch with tests.” This describes an observable outcome.
2. Name the owner: the person responsible for accepting the output. A model cannot accept its own compliance judgment.
3. List inputs: approved source files, a synthetic example and acceptance criteria. Exclude database exports, customer messages, tokens and private keys.
4. List allowed outputs: a local patch, test results and a review note. Keep sending messages, publishing content, merging and deploying outside this first task.
5. Define success: a regression test fails before the patch, passes afterward, existing gates pass, and a human reviews the diff.

Check: someone unfamiliar with the task can tell whether it succeeded without relying on the agent's summary.

## 3. Step two — map the data before installing a runtime

1. Draw where input originates, where prompts travel, where tools execute and where outputs are stored.
2. Include indirect copies: session history, telemetry, crash reports, backups, knowledge bases, screenshots and remote-control views.
3. Identify controller/processor roles and the exact vendor entity. Ask for the processing agreement, subprocessor list, locations, access arrangements, retention, deletion and incident terms.
4. Have the privacy owner assess the actual purpose and data categories. Religious or health information can require additional conditions; a checkbox labelled “consent” is not evidence that those conditions are met.
5. Record the decision and unresolved questions. Unknown region or retention means the personal-data pilot remains blocked.

Check: every arrow has an owner, purpose, permitted data and deletion rule. The EDPB explains that special categories require additional conditions beyond identifying a general legal basis. [EDPB legal basis guidance](https://www.edpb.europa.eu/topics/key-gdpr-concepts/legal-basis_en).

## 4. Step three — prepare a developer pilot

1. Use a dedicated development account and a disposable checkout. Keep production secrets and customer files out of its environment, home directory and mounted volumes.
2. Review the exact CLI version, distribution source and license before installation. Record the selected version; do not use an unreviewed install script as a compliance control.
3. Start with the documented default permission mode. Avoid permission-bypass modes. Confirm the effective settings, including inherited user and managed settings.
4. Review installed hooks, plugins and MCP connections. A harmless-looking tool name does not make its implementation safe.
5. Use a test repository first. Check that attempts to access a canary secret file, write outside the checkout or contact an unapproved host are blocked by operating-system/network policy.
6. Let the agent propose a patch. Run the repository's normal tests independently and inspect all changed files.

The documented command `qoder --permission-mode default` requests default permission behavior; it is not a network sandbox. Qoder's tool permissions and hooks influence tool execution, so validate their effective behavior. Model-service traffic requires separate data-flow review. [CLI permissions](https://docs.qoder.com/cli/permissions).

Check: retain the version, effective policy, denied-action results, approved diff and test output. No Qoder installation or authenticated session was performed in this assessment.

## 5. Step four — choose one execution route if a product requirement emerges

For a future SDK integration, use this proposed boundary:

```text
User interface → Via-Vitae authentication → tenant authorization → job queue
             → isolated worker → approved SDK/runtime → reviewed result
                            ↘ separate audit store
```

1. Authenticate the caller on the server. Verify token signature, issuer, audience, expiry and permitted tenant membership.
2. Create a job with a server-assigned tenant and purpose. Never trust tenant identity supplied in a JSON body.
3. Allocate a separate workspace and restricted process identity. Do not inherit the web server's secret-filled environment.
4. Supply only the tools needed for this task. Permission callbacks must reject unrecognized actions and missing approval.
5. Bound runtime, output size, concurrency and cost. Cancellation must stop the underlying process, not merely hide progress in the UI.
6. Treat prompts, retrieved documents and tool outputs as untrusted data. Test instructions embedded in those inputs that request credential access or policy changes.
7. Return a draft with its provenance. Bind any later approval to the exact content version, tenant and authenticated reviewer.
8. Clean up workspace and session state according to the approved retention design.

The official SDK uses typed messages over a local process transport. Prefer its supported interface to custom JSONL parsing. [SDK architecture](https://docs.qoder.com/cli/sdk/how-it-works). Permission configuration is documented separately; the application still owns authentication and authorization. [SDK permissions](https://docs.qoder.com/cli/sdk/permissions).

For a future Cloud Agents route, replace the local worker runtime with an approved managed environment. First verify service-account identity, token handling, region and deletion. Then test session creation, streaming interruption, retries, cancellation and cleanup with synthetic records. A retry must not create a second external effect after a timeout. Do not enable both runtime routes merely for completeness.

Check: demonstrate cross-tenant denial, prompt-injection resistance, bounded costs, cancellation and cleanup. Hermes's current exclusion policy must be explicitly revised through its governance process before any such runtime is introduced there.

## 6. Step five — evaluate QoderWake with a manual workflow

QoderWake organizes ongoing work around Wakers, groups and resources. Its documentation recommends validating work before automating it. [QoderWake overview](https://docs.qoder.com/qoderwake/overview).

1. Begin with a proposed “Source Review Assistant” role. Give it only approved source material and a report output.
2. Bind a dedicated nonproduction workspace. Do not give the role access to the personal-data estate.
3. Assign the minimum resources. Treat connectors as access grants; inspect what each connector can read and change.
4. Run a manual review and inspect the actual artifact. Test out-of-scope requests and failure behavior.
5. If multiple roles are necessary, define who edits, who verifies and who approves. Make shared-file ownership explicit.
6. Use a staged workflow only after each step has a clear input, output and failure path.
7. Add a scheduled/event trigger only after replay handling, quotas, alerts and a kill switch work. A schedule multiplies a defect as easily as it multiplies useful work.
8. Revalidate after changing role instructions, permissions, resources or runtime version.

Check: the same synthetic task produces an acceptable, traceable result on repeated manual runs. This guide creates no Waker, connector, group or scheduled task.

## 7. Step six — treat remote access and administration as separate features

Qoder Mobile & Web provides remote task access; it is not an embedded Via-Vitae customer UI. [Remote control](https://docs.qoder.com/mobile/app/remote-control).

1. Decide who needs remote access and why. Start with viewing status if approval from a phone is unnecessary.
2. Require organizational identity controls, device/session revocation and the same server-side authorization as desktop use.
3. Exclude sensitive prompt previews from notifications and lock screens.
4. For organization reporting, create a separate least-privilege administration identity where supported; verify actual key scope before using it.
5. Keep keys in a server-side secret manager. Redact them from logs, error messages and exported examples.
6. Test revocation and offboarding, not only successful sign-in.

Check: revoking an operator removes access across every enabled surface. Administration credentials cannot be used by an ordinary product user.

## 8. Step seven — use delivery gates before investing in a platform

The enterprise workflow documentation describes staged development with separate quality checks. The platform document describes a common portal and governance architecture. These are useful design inputs, not proof that Via-Vitae has implemented those controls. [Development workflow](https://docs.qoder.com/enterprise/solutions/ai-native-product-development-workflow), [Enterprise platform](https://docs.qoder.com/enterprise/solutions/enterprise-ai-platforms).

1. Requirements gate: record the expected behavior and explicit exclusions.
2. Design gate: review trust boundaries, failure modes and data use.
3. Implementation gate: require a reviewable patch and regression tests.
4. Verification gate: run tests and security checks independently of the code-producing agent.
5. Release gate: record accountable approval, rollback steps and the exact artifact being deployed.
6. Operations gate: rehearse cancellation, incident handling, restoration and vendor failure.

Check: preserve evidence for each gate. A successful build is only one piece of that evidence.

## 9. Step eight — establish compliance evidence honestly

SOC 2 assurance concerns controls and their examination; this code review is not a SOC 2 report. [AICPA SOC services](https://www.aicpa-cima.com/resources/landing/system-and-organization-controls-soc-suite-of-services).

ISO/IEC 27001 concerns an information security management system, including risk management and organizational processes, not only software settings. [ISO/IEC 27001](https://www.iso.org/standard/27001).

For each proposed control, record its owner, implementation, evidence location, review frequency and unresolved exceptions. Have the accountable privacy/security owners determine legal applicability, retention and acceptable residual risk. Use independent assurance where required. Keep “implemented,” “tested locally,” “deployed,” “operating effectively” and “independently assessed” as distinct statuses.

## 10. Decisions needed before product integration can proceed

- Which product task should Qoder perform, for which users, with which acceptance criteria?
- Must it process customer or pastoral data, or can it use approved source code and synthetic material only?
- Which runtime and contracted service meet the approved data location, retention and processing requirements?
- Who owns identity, privacy review, operational support and release approval?

Until these are resolved, the useful integration is a bounded development workflow proposal; production Qoder execution remains unimplemented and unenabled.
