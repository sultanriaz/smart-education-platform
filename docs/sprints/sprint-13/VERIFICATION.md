# Sprint 13 Verification

Actual checks executed in the packaging environment:

## required_files

Exit code: `0`

```text
missing=[]
```

## gateway_only

Exit code: `0`

```text
direct_service_port_hits=[]
```

## route_coverage

Exit code: `0`

```text
{"student_dashboard": true, "attendance": true, "timetable": true, "learning": true, "assessments": true, "attempt": true, "facilities": true, "notifications": true}
```

## assessment_answer_key_projection

Exit code: `0`

```text
Student assignment serialization contains only choice id/text; no answer-key keys.
```

## assessment_patch_python_syntax

Exit code: `0`

```text
Python syntax compilation passed.
```

## assessment_overlay_pytest

Exit code: `0`

```text
[32m.[0m[33ms[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m                                                                [100%][0m
[32m[32m[1m8 passed[0m, [33m1 skipped[0m[32m in 0.50s[0m[0m
Spreadsheet runtime warmup failed during python startup
Traceback (most recent call last):
  File "/tmp/tmp.L2TH2Y5coc/artifact_tool_v2-2.8.22/artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py", line 26, in warm_spreadsheet_runtime_on_startup
  File "/tmp/tmp.L2TH2Y5coc/artifact_tool_v2-2.8.22/artifact_tool/spreadsheet_warmup.py", line 785, in warm_spreadsheet_runtime
  File "/tmp/tmp.L2TH2Y5coc/artifact_tool_v2-2.8.22/artifact_tool/spreadsheet_warmup.py", line 720, in _warm_feature_flows
  File "/tmp/tmp.L2TH2Y5coc/artifact_tool_v2-2.8.22/artifact_tool/spreadsheet_warmup.py", line 704, in _warm_collaboration_flows
  File "/tmp/tmp.L2TH2Y5coc/artifact_tool_v2-2.8.22/artifact_tool/generated/interface/models.py", line 32317, in hydrate_crdt_from_proto
  File "/tmp/tmp.L2TH2Y5coc/artifact_tool_v2-2.8.22/artifact_tool/rpc/remote.py", line 749, in __call__
  File "/tmp/tmp.L2TH2Y5coc/artifact_tool_v2-2.8.22/artifact_tool/rpc/client.py", line 150, in call
artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.
```

## student_api_contract

Exit code: `0`

```text
{"attendance_gateway": true, "scheduling_gateway": true, "learning_gateway": true, "assessment_gateway": true, "facility_gateway": true, "notification_gateway": true, "authenticated_download": true}
```

## bom_scan

Exit code: `0`

```text
BOM files: []
```

## node_runtime

Exit code: `0`

```text
v22.16.0
```

## Not claimed as verified here

The packaging runtime does not provide a guaranteed npm registry, Docker daemon,
or the fully merged Sprint 1–12 distributed stack. Therefore these remain
repository-integration checks:

- `npm install`
- `npm run typecheck`
- `npm run lint`
- `npm run test`
- `npm run build`
- frontend Docker build/runtime
- live Identity login
- live Attendance/Scheduling/Learning/Facility/Notification APIs
- live Assessment Student read APIs through Gateway
- protected Learning file download through Gateway
- Student end-to-end browser smoke flow
- CORS and deep-link refresh

Codex integration must run them before declaring Sprint 13 fully integrated.
