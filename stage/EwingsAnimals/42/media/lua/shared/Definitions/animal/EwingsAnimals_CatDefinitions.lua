-- Ewing's Animals 0.1.3. Additive original cats; native care and handling.
AnimalDefinitions = AnimalDefinitions or {}
AnimalDefinitions.animals = AnimalDefinitions.animals or {}
AnimalDefinitions.stages = AnimalDefinitions.stages or {}
AnimalDefinitions.breeds = AnimalDefinitions.breeds or {}
AnimalDefinitions.genome = AnimalDefinitions.genome or {}
local species = "ewingsanimals_cat"
local adult = "ewingsanimals_catadult"
local kitten = "ewingsanimals_kitten"
local coat = "ewingsanimals_browntabby"

-- Native raccoon-kit growth baseline, with the same adult destination for both
-- sexes. No mates, births or automatic population distributions are supplied.
local stages = {
    -- Terminal does not mean zero-duration: native initWeight divides by this
    -- even for adults. Zero produces NaN at minAge and hides native pickup.
    [adult] = { ageToGrow = 60 },
    [kitten] = { ageToGrow = 60, nextStage = adult, nextStageMale = adult },
}
AnimalDefinitions.stages[species] = { stages = stages }
local genes = {}
for _, name in ipairs({ "maxSize", "meatRatio", "maxWeight", "lifeExpectancy",
    "resistance", "strength", "hungerResistance", "thirstResistance",
    "aggressiveness", "ageToGrow", "fertility", "stress" }) do
    genes[name] = name
end
AnimalDefinitions.genome[species] = { genes = genes }
local breeds = {
    [coat] = {
        name = coat,
        texture = "EwingsCat_BrownTabby", textureMale = "EwingsCat_BrownTabby",
        rottenTexture = "EwingsCat_BrownTabby",
        invIconMale = "Item_EwingsCat_Adult", invIconFemale = "Item_EwingsCat_Adult",
        invIconBaby = "Item_EwingsCat_Adult",
        invIconMaleDead = "Item_EwingsCat_Adult", invIconFemaleDead = "Item_EwingsCat_Adult",
        invIconBabyDead = "Item_EwingsCat_Adult",
        -- Native milk-container consumer accepts this pure fluid or AnimalMilk.
        -- Does not give cats udders/milk production: female/milk genes are absent.
        milkType = "CowMilk",
        sounds = {}, -- Deliberately silent; no raccoon vocalizations borrowed.
    },
}
AnimalDefinitions.breeds[species] = { breeds = breeds }
AnimalDefinitions.animals[adult] = {
    bodyModel = "EwingsAnimals_CatAdult", animset = "raccoon",
    breeds = breeds, stages = stages, genes = genes, group = species,
    minSize = 0.95, maxSize = 1.05, minWeight = 3.5, maxWeight = 5.5,
    baseEncumbrance = 4.5, minAge = 60, maxAgeGeriatric = 15 * 365,
    -- Native dwarf-adult petting selects this type; it has its own player node.
    -- A baby type does not add a mate, pregnancy or breeding capability.
    babyType = kitten,
    male = false, female = false, minBaby = 0, maxBaby = 0,
    needMom = false, eatFromMother = false, litterEatTogether = false,
    -- Native adult raccoon fear baseline. No forced acceptance, speed override
    -- or replacement flee/pickup action; the stage duration fixes weight math.
    wild = true, canBeDomesticated = true,
    alwaysFleeHumans = true, fleeZombies = true,
    wanderMul = 600, idleTypeNbr = 2, sitRandomly = true,
    canBePicked = true, canBePet = true,
    canBeFeedByHand = true, canBeAttached = false, canBeTransported = true,
    canClimbStairs = true, canClimbFences = false,
    canThump = false, collidable = false,
    udder = false, canBeMilked = false, eatGrass = false,
    attackBack = false, attackIfStressed = false, canDoLaceration = false,
    attackDist = 0, baseDmg = 0, dontAttackOtherMale = true, turnDelta = 0.95,
    shadoww = 0.22, shadowfm = 0.28, shadowbm = 0.28,
    hungerMultiplier = 0.0045, thirstMultiplier = 0.005,
    hungerBoost = 20, thirstBoost = 25, thirstHungerTrigger = 0.1, distToEat = 1,
    -- Native canEatThis matches full item IDs, AnimalFeedType and FoodType.
    eatTypeTrough = "CatFood,Meat,Fish,Base.CatFoodBag",
    feedByHandType = "CatFood,Meat,Fish,Base.CatFoodBag,CowMilk,AnimalMilk",
    feedByHandAnim = "AnimalLureLow",
    minEnclosureSize = 12, trailerBaseSize = 30, addTrackingXp = false,
    corpseSize = 0, dungChancePerDay = 0,
    -- Inherited wild/hurt escape lifecycle retained explicitly, not a pet system.
    wildFleeTimeUntilDeadTimer = 250,
}

-- Same original art at native raccoon-kit scale. Juvenile-specific geometry
-- is not included in this focused behavior update.
local young = {}
for key, value in pairs(AnimalDefinitions.animals[adult]) do young[key] = value end
young.minSize = 0.5
young.maxSize = 0.9
young.minWeight = 1
young.maxWeight = 2.5
young.baseEncumbrance = 1.5
young.minAge = 0
young.wild = false
young.alwaysFleeHumans = false
young.wanderMul = 500
young.hungerMultiplier = 0.001
young.thirstMultiplier = 0.002
young.hungerBoost = 25
young.thirstBoost = 30
young.wildFleeTimeUntilDeadTimer = 150
AnimalDefinitions.animals[kitten] = young
