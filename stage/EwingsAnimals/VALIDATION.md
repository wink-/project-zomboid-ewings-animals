# Offline validation - Ewing's Animals 0.1.4

Target: B42.21 / Steam25485521, Windows.

- Original source mesh: 2919 vertices, 5262 triangles.
- At most 2 normalized bone influences per vertex.
- Installed native Assimp importer: passed; no embedded animation clips.
- Installed native model-script parser: passed.
- Installed native Lua compiler: all runtime Lua scripts passed.
- Installed Kahlua execution: additive adult/kitten registration, growth, diet, milk and scope assertions passed.
- Cat-only petting XML parsed natively; native action delegation/cleanup and normal/dwarf selection assertions passed.
- Native petting supplies its own stress effect and cooldown; no custom stress values or global overrides.
- Native pickup path/action/inventory conversion inspected and stub-tested.
- Actual Java animal-definition loader parsed native raccoons and both cats.
- Installed JVM reproduced NaN weight from zero stage duration and finite pickup-eligible weight with duration 60.
- Cat-only food menu and kitten XML parser checks passed; live menu integration remains pending.
- No pickup/acceptance bypass or save migration was added.
- Original mesh, coat texture and Blender source match v0.1.0 byte for byte.
- Original adult/kitten icons regenerated; native breed path lookup, alpha/padding, exact casing and native hand render sizes checked.
- User confirmed kitten pickup on 0.1.3; this is not 0.1.4 icon or multiplayer validation.
- Four native motion clips sampled at five phases each: 20 offline poses passed.
- Independent linear skinning comparison maximum error: 0.0000040946 model units.
- Reference hashes match the baseline; no native files were changed.
- Seven Blender renders were visually reviewed as an offline contact sheet.
- ZIP contents, CRCs, SHA-256 and repeated-build byte determinism checked.

These results do not constitute gameplay, renderer-integration, save/reload or
multiplayer certification. See ACCEPTANCE.md for pending disposable-world tests.
Milk support is native configuration plus inspected fluid-consumption code;
actual menu/consumption/network behavior remains a gameplay acceptance item.
Validation required no installation, game/server launch, save access or downloads.
