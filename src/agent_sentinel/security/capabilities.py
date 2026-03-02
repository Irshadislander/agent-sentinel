from __future__ import annotations

from dataclasses import dataclass, field

from agent_sentinel.security.capability_model import (
    Capability,
    CapabilityCategory,
    CapabilityRegistry,
    RiskLevel,
)

# ---- Registry ----
REGISTRY = CapabilityRegistry()

# ---- Capability Definitions (Enterprise-ready metadata) ----
REGISTRY.register(
    Capability(
        name="fs.read.public",
        category=CapabilityCategory.FILESYSTEM,
        risk=RiskLevel.LOW,
        description="Read from public filesystem locations.",
    )
)
REGISTRY.register(
    Capability(
        name="fs.read.private",
        category=CapabilityCategory.FILESYSTEM,
        risk=RiskLevel.MEDIUM,
        description="Read from private filesystem locations.",
    )
)
REGISTRY.register(
    Capability(
        name="fs.write.workspace",
        category=CapabilityCategory.FILESYSTEM,
        risk=RiskLevel.MEDIUM,
        description="Write within workspace-controlled directories.",
    )
)
REGISTRY.register(
    Capability(
        name="net.http.get",
        category=CapabilityCategory.NETWORK,
        risk=RiskLevel.MEDIUM,
        description="HTTP GET requests.",
    )
)
REGISTRY.register(
    Capability(
        name="net.http.post",
        category=CapabilityCategory.NETWORK,
        risk=RiskLevel.HIGH,
        description="HTTP POST requests (potential data exfiltration).",
    )
)
REGISTRY.register(
    Capability(
        name="net.external",
        category=CapabilityCategory.NETWORK,
        risk=RiskLevel.HIGH,
        description="Access to external network resources.",
    )
)
REGISTRY.register(
    Capability(
        name="net.internal",
        category=CapabilityCategory.NETWORK,
        risk=RiskLevel.LOW,
        description="Access to trusted internal network resources.",
    )
)

# ---- Backward-compatible string constants (do NOT break existing code) ----
FS_READ_PUBLIC = "fs.read.public"
FS_READ_PRIVATE = "fs.read.private"
FS_WRITE_WORKSPACE = "fs.write.workspace"
NET_HTTP_GET = "net.http.get"
NET_HTTP_POST = "net.http.post"
NET_EXTERNAL = "net.external"
NET_INTERNAL = "net.internal"


# ---- Compatibility helpers used by policy_engine and others ----
def is_known(capability: str) -> bool:
    return REGISTRY.is_known(capability)


def get_capability(capability: str) -> Capability | None:
    return REGISTRY.get(capability)


ALL_CAPABILITIES: set[str] = REGISTRY.all_names()


@dataclass(slots=True)
class CapabilitySet:
    granted: set[str] = field(default_factory=set)

    def has(self, cap: str) -> bool:
        return cap in self.granted

    def require(self, cap: str) -> None:
        if not self.has(cap):
            raise PermissionError(f"missing capability: {cap}")

    def grant(self, cap: str) -> None:
        self.granted.add(cap)

    def revoke(self, cap: str) -> None:
        self.granted.discard(cap)


def minimal_caps() -> CapabilitySet:
    return CapabilitySet(granted={FS_READ_PUBLIC})
