# Ewing's Animals — adult cat prototype 0.1.0

Standalone mod ID: `EwingsAnimals`. Target inspected: Project Zomboid B42.21,
Steam build 25485521, Windows. This is an offline-validated prototype for future
disposable-world testing. It has not been installed or run in the game.

![Offline Blender preview of the original cat](previews/EwingsAnimals_cat_preview.png)

*Offline Blender renders, not in-game screenshots. Stylized angular geometry
and raccoon-derived motion remain visible; game appearance is unverified.*

The first animal is an original, stylized adult brown tabby: newly authored
geometry, UVs, coat, eyes, ears, muzzle, paws, tail and inventory icon. It uses
the installed base game's raccoon motion system by reference. Native raccoons
are unchanged. There are no companion commands, follow systems, combat systems,
kittens, breeding, automatic population spawns, recipes or dependencies on
Companion Dogs/CD: Cats.

## Contents and identifiers

- `stage/EwingsAnimals/`: installable mod folder, with `42/mod.info` and `common/`.
- `art/EwingsCat_Adult.blend`: original authoring model, packed original texture,
  and compatibility armature. No native animation actions are embedded.
- `tools/`: reproducible original-model builder, exporter, parser checks and
  deterministic packager. Tools are not required to play the packaged mod.
- `previews/`: offline Blender images, not screenshots of the game.
- `verification/`: final offline check reports and unchanged-reference hashes.

Stable animal type: `ewingsanimals_catadult`; group: `ewingsanimals_cat`;
coat/breed: `ewingsanimals_browntabby`; model: `EwingsAnimals_CatAdult`.
The mod ID reserves room for future species without renaming the project.

## Future manual install and first spawn

Installation has intentionally not been performed. When ready to test, close
the game and use a disposable user-data directory/world. Extract the install
ZIP so the chosen test `mods` directory contains `EwingsAnimals/42/mod.info`
and `EwingsAnimals/common/`, then enable Ewing's Animals. Do not merge files
into the installation or an unrelated existing mod. Verify the exact loader
layout again if using a different B42 build or a custom `-cachedir`.

Start the disposable world with the game's debug tools. Use its native animal
spawn menu and select type `ewingsanimals_catadult`, breed
`ewingsanimals_browntabby`, live/non-skeleton. The mod does not add a custom
spawn hook or alter any map/trap/migration distributions. If the native menu
does not list the type, stop and inspect the test log rather than adding a
population workaround. Test single-player first; see ACCEPTANCE.md.

Remove the mod only from a disposable test world after deleting the test cats.
Persistent custom animal types can leave incompatible saved entities if the
mod is removed from a valuable world. No valuable save is needed to evaluate
this prototype.

## Care and behavior

Cats start wild and flee people/zombies using native animal behavior. Catching
uses native pickup and its carrying limits; pickup clears native wild status.
Native player acceptance and husbandry interactions may still apply. No tame
companion AI is supplied. Raccoon gait, crouches and timing remain visible;
this is not a new feline animation library.

Place suitable food in a native feeding trough or on accessible ground inside
a livestock zone. The allowlist is FoodType `CatFood`, `Meat`, `Fish`, plus the
existing `Base.CatFoodBag`. Grass, hay, vegetables and broad `All` feeding are
not included. Eligibility is based on the installed native consumer, not a
new cooking/nutrition simulation. Raw/rotten-food handling follows native
rules and needs acceptance testing.

Optional milk uses native fluid handling: when hungry, offer a container of
**pure Cow Milk (`CowMilk`) or pure Animal Milk (`AnimalMilk`)** through native
hand feeding. The native consumer removes fluid and retains the vessel. Sheep
milk, chocolate milk and mixtures are not claimed to work in this first scope.
Setting the breed's `milkType` enables this consumer; cats have no udder,
milk-production genes or milking capability. Milk can affect both hunger and
thirst through native code, but water consumption and thirst remain enabled.

Vanilla's hand-feeding UI filters solid foods more narrowly than the underlying
diet consumer. Solid cat food/meat/fish may therefore be absent from the hand
menu; use ground/trough feeding for this prototype. No global menu override
was added. Milk should take the native fluid branch; verify amount/container
behavior in the test world before relying on it.

Livestock zones encourage ordinary staying and locate care resources. They
are **not physical fences**. Hungry, thirsty or frightened animals may leave.
Keep walls and exits physically closed for an indoor cat; open doors, windows,
stairs, upper floors and panic escape require explicit tests. Adjacent zones
can merge in native behavior. The prototype chooses a 12-square minimum zone
area; that is a mod design choice, not a guarantee of indoor containment.

## Explicit prototype choices and limits

- One adult terminal stage; both sex flags false, no mate/baby references.
- 3.5–5.5 native weight range; 4.5 carrying encumbrance; size range 0.95–1.05.
- Hunger/thirst multipliers 0.0045/0.005, deliberately provisional balance.
- No petting/rope attachment, attacks, fence climbing, grass eating, dung,
  milk/wool/egg production or tracked-population additions.
- Stair climbing, pickup, native transport and normal roaming are enabled.
- Silent first version: no raccoon cries, borrowed cat audio or custom sounds.
- Original living mesh/coat/icon also serve as basic corpse/decay fallbacks.
  No skeleton, skinning/butchering assets or harvesting tables are supplied;
  corpse/harvest behavior is unverified and outside initial acceptance.
- Native `wildFleeTimeUntilDeadTimer=250` is retained explicitly. The engine's
  wild-and-hurt escape lifecycle is not redesigned or described as pet health.
- `alwaysFleeHumans`, wild status, stress and acceptance interact natively;
  the exact post-capture temperament requires observation.

The Assimp mesh import, native script parsing and Lua checks do not certify the
game's renderer, loader integration, animation blending, saves or networking.
Read the concrete test matrix in ACCEPTANCE.md before using the mod beyond a
disposable world.

## Reproduce offline work

Use an already installed Blender and matching B42 installation. No downloads
or pip packages are required. Set the `PZ_GAME_DIR` environment variable to your
own Project Zomboid installation before running the tools. Use Blender's
bundled Python and the installed game's JRE; no machine-specific path is required
in the source. The Java probes compile Lua and import assets without booting a world.

1. Run Blender with `--background --factory-startup --threads 4 --python tools/build_cat.py`.
2. Run `tools/native_probes.py` with Blender's bundled Python to emit tiny local
   JVM probes, then run `tools/validate_package.py` with that Python.
3. Run Blender in background with `tools/check_deformation.py`.
4. Before redistributing the source, run Blender in background with
   `tools/sanitize_authoring.py` to remove local file metadata while checking
   that the original geometry remains unchanged.
5. Run `tools/package_release.py` with the bundled Python, then
   `tools/audit_publication.py` to check the final archives.
   Packaging strips textual/EXIF metadata from project PNGs without changing
   their compressed pixel data.

Only the source/staging tree is written. Native files are read for compatibility
and remain unchanged; no game, save, server or Workshop operation is performed.
