import { describe, expect, it } from "vitest";
import { copy } from "./i18n";

describe("translations", () => {
  it("keeps the same keys in Spanish and English", () => {
    expect(Object.keys(copy.es).sort()).toEqual(Object.keys(copy.en).sort());
  });

  it("contains no blank labels", () => {
    expect(Object.values(copy.es).every((value) => value.trim().length > 0)).toBe(true);
    expect(Object.values(copy.en).every((value) => value.trim().length > 0)).toBe(true);
  });
});
