"""
Generate a CSV of items matching the Chronicle Keeper `items` schema.
Run with the project's venv python to produce `chronicle-keeper/data/items.csv`.

Columns (CSV): sku,name,description,category,sub_type,weight,stackable,max_stack,equippable,equip_slot,damage_min,damage_max,armor_rating,durability_max,consumable,charges_max,effects,tags
"""
import csv
import json
import random
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / 'data' / 'items.csv'
OUT.parent.mkdir(parents=True, exist_ok=True)

NUM = 10000
SEED = 42
random.seed(SEED)

categories = {
    'tool': [
        ('wrench','Wrench'), ('hammer','Hammer'), ('crowbar','Crowbar'), ('rope','Rope'), ('shovel','Shovel'),
        ('lockpick_set','Lockpick Set'), ('multitool','Multitool'), ('screwdriver','Screwdriver'), ('pliers','Pliers'),
        ('torch','Torch'), ('lantern','Lantern'), ('flashlight','Flashlight'), ('matchbox','Matchbox'), ('firestarter','Flint & Steel'), ('headlamp','Headlamp'), ('lantern_oil','Lantern Oil'),
        ('pickaxe','Pickaxe'), ('tongs','Tongs'), ('grinder','Grinder'), ('calipers','Calipers'), ('lantern_stand','Lantern Stand'),
        ('oil_can','Oil Can'), ('battery_pack','Battery Pack'), ('signal_flare','Signal Flare'), ('multimeter','Multimeter'), ('soldering_iron','Soldering Iron'),
        ('vise','Vise'), ('auger','Auger'), ('chisels','Chisels'), ('bolt_cutters','Bolt Cutters'), ('pipe_wrench','Pipe Wrench'),
        ('hydrant_key','Hydrant Key'), ('pressure_gauge','Pressure Gauge'), ('winch','Winch'), ('chain','Chain'), ('jerrycan','Jerrycan'),
        ('ratchet','Ratchet'), ('allen_key','Allen Key'), ('wire_cutters','Wire Cutters'), ('heat_gun','Heat Gun'), ('pressure_washer','Pressure Washer'),
        ('saw','Saw'), ('plane','Plane'), ('file_set','File Set'), ('tape_measure','Tape Measure'), ('level','Level'),
        ('safety_goggles','Safety Goggles'), ('work_gloves','Work Gloves'), ('hose','Hose'), ('crowbar_small','Small Prybar'), ('hand_drill','Hand Drill'),
        ('bench_vise','Bench Vise'), ('calibration_kit','Calibration Kit'), ('glass_cutter','Glass Cutter'), ('staple_gun','Staple Gun'), ('bolt_set','Bolt Set'),('hand_saw','Hand Saw'),
('masonry_hammer','Masonry Hammer'),
('sledgehammer','Sledgehammer'),
('crowbar_heavy','Heavy Prybar'),
('folding_shovel','Folding Shovel'),
('ice_axe','Ice Axe'),
('climbing_pitons','Climbing Pitons'),
('carabiner_set','Carabiner Set'),
('pulley_block','Pulley Block'),
('rope_ladder','Rope Ladder'),

('wire_brush','Wire Brush'),
('steel_brush','Steel Brush'),
('mallet','Mallet'),
('rubber_mallet','Rubber Mallet'),
('hand_axe','Hand Axe'),
('hatchet','Hatchet'),
('wood_chisel','Wood Chisel'),
('metal_file','Metal File'),
('rasp','Rasp'),
('hand_plane_small','Small Hand Plane'),

('trowel','Trowel'),
('brick_jointer','Brick Jointer'),
('spirit_level_long','Long Level'),
('chalk_line','Chalk Line'),
('utility_knife','Utility Knife'),
('box_cutter','Box Cutter'),
('measuring_wheel','Measuring Wheel'),
('compass_tool','Drafting Compass'),
('square_ruler','Square Ruler'),
('clamp_set','Clamp Set'),

('vise_grip','Vise Grip'),
('pipe_cutter','Pipe Cutter'),
('tube_bender','Tube Bender'),
('siphon_pump','Siphon Pump'),
('funnel_set','Funnel Set'),
('grease_gun','Grease Gun'),
('welding_mask','Welding Mask'),
('welding_gloves','Welding Gloves'),
('solder_wire','Solder Wire'),
('heat_resistant_mat','Heat-Resistant Mat'),

('hand_crank_generator','Hand Crank Generator'),
('extension_cord','Extension Cord'),
('toolbox','Toolbox'),
('organizer_case','Organizer Case'),
('magnet_pickup','Magnetic Pickup Tool'),
('stud_finder','Stud Finder'),
('inspection_mirror','Inspection Mirror'),
('telescoping_magnet','Telescoping Magnet'),
('endoscope_cam','Inspection Scope'),
('portable_anvil','Portable Anvil')

    ],
    'clothing': [
        ('cap','Cap'), ('boots','Boots'), ('gloves','Gloves'), ('cloak','Cloak'), ('pants','Trousers'), ('shirt','Shirt'),
        ('socks','Socks'), ('vest','Vest'), ('sandals','Sandals'), ('hood','Hood'), ('bandana','Bandana'), ('gaiters','Gaiters'),
        ('undershirt','Undershirt'), ('overcoat','Overcoat'), ('gloves_fine','Fine Gloves'), ('armor_padding','Armor Padding'), ('lining','Lining'),
        ('stockings','Stockings'), ('apron','Apron'), ('tunic','Tunic'), ('jersey','Jersey'), ('overalls','Overalls'), ('petticoat','Petticoat'),
        ('smock','Smock'), ('muffler','Muffler'), ('armwraps','Armwraps'), ('legwraps','Legwraps'), ('belt','Belt'), ('cape','Cape'),
        ('scarf','Scarf'), ('pajamas','Pajamas'), ('cloak_heavy','Heavy Cloak'), ('raincoat','Raincoat'), ('swimsuit','Swimsuit'),
        ('sports_shoes','Sports Shoes'), ('insoles','Insoles'), ('belt_simple','Simple Belt'), ('glove_liner','Glove Liner'), ('ear_muffs','Ear Muffs'),
        ('visor','Visor'), ('suspenders','Suspenders'), ('wristband','Wristband'), ('cap_wool','Wool Cap'), ('hoodie','Hoodie'),
        ('leggings','Leggings'), ('shorts','Shorts'), ('underpants','Underpants'), ('sweater','Sweater'), ('polo_shirt','Polo Shirt'),('coat_light','Light Coat'),
('coat_fur','Fur Coat'),
('jacket','Jacket'),
('jacket_leather','Leather Jacket'),
('parka','Parka'),
('windbreaker','Windbreaker'),
('poncho','Poncho'),
('tabard','Tabard'),
('surcoat','Surcoat'),
('doublet','Doublet'),

('mittens','Mittens'),
('gauntlets_cloth','Cloth Gauntlets'),
('gauntlets_leather','Leather Gauntlets'),
('armwarmers','Arm Warmers'),
('legwarmers','Leg Warmers'),
('handwraps','Handwraps'),
('neck_wrap','Neck Wrap'),
('shawl','Shawl'),
('wrap_skirt','Wrap Skirt'),
('skirt','Skirt'),

('robe','Robe'),
('robe_heavy','Heavy Robe'),
('kimono','Kimono'),
('sarong','Sarong'),
('kaftan','Kaftan'),
('toga','Toga'),
('bodice','Bodice'),
('corset','Corset'),
('tabi','Tabi Socks'),
('slippers','Slippers'),

('work_shirt','Work Shirt'),
('dress_shirt','Dress Shirt'),
('tank_top','Tank Top'),
('longcoat','Longcoat'),
('trenchcoat','Trench Coat'),
('thermal_shirt','Thermal Shirt'),
('thermal_pants','Thermal Pants'),
('rain_pants','Rain Pants'),
('cargo_pants','Cargo Pants'),
('jeans','Jeans'),

('beanie','Beanie'),
('sun_hat','Sun Hat'),
('straw_hat','Straw Hat'),
('beret','Beret'),
('headband','Headband'),
('face_mask','Face Mask'),
('balaclava','Balaclava'),
('neck_gaiter','Neck Gaiter'),
('ankle_wraps','Ankle Wraps'),
('toe_socks','Toe Socks')

    ],
    'jewelry': [
        ('ring','Ring'), ('necklace','Necklace'), ('bracelet','Bracelet'), ('earring','Earring'), ('amulet','Amulet'),
        ('pendant','Pendant'), ('signet','Signet Ring'), ('brooch','Brooch'), ('torc','Torc'), ('charm','Charm'),
        ('circlet','Circlet'), ('toe_ring','Toe Ring'), ('hairpin','Hairpin'), ('locket','Locket'), ('chain','Chain'),
        ('hair_chain','Hair Chain'), ('ear_cuff','Ear Cuff'), ('bead_necklace','Bead Necklace'), ('metal_pin','Metal Pin'), ('shell_pendant','Shell Pendant'),
        ('gem_chain','Gem Chain'), ('meteor_shard','Meteor Shard'), ('mini_locket','Mini Locket'), ('small_signet','Small Signet'), ('stud','Stud'),
        ('drop_earring','Drop Earring'), ('hoop_earring','Hoop Earring'), ('anklet','Anklet'), ('choker','Choker'), ('wrist_cuff','Wrist Cuff'),
        ('decorative_brooch','Decorative Brooch'), ('simple_pendant','Simple Pendant'), ('layered_chain','Layered Chain'), ('medallion_locket','Medallion Locket'), ('signet_band','Signet Band'),
        ('simple_circlet','Simple Circlet'), ('small_hair_chain','Small Hair Chain'), ('ear_threader','Ear Threader'), ('lariat_necklace','Lariat Necklace'), ('pin_brooch','Pin Brooch'),('bangle','Bangle'),
('armlet','Armlet'),
('armband','Armband'),
('upper_arm_cuff','Upper Arm Cuff'),
('wrist_chain','Wrist Chain'),
('wrist_wrap','Wrist Wrap'),
('bracelet_beaded','Beaded Bracelet'),
('bracelet_metal','Metal Bracelet'),
('bracelet_woven','Woven Bracelet'),
('bracelet_charm','Charm Bracelet'),

('gem_ring','Gem Ring'),
('band_plain','Plain Band'),
('band_engraved','Engraved Band'),
('ring_twisted','Twisted Ring'),
('ring_wire','Wire Ring'),
('ring_double','Double Band Ring'),
('ring_stone','Stone Ring'),
('ring_inlay','Inlay Ring'),
('ring_plated','Plated Ring'),
('ring_spiral','Spiral Ring'),

('necklace_chain_fine','Fine Chain Necklace'),
('necklace_woven','Woven Necklace'),
('necklace_charm','Charm Necklace'),
('necklace_gemstone','Gemstone Necklace'),
('gorget_simple','Simple Gorget'),
('gorget_decorative','Decorative Gorget'),
('torc_simple','Simple Torc'),
('torc_heavy','Heavy Torc'),
('collar_metal','Metal Collar'),
('collar_soft','Soft Collar'),

('ear_stud_gem','Gem Stud'),
('ear_hook','Ear Hook'),
('ear_chain','Ear Chain'),
('ear_drop_gem','Gem Drop Earring'),
('ear_spiral','Spiral Earring'),
('ear_clasp','Ear Clasp'),
('ear_wrap','Ear Wrap'),
('ear_dangle','Dangle Earring'),
('ear_leaf','Leaf Earring'),
('ear_knot','Knot Earring'),

('hair_comb','Hair Comb'),
('hair_spiral','Hair Spiral'),
('hair_band','Hair Band'),
('hair_clip','Hair Clip'),
('hair_clasp','Hair Clasp'),
('hair_crown','Hair Crown'),
('diadem','Diadem'),
('tiara','Tiara'),
('nose_ring','Nose Ring'),
('nose_stud','Nose Stud')

    ],
    'armor': [
        ('leather_armor','Leather Armor'), ('chainmail','Chainmail'), ('plate_armor','Plate Armor'), ('helmet','Helmet'), ('shield','Shield'),
        ('greaves','Greaves'), ('vambraces','Vambraces'), ('cuirass','Cuirass'), ('gauntlets','Gauntlets'), ('pauldrons','Pauldrons'),
        ('bracers','Bracers'), ('leggings','Leggings'), ('boots_heavy','Heavy Boots'), ('gorget','Gorget'), ('belt_armor','Armor Belt'),
        ('scale_mail','Scale Mail'), ('lamellar','Lamellar'), ('brigandine','Brigandine'), ('tassets','Tassets'), ('sabatons','Sabatons'),
        ('chain_hood','Chain Hood'), ('shield_spike','Shield Spike'), ('reinforced_plate','Reinforced Plate'), ('mob_cap','Mob Cap'), ('armored_boots','Armored Boots'),
        ('bracer_small','Small Bracer'), ('knee_pad','Knee Pad'), ('elbow_pad','Elbow Pad'), ('cuir_belt','Cuirass Belt'), ('scale_gauntlet','Scale Gauntlet'),
        ('chain_boots','Chain Boots'), ('reinforced_gloves','Reinforced Gloves'), ('padded_jerkin','Padded Jerkin'), ('lamellar_girdle','Lamellar Girdle'), ('plate_greave','Plate Greave'),('buckler','Buckler'),
('tower_shield','Tower Shield'),
('kite_shield','Kite Shield'),
('heater_shield','Heater Shield'),
('round_shield','Round Shield'),
('reinforced_shield','Reinforced Shield'),
('shield_boss','Shield Boss'),
('shield_rim','Shield Rim'),

('helm_open','Open Helm'),
('helm_closed','Closed Helm'),
('greathelm','Greathelm'),
('barbute','Barbute'),
('sallet','Sallet'),
('kettle_helm','Kettle Helm'),
('visor_helm','Visored Helm'),
('hood_padded','Padded Hood'),

('breastplate','Breastplate'),
('backplate','Backplate'),
('plackart','Plackart'),
('faulds','Faulds'),
('cuisses','Cuisses'),
('poleyns','Poleyns'),
('rerebrace','Rerebrace'),
('spauldron','Spauldron'),

('mail_coif','Mail Coif'),
('mail_shirt','Mail Shirt'),
('mail_gloves','Mail Gloves'),
('mail_leggings','Mail Leggings'),
('mail_collar','Mail Collar'),
('mail_sleeves','Mail Sleeves'),

('gambeson','Gambeson'),
('quilted_jacket','Quilted Jacket'),
('padded_coif','Padded Coif'),
('padded_gloves','Padded Gloves'),
('padded_boots','Padded Boots'),
('padded_pants','Padded Pants'),

('scale_hood','Scale Hood'),
('scale_vest','Scale Vest'),
('scale_boots','Scale Boots'),
('scale_belt','Scale Belt'),

('brigandine_vest','Brigandine Vest'),
('brigandine_gloves','Brigandine Gloves'),
('brigandine_skirt','Brigandine Skirt'),

('armored_cape','Armored Cape'),
('armored_tabard','Armored Tabard'),
('armored_kilt','Armored Kilt'),
('armored_mask','Armored Mask')
    ],
    'weapon': [
        ('shortsword','Shortsword'), ('longsword','Longsword'), ('dagger','Dagger'), ('bow','Bow'), ('crossbow','Crossbow'),
        ('spear','Spear'), ('mace','Mace'), ('axe','Axe'), ('rapier','Rapier'), ('halberd','Halberd'), ('warhammer','Warhammer'), ('kukri','Kukri'),
        ('throwing_axe','Throwing Axe'), ('sling','Sling'), ('blowgun','Blowgun'), ('chakram','Chakram'), ('whip','Whip'), ('club','Club'),
        ('morning_star','Morning Star'), ('estoc','Estoc'), ('fauchard','Fauchard'), ('pellet_gun','Pellet Gun'), ('net','Net'),
        ('spike_thrower','Spike Thrower'), ('harpoon','Harpoon'), ('saber','Saber'), ('scimitar','Scimitar'), ('poleaxe','Poleaxe'),
        ('spear_short','Short Spear'), ('pike','Pike'), ('fighting_knife','Fighting Knife'), ('hatchet','Hatchet'), ('kukri_small','Kukri Small'),
        ('club_heavy','Heavy Club'), ('caster_staff','Caster Staff'), ('throwing_knife','Throwing Knife'), ('net_launcher','Net Launcher'), ('bola','Bola'),
        ('dart','Dart'), ('piercer','Piercer'), ('trident','Trident'), ('war_club','War Club'), ('sai','Sai'),('broadsword','Broadsword'),
('greatsword','Greatsword'),
('claymore','Claymore'),
('falchion','Falchion'),
('cutlass','Cutlass'),
('gladius','Gladius'),
('scythe_war','War Scythe'),
('bardiche','Bardiche'),
('glaive','Glaive'),
('naginata','Naginata'),

('katana','Katana'),
('wakizashi','Wakizashi'),
('tanto','Tanto'),
('jian','Jian'),
('dao','Dao'),
('kris','Kris'),
('stiletto','Stiletto'),
('dirk','Dirk'),
('parrying_dagger','Parrying Dagger'),
('push_dagger','Push Dagger'),

('hand_crossbow','Hand Crossbow'),
('recurve_bow','Recurve Bow'),
('longbow','Longbow'),
('shortbow','Shortbow'),
('sling_staff','Sling Staff'),
('javelin','Javelin'),
('atlatl','Atlatl'),
('throwing_spear','Throwing Spear'),
('bolas_heavy','Heavy Bolas'),
('weighted_net','Weighted Net'),

('quarterstaff','Quarterstaff'),
('bo_staff','Bo Staff'),
('iron_staff','Iron Staff'),
('shillelagh','Shillelagh'),
('cudgel','Cudgel'),
('maul','Maul'),
('flail','Flail'),
('chain_whip','Chain Whip'),
('meteor_hammer','Meteor Hammer'),
('rope_dart','Rope Dart'),

('hand_cannon','Hand Cannon'),
('pepperbox','Pepperbox'),
('air_rifle','Air Rifle'),
('dart_launcher','Dart Launcher'),
('hook_sword','Hook Sword'),
('twin_sai','Twin Sai'),
('spiked_shield','Spiked Shield'),
('war_pick','War Pick'),
('hammer_throw','Throwing Hammer'),
('ice_axe_weapon','Ice Axe Weapon')

    ],
    'fantasy': [
        ('wand','Wand'), ('spellbook','Spellbook'), ('dragon_scale','Dragon Scale'), ('rune_stone','Rune Stone'), ('potion','Potion'),
        ('orb','Orb'), ('talisman','Talisman'), ('sigil','Sigil'), ('phylactery','Phylactery'), ('chalice','Chalice'),
        ('banner','Banner'), ('gemstone','Gemstone'), ('enchanted_cloth','Enchanted Cloth'), ('scepter','Scepter'), ('amulet_major','Major Amulet'),
        ('philter','Philter'), ('enchanted_gem','Enchanted Gem'), ('mystic_rune','Mystic Rune'), ('binding_stone','Binding Stone'), ('seer_eye','Seer Eye'),
        ('etheric_band','Etheric Band'), ('soul_shard','Soul Shard'), ('astral_chart','Astral Chart'), ('driftwood_totem','Driftwood Totem'), ('void_essence','Void Essence'),
        ('enchanted_thread','Enchanted Thread'), ('lesser_talisman','Lesser Talisman'), ('fey_seed','Fey Seed'), ('mystic_orb_small','Mystic Orb Small'), ('bottled_stars','Bottled Stars'),
        ('herbal_concoction','Herbal Concoction'), ('rune_pouch','Rune Pouch'), ('celestial_scroll','Celestial Scroll'), ('soul_amber','Soul Amber'), ('spirit_jar','Spirit Jar'),('arcane_focus','Arcane Focus'),
('mana_crystal','Mana Crystal'),
('eldritch_tome','Eldritch Tome'),
('spirit_totem','Spirit Totem'),
('astral_lantern','Astral Lantern'),
('ether_vial','Ether Vial'),
('mana_vessel','Mana Vessel'),
('arcane_relic','Arcane Relic'),
('mystic_focus','Mystic Focus'),
('sigil_fragment','Sigil Fragment'),

('ancient_tablet','Ancient Tablet'),
('forgotten_idol','Forgotten Idol'),
('runic_tablet','Runic Tablet'),
('eldritch_shard','Eldritch Shard'),
('arcane_seal','Arcane Seal'),
('binding_scroll','Binding Scroll'),
('ritual_candle','Ritual Candle'),
('ritual_ink','Ritual Ink'),
('ritual_bowl','Ritual Bowl'),
('ritual_mask','Ritual Mask'),

('fae_charm','Fae Charm'),
('fae_dust','Fae Dust'),
('fae_bloom','Fae Bloom'),
('spirit_feather','Spirit Feather'),
('wyrm_tooth','Wyrm Tooth'),
('phoenix_ash','Phoenix Ash'),
('shadow_petals','Shadow Petals'),
('moonwater','Moonwater'),
('sunstone','Sunstone'),
('starshard','Starshard'),

('eldritch_core','Eldritch Core'),
('arcane_conduit','Arcane Conduit'),
('mana_thread','Mana Thread'),
('ether_thread','Ether Thread'),
('astral_ink','Astral Ink'),
('soul_thread','Soul Thread'),
('dreamcatcher','Dreamcatcher'),
('memory_crystal','Memory Crystal'),
('echo_stone','Echo Stone'),
('whisper_orb','Whisper Orb'),

('spirit_tether','Spirit Tether'),
('void_fragment','Void Fragment'),
('planar_key','Planar Key'),
('rift_anchor','Rift Anchor'),
('celestial_compass','Celestial Compass'),
('astral_compass','Astral Compass'),
('eldritch_vessel','Eldritch Vessel'),
('arcane_lens','Arcane Lens'),
('mystic_vial','Mystic Vial'),
('etheric_scroll','Etheric Scroll')

    ],
    'sci_fi': [
        ('laser_pistol','Laser Pistol'), ('plasma_rifle','Plasma Rifle'), ('energy_cell','Energy Cell'), ('nano_kit','Nano Repair Kit'), ('grappler','Grappler'),
        ('stabilizer','Stabilizer'), ('sensor_array','Sensor Array'), ('plasma_cell','Plasma Cell'), ('flux_coil','Flux Coil'), ('holo_chip','Holo Chip'),
        ('nanobot_canister','Nanobot Canister'), ('thermal_pad','Thermal Pad'), ('stealth_field','Stealth Field'), ('ai_core','AI Core'), ('quantum_regulator','Quantum Regulator'),
        ('gyro_stabilizer','Gyro Stabilizer'), ('ion_emitter','Ion Emitter'), ('subspace_filter','Subspace Filter'), ('plasma_valve','Plasma Valve'), ('cryocell','Cryo Cell'),
        ('bio_patch','Bio Patch'), ('servo_motor','Servo Motor'), ('optic_lens','Optic Lens'), ('data_tether','Data Tether'), ('phase_shifter','Phase Shifter'),
        ('charger_unit','Charger Unit'), ('data_chip_small','Data Chip Small'), ('sensor_beacon','Sensor Beacon'), ('fusion_core','Fusion Core'), ('plasma_tube','Plasma Tube'),
        ('optic_sensor','Optic Sensor'), ('magnet_ring','Magnet Ring'), ('biolock_patch','Biolock Patch'), ('nano_fabric','Nano Fabric'), ('field_emitter','Field Emitter'),('ion_pistol','Ion Pistol'),
('plasma_cutter','Plasma Cutter'),
('railgun_carbine','Railgun Carbine'),
('coil_pistol','Coil Pistol'),
('arc_blade','Arc Blade'),
('vibro_knife','Vibro Knife'),
('vibro_sword','Vibro Sword'),
('shock_baton','Shock Baton'),
('pulse_grenade','Pulse Grenade'),
('emp_grenade','EMP Grenade'),

('quantum_battery','Quantum Battery'),
('micro_reactor','Micro Reactor'),
('dark_matter_cell','Dark Matter Cell'),
('antimatter_vial','Antimatter Vial'),
('fusion_capacitor','Fusion Capacitor'),
('ion_capacitor','Ion Capacitor'),
('phase_core','Phase Core'),
('tachyon_module','Tachyon Module'),
('gravity_core','Gravity Core'),
('neutrino_cell','Neutrino Cell'),

('holo_projector','Holo Projector'),
('holo_emitter','Holo Emitter'),
('quantum_drive','Quantum Drive'),
('warp_stabilizer','Warp Stabilizer'),
('subspace_anchor','Subspace Anchor'),
('gravity_manipulator','Gravity Manipulator'),
('atmos_filter','Atmospheric Filter'),
('bio_scanner','Bio Scanner'),
('quantum_scanner','Quantum Scanner'),
('spectral_scanner','Spectral Scanner'),

('nanite_swarm','Nanite Swarm'),
('nanite_injector','Nanite Injector'),
('nano_weave','Nano Weave'),
('nano_patch','Nano Patch'),
('adaptive_plating','Adaptive Plating'),
('phase_armor','Phase Armor'),
('kinetic_barrier','Kinetic Barrier'),
('energy_shield','Energy Shield'),
('personal_deflector','Personal Deflector'),
('thermal_shield','Thermal Shield'),

('data_core','Data Core'),
('quantum_key','Quantum Key'),
('logic_matrix','Logic Matrix'),
('neural_link','Neural Link'),
('psi_amplifier','Psi Amplifier'),
('psi_resonator','Psi Resonator'),
('chrono_chip','Chrono Chip'),
('temporal_anchor','Temporal Anchor'),
('void_drive','Void Drive'),
('stellar_map','Stellar Map')

    ],
    'survival': [
        ('bandage','Bandage'), ('medkit','Medkit'), ('water_flask','Water Flask'), ('ration_pack','Ration Pack'), ('herb_bundle','Herb Bundle'), ('poison_vial','Poison Vial'),
        ('compass','Compass'), ('tent','Tent'), ('blanket','Blanket'), ('fishing_kit','Fishing Kit'), ('signal_whistle','Signal Whistle'), ('tinder','Tinder'), ('water_purifier','Water Purifier'), ('sewing_kit','Sewing Kit'), ('climbing_rope','Climbing Rope'), ('emergency_beacon','Emergency Beacon'),
        ('canteen','Canteen'), ('survival_manual','Survival Manual'), ('mosquito_net','Mosquito Net'), ('water_bag','Water Bag'), ('stove','Portable Stove'),
        ('lantern_replace','Lantern Wick'), ('seasonal_kit','Seasonal Kit'), ('weather_foil','Weather Foil'), ('ice_picks','Ice Picks'), ('thermal_suit','Thermal Suit'),
        ('solar_blanket','Solar Blanket'), ('portable_filter','Portable Filter'), ('snow_shoes','Snow Shoes'), ('fire_starter_kit','Fire Starter Kit'), ('signal_mirror','Signal Mirror'),
        ('heat_pack','Heat Pack'), ('signal_rocket','Signal Rocket'), ('machete','Machete'), ('camp_stove','Camp Stove'), ('survival_rope','Survival Rope'),('first_aid_kit','First Aid Kit'),
('splint','Splint'),
('antiseptic_wipes','Antiseptic Wipes'),
('tourniquet','Tourniquet'),
('herbal_salve','Herbal Salve'),
('pain_relief_vial','Pain Relief Vial'),
('water_test_kit','Water Test Kit'),
('iodine_tablets','Iodine Tablets'),
('emergency_bandage','Emergency Bandage'),
('suture_kit','Suture Kit'),

('hand_warmers','Hand Warmers'),
('thermal_blanket','Thermal Blanket'),
('rain_tarp','Rain Tarp'),
('ground_sheet','Ground Sheet'),
('sleeping_bag','Sleeping Bag'),
('sleeping_pad','Sleeping Pad'),
('camp_chair','Camp Chair'),
('camp_hammer','Camp Hammer'),
('tent_poles','Tent Poles'),
('tent_repair_kit','Tent Repair Kit'),

('flint_block','Flint Block'),
('fire_gel','Fire Gel'),
('charcloth','Charcloth'),
('kindling_bundle','Kindling Bundle'),
('windproof_lighter','Windproof Lighter'),
('storm_matches','Storm Matches'),
('torch_oil','Torch Oil'),
('camp_lantern','Camp Lantern'),
('glow_stick','Glow Stick'),
('flare_stick','Flare Stick'),

('map_case','Map Case'),
('topo_map','Topographic Map'),
('altimeter','Altimeter'),
('handheld_radio','Handheld Radio'),
('signal_flag','Signal Flag'),
('trail_markers','Trail Markers'),
('survival_whistle','Survival Whistle'),
('navigation_beads','Navigation Beads'),
('rangefinder','Rangefinder'),
('binoculars','Binoculars'),

('camp_pot','Camp Pot'),
('canteen_cup','Canteen Cup'),
('mess_kit','Mess Kit'),
('food_canister','Food Canister'),
('dry_rations','Dry Rations'),
('water_bladders','Water Bladders'),
('foraging_guide','Foraging Guide'),
('snare_wire','Snare Wire'),
('hand_saw','Hand Saw'),
('folding_spade','Folding Spade')
    ],
    'crafting': [
        ('ore','Ore'), ('ingot','Ingot'), ('cloth','Cloth'), ('leather','Leather'), ('wood_bundle','Wood Bundle'), ('reagent','Alchemy Reagent'),
        ('thread','Thread'), ('glue','Glue'), ('nails','Nails'), ('plank','Plank'), ('gear','Gear'), ('wire','Wire'), ('polymer_sheet','Polymer Sheet'), ('circuit_board','Circuit Board'), ('binding_agent','Binding Agent'), ('dye','Dye'),
        ('acetone','Acetone'), ('resin_powder','Resin Powder'), ('lathe_part','Lathe Part'), ('mold','Mold'), ('adhesive','Adhesive'),
        ('filament','Filament'), ('leather_patch','Leather Patch'), ('bone_fragment','Bone Fragment'), ('veneer','Veneer'), ('casting_sand','Casting Sand'),
        ('mortar_pestle','Mortar & Pestle'), ('anvil','Anvil'), ('forge_coal','Forge Coal'), ('heat_resin','Heat Resin'), ('lathe_bed','Lathe Bed'),
        ('wire_spool','Wire Spool'), ('precision_screws','Precision Screws'), ('glass_sheet','Glass Sheet'), ('stone_chisel','Stone Chisel'), ('binding_cloth','Binding Cloth')
    ],
    'food_drink': [
        ('bread','Bread'), ('cheese','Cheese'), ('wine','Wine'), ('stew','Stew'), ('dried_meat','Dried Meat'),
        ('apple','Apple'), ('ale','Ale'), ('water_bottle','Water Bottle'), ('honey','Honey'), ('jerky','Jerky'), ('pastry','Pastry'), ('fish','Fish'), ('stew_large','Large Stew'), ('mushroom','Mushroom'), ('spice_pack','Spice Pack'),
        ('chewing_herb','Chewing Herb'), ('herbal_tea','Herbal Tea'), ('spiced_wine','Spiced Wine'), ('mead','Mead'), ('nut_mix','Nut Mix'),
        ('stew_packet','Stew Packet'), ('preserved_fruit','Preserved Fruit'), ('canned_fish','Canned Fish'), ('porridge','Porridge'), ('dried_berries','Dried Berries'),
        ('protein_bar','Protein Bar'), ('energy_drink','Energy Drink'), ('salt','Salt'), ('pepper','Pepper'), ('dried_milk','Dried Milk'),('rice','Rice'),
('grain_sack','Grain Sack'),
('flour','Flour'),
('oats','Oats'),
('beans_dried','Dried Beans'),
('lentils','Lentils'),
('hardtack','Hardtack'),
('flatbread','Flatbread'),
('crackers','Crackers'),
('noodle_pack','Noodle Pack'),

('cheese_hard','Hard Cheese'),
('butter','Butter'),
('cream','Cream'),
('yogurt','Yogurt'),
('egg','Egg'),
('pickled_vegetables','Pickled Vegetables'),
('pickled_eggs','Pickled Eggs'),
('salted_fish','Salted Fish'),
('salted_pork','Salted Pork'),
('smoked_sausage','Smoked Sausage'),

('fruit_dried_mix','Dried Fruit Mix'),
('fruit_fresh_mix','Fresh Fruit Mix'),
('berry_bundle','Berry Bundle'),
('vegetable_bundle','Vegetable Bundle'),
('root_vegetables','Root Vegetables'),
('herb_bundle_cooking','Cooking Herb Bundle'),
('soup_can','Canned Soup'),
('broth_cube','Broth Cube'),
('cooking_oil','Cooking Oil'),
('vinegar','Vinegar'),

('tea_leaves','Tea Leaves'),
('coffee_beans','Coffee Beans'),
('coffee_ground','Ground Coffee'),
('cocoa_powder','Cocoa Powder'),
('juice_bottle','Juice Bottle'),
('tonic_water','Tonic Water'),
('sparkling_water','Sparkling Water'),
('fermented_drink','Fermented Drink'),
('cider','Cider'),
('herbal_brew','Herbal Brew'),

('trail_mix','Trail Mix'),
('granola_bar','Granola Bar'),
('biscuit','Biscuit'),
('sweet_roll','Sweet Roll'),
('jam_jar','Jam Jar'),
('syrup_bottle','Syrup Bottle'),
('chocolate_piece','Chocolate Piece'),
('candy_mix','Candy Mix'),
('snack_pack','Snack Pack'),
('meal_ration','Meal Ration')
    ],
    'books': [
        ('scroll','Scroll'), ('codex','Codex'), ('map','Map'), ('journal','Journal'),
        ('atlas','Atlas'), ('bestiary','Bestiary'), ('grimoire','Grimoire'), ('ledger','Ledger'), ('diary','Diary'), ('cookbook','Cookbook'), ('travel_log','Travel Log'), ('treatise','Treatise'), ('pamphlet','Pamphlet'), ('hymnbook','Hymnbook'),
        ('manual','Manual'), ('tome','Tome'), ('scripture','Scripture'), ('archaeology_notes','Archaeology Notes'), ('lectern_map','Lectern Map'),
        ('field_guide','Field Guide'), ('encyclopedia','Encyclopedia'), ('pamphlet_tech','Tech Pamphlet'), ('children_book','Children Book'), ('annotated_map','Annotated Map'),
        ('cook_notes','Cook Notes'), ('battle_tactics','Battle Tactics'), ('herbal_index','Herbal Index'), ('navigation_manual','Navigation Manual'), ('poetry_collection','Poetry Collection')
    ],
    'household': [
        ('bowl','Bowl'), ('rope_coil','Rope Coil'), ('candle','Candle'), ('ink_bottle','Ink Bottle'),
        ('broom','Broom'), ('pot','Pot'), ('spoon','Spoon'), ('chair','Chair'), ('bucket','Bucket'), ('chest','Chest'), ('mirror','Mirror'), ('lamp','Lamp'), ('tapestry','Tapestry'), ('cloth_rag','Cloth Rag'),
        ('lantern_stand_small','Small Lantern Stand'), ('rug','Rug'), ('curtain','Curtain'), ('glass_vase','Glass Vase'), ('picture_frame','Picture Frame'),
        ('lockbox','Lockbox'), ('stool','Stool'), ('shelf','Shelf'), ('watering_can','Watering Can'), ('clothes_pin','Clothes Pin'),
        ('dustpan','Dustpan'), ('iron','Clothes Iron'), ('mop','Mop'), ('spice_rack','Spice Rack'), ('measuring_cup','Measuring Cup')
    ],
    'materials': [
        ('iron_ore','Iron Ore'), ('copper_ore','Copper Ore'), ('silver_dust','Silver Dust'), ('dragonbone_shard','Dragonbone Shard'), ('arcane_crystal','Arcane Crystal'), ('nanofiber','Nanofiber Mesh'),
        ('gold_ore','Gold Ore'), ('mithril_fragment','Mithril Fragment'), ('charcoal','Charcoal'), ('obsidian_shard','Obsidian Shard'), ('crystal_powder','Crystal Powder'), ('leather_strip','Leather Strip'), ('resin','Resin'), ('alloy_ingot','Alloy Ingot'), ('quantum_cell','Quantum Capacitor'), ('graphene_sheet','Graphene Sheet'),
        ('ceramic_shard','Ceramic Shard'), ('sawdust','Sawdust'), ('titanium_scrap','Titanium Scrap'), ('rare_earth','Rare Earth Powder'), ('lubricant','Lubricant'),
        ('solder','Solder'), ('polymer_resin','Polymer Resin'), ('optical_fiber','Optical Fiber'), ('magnetic_core','Magnetic Core'), ('superconductor','Superconductor'),
        ('aluminum_sheet','Aluminum Sheet'), ('nickel_powder','Nickel Powder'), ('zirconia_tile','Zirconia Tile'), ('boron_fiber','Boron Fiber'), ('glass_beads','Glass Beads')
    ]
}
# weights per category (tweak to tune distribution)
# ...

# Normalize category display names to remove embedded adjectives; derive
# human-readable names from keys (e.g. 'lantern_oil' -> 'Lantern Oil').
for cat, items in list(categories.items()):
    categories[cat] = [(k, k.replace('_', ' ').title()) for (k, _) in items]

# weights per category (tweak to tune distribution)

# weights per category (tweak to tune distribution)
category_weights = {
    'tool': 15, 'clothing': 15, 'jewelry': 8, 'armor': 12, 'weapon': 18, 'fantasy': 12, 'sci_fi': 20,
    'survival': 10, 'crafting': 10, 'food_drink': 8, 'books': 5, 'household': 6, 'materials': 7
}

equip_slots = {
    'weapon': ['hands','back'],
    'armor': ['torso','head','legs','hands','back'],
    'clothing': ['head','torso','legs','feet','hands','neck'],
    'jewelry': ['neck','ring']
}

# helper generative patterns
adjectives = ['Ancient','Common','Refined','Sturdy','Fine','Rusted','Pristine','Worn','Blessed','Cursed','Experimental','Compact','Heavy','Light']
materials = ['Iron','Steel','Leather','Wood','Obsidian','Mithril','Composite','Alloy','Ceramic','Glass','Polymer']
fantasy_traits = ['of Fire','of Frost','of Shadows','of the Wolf','of Vitality','of the Magus','of Swiftness']
sci_fi_traits = ['Mk I','Mk II','Prototype','Quantum','Ion-charged','Corvus-series']

rows = []
count = 0

# rarity tiers and multipliers
rarities = [
    ('common', 60, 1.0),
    ('uncommon', 20, 1.15),
    ('rare', 10, 1.35),
    ('epic', 6, 1.7),
    ('legendary', 3, 2.5),
    ('artifact', 1, 4.0)
]

rarity_names = [r[0] for r in rarities]
rarity_weights = [r[1] for r in rarities]
rarity_mult = {r[0]: r[2] for r in rarities}

# prefix / suffix / lore pools for special rolls
prefixes = ['Runed','Enchanted','Vicious','Blessed','Cursed','Stalwart','Voidforged','Arcane','Quantum']
suffixes = ['of the Deep','of Swiftness','of Vitality','of Shadows','of the Magus','of Heroes','Prototype','Prime']
bonus_effects = ['bleed','burn','stun','crit_chance','mana_regen','shield_capacity','hacking_bonus']
curse_pool = ['-hp','-luck','-durability_loss','-slow']
lore_snippets = ['Ancient relic from the First Age.','Inscribed with runes of a lost order.','Used by border rangers.','Rumored to contain a trapped spirit.']

# procedural subtypes
procedural = {
    'weapon': ['short blade','long blade','blunt','polearm','ranged','thrown'],
    'armor': ['light','medium','heavy'],
    'potion': ['healing','mana','stamina','antidote','buff']
}

def make_sku(base, idx):
    return f"{base}-{idx:04d}"

for i in range(NUM):
    # choose category by weighted mix to ensure variety
    keys = list(categories.keys())
    weights = [category_weights.get(k, 5) for k in keys]
    cat_pick = random.choices(keys, weights=weights, k=1)[0]
    base_list = categories[cat_pick]
    base = random.choice(base_list)
    sub_key = base[0]
    name_base = base[1]

    # pick rarity
    rarity = random.choices(rarity_names, weights=rarity_weights, k=1)[0]

    # name composition with richer patterns influenced by rarity
    def gen_name(cat, base):
        title = ''
        mat = random.choice(materials)
        adj = random.choice(adjectives)
        if cat == 'fantasy':
            pattern = random.choice([1,2,3])
            if pattern == 1:
                title = f"{adj} {base} {random.choice(fantasy_traits)}"
            elif pattern == 2:
                title = f"{base} of {random.choice(['the Deep','the North','Storms','the Magus'])}"
            else:
                title = f"{random.choice(['Moon-Touched','Sunforged','Elder'])} {base}"
        elif cat == 'sci_fi':
            # sci-fi compound names
            code = f"{random.choice(['VX','QX','ZX','NX'])}-{random.randint(1,99)}"
            title = f"{mat} {base} {random.choice(sci_fi_traits)} {code}"
        else:
            pattern = random.choice([1,2])
            if pattern == 1:
                title = f"{adj} {mat} {base}"
            else:
                title = f"{base} {random.choice(['of Swiftness','of Might','of Fortune'])}"
        # rarity title append for higher tiers
        if rarity in ('epic','legendary','artifact') and random.random() < 0.6:
            title = f"{title}, {rarity.title()}"
        return title

    name = gen_name(cat_pick, name_base)

    sku = make_sku(sub_key, i+1)
    description = f"{name}: a {cat_pick} item used in various contexts."

    # defaults
    weight = round(random.uniform(0.1, 12.0),2)
    stackable = 0
    max_stack = 1
    equippable = 0
    equip_slot = ''
    damage_min = ''
    damage_max = ''
    armor_rating = ''
    durability_max = ''
    consumable = 0
    charges_max = ''
    effects = {}
    tags = []

    # category specific rules
    if cat_pick in ('tool','clothing','jewelry'):
        # small chance some are stackable (e.g., rope bundles)
        if random.random() < 0.02:
            stackable = 1
            max_stack = random.choice([5,10,20])
        if cat_pick == 'jewelry':
            tags += ['fashion','value']
            # jewelry often provides small metadata
            effects = {"charisma": round(random.uniform(0.01, 0.1), 2)}
            if random.random() < 0.05:
                effects.update({"magic_resist": round(random.uniform(0.01,0.08),2)})
        if cat_pick == 'clothing':
            equip_slot = random.choice(equip_slots['clothing'])
            equippable = 1
            armor_rating = random.choice([0,1,2])
            tags += ['wearable']
        if cat_pick == 'tool':
            tags += ['tool']
            # ropes, shovel bundles
            if sub_key in ('rope','shovel'):
                stackable = 1
                max_stack = random.choice([2,5])
            # light sources and fuel
            if sub_key in ('torch','lantern','headlamp'):
                # torches/lanterns have a fuel amount (charges) and emit light
                consumable = 0
                charges_max = random.randint(5,40)
                effects = {"light_radius": random.randint(4,10), "fuel": charges_max}
                tags += ['light']
            if sub_key == 'flashlight':
                # battery-powered flashlight
                consumable = 0
                charges_max = random.randint(50,250)
                effects = {"light_radius": random.randint(6,14), "energy": charges_max}
                tags += ['light','power']
            if sub_key == 'matchbox':
                consumable = 1
                stackable = 1
                max_stack = random.choice([5,10,20])
                charges_max = random.randint(3,12)
                tags += ['tool','consumable']
            if sub_key in ('lantern_oil',):
                consumable = 1
                stackable = 1
                max_stack = random.choice([1,5,10])
                effects = {"fuel": random.randint(1,10)}
                tags += ['consumable','fuel']
            if sub_key == 'firestarter':
                # flint & steel
                consumable = 0
                tags += ['tool','survival']

    # apply rarity multipliers to stats where applicable
    mult = rarity_mult.get(rarity, 1.0)
    # scale durability and damage if present
    if durability_max:
        try:
            durability_max = int(max(1, int(durability_max) * mult))
        except Exception:
            pass
    if damage_min and damage_max:
        try:
            damage_min = int(max(1, int(damage_min) * mult))
            damage_max = int(max(damage_min, int(damage_max) * mult))
        except Exception:
            pass

    # special roll: small chance for prefix, suffix, bonus, curse, or lore
    special_notes = []
    if random.random() < 0.08:  # prefix
        pref = random.choice(prefixes)
        name = f"{pref} {name}"
        special_notes.append(pref)
    if random.random() < 0.06:  # suffix
        suf = random.choice(suffixes)
        name = f"{name} {suf}"
        special_notes.append(suf)
    if random.random() < 0.04:  # bonus effect
        be = random.choice(bonus_effects)
        # attach small bonus scaled by rarity
        bonus_val = round(random.uniform(0.05, 0.3) * rarity_mult.get(rarity,1.0), 3)
        if effects:
            effects[be] = effects.get(be, 0) + bonus_val
        else:
            effects = {be: bonus_val}
        special_notes.append(be)
    if random.random() < 0.02:  # curse
        curse = random.choice(curse_pool)
        # represent curse as tag for now
        tags += [f"curse:{curse}"]
        special_notes.append(curse)
    if random.random() < 0.03:
        lore = random.choice(lore_snippets)
        special_notes.append(lore)

    # attach rarity tag
    tags.append(rarity)

    if cat_pick == 'armor':
        equippable = 1
        equip_slot = random.choice(equip_slots['armor'])
        armor_rating = random.randint(3,20)
        durability_max = random.randint(20,200)
        tags += ['armor']

    if cat_pick == 'weapon':
        equippable = 1
        equip_slot = random.choice(equip_slots['weapon'])
        dmg = random.randint(3,18)
        damage_min = max(1, dmg - random.randint(0,4))
        damage_max = dmg + random.randint(0,6)
        durability_max = random.randint(10,200)
        tags += ['weapon']

    if cat_pick == 'fantasy':
        # potions and consumables
        if sub_key == 'potion' or random.random() < 0.25:
            consumable = 1
            stackable = 1
            max_stack = random.choice([1,5,10])
            # effects vary
            eff_key = random.choice(['hp','mana','stamina','luck','resistance'])
            effects = {eff_key: random.randint(5,100)}
            tags += ['consumable','fantasy']
        else:
            equippable = random.choice([0,1])
            if equippable:
                equip_slot = random.choice(['hands','neck','torso','head'])
            # magical traits
            if random.random() < 0.2:
                effects = {"magic_power": round(random.uniform(0.05,0.3),2)}
            tags += ['fantasy']

    if cat_pick == 'sci_fi':
        # energy cells consumable
        if sub_key == 'energy_cell' or random.random() < 0.2:
            consumable = 1
            stackable = 1
            max_stack = random.choice([1,5,20])
            effects = {"energy": random.randint(10,500)}
            tags += ['power']
        else:
            # weapons/gear
            equippable = 1 if random.random() < 0.8 else 0
            if equippable:
                equip_slot = random.choice(['hands','back'])
            if 'pistol' in name.lower() or 'rifle' in name.lower():
                dmg = random.randint(8,40)
                damage_min = max(1, dmg - random.randint(0,6))
                damage_max = dmg + random.randint(0,12)
                durability_max = random.randint(30,400)
            tags += ['sci-fi']

    # final safety: ensure numeric empties are quoted as empty strings in CSV
    row = {
        'sku': sku,
        'name': name,
        'description': description,
        'category': cat_pick,
        'sub_type': sub_key,
        'weight': weight,
        'stackable': int(stackable),
        'max_stack': int(max_stack),
        'equippable': int(equippable),
        'equip_slot': equip_slot or '',
        'damage_min': damage_min if damage_min != '' else '',
        'damage_max': damage_max if damage_max != '' else '',
        'armor_rating': armor_rating if armor_rating != '' else '',
        'durability_max': durability_max if durability_max != '' else '',
        'consumable': int(consumable),
        'charges_max': charges_max if charges_max != '' else '',
        'effects': json.dumps(effects) if effects else '',
        'tags': json.dumps(tags) if tags else ''
    }
    rows.append(row)

# write CSV
fieldnames = ['sku','name','description','category','sub_type','weight','stackable','max_stack','equippable','equip_slot','damage_min','damage_max','armor_rating','durability_max','consumable','charges_max','effects','tags']
with open(OUT, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

print(f"Wrote {len(rows)} items to {OUT}")
