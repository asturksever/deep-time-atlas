# Design System: Deep Time Globe

The design language of the Deep Time Atlas family (the 3D globe in `src/globe.html` and the 2D museum screen in `src/template.html`). It is written so Google Stitch, or any other screen generator, can produce new screens that match what has shipped. Exact values come from the built pages.

## 1. Visual Theme & Atmosphere

A planetarium at night. The planet is the interface: it fills the screen edge to edge, lit from the viewer's upper left, with a thin blue atmosphere at the limb and a sparse field of faint stars behind it. Everything else is chrome that floats above the planet on dark, frosted glass. The chrome is quiet, precise and instrument-like, in the manner of a well-made map app or a museum display case after the lights go down.

- **Density 5, Daily App Balanced.** Little chrome on screen, but every panel is information-dense: an age readout, a period, a caption and a ruler with 26 labelled stops.
- **Variance 6, Offset Asymmetric.** No centred layout. The place card is pinned top-left, the tools top-right and the time dock bottom-centre, and the planet sits in the space between them.
- **Motion 5, Fluid and physical.** Motion comes from the planet and from direct manipulation (drag, flick, spin and follow). The chrome barely moves: it responds to presses and changes of state, and never performs.
- **Single theme by design.** Dark only, with `color-scheme: dark`. Space is dark, and the imagery needs a dark surround to read as a planet.

## 2. Color Palette & Roles

Neutrals are cool blue-slate throughout, tuned toward the ocean so the chrome belongs to the planet. There are no warm greys anywhere.

- **Deep Space** (#03050B): page and scene background behind the planet. Never pure black.
- **Night Glass** (rgba(16, 22, 38, 0.62)): floating panel fill, always with 22px backdrop blur and 160% saturation.
- **Solid Night** (#121A2C): Night Glass fallback when reduced transparency is on. The opaque popover uses rgba(18, 26, 44, 0.94).
- **Glass Edge** (rgba(255, 255, 255, 0.09)): 1px panel border, plus a 1px inner top highlight at 6% white, like light catching the material.
- **Pressed Film** (rgba(255, 255, 255, 0.07)): hover and pressed fill on ghost buttons.
- **Starlight Ink** (#EEF2FB): primary text, the large age numerals and the primary button fill.
- **Slate Dim** (#9AA6C2): secondary text, captions, ruler labels and metadata.
- **Slate Faint** (#6B7794): tertiary text, credits and inactive switch rings.
- **Exhibit Coral** (#FF6F61): the single accent. It comes from the red time marker on the museum's ruler. Use it only for the time cursor, city pins, active switches, the city count badge and focus rings (HSB saturation 62%).
- **Data colours, not accents:** the ICS geologic period colours (for example Triassic #812B92 and Cretaceous #7FC64E) appear only as the period strip under the ruler and as the 9px period dot. Never use them for chrome.
- **Planet colours, not tokens:** ocean and land colours come from the NASA imagery itself. The open-ocean colour is sampled from the imagery's deep Pacific at runtime so plate edges don't show a seam.

## 3. Typography Rules

- **Display: Bricolage Grotesque** (800 weight). Use it only for the age numerals and sheet titles. Age: `clamp(2.4rem, 6vw, 3.4rem)`, letter-spacing -0.045em, line-height 0.95, tabular figures. Story headline: 17px, weight 600, letter-spacing -0.01em, `text-wrap: balance`.
- **Interface: system UI** (`system-ui, -apple-system, "Segoe UI"`): buttons, captions and body copy. Body 13.5px with line-height 1.5, and captions held near 60 characters. Using the system face keeps the chrome native and lets the display face carry the brand.
- **Mono: JetBrains Mono** for every number that changes: ruler stops, speed (`20 Myr/s`), palaeolatitudes (`43°N`) and uppercase labels. Labels are 11px, weight 600, uppercase, with letter-spacing 0.12 to 0.14em.
- **Tracking scales with size:** tight (negative) on the large numerals, neutral on body text, open (positive) on small uppercase labels.
- **Banned:** Inter, and any serif in the interface.

## 4. Component Stylings

- **Place card (top-left):** Night Glass, 18px radius, 14px by 16px padding, 360px wide. Contents in order: brand label with a coral dot, then age numerals beside "million years ago", then the period dot and name, then the story headline and caption. Below 640px it spans the full width, clips the caption to 2 lines and adds a "More" text button.
- **Time dock (bottom-centre):** Night Glass, one slim row at most 1040px wide (two rows under 760px): Play, back to 600 Ma (icon), the ruler, speed, Cities. Sources and caveats live behind the i tool, not in the dock.
  - **The ruler:** canvas, 40px tall. It has the exhibit's 26 exact stops, a 5px ICS period strip and a coral cursor with a triangular foot. While held, the cursor foot grows 25% and gains a soft coral halo.
- **Primary button (Play):** a Starlight Ink pill with dark text and an inline triangle or pause icon. This is the only filled button on screen.
- **Ghost buttons:** transparent pills that take Pressed Film on hover (only on devices that can hover). Every pressable element scales to 0.96 over 140ms on press. No glows and no custom cursors, apart from grab and grabbing on the planet.
- **Tool stack (top-right):** a vertical glass group of 40px square icon buttons with 1.7px line icons for recentre, auto-spin and about. A toggled tool turns coral.
- **Popover (Cities):** anchored to its button and scaling from its bottom-right corner. It opens from 0.96 scale with a 4px rise over 180ms and closes in 120ms. Each row has a round switch (coral when on), the city name, its live palaeolatitude in mono and a follow (crosshair) button. Esc or a tap outside closes it.
- **Globe labels:** small frosted pills (66% night, 10px blur) with a coral dot, the city name and its palaeolatitude in mono. They fade out when the city turns past the limb. Tapping one follows that city.
- **Following pill:** top-centre glass pill reading "Following London" with a close button. On phones it sits just above the dock.
- **Sheet (Sources and limits):** a centred modal on a 50% night scrim, rising 10px from 0.98 scale over 240ms. It has headed sections and one Done button.
- **Loading:** a sphere-shaped placeholder at the planet's position with a slow opacity shimmer, plus a short status line ("Building plates 60%"). Use no generic spinner.

## 5. Layout Principles

- The planet is a fixed full-viewport canvas. All chrome floats over it at a 16px gutter plus safe-area insets, and nothing scrolls.
- Panels never overlap each other. The planet may sit under any panel, since the panels are translucent so it stays visible.
- Panels sit in the corners and along the bottom, never in the centre. The centre always belongs to the planet.
- Under 640px: the card spans the top (with room for the 52px tool stack beside it), the dock spans the bottom, the control row wraps, and the camera field of view widens from 35 to 48 degrees so the whole planet fits between them.
- Touch targets are at least 40px on tools and 30px on in-list buttons, with the whole row tappable.

## 6. Motion & Interaction

Motion follows Apple's fluid-interface principles and Emil Kowalski's timing rules, which this project adopted before this file existed. Where they differ from the generic Stitch defaults, they take precedence.

- **Springs use response and damping ratio** (unit mass). The default is critically damped: response 0.35s, damping 1.0, which is roughly stiffness 322 and damping 36. Only a flick (release over 120 Ma/s) gets bounce, at damping 0.85.
- **Flick projection:** at release, take the velocity from the last 100ms and project the resting point with deceleration 0.998, then land on the nearest museum stop. A slow release snaps only within 6px. Past 0 and 600 Ma the cursor rubber-bands instead of stopping hard.
- **Direct manipulation:** the ruler responds on pointer-down and the globe tracks the finger 1:1. Drag speed scales with zoom (rotateSpeed = (distance - 1) x 0.42, between 0.12 and 1), and the planet keeps turning briefly after release.
- **Camera behaviours** are critically damped exponential approaches (time constant about 0.3s): recentre, follow a city, and keep the continents in view. The last one never fires within 4s of a user drag.
- **Chrome timing scale:** press 140ms, small 180ms, medium 240ms, with ease `cubic-bezier(0.23, 1, 0.32, 1)`. Exits are faster than entrances.
- **State changes:** the caption swaps with a 220ms cross-fade that blurs by 2px and lifts by 3px. The period dot changes colour over 240ms.
- **Continuous motion is reserved for the planet:** auto-spin, playback, follow and the star field. UI chrome has no perpetual loops (no pulses, shimmer or floating) except the loading placeholder. This deliberately departs from the generic "perpetual micro-interaction" default: a time machine's chrome should stay still so the planet's motion reads.
- **Keyboard steps never animate:** the arrow keys jump between stops instantly.
- **Reduced motion:** springs and inertia become instant, cross-fades become opacity-only, and auto-spin is disabled. **Reduced transparency:** glass becomes Solid Night.
- **Performance:** chrome animates only transform, opacity and filter. The planet updates one quaternion per plate mesh per frame, so the GPU does the reconstruction.

## 7. Anti-Patterns (Banned)

- No emojis anywhere, including UI copy, labels and commit messages.
- No em dashes in any copy. Use commas, colons or full stops.
- No Inter, and no serif in the interface.
- No pure black (#000000). Space is #03050B.
- No second accent colour. Period colours are data and must never style controls.
- No neon glows, outer-glow shadows or gradient text. The only glows are the physical atmosphere around the planet and the coral halo on a held cursor.
- No centred hero, landing page or marketing layout. The app opens straight onto the planet at 240 Ma, Pangaea.
- No "Scroll to explore", bouncing chevrons or other filler hints. Instructions stay plain and specific: "Drag the globe to turn it."
- No equal three-card feature rows, and no cards inside cards.
- No animation on keyboard-initiated actions, and no `ease-in` on UI.
- No fake precision or invented data. Every number on screen comes from the Merdith 2021 model, the ICS 2023/09 chart or the NASA imagery.
- No AI copy clichés ("Elevate", "Seamless", "Unleash", "Next-Gen"). Name things for what they are: Play, Cities, Sources and limits.
- No claims beyond the model. The surface imagery is today's Earth, and the copy must say so wherever a viewer could mistake it for ancient terrain.
