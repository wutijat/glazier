# Error Codes

The question of how to implement error codes has already been answered a
plethora of ways. An example is how Microsoft uses BSOD codes to identify fatal
failures with the Windows Operating System. Leveraging the same philosophy,
error codes should be added to all exceptions thrown by Glazier. There is a
difference between error codes and error return values. An error code gives a
user actionable feedback. An error return value is a coding technique to
indicate that your code has encountered an error.

## Background

For simplicity, error codes will be put into buckets similar to HTTP status code
mapping (1xx, 2xx, etc.). Four digits will be used for scalability and
disambiguation from HTTP error code mappings. If no status code is defined by
the error, the default will be used (4000). Error codes are included as HTML
anchors for easily troubleshooting issues through documentation.

Error codes achieve the following objectives:

1.  Convey error code
1.  Short*, actionable log messages
1.  Documentation explaining error codes is a living doc and can be updated as
    necessary
1.  Data can be inferred based on the error code itself with where the issue
    originates (e.g. 4011 could relay information regarding file share access
    issues)

\* Having short status codes is essential since every exception will have this
string appended to it. The aim is to give the end consumer concise and
actionable steps for troubleshooting most known errors.

### Top-level buckets

Below are examples of error codes that can be implemented based on existing
Glazier exceptions. This list is not meant to be the final mapping or an
exhaustive enumeration. Always refer to [errors.py](../../glazier/lib/errors.py) for the
latest error code mappings. All critical errors should be added to the error
library, rather than individual libraries. The expectation is error codes point
to anchors in your internal documentation. Error code buckets are shown below:

Code     | Example
-------- | ------------------------------------
**1XXX** | Informational (reserved)
**2XXX** | Success (reserved)
**3XXX** | Redirection (reserved)
**4XXX** | Client Error
4000     | Default error code
41XX     | Unsupported method
42XX     | Time issues
43XX     | Invalid request (ex: too large)
44XX     | Validation Error
45XX     | Request Blocked (ex: firewall/proxy)
49XX     | Unknown/Misc
**5XXX** | Server Error
50XX     | Internal Server Error
53XX     | Service Unavailable