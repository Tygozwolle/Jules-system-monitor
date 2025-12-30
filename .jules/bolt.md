## 2024-02-14 - Redundant System Loops
**Learning:** System hardware checks (like sysfs scans) can be expensive and should be minimized.
**Action:** When scanning `/sys/class/drm` or similar, iterate once and dispatch based on vendor ID rather than multiple loops.
