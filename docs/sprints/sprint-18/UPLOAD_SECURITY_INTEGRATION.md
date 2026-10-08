# Sprint 18 Upload Security

Sprint 18 adds:

```text
FilePolicy
sanitize_filename
validate_upload_metadata
validate_magic_prefix
ClamAVScanner
```

## Learning Service

Reconcile Sprint 7's real upload endpoint.

Before object storage persistence:

1. enforce authenticated Teacher ownership/assignment
2. enforce maximum body/file size
3. sanitize the original filename
4. allow only approved extension
5. allow only approved MIME type
6. inspect file magic where a known signature exists
7. malware-scan when required
8. generate a server-controlled object key
9. upload to private S3-compatible storage
10. persist only metadata/key/version in learning_db

Never trust:

```text
client filename path
Content-Type alone
client-provided object key
file extension alone
```

Recommended Learning baseline:

```text
PDF
PNG
JPEG
plain text
institution-approved Office documents
```

Do not allow executable/script extensions.

## Office documents

DOCX/PPTX/XLSX are ZIP containers.

If these are enabled, validate:

- extension + MIME
- ZIP magic
- archive entry count/expanded-size limits
- no path traversal entries
- malware scan

Codex should add these checks to the actual existing Sprint 7 policy rather than
blindly expanding allowed file types.

## Platform imports

CSV/XLSX imports should have separate stricter policies and size limits.

Parsing must occur in a worker/job where large or malformed inputs cannot block
API workers.

## Malware scanning

Development may run without ClamAV:

```text
MALWARE_SCAN_REQUIRED=false
```

Production should use:

```text
MALWARE_SCAN_REQUIRED=true
CLAMAV_HOST=<internal scanner>
CLAMAV_PORT=3310
```

When malware scanning is required, scanner failure should fail closed for new
uploads. Do not publish an unscanned object as available.

## Downloads

Buckets remain private.

Authorization is checked before:

- streaming a file through the API, or
- issuing a short-lived presigned URL

Presigned URL TTL should remain short and the object key must come from an
authorized database record.
