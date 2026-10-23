# Changelog

## 0.1.2 - behavior and pickup prototype

- Repair zero adult growth duration that can produce NaN weight and hide native pickup; use native raccoon adult duration 60 while keeping the adult terminal.
- Preserve adult/breed IDs and raccoon fear/motion baseline; no rope or acceptance bypass.
- Add friendly non-wild kitten type, scaled original art, native growth and kitten/dwarf petting selection; no breeding or population spawns.
- Add cat-only solid-food menu delegating to native feeding; preserve milk and native petting stress/cooldown.
- Add read-only handling diagnostic for saved invalid weights and unresolved live menu cases. No save migration.
- Native Java definition parsing, JVM float regression, menu/definition/action stubs, XML parsing and deterministic packages checked. Gameplay/MP acceptance pending.

## 0.1.1 â€” local update, publication pending

- Translate `IGUI_Animal_Group_ewingsanimals_cat` as Cats.
- Enable native animal petting and its existing stress effects/cooldown.
- Add one cat-only player animation node using the native adult-raccoon low-pet
  clips and completion event. No global action/menu overrides or original art changes.
- Alias the terminal adult type for native dwarf-adult pet animation selection;
  no kittens, mates, population or balance changes.
- Isolated native parser/action/reference checks added. Live petting and
  multiplayer remain untested; exit/restart is required before updating.
- Inspect native pickup gates/path/inventory conversion. No acceptance threshold
  exists in the native pickup gate; retain native behavior and test its isolated
  paths. The live pickup report remains unreproduced, with no speculative bypass.

## 0.1.0 â€” 2026-10-23, offline prototype

- Original adult brown tabby model, texture, UVs and inventory icon.
- Additive EwingsAnimals species identifiers and native raccoon motion reuse.
- Skittish native roaming/pickup/care; explicit cat food/meat/fish diet.
- Optional pure CowMilk/AnimalMilk hand feeding through native fluid handling.
- No breeding, automatic spawns, companion commands or global overrides.
- Headless Blender previews, native asset/script/Lua checks, pose math checks,
  unchanged-reference hashes and deterministic archive verification.
- Gameplay, save/reload and multiplayer acceptance remain pending.
