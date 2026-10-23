# Disposable-world acceptance for 0.1.3

Offline checks are not gameplay or multiplayer certification. Fully restart
after installation. Use a disposable world and only this mod initially.

| Test | Required observations |
| --- | --- |
| New adult, no cheats or rope | Native Pick Up appears. Diagnostic weight is finite and below Strength-based limit. Native action creates Base.Animal, equips hands, clears wild; drop and repeat. |
| New kitten | Friendly domestic baseline, distinct type/name/scale. Native pickup without rope, drop, care and petting; stress can still produce flight. |
| Adult fear comparison | Compare fresh raccoon sow/boar and cat under similar stress/acceptance/genetics. Same wild/flee/motions, no mod speed multiplier or acceptance threshold. |
| Old adult | After restart inspect handling weight and logged native pickup/wild/attachment/cheat values. Previously saved NaN may remain; do not edit valuable saves or claim automatic repair. |
| Menu failure | If Pick Up is missing, record the handling line and EwingsAnimals handling log. Native rope in animal-cheat mode does not establish a rope requirement. |
| Food | While hunger >=0.1, fresh CatFoodBag, Meat and Fish appear in Offer cat food and use native consumption/acceptance effects. Rotten/spice, unrelated food and full animals excluded. Ground/trough care still works. |
| Milk/water | Pure CowMilk and AnimalMilk use native fluid menu/action, consume finite fluid and retain vessel. Water independent; mixed/other milk unclaimed. |
| Petting | Cats group, Pet, normal/dwarf adult and kitten player alignment, native stress/cooldown/acceptance. Interrupt action and verify movement unblocks. |
| Failure paths | No native pickup when too heavy, no world animal, failed adjacency or distance >=3. No bypass. No rope needed on ordinary valid small animals. |
| Growth | Kitten grows into stable adult through native 60-day baseline adjusted by genes. Adult remains terminal; no mates/births/automatic populations. |
| Home | Accessible resources in a closed house; compare open/closed exits and panic. Zone does not guarantee containment. |
| Save/reload | New adult/kitten in world and carried; restart, drop/pickup, age/coat/stress/acceptance persist. |
| Multiplayer later | Separate disposable server/client with identical build/mod; native ownership, food/fluid sync, pickup/drop, petting, growth, reconnect and server save/reload. |

No valuable save is needed. Preserve failures and relevant errors for diagnosis.
