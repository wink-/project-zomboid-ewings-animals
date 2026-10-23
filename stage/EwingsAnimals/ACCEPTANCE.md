# Disposable-world acceptance — not yet run

Use the exact target build and only Ewing's Animals first. Keep the world and
user-data directory disposable. Capture version, enabled mods and test logs.
Every row below is pending gameplay observation, even if offline checks pass.

| Test | Required observation |
| --- | --- |
| Load and native debug spawn | Cat type/breed listed; one live cat appears; no missing model/texture/bone/Lua errors. Native raccoons still spawn normally. |
| Appearance | Original brown tabby at correct native scale/orientation; correct UVs, opaque coat, visible eyes and ears; no exploding mesh, mirrored limbs or detached parts. |
| Motion | Observe full idle, walk, run, sit/lie, hit/death and transition blends from multiple angles; examine paws/tail, clipping and head tracking. Offline samples cover only four clips. |
| Flee/catch | Approach walking/running, turn away, and try native pickup. Confirm skittishness and carrying behavior; inspect native wild/acceptance state after drop. |
| No companion features | No added follow/command/attack menu or autonomous combat/rope behaviors; zero damage configuration holds. |
| Food positive cases | Separately place existing cat food, meat and fish on accessible ground and in a food trough. Confirm hunger change and native partial-item consumption. |
| Food negative cases | Grass, hay, fruit and vegetables do not become accepted merely because they are nearby. Observe rotten/raw handling; do not infer it from category matching. |
| Milk/container | While hungry, offer pure CowMilk and pure AnimalMilk separately in supported fluid containers. Confirm menu, native action, finite fluid use and retained vessel. Empty/mixed/chocolate/sheep milk should not be assumed supported. |
| Water | Cat still becomes thirsty and drinks native water independently. Test ground water container and water trough; milk is optional. |
| House zone | Ground-floor closed room with resources: ordinary staying, panic from running/noise/zombies, closed/open door contrast, windows and inaccessible resources. Zone alone must not be presented as guaranteed containment. |
| Floor separation | Stairs and an upstairs zone; verify resource discovery, floor boundaries, pathing and inability to escape closed physical exits. |
| Adult only | Multiple adults remain terminal adults; no mating/kittens, dung, eggs, wool or milk production. |
| Native lifecycle | Observe hunger/thirst stress and wild/hurt escape timers in disposable cases. Death/decay/harvesting are unverified; record errors and stop if native fallback fails. |
| Save/reload | Save with a living world cat and with one carried as Base.Animal; reload, drop/pick up and inspect IDs/coat/age/stats. |
| Existing/new regions | Confirm enabling does not generate uncontrolled populations in visited or new areas. No distributions are supplied. |
| Multiplayer later | Separate disposable server/client with identical build and mod: authorized native debug spawn, ownership, movement, pickup/drop, milk/food use, container synchronization, reconnect and server save/restart. |

Roll back by removing the disposable world/user-data directory and staged test
mod only. Do not use these tests to experiment with valuable saved worlds.
