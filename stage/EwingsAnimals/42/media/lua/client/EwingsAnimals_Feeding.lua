-- Extend only the two cat types. Native vanilla feed/pickup/petting functions
-- remain intact; native hand feeding supplies consumption, stress and acceptance.
require "ISUI/Animal/ISAnimalContextMenu"

local function isCat(animal)
    if not animal or not instanceof(animal, "IsoAnimal") then return false end
    local kind = animal:getAnimalType()
    return kind == "ewingsanimals_catadult" or kind == "ewingsanimals_kitten"
end

local function addFood(playerObj, animal, menu)
    if menu.ewingsAnimalsFoodAdded or not animal:canBeFeedByHand()
        or animal:getStats():get(CharacterStat.HUNGER) < 0.1 then return end
    local allowed = animal:getEatTypePossibleFromHand()
    local foods = playerObj:getInventory():getAllEvalRecurse(function(item)
        -- Fluids keep their existing native menu and vessel handling.
        if not instanceof(item, "Food") or item:getFluidContainer()
            or item:isAnimalFeed() or item:isRotten() or item:isSpice()
            or item:getHungerChange() >= 0 then return false end
        local category = item:getFoodType()
        -- Vanilla already handles fruit, vegetables and legacy milk items.
        if category == "Fruits" or category == "Vegetables" or item:getMilkType() then return false end
        return allowed:contains(item:getFullType()) or allowed:contains(category)
    end)
    if foods:isEmpty() then return end
    menu.ewingsAnimalsFoodAdded = true
    local option = menu:addOption(getText("ContextMenu_EwingsAnimals_OfferFood"))
    local sub = ISContextMenu:getNew(menu)
    menu:addSubMenu(option, sub)
    local names = {}
    for index = 0, foods:size() - 1 do
        local food = foods:get(index)
        local name = food:getDisplayName()
        if not names[name] then
            sub:addOption(name, playerObj, AnimalContextMenu.onFeedAnimalFood, animal, food)
            names[name] = true
        end
    end
end

local function fill(player, context, worldobjects, test)
    if test then return end
    local playerObj = getSpecificPlayer(player)
    if not playerObj then return end
    -- B42.21's native animal option carries the actual animal as its highlight
    -- parameter. Attach to that submenu, respecting the native animal selection.
    for _, option in ipairs(context.options) do
        local animal = option.onHighlightParams and option.onHighlightParams[1]
        if isCat(animal) and not animal:isOnHook() and animal:isExistInTheWorld()
            and option.subOption then
            local menu = context:getSubMenu(option.subOption)
            if menu then
                addFood(playerObj, animal, menu)
                -- Report the actual loaded animal without weakening its pickup
                -- gate. Useful when an older saved cat lacks the native option.
                if not menu.ewingsAnimalsHandlingAdded then
                    menu.ewingsAnimalsHandlingAdded = true
                    local weight = animal:getData():getWeight()
                    local limit = 40 + 7 * playerObj:getPerkLevel(Perks.Strength)
                    local info = menu:addOption(getText("ContextMenu_EwingsAnimals_Handling",
                        string.format("%.2f", weight), tostring(limit)))
                    info.notAvailable = true
                    print("EwingsAnimals 0.1.2 handling type=" .. animal:getAnimalType()
                        .. " weight=" .. tostring(weight) .. " limit=" .. tostring(limit)
                        .. " pickup=" .. tostring(animal:canBePicked(playerObj))
                        .. " attach=" .. tostring(animal:getBehavior():canBeAttached())
                        .. " wild=" .. tostring(animal:isWild())
                        .. " animalCheat=" .. tostring(AnimalContextMenu.cheat))
                end
            end
        end
    end
end

Events.OnFillWorldObjectContextMenu.Add(fill)
