import asyncio

from xai_sdk import AsyncClient
from xai_sdk.chat import assistant, system, user

MODEL = "grok-4.3"


async def standalone_compaction():
    """Demonstrates client.chat.compact_context() on a pre-built message list."""
    client = AsyncClient()

    # Build a conversation: real content we care about, then thousands of tokens of filler
    # to demonstrate compaction savings.
    messages = [
        system("You are a concise and knowledgeable science tutor."),
        # === Important context we want preserved through compaction ===
        user("What is the Higgs boson and why is it important?"),
        assistant(
            "The Higgs boson is an elementary particle in the Standard Model of particle physics. "
            "It was predicted in 1964 by Peter Higgs and others, and confirmed experimentally in 2012 "
            "at CERN's Large Hadron Collider. It's important because it's the quantum excitation of the "
            "Higgs field, which gives mass to fundamental particles like quarks and leptons through the "
            "Higgs mechanism. Without the Higgs field, particles would be massless and atoms couldn't form."
        ),
        user("How does the Higgs mechanism actually work?"),
        assistant(
            "The Higgs mechanism works through spontaneous symmetry breaking. The Higgs field permeates "
            "all of space with a nonzero vacuum expectation value. As particles move through this field, "
            "they interact with it -- the stronger the interaction, the more mass the particle acquires. "
            "Think of it like moving through a crowd: a celebrity (strong interaction) gets slowed down "
            "more than an unknown person (weak interaction). Photons don't interact with the Higgs field "
            "at all, which is why they're massless and travel at the speed of light."
        ),
        # === Filler: many turns of trivia to bulk up the context ===
        user("Tell me about the history of the Roman Empire."),
        assistant(
            "The Roman Empire began in 27 BC when Octavian became Augustus, the first emperor. At its peak "
            "under Trajan around 117 AD, it stretched from Britain to Mesopotamia, encompassing the entire "
            "Mediterranean. The empire was characterized by its sophisticated legal system, engineering feats "
            "like aqueducts and roads, and a professional military. The western half fell in 476 AD when "
            "Romulus Augustulus was deposed by Odoacer. The eastern half, the Byzantine Empire, survived "
            "until Constantinople fell to the Ottoman Turks in 1453. Key emperors include Augustus, Trajan, "
            "Hadrian, Marcus Aurelius, Diocletian who split the empire, and Constantine who legalized "
            "Christianity. The Pax Romana, roughly 27 BC to 180 AD, was a period of relative peace and "
            "stability that allowed trade, culture, and infrastructure to flourish across the empire."
        ),
        user("What about the French Revolution?"),
        assistant(
            "The French Revolution began in 1789 with the storming of the Bastille and fundamentally "
            "transformed French society. Key causes included financial crisis from wars and royal "
            "extravagance, Enlightenment ideals challenging absolute monarchy, and widespread inequality "
            "under the Estates system. Major phases include the National Assembly period with the "
            "Declaration of the Rights of Man, the radical Jacobin phase under Robespierre and the Reign "
            "of Terror (1793-94) which saw thousands guillotined, the Thermidorian Reaction, and the "
            "Directory. It ended with Napoleon's coup in 1799. The revolution abolished feudalism, "
            "established civil equality, secularized the state, and inspired democratic movements "
            "worldwide. The metric system, the tricolor flag, and modern concepts of citizenship all "
            "originated from this period. Its legacy includes both the ideals of liberty, equality, "
            "and fraternity, and the cautionary tale of revolutionary violence."
        ),
        user("Explain photosynthesis in detail."),
        assistant(
            "Photosynthesis converts light energy into chemical energy in two main stages. The light-"
            "dependent reactions occur in the thylakoid membranes of chloroplasts. Chlorophyll and other "
            "pigments absorb photons, exciting electrons that pass through two photosystems (PSII and PSI) "
            "and an electron transport chain. Water molecules are split (photolysis), releasing oxygen as "
            "a byproduct. This process generates ATP via chemiosmosis and NADPH. The light-independent "
            "reactions (Calvin cycle) occur in the stroma. CO2 is fixed by RuBisCO onto ribulose "
            "bisphosphate (RuBP), forming 3-phosphoglycerate (3-PGA). ATP and NADPH from the light "
            "reactions reduce 3-PGA to glyceraldehyde-3-phosphate (G3P). Most G3P is recycled to "
            "regenerate RuBP, while some exits to form glucose and other organic molecules. The overall "
            "equation is 6CO2 + 6H2O + light -> C6H12O6 + 6O2. C4 and CAM plants have evolved "
            "modifications to reduce photorespiration in hot, dry environments."
        ),
        user("How do black holes form?"),
        assistant(
            "Black holes form primarily through stellar collapse. When a massive star (roughly 20+ solar "
            "masses) exhausts its nuclear fuel, radiation pressure can no longer support the core against "
            "gravity. The core collapses in milliseconds -- if the remnant exceeds the Tolman-Oppenheimer-"
            "Volkoff limit (about 2-3 solar masses), neutron degeneracy pressure fails and the core "
            "collapses into a singularity surrounded by an event horizon. This often produces a supernova "
            "explosion of the outer layers. Supermassive black holes (millions to billions of solar masses) "
            "at galactic centers likely formed through mergers and accretion over billions of years, though "
            "their exact origin is debated. Intermediate-mass black holes may form in dense star clusters "
            "through runaway collisions. The event horizon radius (Schwarzschild radius) equals 2GM/c^2. "
            "Nothing, not even light, can escape from within the event horizon. Hawking radiation "
            "theoretically causes black holes to slowly evaporate, though this is negligible for "
            "stellar-mass and larger black holes."
        ),
        user("Describe the water cycle."),
        assistant(
            "The water cycle, or hydrological cycle, continuously moves water through Earth's systems. "
            "Evaporation converts surface water from oceans, lakes, and rivers into vapor using solar "
            "energy -- oceans contribute about 86% of atmospheric moisture. Transpiration releases water "
            "vapor from plant leaves through stomata. Together these are called evapotranspiration. Warm, "
            "moist air rises and cools adiabatically, reaching the dew point where condensation forms "
            "clouds on condensation nuclei (dust, pollen, sea salt). Precipitation occurs when cloud "
            "droplets coalesce (warm clouds) or ice crystals grow at the expense of supercooled droplets "
            "(cold clouds, the Bergeron process). Water returns to the surface as rain, snow, sleet, or "
            "hail. On land, some water infiltrates soil (percolation) recharging groundwater aquifers. "
            "Surface runoff flows into streams and rivers, eventually returning to oceans. Groundwater "
            "moves slowly through aquifers and can discharge into springs, rivers, or directly into the "
            "ocean. The cycle is driven by solar energy and gravity. Human activities like deforestation, "
            "urbanization, and groundwater pumping significantly alter local water cycles."
        ),
        user("Tell me about the periodic table."),
        assistant(
            "The periodic table organizes 118 known elements by atomic number (proton count). Dmitri "
            "Mendeleev published the first widely recognized version in 1869, arranging elements by "
            "atomic weight and predicting undiscovered elements. The modern table has 7 periods (rows) "
            "and 18 groups (columns). Elements in the same group share similar chemical properties due "
            "to identical valence electron configurations. Groups include alkali metals (1), alkaline "
            "earth metals (2), halogens (17), and noble gases (18). The table is divided into s-block "
            "(groups 1-2), p-block (13-18), d-block (3-12, transition metals), and f-block (lanthanides "
            "and actinides). Trends across periods include increasing electronegativity, ionization "
            "energy, and electron affinity from left to right, and decreasing atomic radius. Down groups, "
            "atomic radius increases, ionization energy decreases, and metallic character increases. "
            "Elements 1-94 occur naturally; 95-118 are synthetic, created in particle accelerators. "
            "Oganesson (118) is the heaviest element synthesized to date."
        ),
        user("How does the immune system work?"),
        assistant(
            "The immune system has innate and adaptive components. The innate immune system provides "
            "immediate, non-specific defense: physical barriers (skin, mucous membranes), chemical "
            "barriers (stomach acid, lysozyme in tears), and cellular responses from neutrophils, "
            "macrophages, dendritic cells, and natural killer cells. These recognize pathogen-associated "
            "molecular patterns (PAMPs) via pattern recognition receptors (PRRs) like Toll-like receptors. "
            "Inflammation recruits immune cells to infection sites through cytokine signaling. The "
            "complement system, a cascade of plasma proteins, directly lyses pathogens and marks them for "
            "phagocytosis (opsonization). The adaptive immune system is specific and develops memory. "
            "T cells mature in the thymus: helper T cells (CD4+) coordinate responses, cytotoxic T cells "
            "(CD8+) kill infected cells, and regulatory T cells suppress excessive responses. B cells "
            "produce antibodies (immunoglobulins) that neutralize pathogens, activate complement, and "
            "facilitate phagocytosis. After infection, memory B and T cells persist for years, enabling "
            "faster responses to reinfection -- this is the basis of vaccination."
        ),
        user("Explain plate tectonics."),
        assistant(
            "Plate tectonics describes Earth's lithosphere as divided into about 15 major and several "
            "minor plates that float on the semi-fluid asthenosphere. Convection currents in the mantle, "
            "driven by radioactive decay heating, move plates at 1-15 cm/year. At divergent boundaries "
            "(mid-ocean ridges), plates separate and new crust forms from upwelling magma -- the Mid-"
            "Atlantic Ridge creates about 2.5 cm of new crust annually. At convergent boundaries, denser "
            "oceanic crust subducts beneath continental or other oceanic crust, forming deep trenches "
            "(Mariana Trench, 11 km deep), volcanic arcs (Ring of Fire), and mountain ranges (Himalayas "
            "from India-Eurasia collision). Transform boundaries involve lateral sliding (San Andreas "
            "Fault). Evidence for plate tectonics includes matching coastlines (South America and Africa), "
            "fossil distributions, paleomagnetic striping on the ocean floor, and GPS measurements of "
            "plate motion. Earthquakes concentrate at plate boundaries. Hotspot volcanism (Hawaii, "
            "Yellowstone) occurs over mantle plumes independent of plate boundaries."
        ),
    ]

    print(f"Original conversation: {len(messages)} messages")
    print("=" * 60)

    # Create a chat and load the conversation history.
    chat = client.chat.create(model=MODEL, use_encrypted_content=True, messages=messages)

    # Compact the conversation in-place. The server will drop everything
    # before the compaction blob on the next request.
    compaction = await chat.compact()

    print(f"Compaction ID:      {compaction.id}")
    print(f"Dropped messages:   {compaction.dropped_message_count}")
    print(f"Usage:              {compaction.usage}")
    print("=" * 60)

    # Ask a question that requires the compacted context to answer.
    chat.append(user("Based on our earlier conversation, what gives particles their mass?"))
    response = await chat.sample()

    print("\n--- Follow-up using compacted context ---")
    print(f"Grok: {response.content}")
    print(f"\nFollow-up prompt tokens:     {response.usage.prompt_tokens}")
    print(f"Follow-up completion tokens: {response.usage.completion_tokens}")
    print(f"Follow-up total tokens:      {response.usage.total_tokens}")

    # Ask a second follow-up to verify multi-turn still works on top of compacted context.
    chat.append(response)
    chat.append(user("And who predicted that particle?"))
    response2 = await chat.sample()

    print("\n--- Second follow-up ---")
    print(f"Grok: {response2.content}")


async def in_place_compaction():
    """Demonstrates periodic chat.compact() inside a multi-turn conversation loop."""
    client = AsyncClient()
    compact_every = 5

    chat = client.chat.create(model=MODEL, use_encrypted_content=True)
    chat.append(system("You are a helpful assistant. Keep answers brief."))

    turns = 0
    while True:
        prompt = input("You: ")
        if prompt.lower() == "exit":
            break

        chat.append(user(prompt))
        response = await chat.sample()
        print(f"Grok: {response.content}")
        chat.append(response)
        turns += 1

        if turns % compact_every == 0:
            print("\nCompacting conversation...")
            before = len(chat.messages)
            compact = await chat.compact()
            print(
                f"\n  [compacted {before} messages -> {len(chat.messages)} | "
                f"dropped {compact.dropped_message_count} | "
                f"tokens used: {compact.usage.total_tokens}]\n"
            )


if __name__ == "__main__":
    # Uncomment the respective line to run the example.
    asyncio.run(standalone_compaction())
    # asyncio.run(in_place_compaction())
