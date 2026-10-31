"""Vendor unlock tracking for FFXIV scrip vendors."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict


@dataclass
class VendorUnlock:
    """A scrip vendor and whether it is unlocked."""

    name: str
    location: str
    unlocked: bool = False
    notes: str = ""


@dataclass
class VendorBook:
    """Collection of vendor unlocks."""

    vendors: list[VendorUnlock] = field(default_factory=list)

    def add(self, vendor: VendorUnlock) -> None:
        for existing in self.vendors:
            if existing.name == vendor.name:
                raise ValueError(f"Vendor {vendor.name!r} is already tracked.")
        self.vendors.append(vendor)

    def unlock(self, name: str) -> VendorUnlock:
        for vendor in self.vendors:
            if vendor.name == name:
                vendor.unlocked = True
                return vendor
        raise KeyError(f"No vendor named {name!r}.")

    def list_unlocked(self) -> list[VendorUnlock]:
        return [vendor for vendor in self.vendors if vendor.unlocked]

    def to_dict(self) -> dict:
        return [asdict(vendor) for vendor in self.vendors]

    @classmethod
    def from_dict(cls, data: list) -> "VendorBook":
        return cls(vendors=[VendorUnlock(**item) for item in data])
