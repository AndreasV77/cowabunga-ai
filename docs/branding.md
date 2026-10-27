# Cowabunga AI visual identity

Decision: 2026-10-27. The owner approved the uploaded, rotated turquoise shaka
gesture as the visual direction for the logo and favicon.

## Locked direction

- Simple, warm, functional and extensible. Use a gesture, not a character mascot.
- Preserve the approved pose: the little finger extends towards the left and the
  thumb rises towards the upper right. The owner's rotated image supersedes the
  earlier interpretation of an angle measured from vertical. Do not rotate or
  mirror it again as a cleanup.
- Beach-water turquoise. The flat icon uses `#23C7C3`, sampled from the approved
  image. It does not change the rest of the workbench's interface palette.
- No faces, headphones, extra music symbols, borders or background shapes in the
  primary mark. Keep transparent space around the gesture.

## Assets and use

| Asset | Purpose |
|---|---|
| [Approved PNG](../web/public/brand/shaka-approved.png) | Unmodified owner-approved source; keep its original transparency and pose. |
| [Shaka SVG](../web/public/brand/shaka-icon.svg) | Flat, simplified native vector for the workbench header, README and scalable favicon. |

The SVG follows the largest opaque hand contour of the approved PNG, simplified
to 88 vertices at a three-source-pixel tolerance and centered with padding. It is
an editable path with a flat turquoise fill, not a raster embedded inside SVG.
Transparent source RGB values are not part of its silhouette. Small alpha-edge
speckles and tiny contours were excluded; finger pose was not redesigned.

The SVG uses a 256 × 256 viewBox and works at browser favicon dimensions without
requiring separately upscaled or resampled source images. At tiny sizes the
gesture's outer contour is more important than detailed finger creases.

`web/index.html` references the SVG favicon; Vite copies the public assets into
the production build. The header uses the same SVG with an empty alt because its
adjacent linked text already names the project. README uses descriptive alt text.

The source's hidden RGB data can look unusual in image viewers that display
transparent pixels incorrectly. Do not replace its alpha channel with a black
or white background. Use the SVG for normal icon placement.

The original PNG and the derived icon are covered by the project asset terms
only to the extent the licensor holds the relevant rights. Their inclusion is
not a claim of registered trademark status or exclusivity over the shaka gesture.

A wide repository/social cover can be derived from this mark and the existing
name/tagline. Its layout is not established by this decision.

## Verification — 2026-10-27

The copied source PNG matches the approved upload byte for byte. The SVG parses
as XML, and the TypeScript/Vite production build succeeds. Browser inspection
checked the icon at 16, 32, 64 and 128 pixels on light and dark backgrounds, and
confirmed the 36-pixel header asset and favicon reference load. This was a static
asset check, not a new test of backend data or music-generation behavior.
