import { describe, expect, it } from "vitest";
import { copy, storageLocationLabel } from "./i18n";

describe("translations", () => {
  it("keeps the same keys in Spanish and English", () => {
    expect(Object.keys(copy.es).sort()).toEqual(Object.keys(copy.en).sort());
  });

  it("contains no blank labels", () => {
    expect(Object.values(copy.es).every((value) => value.trim().length > 0)).toBe(true);
    expect(Object.values(copy.en).every((value) => value.trim().length > 0)).toBe(true);
  });
});

describe("storage location label", () => {
  it("uses the drive selected by the user", () => {
    expect(storageLocationLabel("C:\\Users\\Zero\\Videos", "es")).toBe("LOCAL · UNIDAD C:");
    expect(storageLocationLabel("d:\\Videos", "en")).toBe("LOCAL · DRIVE D:");
  });

  it("identifies shared network locations", () => {
    expect(storageLocationLabel("\\\\servidor\\videos", "es")).toBe("RED · UBICACIÓN COMPARTIDA");
    expect(storageLocationLabel("//server/videos", "en")).toBe("NETWORK · SHARED LOCATION");
  });
});
