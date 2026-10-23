# Asset and compatibility provenance

Original work for Ewing's Animals: all cat vertex positions, topology, UVs,
surface coat pixels, eyes, nose, ear shells, whisker ribbons, paws, tail,
inventory icon, source generator, exporter, definitions and documentation.
The texture is a deterministic procedural brown tabby atlas, not an edited
native raccoon texture. No Companion Dogs/CD: Cats code or art was accessed,
copied, subscribed to or downloaded.

Compatibility only: the builder reads installed Raccoon_Body.x bone names,
hierarchy and inverse bind alignment. It creates an original mesh weighted to
those compatible joints and computes the export transforms. Compatible bone
identifiers/transforms are technical rig alignment metadata; they are not
claimed as an original replacement for the game's animation rig. The exported
model references `animationsMesh=Raccoon` and `animset=raccoon` in the base game.
No native mesh vertices, UVs, textures, audio, full native model files, DLLs,
JARs or animation clip/keyframe payloads are bundled in either archive.

The authoring .blend contains the original mesh and compatibility armature,
with the original texture packed. Native animation clips are read transiently
for offline previews, not stored as .blend actions or exported AnimationSets.
Preview renders are original geometry in sampled base-game motion poses.

The base game is required and remains subject to its own license. Distribution
licensing for new original project material has not been selected; this is a
public prototype provided for review and testing, with no open-source license
grant implied. No license rights to another mod or proprietary game asset are asserted.

`verification/native_reference_hashes.json` records matching before/after
SHA-256 values for the original principal native references. The private JVM
probes load the installed Jassimp DLL by its supported loader configuration;
the probes and native binaries are not included as runtime mod dependencies.

The 0.1.4 adult/kitten icons are fresh offline Blender views of the existing original packed cat source, with original lighting/camera settings and transparent padding. Native raccoon icon pixels were not extracted or copied. Native texture-pack frame dimensions were inspected as metadata only.
