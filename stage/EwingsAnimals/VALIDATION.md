# Offline validation — Ewing's Animals 0.1.0

Target: B42.21 / Steam25485521, Windows.

- Original source mesh: 2919 vertices, 5262 triangles.
- At most 2 normalized bone influences per vertex.
- Installed native Assimp importer: passed; no embedded animation clips.
- Installed native model-script parser: passed.
- Installed native Lua compiler: both mod scripts passed.
- Installed Kahlua execution: additive registration/adult/diet/milk/scope assertions passed.
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
