from dataclasses import dataclass, field

FS_READ_PUBLIC = "fs.read.public"
FS_READ_PRIVATE = "fs.read.private"
FS_WRITE_WORKSPACE = "fs.write.workspace"
NET_HTTP_GET = "net.http.get"
NET_HTTP_POST = "net.http.post"
NET_EXTERNAL = "net.external"
NET_INTERNAL = "net.internal"


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


# Auto-collect all uppercase string constants so registry never goes stale.
ALL_CAPABILITIES: set[str] = {v for k, v in globals().items() if k.isupper() and isinstance(v, str)}


def is_known(capability: str) -> bool:
    return capability in ALL_CAPABILITIES
