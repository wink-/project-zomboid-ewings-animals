-- Ewing's Animals 0.1.0. Additive, adult-only original cat prototype.
AnimalDefinitions = AnimalDefinitions or {}
AnimalDefinitions.animals = AnimalDefinitions.animals or {}
AnimalDefinitions.stages = AnimalDefinitions.stages or {}
AnimalDefinitions.breeds = AnimalDefinitions.breeds or {}
AnimalDefinitions.genome = AnimalDefinitions.genome or {}
local species = "ewingsanimals_cat"
local adult = "ewingsanimals_catadult"
local coat = "ewingsanimals_browntabby"

-- A terminal stage: no nextStage, hence native isBaby() returns false.
local stages = { [adult] = { ageToGrow = 0 } }
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
    -- No mates, babyType, pregnancy, hutch, wool, milk production or eggs.
    male = false, female = false, minBaby = 0, maxBaby = 0,
    needMom = false, eatFromMother = false, litterEatTogether = false,
    wild = true, canBeDomesticated = true,
    alwaysFleeHumans = true, fleeZombies = true,
    wanderMul = 600, idleTypeNbr = 2, sitRandomly = true,
    canBePicked = true, canBePet = false,
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
