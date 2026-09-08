/**
 * Bengaluru Living Agent Metropolis OS — 3D World Engine v4.0 PRO
 * MASTER REDESIGN:
 * 1. Straight Metro Viaducts & Sleek Inline 3-Car Trains (No wide/swerving trains)
 * 2. High-Visibility Interactive Citizens (Large 18u models, ground hologram beacons,
 *    overhead badges, dynamic walking between waypoints, speech bubbles, hover HUD, click-to-call)
 * 3. Zero-Gap Bengaluru Urban Fabric (Continuous road network with zebra crossings,
 *    dense architectural blocks, 450+ trees, animated auto-rickshaws, BMTC buses, and lakes)
 * 4. Cinematic Lighting & Dynamic Day/Night Cycle
 */

class VoxelMetropolis3D {
    _addNeonWireframe(mesh, colorHex = 0x00f5ff, opacity = 0.88) {
        if (!mesh || !mesh.geometry) return null;
        try {
            const edges = new THREE.EdgesGeometry(mesh.geometry, 22);
            const line = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({
                color: colorHex,
                transparent: true,
                opacity: opacity
            }));
            mesh.add(line);
            return line;
        } catch (e) {
            return null;
        }
    }

    _createWindowAtlas(theme = 'tech') {
        const canvas = document.createElement('canvas');
        canvas.width = 512;
        canvas.height = 512;
        const ctx = canvas.getContext('2d');

        const emitCanvas = document.createElement('canvas');
        emitCanvas.width = 512;
        emitCanvas.height = 512;
        const emitCtx = emitCanvas.getContext('2d');

        const baseColor = theme === 'luxury' ? '#0f172a' : (theme === 'hospital' ? '#0f172a' : '#0a0f1d');
        ctx.fillStyle = baseColor;
        ctx.fillRect(0, 0, 512, 512);

        emitCtx.fillStyle = '#000000';
        emitCtx.fillRect(0, 0, 512, 512);

        const cols = 16;
        const rows = 32;
        const w = 512 / cols;
        const h = 512 / rows;
        const padX = 3.5;
        const padY = 2.5;

        const warmColors = ['#fef08a', '#fde047', '#facc15', '#fbbf24', '#f59e0b', '#fed7aa'];
        const cyanColors = ['#38bdf8', '#00f5ff', '#67e8f9', '#7dd3fc', '#0284c7'];
        const greenColors = ['#34d399', '#10b981', '#6ee7b7'];
        const purpleColors = ['#c084fc', '#e879f9', '#a855f7'];

        for (let r = 0; r < rows; r++) {
            // Horizontal structural spandrel beam
            ctx.fillStyle = '#1e293b';
            ctx.fillRect(0, r * h, 512, 2.0);

            for (let c = 0; c < cols; c++) {
                const x = c * w + padX;
                const y = r * h + padY;
                const pw = w - padX * 2;
                const ph = h - padY * 2;

                const seed = Math.sin(r * 23.7 + c * 47.9 + (theme === 'luxury' ? 91.1 : (theme === 'hospital' ? 44.5 : 12.3))) * 43758.5453;
                const rand = seed - Math.floor(seed);
                
                // ~70% illuminated windows
                const isLit = rand > 0.30;

                if (isLit) {
                    let col;
                    const sub = (rand * 17) % 1;
                    if (theme === 'luxury') {
                        if (sub < 0.65) col = warmColors[Math.floor(sub * 10) % warmColors.length];
                        else if (sub < 0.85) col = cyanColors[Math.floor(sub * 10) % cyanColors.length];
                        else col = purpleColors[Math.floor(sub * 10) % purpleColors.length];
                    } else if (theme === 'hospital') {
                        if (sub < 0.60) col = '#e0f2fe';
                        else if (sub < 0.85) col = '#38bdf8';
                        else col = '#34d399';
                    } else { // tech
                        if (sub < 0.45) col = cyanColors[Math.floor(sub * 10) % cyanColors.length];
                        else if (sub < 0.78) col = warmColors[Math.floor(sub * 10) % warmColors.length];
                        else if (sub < 0.90) col = greenColors[Math.floor(sub * 10) % greenColors.length];
                        else col = purpleColors[Math.floor(sub * 10) % purpleColors.length];
                    }

                    // Diffuse window pane
                    ctx.fillStyle = col;
                    ctx.fillRect(x, y, pw, ph);

                    // Window blinds / interior divider (upper 32% slight shadow)
                    ctx.fillStyle = 'rgba(15, 23, 42, 0.32)';
                    ctx.fillRect(x, y, pw, ph * 0.32);

                    // Emissive map
                    emitCtx.fillStyle = col;
                    emitCtx.fillRect(x, y, pw, ph);
                } else {
                    // Dark / unlit window
                    ctx.fillStyle = '#060b14';
                    ctx.fillRect(x, y, pw, ph);
                    // Glass subtle interior reflection stripe
                    ctx.fillStyle = '#111d33';
                    ctx.fillRect(x, y + ph * 0.45, pw, 1.0);
                }
            }
        }

        const mapTex = new THREE.CanvasTexture(canvas);
        mapTex.wrapS = THREE.RepeatWrapping;
        mapTex.wrapT = THREE.RepeatWrapping;
        mapTex.repeat.set(1.5, 3.0);
        mapTex.generateMipmaps = false;
        mapTex.minFilter = THREE.LinearFilter;
        mapTex.magFilter = THREE.LinearFilter;

        const emitTex = new THREE.CanvasTexture(emitCanvas);
        emitTex.wrapS = THREE.RepeatWrapping;
        emitTex.wrapT = THREE.RepeatWrapping;
        emitTex.repeat.set(1.5, 3.0);
        emitTex.generateMipmaps = false;
        emitTex.minFilter = THREE.LinearFilter;
        emitTex.magFilter = THREE.LinearFilter;

        const mat = new THREE.MeshStandardMaterial({
            map: mapTex,
            emissiveMap: emitTex,
            emissive: 0xffffff,
            emissiveIntensity: 1.15,
            roughness: 0.32,
            metalness: 0.45
        });

        if (!this.buildingWindowMaterials) this.buildingWindowMaterials = [];
        this.buildingWindowMaterials.push(mat);
        return mat;
    }

    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.citizens3D = new Map();
        this.trains3D = [];
        this.vehicles3D = [];
        this.bmtcBuses = [];
        this.animals = { dogs: [], cats: [], birds: [] };
        this.voxelBlocks = new Map();
        this.governorAvatar = null;
        this.cameraMode = 'orbit';
        this.keys = {};
        this.clock = new THREE.Clock();
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        this.sectorObjects = new Map();
        this.timeOfDay = 0.35;
        this.rainParticles = null;
        this.isRaining = false;
        this.starField = null;
        this.sunMesh = null;
        this.moonMesh = null;
        this.skyDome = null;
        this.sunLight = null;
        this.ambientLight = null;
        this.hemiLight = null;
        this.pointLights = [];
        this.particleSystems = [];
        this.cloudMeshes = [];
        this.streetLights = [];
        this.hoverCitizen = null;
        this.selectedCitizen = null;
        this.tooltipEl = null;
        this.animTime = 0;
        this.rooftopBeacons = [];
        this.buildingWindowMaterials = [];
        this.windowAtlasMat = null;
        this.luxuryWindowMat = null;
        this.hospitalWindowMat = null;
        this._scratchV1 = new THREE.Vector3();
        this._scratchV2 = new THREE.Vector3();
        this._scratchV3 = new THREE.Vector3();
        this._scratchLook = new THREE.Vector3();

        // COMPACT, GEOGRAPHICALLY LOGICAL BENGALURU GRID (Zero Gaps, Straight Metro Corridors)
        this.GRID_CELL = 115;

        this.SECTOR_LAYOUT = {
            // East-West Central Purple Spine (gy = 0)
            "Majestic_Metro_Interchange": { gx: -3, gy:  0,   name: "🚇 Majestic Metro Hub",     color: 0x3fb950, bldgH: 48, radius: 36, type: 'transit' },
            "Vidhana_Soudha_Capitol":     { gx: -2, gy:  0,   name: "🏛️ Vidhana Soudha",         color: 0x7ee787, bldgH: 56, radius: 38, type: 'capitol' },
            "Cubbon_Park_Canopy":         { gx: -1, gy:  0,   name: "🌳 Cubbon Park",             color: 0x2ea043, bldgH: 18, radius: 38, type: 'park' },
            "Church_Street_Cafes":        { gx:  0, gy:  0,   name: "☕ Church Street Cafes",     color: 0xf0883e, bldgH: 36, radius: 32, type: 'culture' },
            "Indiranagar_100ft_Startups": { gx:  1, gy:  0,   name: "🚀 Indiranagar 100ft",       color: 0xbc8cff, bldgH: 42, radius: 34, type: 'startups' },
            "Bagmane_Tech_Park":          { gx:  2, gy:  0,   name: "💻 Bagmane Tech Park",       color: 0x58a6ff, bldgH: 62, radius: 36, type: 'tech' },
            "Whitefield_ITPB":            { gx:  3, gy:  0,   name: "🌐 Whitefield ITPB",         color: 0x388bfd, bldgH: 72, radius: 40, type: 'tech' },

            // North-South West Green Line (gx = -3)
            "IISc_Research_Campus":       { gx: -3, gy: -2,   name: "🔬 IISc Deep Tech",         color: 0x79c0ff, bldgH: 44, radius: 34, type: 'research' },
            "Gandhi_Bazaar_Heritage":     { gx: -3, gy:  1.5, name: "🏪 Gandhi Bazaar",          color: 0xdb6d28, bldgH: 26, radius: 30, type: 'heritage' },

            // North-South Center Blue Line (gx = 0)
            "Kempegowda_Airport_BLR":     { gx:  0, gy: -3,   name: "✈️ BLR Airport (KIA)",      color: 0xe3b341, bldgH: 30, radius: 42, type: 'airport' },
            "Manyata_Tech_Park":          { gx:  0, gy: -1.5, name: "🏢 Manyata Tech Park",      color: 0x58a6ff, bldgH: 68, radius: 38, type: 'tech' },
            "Silk_Board_Junction":        { gx:  0, gy:  1.5, name: "🚦 Silk Board Flyover",     color: 0xf85149, bldgH: 32, radius: 36, type: 'transit' },
            "Electronic_City_Phase_1":    { gx:  0, gy:  3,   name: "🖥️ Electronic City Hub",    color: 0x388bfd, bldgH: 74, radius: 42, type: 'tech' },

            // Adjacent Urban Districts & Nightlife / Fitness
            "UB_City_Luxury_Towers":      { gx: -1, gy:  1,   name: "💎 UB City Towers",         color: 0xd29922, bldgH: 96, radius: 34, type: 'luxury' },
            "Nexus_Koramangala_Mall":     { gx:  1, gy:  1,   name: "🛍️ Koramangala Mall",      color: 0xe3b341, bldgH: 46, radius: 36, type: 'commercial' },
            "HSR_Layout_Residences":      { gx:  1, gy:  2,   name: "🏡 HSR Layout Homes",       color: 0xa371f7, bldgH: 32, radius: 34, type: 'residential' },
            "Koramangala_Microbrewery_Pub": { gx: 2, gy: 1,   name: "🍺 Koramangala Brewery & Pub", color: 0xf59e0b, bldgH: 38, radius: 34, type: 'pub' },
            "HSR_Cult_Fit_Gym":            { gx: 2, gy: 2,   name: "🏋️ HSR Cult.fit Elite Gym",   color: 0xef4444, bldgH: 36, radius: 34, type: 'gym' },
            "MG_Road_Boulevard":           { gx: -1, gy: -1,  name: "🚌 MG Road BMTC & Metro Hub",  color: 0x06b6d4, bldgH: 42, radius: 36, type: 'transit' },
            "Bull_Temple_Basavanagudi":    { gx: -2, gy:  2,   name: "🛕 Bull Temple (Dodda Basavana Gudi)", color: 0xf59e0b, bldgH: 46, radius: 36, type: 'temple' },
            "St_Marks_Cathedral_Churches": { gx: -1, gy: -0.5, name: "⛪ St. Mark's Cathedral & Basilica", color: 0x60a5fa, bldgH: 52, radius: 36, type: 'church' },
            "Dev_Coliving_Citizen_Residences": { gx: 1, gy: -1, name: "🏘️ Dev Co-Living PG & Citizen Homes", color: 0xec4899, bldgH: 40, radius: 36, type: 'housing' },
            "Bengaluru_Care_Hospital_Clinic":  { gx: 0, gy:  0.8, name: "🏥 Narayana Health Care Clinic", color: 0x10b981, bldgH: 38, radius: 34, type: 'care' }
        };

        // EXPLICIT REAL-WORLD BENGALURU VENUE SEATING & ACTIVITY SPOTS
        this.VENUE_SPOTS = {
            'IISc_Research_Campus': [
                { x:   0.0, z: -8.0, rot: 0,         desc: 'Prof. Ramanathan Quantum Lecture Podium', type: 'teacher' },
                { x:  -8.0, z: -2.0, rot: Math.PI,   desc: 'Academy Tier-1 Student Desk L', type: 'student' },
                { x:   8.0, z: -2.0, rot: Math.PI,   desc: 'Academy Tier-1 Student Desk R', type: 'student' },
                { x: -12.0, z:  4.0, rot: Math.PI,   desc: 'Academy Tier-2 Student Desk L', type: 'student' },
                { x:   0.0, z:  4.0, rot: Math.PI,   desc: 'Academy Tier-2 Student Desk C', type: 'student' },
                { x:  12.0, z:  4.0, rot: Math.PI,   desc: 'Academy Tier-2 Student Desk R', type: 'student' },
                { x:  -6.0, z: 10.0, rot: Math.PI,   desc: 'Neuromorphic Silicon Lab Bench A', type: 'desk' },
                { x:   6.0, z: 10.0, rot: Math.PI,   desc: 'Bioinformatics Lab Bench B', type: 'desk' }
            ],

            'Manyata_Tech_Park': [
                { x: -12, z:  8.8, rot: Math.PI,    desc: 'Manyata Cloud Desk #1', type: 'desk' },
                { x:  12, z:  8.8, rot: Math.PI,    desc: 'Manyata Cloud Desk #2', type: 'desk' },
                { x: -12, z: 13.2, rot: 0,          desc: 'Manyata Cloud Desk #3', type: 'desk' },
                { x:  12, z: 13.2, rot: 0,          desc: 'Manyata Cloud Desk #4', type: 'desk' },
                { x:  -5, z: -5.0, rot:  Math.PI/2, desc: 'Sprint Boardroom Seat A', type: 'meeting' },
                { x:   5, z: -5.0, rot: -Math.PI/2, desc: 'Sprint Boardroom Seat B', type: 'meeting' },
                { x:  -2, z: -2.0, rot: Math.PI,    desc: 'Sprint Boardroom Seat C', type: 'meeting' },
                { x:   2, z: -8.0, rot: 0,          desc: 'Sprint Boardroom Seat D', type: 'meeting' }
            ],
            'Whitefield_ITPB': [
                { x: -12, z:  8.8, rot: Math.PI,    desc: 'ITPB Enterprise AI Desk #1', type: 'desk' },
                { x:  12, z:  8.8, rot: Math.PI,    desc: 'ITPB Enterprise AI Desk #2', type: 'desk' },
                { x: -12, z: 13.2, rot: 0,          desc: 'ITPB Enterprise AI Desk #3', type: 'desk' },
                { x:  12, z: 13.2, rot: 0,          desc: 'ITPB Enterprise AI Desk #4', type: 'desk' },
                { x:  -5, z: -5.0, rot:  Math.PI/2, desc: 'Architecture Review Seat A', type: 'meeting' },
                { x:   5, z: -5.0, rot: -Math.PI/2, desc: 'Architecture Review Seat B', type: 'meeting' }
            ],
            'Bagmane_Tech_Park': [
                { x: -12, z:  8.8, rot: Math.PI,    desc: 'Bagmane Systems Desk #1', type: 'desk' },
                { x:  12, z:  8.8, rot: Math.PI,    desc: 'Bagmane Systems Desk #2', type: 'desk' },
                { x: -12, z: 13.2, rot: 0,          desc: 'Bagmane Systems Desk #3', type: 'desk' },
                { x:  12, z: 13.2, rot: 0,          desc: 'Bagmane Systems Desk #4', type: 'desk' },
                { x:  -5, z: -5.0, rot:  Math.PI/2, desc: 'DevOps Standup Seat A', type: 'meeting' },
                { x:   5, z: -5.0, rot: -Math.PI/2, desc: 'DevOps Standup Seat B', type: 'meeting' }
            ],
            'Church_Street_Cafes': [
                { x: -12.6, z:  3.0, rot:  Math.PI/2, desc: 'Church St. Roasters Table #1A', type: 'cafe' },
                { x:  -7.4, z:  3.0, rot: -Math.PI/2, desc: 'Church St. Roasters Table #1B', type: 'cafe' },
                { x:   7.4, z:  3.0, rot:  Math.PI/2, desc: 'Church St. Roasters Table #2A', type: 'cafe' },
                { x:  12.6, z:  3.0, rot: -Math.PI/2, desc: 'Church St. Roasters Table #2B', type: 'cafe' },
                { x:  -2.6, z: -3.0, rot:  Math.PI/2, desc: 'Patio Umbrella Table #3A', type: 'cafe' },
                { x:   2.6, z: -3.0, rot: -Math.PI/2, desc: 'Patio Umbrella Table #3B', type: 'cafe' },
                { x:   0.0, z: -8.0, rot: Math.PI,    desc: 'Espresso Bar Order Counter', type: 'darshini' }
            ],
            'Indiranagar_100ft_Startups': [
                { x: -9.0, z:  6.0, rot: Math.PI,    desc: 'Indiranagar AI Studio Desk L', type: 'desk' },
                { x:  9.0, z:  6.0, rot: Math.PI,    desc: 'Indiranagar AI Studio Desk R', type: 'desk' },
                { x: -4.0, z: -4.0, rot:  Math.PI/2, desc: 'Founder Lounge Seat A', type: 'meeting' },
                { x:  4.0, z: -4.0, rot: -Math.PI/2, desc: 'Founder Lounge Seat B', type: 'meeting' }
            ],
            'Gandhi_Bazaar_Heritage': [
                { x: -4.0, z: -5.0, rot: Math.PI,    desc: 'Vidyarthi Bhavan Coffee Counter #1', type: 'darshini' },
                { x:  0.0, z: -5.0, rot: Math.PI,    desc: 'Vidyarthi Bhavan Coffee Counter #2', type: 'darshini' },
                { x:  4.0, z: -5.0, rot: Math.PI,    desc: 'Vidyarthi Bhavan Coffee Counter #3', type: 'darshini' },
                { x: -8.0, z:  5.0, rot:  Math.PI/2, desc: 'Heritage Dosa Table #1', type: 'cafe' },
                { x:  8.0, z:  5.0, rot: -Math.PI/2, desc: 'Heritage Dosa Table #2', type: 'cafe' }
            ],
            'Nexus_Koramangala_Mall': [
                { x: -10.0, z: 2.0, rot: 0,          desc: 'Koramangala Gadget Store Counter', type: 'darshini' },
                { x:   0.0, z: 2.0, rot: 0,          desc: 'Koramangala Bookstore Counter', type: 'darshini' },
                { x:  10.0, z: 2.0, rot: 0,          desc: 'Koramangala Coffee Lounge', type: 'cafe' }
            ],
            'Koramangala_Microbrewery_Pub': [
                { x:  2.0, z:  5.6, rot: Math.PI,    desc: 'Brewery Bar Stool #1 (Fresh IPA)', type: 'pub' },
                { x:  7.0, z:  5.6, rot: Math.PI,    desc: 'Brewery Bar Stool #2 (Belgian Wit)', type: 'pub' },
                { x: 12.0, z:  5.6, rot: Math.PI,    desc: 'Brewery Bar Stool #3 (Chocolate Stout)', type: 'pub' },
                { x: 17.0, z:  5.6, rot: Math.PI,    desc: 'Brewery Bar Stool #4 (Apple Cider)', type: 'pub' },
                { x: -8.0, z:  8.0, rot:  Math.PI/2, desc: 'Brewery Keg Table #A', type: 'pub' },
                { x: 10.0, z: 12.0, rot: -Math.PI/2, desc: 'Brewery Keg Table #B', type: 'pub' }
            ],
            'HSR_Cult_Fit_Gym': [
                { x: -12.0, z:  0.0, rot: Math.PI,   desc: 'Cult.fit Treadmill #1 (Sprint)', type: 'gym_run' },
                { x:  -5.0, z:  0.0, rot: Math.PI,   desc: 'Cult.fit Treadmill #2 (Endurance)', type: 'gym_run' },
                { x:   6.0, z: -4.0, rot: 0,         desc: 'Olympic Barbell Bench Press', type: 'gym_lift' },
                { x:  15.0, z: -4.0, rot: 0,         desc: 'Dumbbell Power Station', type: 'gym_lift' },
                { x:  10.0, z:  6.0, rot: Math.PI,   desc: 'Calisthenics Chin-Up Rig', type: 'gym_lift' }
            ],
            'Cubbon_Park_Canopy': [
                { x: -14.0, z:   0.0, rot:  Math.PI/2, desc: 'Cubbon Rain Tree Bench #1', type: 'park_sit' },
                { x:  14.0, z:   0.0, rot: -Math.PI/2, desc: 'Cubbon Jacaranda Bench #2', type: 'park_sit' },
                { x:   0.0, z: -14.0, rot: Math.PI,    desc: 'Cubbon Fountain View Bench', type: 'park_sit' },
                { x:   0.0, z:  14.0, rot: 0,          desc: 'Cubbon Bamboo Grove Bench', type: 'park_sit' },
                { x: -10.0, z:  10.0, rot:  Math.PI/4, desc: 'Cubbon Morning Jogging Trail', type: 'jog' },
                { x:  10.0, z: -10.0, rot: -Math.PI/4, desc: 'Cubbon Evening Jogging Trail', type: 'jog' }
            ],
            'MG_Road_Boulevard': [
                { x: -12.0, z:  4.0, rot: Math.PI,    desc: 'BMTC Electric Bus Bay #1', type: 'bus_wait' },
                { x:  -4.0, z:  4.0, rot: Math.PI,    desc: 'BMTC Volvo Airport Express Bay', type: 'bus_wait' },
                { x:   6.0, z:  4.0, rot: Math.PI,    desc: 'MG Road Metro Boulevard Bench', type: 'park_sit' },
                { x:  14.0, z:  4.0, rot: Math.PI,    desc: 'MG Road Pedestrian Walkway', type: 'transit' }
            ],
            'Bull_Temple_Basavanagudi': [
                { x:   0.0, z: -10.0, rot: 0,          desc: 'Sanctum Nandi Monolith Shrine', type: 'temple_pray' },
                { x: -12.0, z:   6.0, rot:  Math.PI/2, desc: 'Temple Mandapam Mat #1', type: 'temple_pray' },
                { x:  12.0, z:   6.0, rot: -Math.PI/2, desc: 'Temple Mandapam Mat #2', type: 'temple_pray' },
                { x:   0.0, z:  12.0, rot: Math.PI,    desc: 'Prasad & Flower Stall Bench', type: 'bench' }
            ],
            'St_Marks_Cathedral_Churches': [
                { x:  -8.0, z:   0.0, rot: Math.PI,    desc: 'Cathedral Choir Pew #1', type: 'church_pew' },
                { x:   8.0, z:   0.0, rot: Math.PI,    desc: 'Cathedral Choir Pew #2', type: 'church_pew' },
                { x:   0.0, z:  12.0, rot: 0,          desc: 'Community Fellowship Lawn Bench', type: 'bench' }
            ],
            'Dev_Coliving_Citizen_Residences': [
                { x: -10.0, z:  -8.0, rot: 0,          desc: 'Resident Pod Room 101', type: 'desk' },
                { x:  10.0, z:  -8.0, rot: 0,          desc: 'Resident Pod Room 102', type: 'desk' },
                { x:   0.0, z:  10.0, rot: Math.PI,    desc: 'Rooftop Community Lounge', type: 'bench' }
            ],
            'Bengaluru_Care_Hospital_Clinic': [
                { x: -10.0, z:   2.0, rot: 0,          desc: 'Triage & Consultation Desk', type: 'desk' },
                { x:  10.0, z:   2.0, rot: Math.PI,    desc: 'Wellness Recovery Bed #1', type: 'bench' },
                { x:   0.0, z:  10.0, rot: Math.PI,    desc: 'Emergency Ambulance Dropoff Bay', type: 'bench' }
            ]
        };

        this.BLOCK_PALETTE = {
            solar_panel:         { color: 0x00f5d4, emissive: 0x004433, metalness: 0.9, roughness: 0.1 },
            server_rack:         { color: 0x3a86ff, emissive: 0x001144, metalness: 0.7, roughness: 0.3 },
            fiber_conduit:       { color: 0x8338ec, emissive: 0x330066, metalness: 0.5, roughness: 0.4 },
            concrete_wall:       { color: 0x64748b, emissive: 0x000000, metalness: 0.1, roughness: 0.9 },
            glass_facade:        { color: 0x38bdf8, emissive: 0x002255, opacity: 0.65, transparent: true, metalness: 0.9, roughness: 0.1 },
            metro_track_rail:    { color: 0xa855f7, emissive: 0x440077, metalness: 0.8, roughness: 0.2 },
            ev_charging_station: { color: 0x06b6d4, emissive: 0x002244, metalness: 0.6, roughness: 0.3 },
            filter_coffee_kiosk: { color: 0xd97706, emissive: 0x331100, metalness: 0.2, roughness: 0.7 },
            road_patch:          { color: 0x1e293b, emissive: 0x000000, metalness: 0.1, roughness: 0.9 },
            voltage_transformer: { color: 0xef4444, emissive: 0x440000, metalness: 0.6, roughness: 0.4 },
            tree_canopy:         { color: 0x22c55e, emissive: 0x002200, metalness: 0.0, roughness: 0.9 }
        };

        this._buildSectorWorldPos();
        this.init();
    }

    _buildSectorWorldPos() {
        this._sectorWorldPos = {};
        for (const [key, s] of Object.entries(this.SECTOR_LAYOUT)) {
            this._sectorWorldPos[key] = {
                x: s.gx * this.GRID_CELL,
                z: s.gy * this.GRID_CELL
            };
        }
    }

    init() {
        const width  = this.container.clientWidth  || 900;
        const height = this.container.clientHeight || 680;

        this.scene = new THREE.Scene();
        this.scene.fog = new THREE.FogExp2(0x0c1929, 0.00045);

        this.camera = new THREE.PerspectiveCamera(54, width / height, 2, 7000);
        this.camera.position.set(0, 490, 580);

        this.renderer = new THREE.WebGLRenderer({ antialias: false, powerPreference: 'high-performance' });
        this.renderer.setSize(width, height);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.0));
        this.renderer.shadowMap.enabled = false;
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        this.renderer.toneMappingExposure = 1.35;
        this.container.appendChild(this.renderer.domElement);

        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.08;
        this.controls.maxPolarAngle = Math.PI / 1.95;
        this.controls.minDistance = 25;
        this.controls.maxDistance = 2400;
        this.controls.target.set(0, 20, 0);

        // LIGHTING
        this.ambientLight = new THREE.AmbientLight(0x4a6288, 3.2);
        this.scene.add(this.ambientLight);

        this.hemiLight = new THREE.HemisphereLight(0xbfe3ff, 0x3d4a34, 2.4);
        this.scene.add(this.hemiLight);

        this.sunLight = new THREE.DirectionalLight(0xfff8e7, 5.0);
        this.sunLight.position.set(380, 640, 320);
        this.sunLight.castShadow = true;
        this.sunLight.shadow.mapSize.set(1024, 1024);
        this.sunLight.shadow.camera.near = 10;
        this.sunLight.shadow.camera.far  = 3200;
        const sd = 750;
        this.sunLight.shadow.camera.left   = -sd;
        this.sunLight.shadow.camera.right  =  sd;
        this.sunLight.shadow.camera.top    =  sd;
        this.sunLight.shadow.camera.bottom = -sd;
        this.sunLight.shadow.bias = -0.0003;
        this.scene.add(this.sunLight);

        const fillLight = new THREE.DirectionalLight(0x487bb0, 1.8);
        fillLight.position.set(-350, 300, -280);
        this.scene.add(fillLight);

        // WORLD BUILDING
        this.windowAtlasMat = this._createWindowAtlas('tech');
        this.luxuryWindowMat = this._createWindowAtlas('luxury');
        this.hospitalWindowMat = this._createWindowAtlas('hospital');

        this.createCinematicSky();
        this.createGroundTerrain();
        this.createConnectedRoadNetwork();
        this.createCityFillBlocks();
        this.createLakes();
        this.create16BengaluruSectors();
        this.createElevatedMetroRailNetwork();
        this.createAnimatedVehicles();
        this.createBMTCBusFleet();
        this.createLivingAnimals();
        this.createGovernorAvatar();
        this.createStarField();
        this.createRainSystem();
        this.createClouds();
        this.createTooltip();

        window.addEventListener('resize',  () => this.onWindowResize());
        window.addEventListener('keydown', (e) => this.onKeyDown(e));
        window.addEventListener('keyup',   (e) => this.onKeyUp(e));
        this.renderer.domElement.addEventListener('click',     (e) => this.onCanvasClick(e));
        this.renderer.domElement.addEventListener('dblclick',  (e) => this.onCanvasDblClick(e));
        this.renderer.domElement.addEventListener('mousemove', (e) => this.onMouseMove(e));

        this.animate = this.animate.bind(this);
        requestAnimationFrame(this.animate);
    }

    createTooltip() {
        this.tooltipEl = document.createElement('div');
        Object.assign(this.tooltipEl.style, {
            position: 'absolute', pointerEvents: 'none', display: 'none',
            background: 'rgba(11, 18, 30, 0.95)',
            border: '1px solid #38bdf8',
            boxShadow: '0 8px 32px rgba(0,0,0,0.6), 0 0 12px rgba(56,189,248,0.3)',
            backdropFilter: 'blur(8px)',
            color: '#fff', padding: '10px 14px', borderRadius: '8px',
            fontSize: '12px', fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            zIndex: '50', maxWidth: '240px', lineHeight: '1.4'
        });
        this.container.style.position = 'relative';
        this.container.appendChild(this.tooltipEl);
    }

    createCinematicSky() {
        const skyGeo = new THREE.SphereGeometry(3200, 32, 16);
        const skyMat = new THREE.ShaderMaterial({
            side: THREE.BackSide,
            uniforms: {
                topColor:    { value: new THREE.Color(0x0a224a) },
                bottomColor: { value: new THREE.Color(0x2d68a8) },
                offset:      { value: 500 },
                exponent:    { value: 0.55 }
            },
            vertexShader: "varying vec3 vWorldPosition; void main() { vec4 worldPos = modelMatrix * vec4(position, 1.0); vWorldPosition = worldPos.xyz; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }",
            fragmentShader: "uniform vec3 topColor; uniform vec3 bottomColor; uniform float offset; uniform float exponent; varying vec3 vWorldPosition; void main() { float h = normalize(vWorldPosition + vec3(0.0, offset, 0.0)).y; gl_FragColor = vec4(mix(bottomColor, topColor, max(pow(max(h, 0.0), exponent), 0.0)), 1.0); }"
        });
        this.skyDome = new THREE.Mesh(skyGeo, skyMat);
        this.scene.add(this.skyDome);
        this.skyUniforms = skyMat.uniforms;

        const sunGeo  = new THREE.SphereGeometry(28, 20, 20);
        const sunMat  = new THREE.MeshBasicMaterial({ color: 0xfffae0 });
        this.sunMesh  = new THREE.Mesh(sunGeo, sunMat);
        this.scene.add(this.sunMesh);

        const moonGeo = new THREE.SphereGeometry(16, 16, 16);
        const moonMat = new THREE.MeshBasicMaterial({ color: 0xd8e4fc });
        this.moonMesh = new THREE.Mesh(moonGeo, moonMat);
        this.scene.add(this.moonMesh);
    }

    createClouds() {
        const cloudMat = new THREE.MeshStandardMaterial({
            color: 0xffffff, transparent: true, opacity: 0.35, roughness: 0.95
        });
        for (let i = 0; i < 22; i++) {
            const g = new THREE.Group();
            const numPuffs = 4 + Math.floor(Math.random() * 4);
            for (let p = 0; p < numPuffs; p++) {
                const r = 24 + Math.random() * 26;
                const puff = new THREE.Mesh(new THREE.SphereGeometry(r, 8, 6), cloudMat);
                puff.position.set((Math.random()-.5)*60, (Math.random()-.5)*12, (Math.random()-.5)*35);
                puff.scale.y = 0.5;
                g.add(puff);
            }
            g.position.set((Math.random()-.5)*1600, 320 + Math.random()*90, (Math.random()-.5)*1600);
            this.scene.add(g);
            this.cloudMeshes.push({ group: g, speed: 2.0 + Math.random() * 3.0 });
        }
    }

    createStarField() {
        const count = 3200;
        const geo   = new THREE.BufferGeometry();
        const pos   = new Float32Array(count * 3);
        for (let i = 0; i < count; i++) {
            const theta = Math.random() * Math.PI * 2;
            const phi   = Math.acos(2 * Math.random() - 1);
            const r = 2400 + Math.random() * 400;
            pos[i*3]   = r * Math.sin(phi) * Math.cos(theta);
            pos[i*3+1] = Math.abs(r * Math.cos(phi)) + 60;
            pos[i*3+2] = r * Math.sin(phi) * Math.sin(theta);
        }
        geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
        const mat = new THREE.PointsMaterial({ color: 0xffffff, size: 2.4, sizeAttenuation: true });
        this.starField = new THREE.Points(geo, mat);
        this.scene.add(this.starField);
    }

    createGroundTerrain() {
        const groundGeo = new THREE.PlaneGeometry(2400, 2400, 1, 1);
        const groundMat = new THREE.MeshStandardMaterial({
            color: 0x111a24, roughness: 0.94, metalness: 0.05
        });
        const ground = new THREE.Mesh(groundGeo, groundMat);
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        this.scene.add(ground);

        const gridHelper = new THREE.GridHelper(1600, 40, 0x1e3a5f, 0x142334);
        gridHelper.position.y = 0.15;
        this.scene.add(gridHelper);
    }

    createConnectedRoadNetwork() {
        const roadMat     = new THREE.MeshStandardMaterial({ color: 0x16202c, roughness: 0.9, metalness: 0.08 });
        const markingMat  = new THREE.MeshBasicMaterial({ color: 0xfacc15 });
        const whiteMat    = new THREE.MeshBasicMaterial({ color: 0xffffff });
        const sidewalkMat = new THREE.MeshStandardMaterial({ color: 0x223042, roughness: 0.82 });
        const poleMat     = new THREE.MeshStandardMaterial({ color: 0x334155, metalness: 0.7, roughness: 0.3 });
        const bulbMat     = new THREE.MeshBasicMaterial({ color: 0xfef08a });

        const CITY_SPAN = 460;
        const ROAD_WIDTH = 14;
        const dummy = new THREE.Object3D();

        const ewLanes = [-230, -115, 0, 115, 230];
        const nsLanes = [-345, -230, -115, 0, 115, 230, 345];

        // 1. Long Continuous Road and Sidewalk Slabs
        ewLanes.forEach(z => {
            const road = new THREE.Mesh(new THREE.BoxGeometry(CITY_SPAN * 2, 0.4, ROAD_WIDTH), roadMat);
            road.position.set(0, 0.2, z);
            this.scene.add(road);

            [-ROAD_WIDTH/2 - 2, ROAD_WIDTH/2 + 2].forEach(offsetZ => {
                const sw = new THREE.Mesh(new THREE.BoxGeometry(CITY_SPAN * 2, 0.6, 4), sidewalkMat);
                sw.position.set(0, 0.3, z + offsetZ);
                this.scene.add(sw);
            });
        });

        nsLanes.forEach(x => {
            const road = new THREE.Mesh(new THREE.BoxGeometry(ROAD_WIDTH, 0.4, CITY_SPAN * 2), roadMat);
            road.position.set(x, 0.2, 0);
            this.scene.add(road);

            [-ROAD_WIDTH/2 - 2, ROAD_WIDTH/2 + 2].forEach(offsetX => {
                const sw = new THREE.Mesh(new THREE.BoxGeometry(4, 0.6, CITY_SPAN * 2), sidewalkMat);
                sw.position.set(x + offsetX, 0.3, 0);
                this.scene.add(sw);
            });
        });

        // 2. High-Performance Instanced Yellow Center Dashes (1 draw call instead of 500+)
        const dashGeo = new THREE.BoxGeometry(10, 0.45, 0.5);
        const dashInst = new THREE.InstancedMesh(dashGeo, markingMat, 650);
        dashInst.instanceMatrix.setUsage(THREE.StaticDrawUsage);
        let dashCount = 0;

        ewLanes.forEach(z => {
            for (let x = -CITY_SPAN + 10; x <= CITY_SPAN - 10; x += 22) {
                dummy.position.set(x, 0.25, z);
                dummy.rotation.set(0, 0, 0);
                dummy.scale.set(1, 1, 1);
                dummy.updateMatrix();
                dashInst.setMatrixAt(dashCount++, dummy.matrix);
            }
        });

        nsLanes.forEach(x => {
            for (let z = -CITY_SPAN + 10; z <= CITY_SPAN - 10; z += 22) {
                dummy.position.set(x, 0.25, z);
                dummy.rotation.set(0, Math.PI / 2, 0);
                dummy.scale.set(1, 1, 1);
                dummy.updateMatrix();
                dashInst.setMatrixAt(dashCount++, dummy.matrix);
            }
        });
        dashInst.count = dashCount;
        dashInst.instanceMatrix.needsUpdate = true;
        this.scene.add(dashInst);

        // 3. High-Performance Instanced Zebra Crosswalks (1 draw call instead of 175)
        const zebraGeo = new THREE.BoxGeometry(ROAD_WIDTH * 0.8, 0.45, 0.9);
        const zebraInst = new THREE.InstancedMesh(zebraGeo, whiteMat, 250);
        zebraInst.instanceMatrix.setUsage(THREE.StaticDrawUsage);
        let zebraCount = 0;

        nsLanes.forEach(x => {
            ewLanes.forEach(z => {
                for (let i = -4; i <= 4; i += 2) {
                    dummy.position.set(x, 0.26, z + i * 1.5 + (i > 0 ? 9 : -9));
                    dummy.rotation.set(0, 0, 0);
                    dummy.scale.set(1, 1, 1);
                    dummy.updateMatrix();
                    zebraInst.setMatrixAt(zebraCount++, dummy.matrix);
                }
            });
        });
        zebraInst.count = zebraCount;
        zebraInst.instanceMatrix.needsUpdate = true;
        this.scene.add(zebraInst);

        // 4. High-Performance Instanced Street Lights (2 draw calls instead of 336)
        const poleGeo = new THREE.CylinderGeometry(0.35, 0.5, 14, 6);
        const poleInst = new THREE.InstancedMesh(poleGeo, poleMat, 150);
        poleInst.instanceMatrix.setUsage(THREE.StaticDrawUsage);

        const bulbGeo = new THREE.SphereGeometry(0.7, 8, 6);
        const bulbInst = new THREE.InstancedMesh(bulbGeo, bulbMat, 150);
        bulbInst.instanceMatrix.setUsage(THREE.StaticDrawUsage);

        let lightCount = 0;
        nsLanes.forEach(x => {
            for (let z = -CITY_SPAN + 25; z <= CITY_SPAN - 25; z += 55) {
                const lx = x + ROAD_WIDTH / 2 + 2.5;
                dummy.position.set(lx, 7.0, z);
                dummy.rotation.set(0, 0, 0);
                dummy.scale.set(1, 1, 1);
                dummy.updateMatrix();
                poleInst.setMatrixAt(lightCount, dummy.matrix);

                dummy.position.set(lx - 2.5, 13.5, z);
                dummy.updateMatrix();
                bulbInst.setMatrixAt(lightCount, dummy.matrix);
                lightCount++;
            }
        });
        poleInst.count = lightCount;
        bulbInst.count = lightCount;
        poleInst.instanceMatrix.needsUpdate = true;
        bulbInst.instanceMatrix.needsUpdate = true;
        this.scene.add(poleInst);
        this.scene.add(bulbInst);
    }

    createCityFillBlocks() {
        const rng = this._seededRng(108);

        // 1. High-Performance Instanced Infill Buildings (1 draw call instead of 680+)
        const bGeo = new THREE.BoxGeometry(1, 1, 1);
        const bMat = this.windowAtlasMat || this._createWindowAtlas('tech');
        const buildingInst = new THREE.InstancedMesh(bGeo, bMat, 340);
        buildingInst.instanceMatrix.setUsage(THREE.StaticDrawUsage);

        const paletteColors = [0xffffff, 0xe2e8f0, 0xdbeafe, 0xe0e7ff, 0xcffafe, 0xfef3c7];
        const dummy = new THREE.Object3D();
        let validBuildings = 0;

        for (let i = 0; i < 340; i++) {
            const bx = (rng() - 0.5) * 880;
            const bz = (rng() - 0.5) * 880;

            let blocked = false;
            for (const pos of Object.values(this._sectorWorldPos)) {
                const dx = bx - pos.x, dz = bz - pos.z;
                if (Math.sqrt(dx * dx + dz * dz) < 52) { blocked = true; break; }
            }
            const roadSnapX = Math.abs(bx % 115);
            const roadSnapZ = Math.abs(bz % 115);
            if (roadSnapX < 12 || roadSnapZ < 12) blocked = true;
            if (blocked) continue;

            const bh = 12 + rng() * 38;
            const bw = 10 + rng() * 14;
            const bd = 10 + rng() * 14;

            dummy.position.set(bx, bh / 2 + 0.3, bz);
            dummy.scale.set(bw, bh, bd);
            dummy.rotation.set(0, 0, 0);
            dummy.updateMatrix();

            buildingInst.setMatrixAt(validBuildings, dummy.matrix);
            const pCol = new THREE.Color(paletteColors[Math.floor(rng() * paletteColors.length)]);
            buildingInst.setColorAt(validBuildings, pCol);

            // Rooftop aviation warning beacons for tall buildings
            if (bh > 28) {
                const beaconGeo = new THREE.SphereGeometry(0.75, 6, 6);
                const beaconMat = new THREE.MeshBasicMaterial({ color: 0xff0033 });
                const beaconMesh = new THREE.Mesh(beaconGeo, beaconMat);
                beaconMesh.position.set(bx, bh + 0.8, bz);
                this.scene.add(beaconMesh);
                this.rooftopBeacons.push({
                    mesh: beaconMesh,
                    phase: (bx + bz) * 0.1
                });
            }

            validBuildings++;
        }
        buildingInst.count = validBuildings;
        buildingInst.instanceMatrix.needsUpdate = true;
        if (buildingInst.instanceColor) buildingInst.instanceColor.needsUpdate = true;
        this.scene.add(buildingInst);

        // 2. High-Performance Instanced Greenery & Trees (2 draw calls instead of 960)
        const trunkGeo = new THREE.CylinderGeometry(0.7, 1.2, 10, 6);
        const trunkMat = new THREE.MeshStandardMaterial({ color: 0x45220a, roughness: 0.95 });
        const trunkInst = new THREE.InstancedMesh(trunkGeo, trunkMat, 480);
        trunkInst.instanceMatrix.setUsage(THREE.StaticDrawUsage);

        const canopyGeo = new THREE.IcosahedronGeometry(5.0, 1);
        const canopyMat = new THREE.MeshStandardMaterial({ color: 0x16a34a, roughness: 0.9 });
        const canopyInst = new THREE.InstancedMesh(canopyGeo, canopyMat, 480);
        canopyInst.instanceMatrix.setUsage(THREE.StaticDrawUsage);

        const treeColors = [0x15803d, 0x16a34a, 0x22c55e, 0xea580c, 0x9333ea];
        let validTrees = 0;

        for (let i = 0; i < 480; i++) {
            const tx = (rng() - 0.5) * 920;
            const tz = (rng() - 0.5) * 920;

            let blocked = false;
            for (const pos of Object.values(this._sectorWorldPos)) {
                const dx = tx - pos.x, dz = tz - pos.z;
                if (Math.sqrt(dx * dx + dz * dz) < 40) { blocked = true; break; }
            }
            if (blocked) continue;

            const th = 8 + rng() * 9;
            const scaleY = th / 10.0;
            dummy.position.set(tx, th / 2, tz);
            dummy.scale.set(1, scaleY, 1);
            dummy.rotation.set(0, 0, 0);
            dummy.updateMatrix();
            trunkInst.setMatrixAt(validTrees, dummy.matrix);

            const canopyR = (4.5 + rng() * 4.5) / 5.0;
            dummy.position.set(tx, th + canopyR * 2.2, tz);
            dummy.scale.set(canopyR, canopyR, canopyR);
            dummy.updateMatrix();
            canopyInst.setMatrixAt(validTrees, dummy.matrix);

            const col = new THREE.Color(treeColors[Math.floor(rng() * treeColors.length)]);
            canopyInst.setColorAt(validTrees, col);
            validTrees++;
        }
        trunkInst.count = validTrees;
        canopyInst.count = validTrees;
        trunkInst.instanceMatrix.needsUpdate = true;
        canopyInst.instanceMatrix.needsUpdate = true;
        if (canopyInst.instanceColor) canopyInst.instanceColor.needsUpdate = true;
        this.scene.add(trunkInst);
        this.scene.add(canopyInst);
    }

    _seededRng(seed) {
        let s = seed;
        return () => { s = (s * 1664525 + 1013904223) & 0xffffffff; return (s >>> 0) / 0xffffffff; };
    }

    createLakes() {
        const waterMat = new THREE.MeshStandardMaterial({
            color: 0x0891b2, emissive: 0x003355, emissiveIntensity: 0.4,
            roughness: 0.05, metalness: 0.45, transparent: true, opacity: 0.88
        });

        const ulGeo = new THREE.CircleGeometry(42, 40);
        const ul = new THREE.Mesh(ulGeo, waterMat);
        ul.rotation.x = -Math.PI / 2;
        ul.position.set(60, 0.4, 55);
        this.scene.add(ul);
        const ulLight = new THREE.PointLight(0x06b6d4, 1.8, 120);
        ulLight.position.set(60, 8, 55);
        this.scene.add(ulLight);

        const blPts = new THREE.EllipseCurve(0, 0, 58, 34, 0, Math.PI * 2, false, 0).getPoints(40);
        const bl = new THREE.Mesh(new THREE.ShapeGeometry(new THREE.Shape(blPts)), waterMat.clone());
        bl.rotation.x = -Math.PI / 2;
        bl.position.set(80, 0.4, 190);
        this.scene.add(bl);

        const st = new THREE.Mesh(new THREE.CircleGeometry(28, 32), waterMat.clone());
        st.rotation.x = -Math.PI / 2;
        st.position.set(-230, 0.4, -180);
        this.scene.add(st);
    }

    create16BengaluruSectors() {
        Object.entries(this.SECTOR_LAYOUT).forEach(([key, s]) => {
            const wp = this._sectorWorldPos[key];
            const { x, z } = wp;
            const group = new THREE.Group();
            group.position.set(x, 0, z);

            const plazaGeo = new THREE.CylinderGeometry(s.radius, s.radius + 5, 3.0, 36);
            const plazaMat = new THREE.MeshStandardMaterial({
                color: 0x142438, roughness: 0.75, metalness: 0.25
            });
            const plaza = new THREE.Mesh(plazaGeo, plazaMat);
            plaza.position.y = 1.5;
            plaza.receiveShadow = true;
            group.add(plaza);

            const decalGeo = new THREE.TorusGeometry(s.radius - 1.5, 1.2, 8, 48);
            const decalMat = new THREE.MeshBasicMaterial({ color: s.color });
            const decal = new THREE.Mesh(decalGeo, decalMat);
            decal.rotation.x = -Math.PI / 2;
            decal.position.y = 3.1;
            group.add(decal);

            const auraGeo = new THREE.TorusGeometry(s.radius + 3.5, 0.5, 6, 48);
            const auraMat = new THREE.MeshBasicMaterial({ color: s.color, transparent: true, opacity: 0.6 });
            const auraMesh = new THREE.Mesh(auraGeo, auraMat);
            auraMesh.rotation.x = -Math.PI / 2;
            auraMesh.position.y = 0.5;
            group.add(auraMesh);

            this.buildSectorArchitecture(key, group, s);

            const label = this.createTextSprite(s.name, s.color, 14);
            label.position.set(0, s.bldgH + 24, 0);
            group.add(label);

            const hitGeo = new THREE.CylinderGeometry(s.radius, s.radius, s.bldgH + 10, 12);
            const hitMat = new THREE.MeshBasicMaterial({ visible: false });
            const hitMesh = new THREE.Mesh(hitGeo, hitMat);
            hitMesh.position.y = (s.bldgH + 10) / 2;
            hitMesh.userData = { type: 'sector', key, name: s.name };
            group.add(hitMesh);

            this.scene.add(group);
            this.sectorObjects.set(key, { group, worldX: x, worldZ: z, metadata: s });
        });
    }

    buildSectorArchitecture(key, group, s) {
        const c = s.color;
        const glassMat = (col) => new THREE.MeshStandardMaterial({
            color: col, metalness: 0.95, roughness: 0.08, transparent: true, opacity: 0.78
        });
        const concMat = (col) => new THREE.MeshStandardMaterial({
            color: col, roughness: 0.58, metalness: 0.25
        });
        const emitMat = (col, em) => new THREE.MeshStandardMaterial({
            color: col, emissive: em, emissiveIntensity: 0.95
        });

        if (key === 'Kempegowda_Airport_BLR') {
            const terminal = new THREE.Mesh(new THREE.BoxGeometry(84, 16, 28), concMat(0xe2d7bf));
            terminal.position.set(0, 11, -12);
            terminal.castShadow = true;
            group.add(terminal);

            const atc = new THREE.Mesh(new THREE.CylinderGeometry(3.5, 4.5, 42, 12), concMat(0xc4b89e));
            atc.position.set(32, 24, -12);
            group.add(atc);
            const cab = new THREE.Mesh(new THREE.CylinderGeometry(6.5, 5.5, 8, 14), glassMat(0x38bdf8));
            cab.position.set(32, 47, -12);
            group.add(cab);

            for (let i = -5; i <= 5; i++) {
                const rl = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.6, 1.2), emitMat(0xfef08a, 0xfef08a));
                rl.position.set(i * 7.5, 1.8, -28);
                group.add(rl);
            }

        } else if (key === 'Vidhana_Soudha_Capitol') {
            const base = new THREE.Mesh(new THREE.BoxGeometry(54, 18, 30), concMat(0xd4cbb4));
            base.position.set(0, 12, -8);
            base.castShadow = true;
            group.add(base);

            for (let i = -3; i <= 3; i++) {
                const col = new THREE.Mesh(new THREE.CylinderGeometry(1.6, 2.0, 16, 10), concMat(0xc5bb9f));
                col.position.set(i * 7.5, 12, 8);
                group.add(col);
            }
            const drum = new THREE.Mesh(new THREE.CylinderGeometry(9, 10, 10, 18), concMat(0xcdb870));
            drum.position.set(0, 26, -8);
            group.add(drum);
            const dome = new THREE.Mesh(new THREE.SphereGeometry(12, 24, 12, 0, Math.PI*2, 0, Math.PI/2),
                new THREE.MeshStandardMaterial({ color: 0xf59e0b, metalness: 0.95, roughness: 0.05, emissive: 0xb45309, emissiveIntensity: 0.4 }));
            dome.position.set(0, 31, -8);
            group.add(dome);

        } else if (key === 'UB_City_Luxury_Towers') {
            const towers = [
                { h: 96, ox: -16, oz: -8 },
                { h: 78, ox:   0, oz:  2 },
                { h: 64, ox:  16, oz: -6 }
            ];
            const luxMat = this.luxuryWindowMat || this._createWindowAtlas('luxury');
            towers.forEach(t => {
                const tw = new THREE.Mesh(new THREE.BoxGeometry(14, t.h, 14), luxMat);
                tw.position.set(t.ox, t.h / 2 + 3, t.oz);
                tw.castShadow = true;
                group.add(tw);
                this._addNeonWireframe(tw, 0xffb700, 0.7);

                // Luxury Golden Crown
                const crown = new THREE.Mesh(new THREE.BoxGeometry(15, 2.8, 15), emitMat(0xffb700, 0xffb700));
                crown.position.set(t.ox, t.h + 4, t.oz);
                group.add(crown);
                this._addNeonWireframe(crown, 0xffffff, 0.95);

                // Communication Spire with Aviation Warning Beacon
                const spire = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.5, 14, 6), concMat(0x64748b));
                spire.position.set(t.ox, t.h + 12, t.oz);
                group.add(spire);

                const beacon = new THREE.Mesh(new THREE.SphereGeometry(0.85, 8, 8), new THREE.MeshBasicMaterial({ color: 0xff0033 }));
                beacon.position.set(t.ox, t.h + 19, t.oz);
                group.add(beacon);
                this.rooftopBeacons.push({ mesh: beacon, phase: t.ox * 0.2 });

                // GLM-5.2 Architectural Crown: Rooftop Helipad on Tallest UB City Tower
                if (t.ox === -16) {
                    const padBase = new THREE.Mesh(new THREE.CylinderGeometry(7.5, 7.5, 0.8, 24), concMat(0x1e2430));
                    padBase.position.set(t.ox, t.h + 5.6, t.oz);
                    group.add(padBase);
                    const padRing = new THREE.Mesh(new THREE.RingGeometry(5.4, 6.2, 24), new THREE.MeshBasicMaterial({ color: 0xffd700, side: THREE.DoubleSide }));
                    padRing.rotation.x = -Math.PI / 2;
                    padRing.position.set(t.ox, t.h + 6.05, t.oz);
                    group.add(padRing);
                    const hMat = new THREE.MeshBasicMaterial({ color: 0xffd700 });
                    const hL = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.1, 3.6), hMat);
                    hL.position.set(t.ox - 1.4, t.h + 6.06, t.oz);
                    group.add(hL);
                    const hR = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.1, 3.6), hMat);
                    hR.position.set(t.ox + 1.4, t.h + 6.06, t.oz);
                    group.add(hR);
                    const hMid = new THREE.Mesh(new THREE.BoxGeometry(2.1, 0.1, 0.7), hMat);
                    hMid.position.set(t.ox, t.h + 6.06, t.oz);
                    group.add(hMid);
                    for (let a = 0; a < 8; a++) {
                        const ang = (a / 8) * Math.PI * 2;
                        const hl = new THREE.Mesh(new THREE.SphereGeometry(0.35, 6, 6), new THREE.MeshBasicMaterial({ color: a % 2 === 0 ? 0x10b981 : 0xffaa00 }));
                        hl.position.set(t.ox + Math.cos(ang) * 6.8, t.h + 6.1, t.oz + Math.sin(ang) * 6.8);
                        group.add(hl);
                    }
                }
            });

        } else if (key === 'Cubbon_Park_Canopy') {
            for (let i = 0; i < 24; i++) {
                const tx = (Math.random() - 0.5) * 56, tz = (Math.random() - 0.5) * 56;
                const th = 10 + Math.random() * 8;
                const trunk = new THREE.Mesh(new THREE.CylinderGeometry(1.0, 1.5, th, 7), concMat(0x5c3d1e));
                trunk.position.set(tx, th / 2 + 2, tz);
                group.add(trunk);
                const ls = 7 + Math.random() * 5;
                const leaves = new THREE.Mesh(new THREE.IcosahedronGeometry(ls, 1),
                    new THREE.MeshStandardMaterial({ color: [0x15803d, 0x166534, 0x16a34a, 0x22c55e][Math.floor(Math.random() * 4)], roughness: 0.9 }));
                leaves.position.set(tx, th + ls * 0.5 + 2, tz);
                group.add(leaves);
            }
            const bs = new THREE.Mesh(new THREE.CylinderGeometry(9, 11, 6, 12), concMat(0xf4ebd0));
            bs.position.set(0, 5, 0);
            group.add(bs);
            const bsRoof = new THREE.Mesh(new THREE.ConeGeometry(13, 8, 12), concMat(0xd97706));
            bsRoof.position.set(0, 12, 0);
            group.add(bsRoof);

        } else if (key === 'Majestic_Metro_Interchange') {
            const station = new THREE.Mesh(new THREE.BoxGeometry(52, 20, 28), concMat(0x1e3a5f));
            station.position.set(0, 13, -10);
            station.castShadow = true;
            group.add(station);
            const canopy = new THREE.Mesh(new THREE.BoxGeometry(60, 2.5, 36), glassMat(0x38bdf8));
            canopy.position.set(0, 24, -10);
            group.add(canopy);

        } else if (key === 'Electronic_City_Phase_1') {
            const ecMat = this.windowAtlasMat || this._createWindowAtlas('tech');
            [-18, 18].forEach((ox, bi) => {
                const t = new THREE.Mesh(new THREE.BoxGeometry(16, 74, 16), ecMat);
                t.position.set(ox, 40, -10);
                t.castShadow = true;
                group.add(t);
                this._addNeonWireframe(t, 0x00f5ff, 0.75);

                const top = new THREE.Mesh(new THREE.BoxGeometry(18, 3.2, 18), emitMat(0x38bdf8, 0x0284c7));
                top.position.set(ox, 78, -10);
                group.add(top);
                this._addNeonWireframe(top, 0x00f5ff, 0.95);

                const spire = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.5, 16, 6), concMat(0x475569));
                spire.position.set(ox, 86, -10);
                group.add(spire);

                const beacon = new THREE.Mesh(new THREE.SphereGeometry(0.85, 8, 8), new THREE.MeshBasicMaterial({ color: 0xff0033 }));
                beacon.position.set(ox, 94, -10);
                group.add(beacon);
                this.rooftopBeacons.push({ mesh: beacon, phase: bi * 1.5 });
            });
            const dc = new THREE.Mesh(new THREE.BoxGeometry(28, 18, 22), concMat(0x0f172a));
            dc.position.set(0, 12, 10);
            group.add(dc);

                } else if (key === 'IISc_Research_Campus') {
            this._buildAcademyAndSchool(key, group, s, glassMat, concMat, emitMat);
        } else if (key === 'Manyata_Tech_Park' || key === 'Whitefield_ITPB' || key === 'Bagmane_Tech_Park') {
            this._buildTechParkOffice(key, group, s, glassMat, concMat, emitMat);
        } else if (key === 'Church_Street_Cafes') {
            this._buildArtisanCafe(key, group, s, glassMat, concMat, emitMat);
        } else if (key === 'Indiranagar_100ft_Startups') {
            this._buildStartupStudio(key, group, s, glassMat, concMat, emitMat);
        } else if (key === 'Gandhi_Bazaar_Heritage') {
            this._buildHeritageDarshini(key, group, s, glassMat, concMat, emitMat);
        } else if (key === 'Nexus_Koramangala_Mall') {
            this._buildCommercialMallShops(key, group, s, glassMat, concMat, emitMat);
        } else if (key === 'Koramangala_Microbrewery_Pub') {
            this._buildCraftMicrobrewery(key, group, s, glassMat, concMat, emitMat);
        } else if (key === 'HSR_Cult_Fit_Gym') {
            this._buildCultFitGym(key, group, s, glassMat, concMat, emitMat);
        } else if (key === 'Cubbon_Park_Canopy') {
            this._buildBotanicalPark(key, group, s, glassMat, concMat, emitMat);
        } else if (key === 'MG_Road_Boulevard' || key === 'Majestic_Metro_Interchange') {
            this._buildBMTCBusTerminal(key, group, s, glassMat, concMat, emitMat);
        } else if (key === 'Bull_Temple_Basavanagudi') {
            this._buildTempleArchitecture(key, group, s, glassMat, concMat, emitMat);
        } else if (key === 'St_Marks_Cathedral_Churches') {
            this._buildChurchArchitecture(key, group, s, glassMat, concMat, emitMat);
        } else if (key === 'Dev_Coliving_Citizen_Residences') {
            this._buildCoLivingResidences(key, group, s, glassMat, concMat, emitMat);
        } else if (key === 'Bengaluru_Care_Hospital_Clinic') {
            this._buildCareHospital(key, group, s, glassMat, concMat, emitMat);
        } else {
            const bMat = this.windowAtlasMat || this._createWindowAtlas('tech');
            [-14, 14].forEach((ox, bi) => {
                const bh = s.bldgH * (0.65 + bi * 0.3);
                const bw = 14, bd = 14;
                const bMesh = new THREE.Mesh(new THREE.BoxGeometry(bw, bh, bd), bMat);
                bMesh.position.set(ox, bh / 2 + 3, -10);
                bMesh.castShadow = true;
                group.add(bMesh);
                this._addNeonWireframe(bMesh, c, 0.7);

                if (bh > 36) {
                    const spire = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.45, 10, 4), concMat(0x64748b));
                    spire.position.set(ox, bh + 8, -10);
                    group.add(spire);

                    const beacon = new THREE.Mesh(new THREE.SphereGeometry(0.75, 6, 6), new THREE.MeshBasicMaterial({ color: 0xff0033 }));
                    beacon.position.set(ox, bh + 13, -10);
                    group.add(beacon);
                    this.rooftopBeacons.push({ mesh: beacon, phase: ox * 0.3 });
                }
            });
        }
    }

    _buildAcademyAndSchool(key, group, s, glassMat, concMat, emitMat) {
        // The Bangalore Academy & Computing Institute (IISc Campus)
        // 1. Tiered Amphitheater Main Floor
        const hallFloor = new THREE.Mesh(new THREE.BoxGeometry(50, 0.8, 36), concMat(0x0f172a));
        hallFloor.position.set(0, 2.6, 4);
        group.add(hallFloor);
        this._addNeonWireframe(hallFloor, 0x00f5ff, 0.75);

        // Glass Curtain Perimeter with Neon Top Railing
        const backGlass = new THREE.Mesh(new THREE.BoxGeometry(50, 14, 0.4), glassMat(0x38bdf8));
        backGlass.position.set(0, 9.6, -14);
        group.add(backGlass);
        this._addNeonWireframe(backGlass, 0x00f5ff, 0.6);

        const leftGlass = new THREE.Mesh(new THREE.BoxGeometry(0.4, 14, 36), glassMat(0x38bdf8));
        leftGlass.position.set(-25, 9.6, 4);
        group.add(leftGlass);

        const rightGlass = new THREE.Mesh(new THREE.BoxGeometry(0.4, 14, 36), glassMat(0x38bdf8));
        rightGlass.position.set(25, 9.6, 4);
        group.add(rightGlass);

        // Academy Canopy / Roof Structure
        const roofSlab = new THREE.Mesh(new THREE.BoxGeometry(52, 0.6, 38), concMat(0x1e293b));
        roofSlab.position.set(0, 16.8, 4);
        group.add(roofSlab);
        this._addNeonWireframe(roofSlab, 0xffb700, 0.9);

        // 2. High-Tech Digital Smart Blackboard (18m x 6.5m)
        const boardFrame = new THREE.Mesh(new THREE.BoxGeometry(22, 7.5, 0.6), concMat(0x020617));
        boardFrame.position.set(0, 8.5, -13.4);
        group.add(boardFrame);
        this._addNeonWireframe(boardFrame, 0x00ff88, 0.95);

        // Glowing Screen Surface
        const boardScreen = new THREE.Mesh(new THREE.PlaneGeometry(21.2, 6.8), emitMat(0x002b36, 0x00ffcc));
        boardScreen.position.set(0, 8.5, -13.05);
        group.add(boardScreen);

        // Digital Blackboard Code Lines (Visual Representation)
        const codeLinesCount = 7;
        for (let l = 0; l < codeLinesCount; l++) {
            const lineMesh = new THREE.Mesh(
                new THREE.BoxGeometry(16 - (l % 3) * 3, 0.22, 0.05),
                emitMat(l % 2 === 0 ? 0x00f5ff : 0xffb700, l % 2 === 0 ? 0x00f5ff : 0xffb700)
            );
            lineMesh.position.set(-1.5, 10.8 - l * 0.75, -13.0);
            group.add(lineMesh);
        }

        // 3. Teacher's Stage & Illuminated Smart Podium
        const stage = new THREE.Mesh(new THREE.BoxGeometry(16, 0.8, 8), concMat(0x1e293b));
        stage.position.set(0, 3.2, -8);
        group.add(stage);
        this._addNeonWireframe(stage, 0xffb700, 0.85);

        const lectern = new THREE.Mesh(new THREE.BoxGeometry(2.4, 2.8, 1.4), concMat(0x334155));
        lectern.position.set(0, 4.8, -8);
        group.add(lectern);
        this._addNeonWireframe(lectern, 0x00f5ff, 0.9);

        // Lectern Interactive Touch Screen
        const lecternScreen = new THREE.Mesh(new THREE.BoxGeometry(2.0, 0.08, 1.0), emitMat(0x00f5ff, 0x00f5ff));
        lecternScreen.position.set(0, 6.25, -8);
        lecternScreen.rotation.x = -0.3;
        group.add(lecternScreen);

        // 4. Student Tiered Desks & High-Performance Laptops
        const rows = [
            { z: -1, y: 3.0, desks: [-12, -4, 4, 12] },
            { z: 9,  y: 3.6, desks: [-14, -6, 2, 10] },
            { z: 17, y: 4.2, desks: [-12, -4, 4, 12] }
        ];

        rows.forEach((row, rIdx) => {
            const riser = new THREE.Mesh(new THREE.BoxGeometry(44, 0.6, 7.5), concMat(0x1e293b));
            riser.position.set(0, row.y - 0.3, row.z);
            group.add(riser);

            row.desks.forEach((dx) => {
                // Wooden / Steel Desk
                const deskTop = new THREE.Mesh(new THREE.BoxGeometry(4.2, 0.18, 2.0), concMat(0x475569));
                deskTop.position.set(dx, row.y + 1.5, row.z);
                group.add(deskTop);
                this._addNeonWireframe(deskTop, 0x00f5ff, 0.5);

                const deskLeg = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 1.5, 6), concMat(0x0f172a));
                deskLeg.position.set(dx - 1.8, row.y + 0.75, row.z);
                group.add(deskLeg);
                const deskLeg2 = deskLeg.clone();
                deskLeg2.position.set(dx + 1.8, row.y + 0.75, row.z);
                group.add(deskLeg2);

                // Student Chair
                const seat = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.15, 1.6), concMat(0x2563eb));
                seat.position.set(dx, row.y + 0.9, row.z + 1.6);
                group.add(seat);

                // Open Laptop Base
                const lapBase = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.06, 0.9), concMat(0x94a3b8));
                lapBase.position.set(dx, row.y + 1.62, row.z);
                group.add(lapBase);

                // Open Laptop Screen (Tilted)
                const lapScreen = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.8, 0.05), concMat(0x1e293b));
                lapScreen.position.set(dx, row.y + 2.05, row.z - 0.42);
                lapScreen.rotation.x = 0.22;
                group.add(lapScreen);

                // Glowing Laptop Display (Cyan / Amber)
                const lapGlow = new THREE.Mesh(new THREE.PlaneGeometry(1.1, 0.7), emitMat(rIdx % 2 === 0 ? 0x00f5ff : 0xffb700, rIdx % 2 === 0 ? 0x00f5ff : 0xffb700));
                lapGlow.position.set(dx, row.y + 2.05, row.z - 0.39);
                lapGlow.rotation.x = 0.22;
                group.add(lapGlow);

                // Student Notebook / Tablet
                const noteTab = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.04, 1.1), emitMat(0x10b981, 0x10b981));
                noteTab.position.set(dx + 1.3, row.y + 1.62, row.z);
                group.add(noteTab);
            });
        });

        // 5. Server Cluster Rack (IISc High-Performance AI Lab)
        const rackMesh = new THREE.Mesh(new THREE.BoxGeometry(3.6, 8.0, 2.2), concMat(0x0b1120));
        rackMesh.position.set(-21, 6.6, -10);
        group.add(rackMesh);
        this._addNeonWireframe(rackMesh, 0x00ff88, 0.9);

        for (let led = 0; led < 8; led++) {
            const ledLight = new THREE.Mesh(new THREE.BoxGeometry(3.0, 0.15, 0.08), emitMat(led % 2 === 0 ? 0x00ff88 : 0x00f5ff, led % 2 === 0 ? 0x00ff88 : 0x00f5ff));
            ledLight.position.set(-21, 3.5 + led * 0.85, -8.85);
            group.add(ledLight);
        }

        // Room Warm Ambient Spot
        const hallLight = new THREE.PointLight(0x00f5ff, 1.4, 45);
        hallLight.position.set(0, 14, 0);
        group.add(hallLight);
    }

    _buildTechParkOffice(key, group, s, glassMat, concMat, emitMat) {
        // 1. Sleek Glass Tech Park Office Pavilion
        const officeFloor = new THREE.Mesh(new THREE.BoxGeometry(46, 0.6, 32), concMat(0x0f172a));
        officeFloor.position.set(0, 2.8, 4);
        group.add(officeFloor);

        // Glass Curtain Walls
        const glassWall = new THREE.Mesh(new THREE.BoxGeometry(46, 12, 0.4), glassMat(0x38bdf8));
        glassWall.position.set(0, 8.8, -12);
        group.add(glassWall);
        const glassSideL = new THREE.Mesh(new THREE.BoxGeometry(0.4, 12, 32), glassMat(0x38bdf8));
        glassSideL.position.set(-23, 8.8, 4);
        group.add(glassSideL);
        const glassSideR = glassSideL.clone();
        glassSideR.position.x = 23;
        group.add(glassSideR);

        // Office Roof Canopy
        const roof = new THREE.Mesh(new THREE.BoxGeometry(48, 1.2, 34), concMat(0x1e293b));
        roof.position.set(0, 15, 4);
        group.add(roof);
        this._addNeonWireframe(roof, 0x00f5ff, 0.75);

        // Corporate High-Rise Skyscraper Tower Rising Behind Office Pavilion
        const towerMat = this.windowAtlasMat || this._createWindowAtlas('tech');
        const mainTower = new THREE.Mesh(new THREE.BoxGeometry(46, 74, 18), towerMat);
        mainTower.position.set(0, 40, -23);
        mainTower.castShadow = true;
        group.add(mainTower);
        this._addNeonWireframe(mainTower, 0x00f5ff, 0.85);

        // Tower Glowing Parapet Crown
        const crown = new THREE.Mesh(new THREE.BoxGeometry(48, 3.2, 20), emitMat(0x0284c7, 0x38bdf8));
        crown.position.set(0, 78, -23);
        group.add(crown);
        this._addNeonWireframe(crown, 0x00f5ff, 0.95);

        // Corporate Communication Spire with Aviation Warning Beacon
        const spire = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.7, 18, 6), concMat(0x475569));
        spire.position.set(0, 88, -23);
        group.add(spire);

        const beacon = new THREE.Mesh(new THREE.SphereGeometry(1.0, 8, 8), new THREE.MeshBasicMaterial({ color: 0xff0033 }));
        beacon.position.set(0, 97.5, -23);
        group.add(beacon);
        this.rooftopBeacons.push({ mesh: beacon, phase: 0.0 });

        // Workstation Desks (4 Coding Desks with Dual Glowing Monitors & Chairs)
        const deskMat = concMat(0x334155);
        const screenMatBlue = emitMat(0x0284c7, 0x38bdf8);
        const screenMatGreen = emitMat(0x059669, 0x10b981);
        const chairMat = concMat(0x1e293b);

        const deskPositions = [
            { x: -12, z:  7, rot: 0 },
            { x:  12, z:  7, rot: 0 },
            { x: -12, z: 15, rot: Math.PI },
            { x:  12, z: 15, rot: Math.PI }
        ];

        deskPositions.forEach((dp, i) => {
            const desk = new THREE.Mesh(new THREE.BoxGeometry(8, 0.35, 4.2), deskMat);
            desk.position.set(dp.x, 4.8, dp.z);
            group.add(desk);

            const leg1 = new THREE.Mesh(new THREE.BoxGeometry(0.3, 2.0, 0.3), concMat(0x64748b));
            leg1.position.set(dp.x - 3.7, 3.8, dp.z - 1.8);
            group.add(leg1);
            const leg2 = leg1.clone(); leg2.position.x = dp.x + 3.7; group.add(leg2);

            // High-Fidelity Dual Curved Glowing Monitors (Autopolis Style)
            const m1 = new THREE.Mesh(new THREE.BoxGeometry(3.2, 1.9, 0.12), emitMat(0x00f5ff, 0x38bdf8));
            m1.position.set(dp.x - 1.8, 6.2, dp.z + (dp.rot === 0 ? -1.4 : 1.4));
            m1.rotation.y = (dp.rot === 0 ? 0.18 : -0.18);
            group.add(m1);
            this._addNeonWireframe(m1, 0x00f5ff, 0.95);

            const m2 = new THREE.Mesh(new THREE.BoxGeometry(3.2, 1.9, 0.12), emitMat(0x00ff88, 0x10b981));
            m2.position.set(dp.x + 1.8, 6.2, dp.z + (dp.rot === 0 ? -1.4 : 1.4));
            m2.rotation.y = (dp.rot === 0 ? -0.22 : 0.22);
            group.add(m2);
            this._addNeonWireframe(m2, 0x00ff88, 0.95);

            // Backlit Mechanical RGB Keyboard
            const kb = new THREE.Mesh(new THREE.BoxGeometry(2.6, 0.12, 1.1), emitMat(0xff007f, 0xa855f7));
            kb.position.set(dp.x, 5.0, dp.z + (dp.rot === 0 ? -0.3 : 0.3));
            group.add(kb);

            // Workstation Gaming PC Tower with RGB Window
            const pcTower = new THREE.Mesh(new THREE.BoxGeometry(1.2, 2.8, 2.4), concMat(0x0f172a));
            pcTower.position.set(dp.x + 3.2, 4.2, dp.z);
            group.add(pcTower);
            this._addNeonWireframe(pcTower, 0x00f5ff, 0.85);
            const pcRgb = new THREE.Mesh(new THREE.BoxGeometry(0.1, 2.0, 1.8), emitMat(0x00f5ff, 0xff007f));
            pcRgb.position.set(dp.x + 3.8, 4.2, dp.z);
            group.add(pcRgb);

            // Brass Degree Filter Coffee Tumbler
            const coffee = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.45, 0.9, 8), concMat(0xd97706));
            coffee.position.set(dp.x - 2.8, 5.3, dp.z + (dp.rot === 0 ? -0.3 : 0.3));
            group.add(coffee);

            const seat = new THREE.Mesh(new THREE.BoxGeometry(3.2, 0.4, 3.2), chairMat);
            seat.position.set(dp.x, 4.2, dp.z + (dp.rot === 0 ? 1.8 : -1.8));
            group.add(seat);
            const backrest = new THREE.Mesh(new THREE.BoxGeometry(3.0, 3.2, 0.4), chairMat);
            backrest.position.set(dp.x, 5.8, dp.z + (dp.rot === 0 ? 3.2 : -3.2));
            group.add(backrest);
        });

        // Conference Room (Central Oval Table & Whiteboard)
        const confTable = new THREE.Mesh(new THREE.BoxGeometry(16, 0.4, 8), concMat(0x475569));
        confTable.position.set(0, 4.8, -5);
        group.add(confTable);

        const wb = new THREE.Mesh(new THREE.PlaneGeometry(14, 6), emitMat(0xffffff, 0xf1f5f9));
        wb.position.set(0, 9.5, -11.6);
        group.add(wb);

        const confChairs = [
            { x: -5, z: -5 },
            { x:  5, z: -5 },
            { x: -2, z: -2 },
            { x:  2, z: -8 }
        ];
        confChairs.forEach(cp => {
            const cs = new THREE.Mesh(new THREE.BoxGeometry(2.8, 0.35, 2.8), chairMat);
            cs.position.set(cp.x, 4.2, cp.z);
            group.add(cs);
        });
    }

    _buildArtisanCafe(key, group, s, glassMat, concMat, emitMat) {
        // Warm Brick Timber Patio
        const deck = new THREE.Mesh(new THREE.CylinderGeometry(28, 29, 0.5, 28), concMat(0x4a2e18));
        deck.position.set(0, 2.7, 0);
        group.add(deck);

        // Cafe Counter / Kiosk ("CHURCH ST. ROASTERS")
        const counter = new THREE.Mesh(new THREE.BoxGeometry(18, 4.0, 5.5), concMat(0x27170c));
        counter.position.set(0, 4.8, -12);
        group.add(counter);

        const coffeeMachine = new THREE.Mesh(new THREE.BoxGeometry(3.5, 2.4, 2.2), concMat(0x94a3b8));
        coffeeMachine.position.set(-4, 7.8, -12);
        group.add(coffeeMachine);

        const awning = new THREE.Mesh(new THREE.BoxGeometry(20, 0.6, 7), emitMat(0xf97316, 0xea580c));
        awning.rotation.x = Math.PI * 0.12;
        awning.position.set(0, 10.5, -10);
        group.add(awning);

        // 3 Cafe Tables with Striped Umbrellas
        const tableSpots = [
            { x: -10, z:  3, color: 0xf59e0b },
            { x:  10, z:  3, color: 0x06b6d4 },
            { x:   0, z: -3, color: 0x10b981 }
        ];

        tableSpots.forEach(tp => {
            const table = new THREE.Mesh(new THREE.CylinderGeometry(3.8, 3.8, 0.35, 16), concMat(0x78350f));
            table.position.set(tp.x, 4.8, tp.z);
            group.add(table);
            const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.35, 2.0, 8), concMat(0x334155));
            leg.position.set(tp.x, 3.8, tp.z);
            group.add(leg);

            const cup1 = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.25, 0.5, 8), emitMat(0xffffff, 0xf8fafc));
            cup1.position.set(tp.x - 1.2, 5.2, tp.z + 0.4);
            group.add(cup1);
            const cup2 = cup1.clone(); cup2.position.x = tp.x + 1.2; group.add(cup2);

            const laptop = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.1, 1.2), concMat(0x64748b));
            laptop.position.set(tp.x, 5.0, tp.z - 0.8);
            group.add(laptop);

            const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 10, 8), concMat(0xd4d4d8));
            pole.position.set(tp.x, 8.0, tp.z);
            group.add(pole);

            const canopy = new THREE.Mesh(new THREE.ConeGeometry(5.4, 2.0, 12), emitMat(tp.color, tp.color));
            canopy.position.set(tp.x, 12.8, tp.z);
            group.add(canopy);

            [-2.6, 2.6].forEach(cx => {
                const chair = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.3, 2.4), concMat(0x374151));
                chair.position.set(tp.x + cx, 4.2, tp.z);
                group.add(chair);
            });
        });
    }

    _buildStartupStudio(key, group, s, glassMat, concMat, emitMat) {
        // Indiranagar 100ft AI Startup Loft Studio
        const studioFloor = new THREE.Mesh(new THREE.BoxGeometry(40, 0.5, 28), concMat(0x18181b));
        studioFloor.position.set(0, 2.8, 0);
        group.add(studioFloor);

        const glassFront = new THREE.Mesh(new THREE.BoxGeometry(40, 10, 0.4), glassMat(0xbc8cff));
        glassFront.position.set(0, 7.8, -10);
        group.add(glassFront);

        [-9, 9].forEach(dx => {
            const sDesk = new THREE.Mesh(new THREE.BoxGeometry(7, 0.35, 3.8), concMat(0x71717a));
            sDesk.position.set(dx, 5.8, 4);
            group.add(sDesk);
            const m = new THREE.Mesh(new THREE.BoxGeometry(2.6, 1.8, 0.15), emitMat(0xa855f7, 0xc084fc));
            m.position.set(dx, 7.0, 3.0);
            group.add(m);
        });

        const loungeTable = new THREE.Mesh(new THREE.CylinderGeometry(4.2, 4.2, 0.4, 16), concMat(0x27272a));
        loungeTable.position.set(0, 4.4, -4);
        group.add(loungeTable);
    }

    _buildHeritageDarshini(key, group, s, glassMat, concMat, emitMat) {
        // Basavanagudi Heritage Darshini (Vidyarthi Bhavan style)
        const counter = new THREE.Mesh(new THREE.BoxGeometry(22, 4.2, 5.0), concMat(0xd4d4d8));
        counter.position.set(0, 4.8, -8);
        group.add(counter);

        for (let i = -3; i <= 3; i += 2) {
            const tumbler = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.35, 0.9, 8), emitMat(0xd97706, 0xb45309));
            tumbler.position.set(i * 2.8, 7.4, -7.5);
            group.add(tumbler);
        }

        const awning = new THREE.Mesh(new THREE.BoxGeometry(24, 0.5, 6), emitMat(0x15803d, 0x166534));
        awning.rotation.x = Math.PI * 0.1;
        awning.position.set(0, 10.0, -6);
        group.add(awning);

        [-8, 8].forEach(tx => {
            const table = new THREE.Mesh(new THREE.CylinderGeometry(3.4, 3.4, 0.3, 14), concMat(0xe2e8f0));
            table.position.set(tx, 5.0, 5);
            group.add(table);
            const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.4, 2.2, 8), concMat(0x64748b));
            leg.position.set(tx, 3.8, 5);
            group.add(leg);
        });
    }

    _buildCommercialMallShops(key, group, s, glassMat, concMat, emitMat) {
        // Koramangala Mall Shops & Displays
        const mallFloor = new THREE.Mesh(new THREE.BoxGeometry(44, 0.5, 26), concMat(0x1e293b));
        mallFloor.position.set(0, 2.8, 0);
        group.add(mallFloor);

        [-12, 0, 12].forEach((sx, i) => {
            const shopWall = new THREE.Mesh(new THREE.BoxGeometry(10, 8, 0.4), glassMat(0x38bdf8));
            shopWall.position.set(sx, 7.0, -8);
            group.add(shopWall);

            const awn = new THREE.Mesh(new THREE.BoxGeometry(10, 0.4, 4), emitMat(0xe3b341, 0xb45309));
            awn.position.set(sx, 11.2, -6);
            group.add(awn);
        });
    }

    _buildCraftMicrobrewery(key, group, s, glassMat, concMat, emitMat) {
        // Koramangala / Indiranagar Craft Beer Microbrewery (Toit Style)
        const brewFloor = new THREE.Mesh(new THREE.BoxGeometry(46, 0.6, 32), concMat(0x27170c));
        brewFloor.position.set(0, 2.8, 0);
        group.add(brewFloor);

        // Brick & Glass Facade
        const backWall = new THREE.Mesh(new THREE.BoxGeometry(46, 14, 0.5), concMat(0x451a03));
        backWall.position.set(0, 9.8, -15.5);
        group.add(backWall);

        const neonSign = new THREE.Mesh(new THREE.BoxGeometry(32, 2.4, 0.3), emitMat(0xf59e0b, 0xd97706));
        neonSign.position.set(0, 15.5, -15.2);
        group.add(neonSign);

        // 2 Shining Copper Fermentation Kettles
        const copperMat = new THREE.MeshStandardMaterial({ color: 0xb45309, metalness: 0.9, roughness: 0.15 });
        [-15, -7].forEach(kx => {
            const kettle = new THREE.Mesh(new THREE.CylinderGeometry(3.6, 3.6, 11, 18), copperMat);
            kettle.position.set(kx, 8.5, -9);
            group.add(kettle);

            const dome = new THREE.Mesh(new THREE.SphereGeometry(3.6, 16, 12, 0, Math.PI * 2, 0, Math.PI / 2), copperMat);
            dome.position.set(kx, 14.0, -9);
            group.add(dome);

            const pipe = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.3, 8, 8), concMat(0xd4d4d8));
            pipe.position.set(kx, 10, -5);
            pipe.rotation.x = Math.PI / 2;
            group.add(pipe);
        });

        // Polished Teak Bar Counter
        const barCounter = new THREE.Mesh(new THREE.BoxGeometry(24, 4.4, 4.0), concMat(0x78350f));
        barCounter.position.set(8, 5.0, 0);
        group.add(barCounter);

        // Draft Beer Taps
        for (let t = -3; t <= 3; t += 2) {
            const tap = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.22, 1.6, 8), concMat(0xe2e8f0));
            tap.position.set(8 + t * 2.2, 7.8, 0);
            group.add(tap);
        }

        // 4 High Bar Stools
        [2, 7, 12, 17].forEach(bx => {
            const stoolSeat = new THREE.Mesh(new THREE.CylinderGeometry(1.4, 1.4, 0.35, 12), concMat(0x0f172a));
            stoolSeat.position.set(bx, 4.2, 4.6);
            group.add(stoolSeat);
            const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.25, 3.8, 8), concMat(0xd4d4d8));
            leg.position.set(bx, 2.1, 4.6);
            group.add(leg);
        });

        // 2 High Barrel Tables with Foaming Beer Mugs
        [
            { x: -8, z: 8 },
            { x: 10, z: 12 }
        ].forEach(bp => {
            const barrel = new THREE.Mesh(new THREE.CylinderGeometry(2.6, 2.4, 4.2, 14), concMat(0x451a03));
            barrel.position.set(bp.x, 4.9, bp.z);
            group.add(barrel);

            // Frothy Beer Mugs
            [-0.8, 0.8].forEach(mx => {
                const mug = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.35, 0.9, 8), emitMat(0xfbbf24, 0xd97706));
                mug.position.set(bp.x + mx, 7.4, bp.z);
                group.add(mug);
                const foam = new THREE.Mesh(new THREE.SphereGeometry(0.42, 8, 6), emitMat(0xffffff, 0xf8fafc));
                foam.position.set(bp.x + mx, 7.85, bp.z);
                group.add(foam);
            });
        });
    }

    _buildCultFitGym(key, group, s, glassMat, concMat, emitMat) {
        // HSR / Indiranagar Cult.fit High-Tech Fitness Hub
        const gymFloor = new THREE.Mesh(new THREE.BoxGeometry(44, 0.5, 30), concMat(0x0f172a));
        gymFloor.position.set(0, 2.8, 0);
        group.add(gymFloor);

        // Agility Ladder Floor Markings
        const ladder = new THREE.Mesh(new THREE.BoxGeometry(32, 0.05, 4), emitMat(0xf97316, 0xea580c));
        ladder.position.set(0, 3.1, 8);
        group.add(ladder);

        // Glowing Neon Wall Slogan
        const gymBack = new THREE.Mesh(new THREE.BoxGeometry(44, 12, 0.5), concMat(0x18181b));
        gymBack.position.set(0, 8.8, -14.5);
        group.add(gymBack);

        const neonSlogan = new THREE.Mesh(new THREE.BoxGeometry(30, 2.0, 0.2), emitMat(0xef4444, 0xdc2626));
        neonSlogan.position.set(0, 13.0, -14.2);
        group.add(neonSlogan);

        // 2 Motorized Treadmills
        [-12, -5].forEach(tx => {
            const belt = new THREE.Mesh(new THREE.BoxGeometry(3.6, 0.4, 7.5), concMat(0x27272a));
            belt.position.set(tx, 3.4, 0);
            group.add(belt);

            const console = new THREE.Mesh(new THREE.BoxGeometry(2.8, 1.4, 0.4), emitMat(0x06b6d4, 0x0891b2));
            console.position.set(tx, 6.2, -3.4);
            group.add(console);

            [-1.6, 1.6].forEach(hx => {
                const bar = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 3.2, 6), concMat(0xd4d4d8));
                bar.position.set(tx + hx, 4.8, -1.6);
                group.add(bar);
            });
        });

        // Olympic Bench Press Station
        const bench = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.8, 6.0), concMat(0x18181b));
        bench.position.set(6, 3.6, -4);
        group.add(bench);

        const barRackL = new THREE.Mesh(new THREE.BoxGeometry(0.3, 4.2, 0.3), concMat(0x71717a));
        barRackL.position.set(4.6, 5.2, -6.5);
        group.add(barRackL);
        const barRackR = barRackL.clone();
        barRackR.position.x = 7.4;
        group.add(barRackR);

        const barbell = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 6.5, 8), concMat(0xe2e8f0));
        barbell.rotation.z = Math.PI / 2;
        barbell.position.set(6, 6.8, -6.5);
        group.add(barbell);

        [-2.8, 2.8].forEach(wx => {
            const plate = new THREE.Mesh(new THREE.CylinderGeometry(1.2, 1.2, 0.35, 12), concMat(0x0f172a));
            plate.rotation.z = Math.PI / 2;
            plate.position.set(6 + wx, 6.8, -6.5);
            group.add(plate);
        });

        // Dumbbell Rack
        const dRack = new THREE.Mesh(new THREE.BoxGeometry(8.0, 2.2, 1.4), concMat(0x52525b));
        dRack.position.set(15, 4.2, -4);
        group.add(dRack);

        // Pull-Up Calisthenics Rig
        const rigPostL = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 9.0, 8), concMat(0xef4444));
        rigPostL.position.set(8, 7.5, 6);
        group.add(rigPostL);
        const rigPostR = rigPostL.clone();
        rigPostR.position.x = 13;
        group.add(rigPostR);
        const chinBar = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.15, 5.0, 8), concMat(0xd4d4d8));
        chinBar.rotation.z = Math.PI / 2;
        chinBar.position.set(10.5, 11.8, 6);
        group.add(chinBar);
    }

    _buildBotanicalPark(key, group, s, glassMat, concMat, emitMat) {
        // Historic Cubbon Park 300-Acre Botanical Canopy & Jogging Grounds
        const grassDisc = new THREE.Mesh(new THREE.CylinderGeometry(34, 35, 0.5, 32), concMat(0x16a34a));
        grassDisc.position.set(0, 2.7, 0);
        group.add(grassDisc);

        // Cobblestone Jogging Ring
        const trackGeo = new THREE.RingGeometry(18, 24, 32);
        const trackMat = new THREE.MeshStandardMaterial({ color: 0xd4d4d8, roughness: 0.8 });
        const track = new THREE.Mesh(trackGeo, trackMat);
        track.rotation.x = -Math.PI / 2;
        track.position.y = 2.96;
        group.add(track);

        // Central Ornate 2-Tier Fountain
        const pool = new THREE.Mesh(new THREE.CylinderGeometry(7.0, 7.4, 1.2, 24), concMat(0xf8fafc));
        pool.position.set(0, 3.4, 0);
        group.add(pool);

        const waterDisc = new THREE.Mesh(new THREE.CircleGeometry(6.6, 24), emitMat(0x0284c7, 0x38bdf8));
        waterDisc.rotation.x = -Math.PI / 2;
        waterDisc.position.set(0, 3.9, 0);
        group.add(waterDisc);

        const fountainTier2 = new THREE.Mesh(new THREE.CylinderGeometry(3.0, 3.4, 1.0, 16), concMat(0xf8fafc));
        fountainTier2.position.set(0, 5.0, 0);
        group.add(fountainTier2);

        const jet = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.8, 3.5, 8), emitMat(0xe0f2fe, 0xbae6fd));
        jet.position.set(0, 7.2, 0);
        group.add(jet);

        // 4 Park Benches Shaded by Canopy Trees
        [
            { x: -14, z:   0, rot:  Math.PI/2 },
            { x:  14, z:   0, rot: -Math.PI/2 },
            { x:   0, z: -14, rot: Math.PI },
            { x:   0, z:  14, rot: 0 }
        ].forEach(bp => {
            const bench = new THREE.Mesh(new THREE.BoxGeometry(4.2, 0.4, 1.4), concMat(0x78350f));
            bench.position.set(bp.x, 3.8, bp.z);
            bench.rotation.y = bp.rot;
            group.add(bench);
        });

        // Vibrant Flowering Trees (Gulmohar Crimson & Jacaranda Purple)
        const treeSpots = [
            { x: -18, z: -16, col: 0xdc2626 }, // Gulmohar
            { x:  18, z: -16, col: 0xa855f7 }, // Jacaranda
            { x: -18, z:  16, col: 0x15803d }, // Rain Tree
            { x:  18, z:  16, col: 0x22c55e }  // Canopy Tree
        ];
        treeSpots.forEach(tp => {
            const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.7, 1.0, 7.5, 8), concMat(0x451a03));
            trunk.position.set(tp.x, 6.5, tp.z);
            group.add(trunk);

            const canopy = new THREE.Mesh(new THREE.SphereGeometry(4.8, 10, 8), emitMat(tp.col, tp.col));
            canopy.position.set(tp.x, 12.0, tp.z);
            group.add(canopy);
        });
    }

    _buildBMTCBusTerminal(key, group, s, glassMat, concMat, emitMat) {
        // MG Road Boulevard & Majestic Transit Concourse
        const termFloor = new THREE.Mesh(new THREE.BoxGeometry(50, 0.5, 32), concMat(0x1e293b));
        termFloor.position.set(0, 2.8, 0);
        group.add(termFloor);

        // Modern Curved Steel Bus Shelter
        const shelterRoof = new THREE.Mesh(new THREE.BoxGeometry(28, 0.4, 8.0), emitMat(0x0284c7, 0x0369a1));
        shelterRoof.position.set(0, 8.2, 0);
        shelterRoof.rotation.x = -Math.PI * 0.05;
        group.add(shelterRoof);

        [-12, 0, 12].forEach(px => {
            const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.3, 5.4, 8), concMat(0xd4d4d8));
            pole.position.set(px, 5.5, -3.5);
            group.add(pole);
        });

        // Glowing Digital BMTC Route Board
        const routeBoard = new THREE.Mesh(new THREE.BoxGeometry(22, 1.4, 0.2), emitMat(0xfacc15, 0xeab308));
        routeBoard.position.set(0, 7.2, -3.4);
        group.add(routeBoard);

        // Waiting Benches
        [-8, 8].forEach(bx => {
            const b = new THREE.Mesh(new THREE.BoxGeometry(5.0, 0.35, 1.2), concMat(0x64748b));
            b.position.set(bx, 3.8, -1.0);
            group.add(b);
        });
    }

    _buildTempleArchitecture(key, group, s, glassMat, concMat, emitMat) {
        // Dravidian Stone Sanctum Plinth
        const plinth = new THREE.Mesh(new THREE.BoxGeometry(42, 3.5, 36), concMat(0x3f3f46));
        plinth.position.set(0, 3.25, -4);
        plinth.castShadow = true;
        group.add(plinth);

        // Main Mandapam Hall
        const mandapam = new THREE.Mesh(new THREE.BoxGeometry(32, 10, 24), concMat(0x52525b));
        mandapam.position.set(0, 9.5, 0);
        mandapam.castShadow = true;
        group.add(mandapam);

        // Mandapam Stone Pillars
        [-13, -7, 7, 13].forEach(px => {
            [-8, 8].forEach(pz => {
                const pillar = new THREE.Mesh(new THREE.CylinderGeometry(0.75, 0.9, 9.8, 8), concMat(0x71717a));
                pillar.position.set(px, 9.5, pz);
                group.add(pillar);
            });
        });

        // Stepped Dravidian Gopuram Tower (4 Tiers)
        const tierDims = [
            { w: 22, h: 6.0, d: 16, y: 17.5, col: 0x78716c },
            { w: 18, h: 5.5, d: 13, y: 23.0, col: 0x854d0e },
            { w: 14, h: 5.0, d: 10, y: 28.0, col: 0xa16207 },
            { w: 10, h: 4.5, d:  8, y: 32.5, col: 0xb45309 }
        ];
        tierDims.forEach(t => {
            const tm = new THREE.Mesh(new THREE.BoxGeometry(t.w, t.h, t.d), concMat(t.col));
            tm.position.set(0, t.y, -7);
            tm.castShadow = true;
            group.add(tm);
        });

        // Golden Kalasam Finials atop Gopuram
        [-3.5, 0, 3.5].forEach(kx => {
            const kalasam = new THREE.Mesh(new THREE.ConeGeometry(0.8, 3.2, 8), emitMat(0xfbbf24, 0xd97706));
            kalasam.position.set(kx, 36.2, -7);
            group.add(kalasam);
        });

        // Monolithic Black Granite Nandi Statue at Front
        const nandiBody = new THREE.Mesh(new THREE.BoxGeometry(6.5, 4.0, 9.0), concMat(0x18181b));
        nandiBody.position.set(0, 5.5, 12);
        group.add(nandiBody);
        const nandiHump = new THREE.Mesh(new THREE.SphereGeometry(2.0, 8, 8), concMat(0x18181b));
        nandiHump.position.set(0, 8.0, 10);
        group.add(nandiHump);
        const nandiHead = new THREE.Mesh(new THREE.BoxGeometry(3.5, 3.0, 4.5), concMat(0x18181b));
        nandiHead.position.set(0, 7.5, 16);
        group.add(nandiHead);

        // Golden Aarti & Oil Lamp Warm Glow
        const lampLight = new THREE.PointLight(0xf59e0b, 2.5, 45);
        lampLight.position.set(0, 8, 4);
        group.add(lampLight);
    }

    _buildChurchArchitecture(key, group, s, glassMat, concMat, emitMat) {
        // Classical Stone Foundation & Nave
        const nave = new THREE.Mesh(new THREE.BoxGeometry(26, 16, 48), concMat(0xe2e8f0));
        nave.position.set(0, 9.5, -4);
        nave.castShadow = true;
        group.add(nave);

        // Gothic Arched Roof
        const roof = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 14, 48, 3), concMat(0x475569));
        roof.rotation.z = Math.PI;
        roof.rotation.y = Math.PI / 2;
        roof.position.set(0, 21.5, -4);
        group.add(roof);

        // Tower & Bell Spire at Front
        const belfry = new THREE.Mesh(new THREE.BoxGeometry(12, 32, 12), concMat(0xcbd5e1));
        belfry.position.set(0, 18, 16);
        belfry.castShadow = true;
        group.add(belfry);

        // Spire Cone
        const spire = new THREE.Mesh(new THREE.ConeGeometry(5.5, 20, 8), concMat(0x334155));
        spire.position.set(0, 44, 16);
        group.add(spire);

        // St. Mark's Gold Cross Finial
        const crossV = new THREE.Mesh(new THREE.BoxGeometry(0.6, 5.0, 0.6), emitMat(0xfef08a, 0xeab308));
        crossV.position.set(0, 56, 16);
        group.add(crossV);
        const crossH = new THREE.Mesh(new THREE.BoxGeometry(2.8, 0.6, 0.6), emitMat(0xfef08a, 0xeab308));
        crossH.position.set(0, 57.2, 16);
        group.add(crossH);

        // Glowing Stained Glass Rose Window
        const roseWin = new THREE.Mesh(new THREE.CircleGeometry(3.6, 16), emitMat(0x38bdf8, 0x0284c7));
        roseWin.position.set(0, 24, 22.1);
        group.add(roseWin);

        // Churchyard Garden Benches
        [-11, 11].forEach(bx => {
            const bench = new THREE.Mesh(new THREE.BoxGeometry(6.0, 0.4, 1.4), concMat(0x94a3b8));
            bench.position.set(bx, 2.0, 12);
            group.add(bench);
        });
    }

    _buildCoLivingResidences(key, group, s, glassMat, concMat, emitMat) {
        // 4-Story Modern Residential Block with Glowing Windows
        const bldg = new THREE.Mesh(new THREE.BoxGeometry(36, 28, 30), this.luxuryWindowMat || this._createWindowAtlas('luxury'));
        bldg.position.set(0, 15.5, -3);
        bldg.castShadow = true;
        group.add(bldg);
        this._addNeonWireframe(bldg, 0xec4899, 0.75);

        // Front Balcony Facades for Citizen Rooms
        [7, 14, 21, 28].forEach(floorY => {
            [-9, 9].forEach(bx => {
                const balc = new THREE.Mesh(new THREE.BoxGeometry(8, 0.4, 3.5), concMat(0xf3f4f6));
                balc.position.set(bx, floorY, 13);
                group.add(balc);
                const rail = new THREE.Mesh(new THREE.BoxGeometry(8, 1.2, 0.2), glassMat(0x38bdf8));
                rail.position.set(bx, floorY + 0.6, 14.7);
                group.add(rail);
            });
        });

        // Rooftop Community Pergola & Garden Patio
        const pergola = new THREE.Mesh(new THREE.BoxGeometry(22, 1.0, 18), concMat(0xd97706));
        pergola.position.set(0, 31, -3);
        group.add(pergola);

        // Warm Interior Room Lights
        [-9, 9].forEach(rx => {
            [10, 17, 24].forEach(ry => {
                const win = new THREE.Mesh(new THREE.BoxGeometry(4.0, 2.8, 0.2), emitMat(0xfef08a, 0xf59e0b));
                win.position.set(rx, ry, 12.1);
                group.add(win);
            });
        });

        // Glowing Neon "DEV CO-LIVING PG" Signboard
        const sign = new THREE.Mesh(new THREE.BoxGeometry(18, 2.0, 0.3), emitMat(0xec4899, 0xdb2777));
        sign.position.set(0, 5.0, 12.3);
        group.add(sign);
    }

    _buildCareHospital(key, group, s, glassMat, concMat, emitMat) {
        // Main Medical Wing with Illuminated Windows
        const hospital = new THREE.Mesh(new THREE.BoxGeometry(38, 22, 28), this.hospitalWindowMat || this._createWindowAtlas('hospital'));
        hospital.position.set(0, 12.5, -4);
        hospital.castShadow = true;
        group.add(hospital);
        this._addNeonWireframe(hospital, 0x10b981, 0.8);

        // Turquoise Clinical Accent Band
        const band = new THREE.Mesh(new THREE.BoxGeometry(38.2, 2.2, 28.2), concMat(0x0f766e));
        band.position.set(0, 13.0, -4);
        group.add(band);

        // Covered Emergency Ambulance Drop-Off Portico
        const portico = new THREE.Mesh(new THREE.BoxGeometry(20, 1.0, 12), concMat(0x334155));
        portico.position.set(0, 6.5, 14);
        group.add(portico);
        [-8, 8].forEach(px => {
            const pillar = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.4, 5.0, 8), concMat(0x94a3b8));
            pillar.position.set(px, 3.5, 18);
            group.add(pillar);
        });

        // Glowing Medical Cross Emblem
        const crossV = new THREE.Mesh(new THREE.BoxGeometry(1.6, 5.4, 0.4), emitMat(0x10b981, 0x059669));
        crossV.position.set(0, 19, 10.3);
        group.add(crossV);
        const crossH = new THREE.Mesh(new THREE.BoxGeometry(5.4, 1.6, 0.4), emitMat(0x10b981, 0x059669));
        crossH.position.set(0, 19, 10.3);
        group.add(crossH);

        // Red Emergency Ambulance Beacon Light
        const beacon = new THREE.Mesh(new THREE.SphereGeometry(0.6, 8, 8), emitMat(0xef4444, 0xdc2626));
        beacon.position.set(0, 7.2, 14);
        group.add(beacon);
        const beaconLight = new THREE.PointLight(0xef4444, 1.8, 35);
        beaconLight.position.set(0, 7.5, 14);
        group.add(beaconLight);
    }

    createBMTCBusFleet() {
        this.bmtcBuses = [];
        const BUS_TYPES = [
            {
                name: 'BMTC Vajra Volvo AC',
                route: '335-E: MAJESTIC - KADO UGODI',
                bodyColor: 0x1d4ed8, // Royal Blue
                stripeColor: 0xffffff,
                ac: true
            },
            {
                name: 'BMTC Vayu Vajra Airport Express',
                route: 'KIA-8: AIRPORT - ELECTRONIC CITY',
                bodyColor: 0x1e40af, // Deep Blue
                stripeColor: 0x60a5fa,
                ac: true
            },
            {
                name: 'BMTC Electric Metro Feeder',
                route: 'MF-1: INDIRANAGAR - WHITEFIELD',
                bodyColor: 0x15803d, // Emerald Green
                stripeColor: 0xffffff,
                ac: false
            }
        ];

        for (let i = 0; i < 6; i++) {
            const config = BUS_TYPES[i % BUS_TYPES.length];
            const busGroup = new THREE.Group();

            const bodyMat = new THREE.MeshStandardMaterial({
                color: config.bodyColor,
                roughness: 0.3,
                metalness: 0.4
            });
            const whiteMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.4 });
            const windowMat = new THREE.MeshStandardMaterial({
                color: 0x0284c7,
                roughness: 0.1,
                metalness: 0.8,
                transparent: true,
                opacity: 0.75
            });
            const ledMat = new THREE.MeshBasicMaterial({ color: 0xfacc15 });
            const darkMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.7 });
            const headlightMat = new THREE.MeshBasicMaterial({ color: 0xfef08a });
            const taillightMat = new THREE.MeshBasicMaterial({ color: 0xef4444 });

            // 1. Aerodynamic Bus Body
            const body = new THREE.Mesh(new THREE.BoxGeometry(4.6, 4.4, 15.0), bodyMat);
            body.position.y = 2.8;
            busGroup.add(body);

            // 2. White Roof with AC Unit
            const roof = new THREE.Mesh(new THREE.BoxGeometry(4.4, 0.5, 14.6), whiteMat);
            roof.position.y = 5.1;
            busGroup.add(roof);

            if (config.ac) {
                const acUnit = new THREE.Mesh(new THREE.BoxGeometry(3.2, 0.7, 4.2), new THREE.MeshStandardMaterial({ color: 0xd4d4d8 }));
                acUnit.position.set(0, 5.5, -1.0);
                busGroup.add(acUnit);
            }

            // 3. Panoramic Side Windows
            [-2.33, 2.33].forEach(wx => {
                const sideWin = new THREE.Mesh(new THREE.BoxGeometry(0.1, 1.4, 12.5), windowMat);
                sideWin.position.set(wx, 3.4, 0.2);
                busGroup.add(sideWin);
            });

            // 4. Front Windshield & LED Route Board
            const frontWin = new THREE.Mesh(new THREE.BoxGeometry(4.3, 1.8, 0.2), windowMat);
            frontWin.position.set(0, 3.3, 7.5);
            busGroup.add(frontWin);

            const ledBoard = new THREE.Mesh(new THREE.BoxGeometry(3.6, 0.7, 0.2), ledMat);
            ledBoard.position.set(0, 4.5, 7.52);
            busGroup.add(ledBoard);

            // 5. Lights
            [-1.6, 1.6].forEach(hx => {
                const hl = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.4, 0.2), headlightMat);
                hl.position.set(hx, 1.5, 7.52);
                busGroup.add(hl);

                const tl = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.6, 0.2), taillightMat);
                tl.position.set(hx, 1.6, -7.52);
                busGroup.add(tl);
            });

            // 6. Rotating Wheels
            const wheels = [];
            const wheelGeo = new THREE.CylinderGeometry(1.0, 1.0, 0.6, 12);
            wheelGeo.rotateZ(Math.PI / 2);

            [
                { x: -2.3, z:  4.5 },
                { x:  2.3, z:  4.5 },
                { x: -2.3, z: -3.8 },
                { x:  2.3, z: -3.8 },
                { x: -2.3, z: -5.5 },
                { x:  2.3, z: -5.5 }
            ].forEach(wPos => {
                const wh = new THREE.Mesh(wheelGeo, darkMat);
                wh.position.set(wPos.x, 1.0, wPos.z);
                busGroup.add(wh);
                wheels.push(wh);
            });

            const busTag = this.createTextSprite(`🚌 ${config.name}`, config.bodyColor, 11);
            busTag.position.y = 8.5;
            busGroup.add(busTag);

            this.scene.add(busGroup);

            const isEW = (i % 2 === 0);
            const lanes = [-230, -115, 0, 115, 230];
            const lanePos = lanes[i % lanes.length];

            this.bmtcBuses.push({
                group: busGroup,
                wheels,
                config,
                isEW,
                lanePos,
                pos: (i - 2.5) * 160,
                speed: 1.6 + (i % 3) * 0.4,
                dir: (i % 4 < 2 ? 1 : -1)
            });
        }
    }

    createLivingAnimals() {
        this.animals = { dogs: [], cats: [], birds: [] };

        // 1. DOGS (8 Dogs: Indie Strays & Golden Retrievers)
        const dogColors = [0xd97706, 0xf59e0b, 0x78350f, 0xfef3c7];
        const dogParks = [
            { x: -115, z: 0 },    // Cubbon Park
            { x: -115, z: 12 },   // Cubbon Fountain
            { x:    0, z: 15 },   // Church St
            { x:  115, z: 10 },   // Indiranagar
            { x: -345, z: 172 },  // Gandhi Bazaar
            { x:  230, z: 115 },  // Koramangala Brewery
            { x:  230, z: 230 },  // HSR Gym
            { x: -115, z: -115 }  // MG Road Boulevard
        ];

        for (let i = 0; i < 8; i++) {
            const dGroup = new THREE.Group();
            const col = dogColors[i % dogColors.length];
            const mat = new THREE.MeshStandardMaterial({ color: col, roughness: 0.7 });
            const darkMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.8 });

            const body = new THREE.Mesh(new THREE.BoxGeometry(1.0, 1.2, 2.2), mat);
            body.position.y = 1.4;
            dGroup.add(body);

            const head = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.9, 0.9), mat);
            head.position.set(0, 2.2, 1.2);
            dGroup.add(head);

            const snout = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.4, 0.6), mat);
            snout.position.set(0, 2.0, 1.7);
            dGroup.add(snout);

            const nose = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.2, 0.1), darkMat);
            nose.position.set(0, 2.15, 2.05);
            dGroup.add(nose);

            [-0.35, 0.35].forEach(ex => {
                const ear = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.5, 0.2), mat);
                ear.position.set(ex, 2.5, 1.0);
                dGroup.add(ear);
            });

            const legGeo = new THREE.BoxGeometry(0.3, 1.1, 0.3);
            legGeo.translate(0, -0.55, 0);

            const legs = [];
            [
                { x: -0.4, z:  0.8 },
                { x:  0.4, z:  0.8 },
                { x: -0.4, z: -0.8 },
                { x:  0.4, z: -0.8 }
            ].forEach(lo => {
                const leg = new THREE.Mesh(legGeo, mat);
                leg.position.set(lo.x, 1.1, lo.z);
                dGroup.add(leg);
                legs.push(leg);
            });

            const tailGeo = new THREE.BoxGeometry(0.2, 0.2, 1.0);
            tailGeo.translate(0, 0, -0.5);
            const tail = new THREE.Mesh(tailGeo, mat);
            tail.position.set(0, 1.6, -1.1);
            tail.rotation.x = Math.PI * 0.25;
            dGroup.add(tail);

            const baseP = dogParks[i % dogParks.length];
            dGroup.position.set(baseP.x + (Math.random() - 0.5) * 20, 0, baseP.z + (Math.random() - 0.5) * 20);
            this.scene.add(dGroup);

            this.animals.dogs.push({
                group: dGroup,
                legs,
                tail,
                target: new THREE.Vector3(baseP.x, 0, baseP.z),
                basePos: baseP,
                walkCycle: Math.random() * 10,
                speed: 0.08 + Math.random() * 0.04
            });
        }

        // 2. CATS (6 Cats)
        const catColors = [0x1e293b, 0xd97706, 0xf8fafc, 0xb45309];
        const catSpots = [
            { x: -115, z: -5 },   // Cubbon Park wall
            { x:    0, z: -10 },  // Church St cafe ledge
            { x: -345, z: 165 },  // Gandhi Bazaar coffee stall
            { x:  115, z: -8 },   // Indiranagar alley
            { x:  230, z: 110 },  // Brewery patio
            { x:  230, z: 220 }   // HSR Gym porch
        ];

        for (let i = 0; i < 6; i++) {
            const cGroup = new THREE.Group();
            const col = catColors[i % catColors.length];
            const mat = new THREE.MeshStandardMaterial({ color: col, roughness: 0.6 });

            const body = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.8, 1.4), mat);
            body.position.y = 0.9;
            cGroup.add(body);

            const head = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.6, 0.6), mat);
            head.position.set(0, 1.4, 0.8);
            cGroup.add(head);

            [-0.22, 0.22].forEach(ex => {
                const ear = new THREE.Mesh(new THREE.ConeGeometry(0.18, 0.35, 4), mat);
                ear.position.set(ex, 1.85, 0.8);
                cGroup.add(ear);
            });

            const tailGeo = new THREE.CylinderGeometry(0.1, 0.08, 1.1, 6);
            tailGeo.translate(0, 0.55, 0);
            const tail = new THREE.Mesh(tailGeo, mat);
            tail.position.set(0, 1.0, -0.7);
            tail.rotation.x = -Math.PI * 0.35;
            cGroup.add(tail);

            const legGeo = new THREE.BoxGeometry(0.2, 0.7, 0.2);
            legGeo.translate(0, -0.35, 0);
            const legs = [];
            [
                { x: -0.25, z:  0.5 },
                { x:  0.25, z:  0.5 },
                { x: -0.25, z: -0.5 },
                { x:  0.25, z: -0.5 }
            ].forEach(lo => {
                const leg = new THREE.Mesh(legGeo, mat);
                leg.position.set(lo.x, 0.7, lo.z);
                cGroup.add(leg);
                legs.push(leg);
            });

            const sp = catSpots[i % catSpots.length];
            cGroup.position.set(sp.x + (Math.random() - 0.5) * 8, 0, sp.z + (Math.random() - 0.5) * 8);
            this.scene.add(cGroup);

            this.animals.cats.push({
                group: cGroup,
                legs,
                tail,
                spot: sp,
                timer: Math.random() * 5,
                curled: Math.random() < 0.4
            });
        }

        // 3. BIRDS (32 Sky Birds: Pigeons, Parakeets, Mynas)
        const birdColors = [0x64748b, 0x16a34a, 0x94a3b8, 0x0284c7, 0x059669];
        for (let i = 0; i < 32; i++) {
            const bGroup = new THREE.Group();
            const bCol = birdColors[i % birdColors.length];
            const mat = new THREE.MeshStandardMaterial({ color: bCol, roughness: 0.4 });
            const beakMat = new THREE.MeshBasicMaterial({ color: 0xf59e0b });

            const body = new THREE.Mesh(new THREE.ConeGeometry(0.6, 1.8, 6), mat);
            body.rotation.x = Math.PI / 2;
            bGroup.add(body);

            const beak = new THREE.Mesh(new THREE.ConeGeometry(0.2, 0.5, 4), beakMat);
            beak.rotation.x = -Math.PI / 2;
            beak.position.set(0, 0, 1.1);
            bGroup.add(beak);

            const wingGeo = new THREE.BoxGeometry(1.6, 0.08, 0.8);
            wingGeo.translate(0.8, 0, 0);
            const rWing = new THREE.Mesh(wingGeo, mat);
            rWing.position.set(0.3, 0.1, 0);
            bGroup.add(rWing);

            const lWingGeo = new THREE.BoxGeometry(1.6, 0.08, 0.8);
            lWingGeo.translate(-0.8, 0, 0);
            const lWing = new THREE.Mesh(lWingGeo, mat);
            lWing.position.set(-0.3, 0.1, 0);
            bGroup.add(lWing);

            const angle = (i / 32) * Math.PI * 2;
            const radius = 180 + (i % 4) * 45;
            bGroup.position.set(
                Math.cos(angle) * radius,
                75 + Math.sin(i * 1.5) * 25,
                Math.sin(angle) * radius
            );
            this.scene.add(bGroup);

            this.animals.birds.push({
                group: bGroup,
                lWing,
                rWing,
                seed: i * 0.45,
                radius,
                angle,
                speed: 0.008 + (i % 5) * 0.002,
                altBase: 70 + (i % 6) * 8
            });
        }
    }

    createElevatedMetroRailNetwork() {
        const METRO_LINES = [
            {
                name: 'Purple Line (East-West)',
                color: 0xb000b0,
                stations: [
                    'Majestic_Metro_Interchange',
                    'Vidhana_Soudha_Capitol',
                    'Cubbon_Park_Canopy',
                    'Church_Street_Cafes',
                    'Indiranagar_100ft_Startups',
                    'Bagmane_Tech_Park',
                    'Whitefield_ITPB'
                ]
            },
            {
                name: 'Green Line (North-South West)',
                color: 0x008b3a,
                stations: [
                    'IISc_Research_Campus',
                    'Majestic_Metro_Interchange',
                    'Gandhi_Bazaar_Heritage'
                ]
            },
            {
                name: 'Airport Blue Line (North-South Center)',
                color: 0x0077cc,
                stations: [
                    'Kempegowda_Airport_BLR',
                    'Manyata_Tech_Park',
                    'Church_Street_Cafes',
                    'Silk_Board_Junction',
                    'Electronic_City_Phase_1'
                ]
            }
        ];

        const TRACK_ELEVATION = 25;

        METRO_LINES.forEach(line => {
            const stationPts = [];
            line.stations.forEach(k => {
                const s = this.sectorObjects.get(k);
                if (s) stationPts.push(new THREE.Vector3(s.worldX, TRACK_ELEVATION, s.worldZ));
            });
            if (stationPts.length < 2) return;

            const segments = [];
            for (let i = 0; i < stationPts.length - 1; i++) {
                const p1 = stationPts[i];
                const p2 = stationPts[i + 1];
                const segLen = p1.distanceTo(p2);
                segments.push({ p1, p2, len: segLen });

                const mid = new THREE.Vector3().addVectors(p1, p2).multiplyScalar(0.5);
                const beamGeo = new THREE.BoxGeometry(6.4, 2.2, segLen);
                const beamMat = new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.6, metalness: 0.3 });
                const beam = new THREE.Mesh(beamGeo, beamMat);
                beam.position.copy(mid);
                beam.lookAt(p2);
                this.scene.add(beam);

                [-1.8, 1.8].forEach(railOffset => {
                    const railGeo = new THREE.BoxGeometry(0.4, 0.5, segLen);
                    const railMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.9, roughness: 0.2 });
                    const rail = new THREE.Mesh(railGeo, railMat);
                    rail.position.set(railOffset, 1.25, 0);
                    beam.add(rail);
                });

                const thirdRailGeo = new THREE.BoxGeometry(0.3, 0.4, segLen);
                const thirdRailMat = new THREE.MeshBasicMaterial({ color: line.color });
                const thirdRail = new THREE.Mesh(thirdRailGeo, thirdRailMat);
                thirdRail.position.set(0, 1.2, 0);
                beam.add(thirdRail);

                const numPiers = Math.max(2, Math.floor(segLen / 45));
                for (let pi = 1; pi < numPiers; pi++) {
                    const t = pi / numPiers;
                    const pierPt = new THREE.Vector3().lerpVectors(p1, p2, t);
                    const pier = new THREE.Mesh(
                        new THREE.CylinderGeometry(1.6, 2.2, TRACK_ELEVATION, 8),
                        new THREE.MeshStandardMaterial({ color: 0x475569, roughness: 0.7 })
                    );
                    pier.position.set(pierPt.x, TRACK_ELEVATION / 2, pierPt.z);
                    this.scene.add(pier);
                }
            }

            const trainGroup = new THREE.Group();
            const carMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, metalness: 0.85, roughness: 0.15 });
            const stripeMat = new THREE.MeshBasicMaterial({ color: line.color });
            const windowMat = new THREE.MeshBasicMaterial({ color: 0x38bdf8 });

            const CAR_LEN = 13.0;
            const CAR_GAP = 1.5;

            for (let c = 0; c < 3; c++) {
                const car = new THREE.Group();
                const body = new THREE.Mesh(new THREE.BoxGeometry(4.0, 4.2, CAR_LEN), carMat);
                body.position.y = 2.4;
                car.add(body);

                const stripe = new THREE.Mesh(new THREE.BoxGeometry(4.05, 0.8, CAR_LEN + 0.05), stripeMat);
                stripe.position.y = 2.4;
                car.add(stripe);

                for (let wi = -2; wi <= 2; wi++) {
                    [-2.03, 2.03].forEach(wx => {
                        const win = new THREE.Mesh(new THREE.PlaneGeometry(1.8, 1.4), windowMat);
                        win.position.set(wx, 2.8, wi * 2.4);
                        win.rotation.y = wx > 0 ? Math.PI/2 : -Math.PI/2;
                        car.add(win);
                    });
                }

                if (c === 0) {
                    const nose = new THREE.Mesh(new THREE.ConeGeometry(2.0, 2.5, 4), carMat);
                    nose.rotation.x = -Math.PI / 2;
                    nose.position.set(0, 2.4, -CAR_LEN / 2 - 1.2);
                    car.add(nose);

                    [-1.1, 1.1].forEach(hx => {
                        const hl = new THREE.Mesh(new THREE.SphereGeometry(0.35, 8, 6), new THREE.MeshBasicMaterial({ color: 0xfef9c3 }));
                        hl.position.set(hx, 2.0, -CAR_LEN / 2 - 1.4);
                        car.add(hl);
                    });

                    const spot = new THREE.SpotLight(0xfef9c3, 3.5, 80, 0.35);
                    spot.position.set(0, 2.0, -CAR_LEN / 2 - 2.0);
                    spot.target.position.set(0, 0, -CAR_LEN / 2 - 40);
                    car.add(spot);
                    car.add(spot.target);
                }

                if (c === 2) {
                    [-1.1, 1.1].forEach(rx => {
                        const redLight = new THREE.Mesh(new THREE.SphereGeometry(0.3, 8, 6), new THREE.MeshBasicMaterial({ color: 0xef4444 }));
                        redLight.position.set(rx, 2.0, CAR_LEN / 2 + 0.1);
                        car.add(redLight);
                    });
                }

                car.position.set(0, 0, c * (CAR_LEN + CAR_GAP));
                trainGroup.add(car);
            }

            this.scene.add(trainGroup);
            this.trains3D.push({
                group: trainGroup,
                segments,
                curSeg: 0,
                t: Math.random(),
                speed: 0.0035 + Math.random() * 0.0015,
                forward: true
            });
        });
    }

    createAnimatedVehicles() {
        const autoMat = new THREE.MeshStandardMaterial({ color: 0xfacc15, roughness: 0.4 });
        const autoGreen = new THREE.MeshStandardMaterial({ color: 0x15803d, roughness: 0.5 });
        const busMat = new THREE.MeshStandardMaterial({ color: 0x16a34a, roughness: 0.4 });
        const cabMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.3 });

        const numVehicles = 36;
        for (let i = 0; i < numVehicles; i++) {
            const vGroup = new THREE.Group();
            const type = i % 3;

            if (type === 0) {
                const base = new THREE.Mesh(new THREE.BoxGeometry(3.0, 1.6, 4.4), autoGreen);
                base.position.y = 1.0; vGroup.add(base);
                const hood = new THREE.Mesh(new THREE.BoxGeometry(2.8, 1.4, 3.2), autoMat);
                hood.position.set(0, 2.2, -0.4); vGroup.add(hood);
                const headlight = new THREE.Mesh(new THREE.SphereGeometry(0.3, 6, 6), new THREE.MeshBasicMaterial({ color: 0xfef08a }));
                headlight.position.set(0, 1.2, -2.3); vGroup.add(headlight);
            } else if (type === 1) {
                const bus = new THREE.Mesh(new THREE.BoxGeometry(4.2, 3.6, 12.0), busMat);
                bus.position.y = 2.0; vGroup.add(bus);
                const win = new THREE.Mesh(new THREE.BoxGeometry(4.25, 1.2, 10.5), new THREE.MeshBasicMaterial({ color: 0x7dd3fc }));
                win.position.y = 2.5; vGroup.add(win);
            } else {
                const cab = new THREE.Mesh(new THREE.BoxGeometry(3.4, 2.0, 6.4), cabMat);
                cab.position.y = 1.2; vGroup.add(cab);
            }

            const isEW = Math.random() < 0.5;
            const lanes = [-230, -115, 0, 115, 230];
            const lanePos = lanes[Math.floor(Math.random() * lanes.length)];

            this.scene.add(vGroup);
            this.vehicles3D.push({
                group: vGroup,
                isEW,
                lanePos,
                pos: (Math.random() - 0.5) * 800,
                speed: 1.2 + Math.random() * 1.5,
                dir: Math.random() < 0.5 ? 1 : -1
            });
        }
    }

    updateCitizens(personaStates) {
        if (!personaStates || !Array.isArray(personaStates)) return;

        const DEPT_CONFIG = {
            'Core Architecture':       { color: 0x3b82f6, icon: '⚡' },
            'Systems SRE':             { color: 0x06b6d4, icon: '🛠️' },
            'DevOps & Infrastructure': { color: 0x0ea5e9, icon: '🚀' },
            'Code Synthesis':          { color: 0x8b5cf6, icon: '🧠' },
            'Market Intelligence':     { color: 0xa855f7, icon: '📊' },
            'UI & Frontend Systems':   { color: 0xec4899, icon: '🎨' },
            'Academic Research':       { color: 0x6366f1, icon: '🔬' },
            'Hardware R&D':            { color: 0x10b981, icon: '💻' },
            'Cyber Defense':           { color: 0xef4444, icon: '🛡️' },
            'Venture Capital':         { color: 0xf59e0b, icon: '💼' },
            'Fintech':                 { color: 0xeab308, icon: '📈' },
            'City Administration':     { color: 0x14b8a6, icon: '🏛️' },
            'Judiciary':               { color: 0xd97706, icon: '⚖️' },
            'Default':                 { color: 0x64748b, icon: '👤' }
        };

        const zoneCounts = {};

        personaStates.forEach((p) => {
            const zKey = p.zone;
            if (!zoneCounts[zKey]) zoneCounts[zKey] = 0;
            const spotIdx = zoneCounts[zKey]++;

            let cit = this.citizens3D.get(p.id);
            const sector = this.sectorObjects.get(p.zone);
            const basePos = sector ? { x: sector.worldX, z: sector.worldZ } : { x: 0, z: 0 };
            const radius = sector ? sector.metadata.radius : 32;

            const spots = this.VENUE_SPOTS[p.zone] || [];
            let tx, tz, spotRot = 0, pose = 'transit', venueDesc = `${p.zone.replace(/_/g, ' ')} Promenade`;

            if (spotIdx < spots.length) {
                const s = spots[spotIdx];
                tx = basePos.x + s.x;
                tz = basePos.z + s.z;
                spotRot = s.rot;
                pose = s.type; // 'desk', 'cafe', 'meeting', 'darshini'
                venueDesc = s.desc;
            } else {
                const spreadAngle = (spotIdx * 0.618033 * Math.PI * 2);
                const promenadeOffsetZ = 12 + (spotIdx % 5) * 4.2;
                const promenadeOffsetX = Math.sin(spreadAngle) * (radius * 0.65);
                tx = basePos.x + promenadeOffsetX;
                tz = basePos.z + promenadeOffsetZ;
                pose = 'transit';
                spotRot = Math.random() * Math.PI * 2;
            }

            const conf = DEPT_CONFIG[p.department] || DEPT_CONFIG['Default'];
            const cColor = conf.color;

            if (!cit) {
                const group = new THREE.Group();
                const initY = (pose === 'desk' || pose === 'cafe' || pose === 'meeting' || pose === 'park_sit' || pose === 'bus_wait') ? -1.0 : (pose === 'pub' ? -0.6 : 1.5);
                group.position.set(tx, initY, tz);
                group.rotation.y = spotRot;

                const bodyMat = new THREE.MeshStandardMaterial({
                    color: cColor,
                    emissive: cColor,
                    emissiveIntensity: 0.42,
                    roughness: 0.35, metalness: 0.2
                });
                const skinMat = new THREE.MeshStandardMaterial({ color: 0xfcd34d, roughness: 0.5 });
                const darkMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.6 });

                const torso = new THREE.Mesh(new THREE.BoxGeometry(4.6, 6.8, 3.2), bodyMat);
                torso.position.y = 8.8;
                group.add(torso);

                const head = new THREE.Mesh(new THREE.BoxGeometry(4.0, 4.0, 4.0), skinMat);
                head.position.y = 14.8;
                group.add(head);

                const visor = new THREE.Mesh(new THREE.BoxGeometry(3.6, 1.2, 0.4), new THREE.MeshBasicMaterial({ color: 0x38bdf8 }));
                visor.position.set(0, 15.0, 2.1);
                group.add(visor);

                // Pivot arm at shoulder joint (y = 11.5)
                const armGeo = new THREE.BoxGeometry(1.5, 6.4, 1.5);
                armGeo.translate(0, -3.2, 0);
                const lArm = new THREE.Mesh(armGeo, bodyMat);
                lArm.position.set(-3.2, 11.5, 0);
                group.add(lArm);
                const rArm = new THREE.Mesh(armGeo, bodyMat);
                rArm.position.set(3.2, 11.5, 0);
                group.add(rArm);

                // Pivot leg at hip joint (y = 7.5)
                const legGeo = new THREE.BoxGeometry(1.8, 7.5, 1.8);
                legGeo.translate(0, -3.75, 0);
                const lLeg = new THREE.Mesh(legGeo, darkMat);
                lLeg.position.set(-1.2, 7.5, 0);
                group.add(lLeg);
                const rLeg = new THREE.Mesh(legGeo, darkMat);
                rLeg.position.set(1.2, 7.5, 0);
                group.add(rLeg);

                const beaconGroup = new THREE.Group();
                const ringGeo = new THREE.TorusGeometry(4.4, 0.42, 8, 28);
                const ringMat = new THREE.MeshBasicMaterial({ color: cColor });
                const beaconRing = new THREE.Mesh(ringGeo, ringMat);
                beaconRing.rotation.x = Math.PI / 2;
                beaconRing.position.y = 0.2;
                beaconGroup.add(beaconRing);

                const innerDisc = new THREE.Mesh(
                    new THREE.CircleGeometry(3.8, 24),
                    new THREE.MeshBasicMaterial({ color: cColor, transparent: true, opacity: 0.45 })
                );
                innerDisc.rotation.x = -Math.PI / 2;
                innerDisc.position.y = 0.22;
                beaconGroup.add(innerDisc);

                const beamMesh = new THREE.Mesh(
                    new THREE.CylinderGeometry(3.8, 3.8, 28, 16, 1, true),
                    new THREE.MeshBasicMaterial({ color: cColor, transparent: true, opacity: 0.18, side: THREE.DoubleSide })
                );
                beamMesh.position.y = 14;
                beaconGroup.add(beamMesh);
                group.add(beaconGroup);

                let lifePrefix = '';
                if (p.has_company) lifePrefix += '👑 ';
                if (p.marital_status === 'MARRIED') lifePrefix += '💍 ';
                else if (p.marital_status === 'DATING') lifePrefix += '❤️ ';
                if (p.children_count > 0) lifePrefix += '🍼 ';

                const poseIcon = (pose === 'desk' ? '💻' : (pose === 'cafe' ? '☕' : (pose === 'meeting' ? '🗣️' : (pose === 'darshini' ? '☕' : (pose === 'pub' ? '🍺' : (pose === 'gym_run' || pose === 'gym_lift' ? '🏋️' : (pose === 'park_sit' || pose === 'jog' ? '🌳' : (pose === 'bus_wait' ? '🚌' : conf.icon))))))));
                const nameTag = this.createTextSprite(`${lifePrefix}${poseIcon} ${p.name || p.id}`, cColor, 12);
                nameTag.position.y = 23;
                group.add(nameTag);

                const hitGeo = new THREE.CylinderGeometry(5.5, 5.5, 24, 10);
                const hitMat = new THREE.MeshBasicMaterial({ visible: false });
                const hitMesh = new THREE.Mesh(hitGeo, hitMat);
                hitMesh.position.y = 12;
                hitMesh.userData = { type: 'citizen', id: p.id, persona: p };
                group.add(hitMesh);

                this.scene.add(group);

                cit = {
                    group, torso, head, lArm, rArm, lLeg, rLeg,
                    beaconRing, beaconGroup, nameTag, hitMesh,
                    targetX: tx, targetZ: tz,
                    spotRot, pose, venueDesc,
                    currentWaypoint: 0,
                    walkCycle: Math.random() * 10,
                    persona: p,
                    color: cColor,
                    speechTimer: 0,
                    speechSprite: null,
                    idleTimer: Math.random() * 4
                };
                this.citizens3D.set(p.id, cit);
            } else {
                cit.persona = p;
                cit.targetX = tx;
                cit.targetZ = tz;
                cit.spotRot = spotRot;
                cit.pose = pose;
                cit.venueDesc = venueDesc;

                if (p.speech_bubble && p.speech_bubble.length > 2 && cit.speechTimer <= 0) {
                    this.showSpeechBubble(cit, p.speech_bubble);
                }
            }
        });
    }

    showSpeechBubble(cit, text) {
        if (cit.speechSprite) {
            cit.group.remove(cit.speechSprite);
            if (cit.speechSprite.material) {
                if (cit.speechSprite.material.map) cit.speechSprite.material.map.dispose();
                cit.speechSprite.material.dispose();
            }
            cit.speechSprite = null;
        }
        cit.speechSprite = this.createSpeechBubble(text, cit.color);
        cit.speechSprite.position.y = 29;
        cit.group.add(cit.speechSprite);
        cit.speechTimer = 6.5;
    }

    createTextSprite(text, colorHex, fontSize = 12) {
        const canvas = document.createElement('canvas');
        const ctx    = canvas.getContext('2d');
        canvas.width  = 512;
        canvas.height = 112;

        ctx.fillStyle = 'rgba(11, 18, 30, 0.94)';
        ctx.beginPath();
        if (ctx.roundRect) ctx.roundRect(8, 8, 496, 96, 16);
        else ctx.rect(8, 8, 496, 96);
        ctx.fill();

        const hexStr = typeof colorHex === 'number' ? '#' + colorHex.toString(16).padStart(6, '0') : colorHex;
        ctx.strokeStyle = hexStr;
        ctx.lineWidth = 4;
        ctx.beginPath();
        if (ctx.roundRect) ctx.roundRect(8, 8, 496, 96, 16);
        else ctx.rect(8, 8, 496, 96);
        ctx.stroke();

        ctx.fillStyle = '#ffffff';
        ctx.font = `bold ${fontSize + 12}px -apple-system, sans-serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(text, 256, 56);

        const texture = new THREE.CanvasTexture(canvas);
        texture.generateMipmaps = false;
        texture.minFilter = THREE.LinearFilter;
        texture.magFilter = THREE.LinearFilter;
        const mat = new THREE.SpriteMaterial({ map: texture, transparent: true, depthTest: false });
        const spr = new THREE.Sprite(mat);
        spr.scale.set(44, 10, 1);
        return spr;
    }

    createSpeechBubble(text, colorHex = 0x38bdf8) {
        const canvas = document.createElement('canvas');
        const ctx    = canvas.getContext('2d');
        canvas.width  = 440;
        canvas.height = 100;

        ctx.fillStyle = 'rgba(8, 14, 24, 0.96)';
        if (ctx.roundRect) { ctx.beginPath(); ctx.roundRect(6, 6, 428, 76, 14); ctx.fill(); }
        else ctx.fillRect(6, 6, 428, 76);

        const hx = typeof colorHex === 'number' ? '#' + colorHex.toString(16).padStart(6, '0') : colorHex;
        ctx.strokeStyle = hx;
        ctx.lineWidth = 3;
        if (ctx.roundRect) { ctx.beginPath(); ctx.roundRect(6, 6, 428, 76, 14); ctx.stroke(); }
        else ctx.strokeRect(6, 6, 428, 76);

        ctx.fillStyle = 'rgba(8, 14, 24, 0.96)';
        ctx.beginPath(); ctx.moveTo(40, 82); ctx.lineTo(24, 98); ctx.lineTo(60, 82); ctx.fill();

        ctx.fillStyle = '#f8fafc';
        ctx.font = 'bold 20px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(text.slice(0, 32), 220, 44);

        const texture = new THREE.CanvasTexture(canvas);
        texture.generateMipmaps = false;
        texture.minFilter = THREE.LinearFilter;
        texture.magFilter = THREE.LinearFilter;
        const mat = new THREE.SpriteMaterial({ map: texture, transparent: true, depthTest: false });
        const spr = new THREE.Sprite(mat);
        spr.scale.set(40, 9, 1);
        return spr;
    }

    syncVoxelBlocks(zoneBlocks) {
        if (!zoneBlocks || !Array.isArray(zoneBlocks)) return;
        zoneBlocks.forEach(b => {
            const key = `${b.zone}_${b.x}_${b.y}_${b.z || 0}`;
            if (this.voxelBlocks.has(key)) return;

            const sector = this.sectorObjects.get(b.zone);
            if (!sector) return;

            const wX = sector.worldX + (b.x - 15) * 2.6;
            const wZ = sector.worldZ + (b.y - 15) * 2.6;
            const wY = 5 + (b.z || 0) * 4;

            const pd = this.BLOCK_PALETTE[b.block_type] || { color: 0x64748b, emissive: 0x000000, metalness: 0.3, roughness: 0.7 };
            const mat = new THREE.MeshStandardMaterial({
                color: pd.color, emissive: pd.emissive || 0x000000, emissiveIntensity: 0.65,
                metalness: pd.metalness || 0.3, roughness: pd.roughness || 0.7,
                transparent: pd.transparent || false, opacity: pd.opacity || 1.0
            });
            const mesh = new THREE.Mesh(new THREE.BoxGeometry(3.6, 3.6, 3.6), mat);
            mesh.position.set(wX, wY, wZ);
            mesh.castShadow = true; mesh.receiveShadow = true;
            mesh.scale.setScalar(0.05);
            this.scene.add(mesh);
            this.voxelBlocks.set(key, { mesh, targetScale: 1.0 });
            this.spawnPlacementParticles(wX, wY, wZ, pd.color);
        });
    }

    spawnPlacementParticles(x, y, z, color) {
        const count = 18;
        const geo   = new THREE.BufferGeometry();
        const pos   = new Float32Array(count * 3);
        const vel   = [];
        for (let i = 0; i < count; i++) {
            pos[i*3] = x; pos[i*3+1] = y; pos[i*3+2] = z;
            vel.push({ x: (Math.random()-.5)*5, y: 2.0 + Math.random()*6, z: (Math.random()-.5)*5 });
        }
        geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
        const mat = new THREE.PointsMaterial({ color, size: 1.6, transparent: true, opacity: 0.95 });
        const pts = new THREE.Points(geo, mat);
        this.scene.add(pts);
        this.particleSystems.push({ pts, vel, life: 1.2, posAttr: geo.attributes.position });
    }

    createGovernorAvatar() {
        this.governorAvatar = new THREE.Group();
        this.governorAvatar.position.set(0, 2.5, 0);

        const bodyMat = new THREE.MeshStandardMaterial({ color: 0xd97706, metalness: 0.85, roughness: 0.18, emissive: 0xb45309, emissiveIntensity: 0.4 });
        const headMat = new THREE.MeshStandardMaterial({ color: 0xfef3c7, roughness: 0.5 });
        const capeMat = new THREE.MeshStandardMaterial({ color: 0xdc2626, roughness: 0.75 });
        const bootMat = new THREE.MeshStandardMaterial({ color: 0x1c1917, roughness: 0.7 });

        const torso = new THREE.Mesh(new THREE.BoxGeometry(5.4, 7.5, 3.4), bodyMat);
        torso.position.y = 8.5; torso.castShadow = true; this.governorAvatar.add(torso);

        const head = new THREE.Mesh(new THREE.BoxGeometry(4.6, 4.6, 4.6), headMat);
        head.position.y = 14.8; this.governorAvatar.add(head);

        const crown = new THREE.Mesh(new THREE.CylinderGeometry(3.0, 3.5, 2.8, 6),
            new THREE.MeshStandardMaterial({ color: 0xf59e0b, metalness: 1.0, emissive: 0xb45309, emissiveIntensity: 0.6 }));
        crown.position.y = 18.6; this.governorAvatar.add(crown);

        const cape = new THREE.Mesh(new THREE.BoxGeometry(5.8, 10.0, 0.5), capeMat);
        cape.position.set(0, 8.0, -2.0); this.governorAvatar.add(cape);

        this.govLeftArm  = new THREE.Mesh(new THREE.BoxGeometry(1.6, 6.8, 1.6), bodyMat);
        this.govLeftArm.position.set(-3.8, 8.5, 0); this.governorAvatar.add(this.govLeftArm);
        this.govRightArm = new THREE.Mesh(new THREE.BoxGeometry(1.6, 6.8, 1.6), bodyMat);
        this.govRightArm.position.set(3.8, 8.5, 0); this.governorAvatar.add(this.govRightArm);

        this.govLeftLeg  = new THREE.Mesh(new THREE.BoxGeometry(2.0, 7.0, 2.0), bootMat);
        this.govLeftLeg.position.set(-1.4, 3.5, 0); this.governorAvatar.add(this.govLeftLeg);
        this.govRightLeg = new THREE.Mesh(new THREE.BoxGeometry(2.0, 7.0, 2.0), bootMat);
        this.govRightLeg.position.set(1.4, 3.5, 0); this.governorAvatar.add(this.govRightLeg);

        this.govWalkCycle = 0;

        const tag = this.createTextSprite('👑 Governor Lalith', 0xf59e0b, 15);
        tag.position.y = 26; this.governorAvatar.add(tag);

        const auraGeo = new THREE.SphereGeometry(10, 16, 8);
        const auraMat = new THREE.MeshBasicMaterial({ color: 0xf59e0b, transparent: true, opacity: 0.08, side: THREE.BackSide });
        this.governorAvatar.add(new THREE.Mesh(auraGeo, auraMat));

        const govLight = new THREE.PointLight(0xf59e0b, 2.5, 45);
        govLight.position.y = 12;
        this.governorAvatar.add(govLight);

        this.scene.add(this.governorAvatar);
    }

    createRainSystem() {
        const count = 8000;
        const geo   = new THREE.BufferGeometry();
        const pos   = new Float32Array(count * 3);
        for (let i = 0; i < count; i++) {
            pos[i*3]   = (Math.random() - 0.5) * 1200;
            pos[i*3+1] = Math.random() * 450;
            pos[i*3+2] = (Math.random() - 0.5) * 1200;
        }
        geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
        const mat = new THREE.PointsMaterial({ color: 0x93c5fd, size: 0.8, transparent: true, opacity: 0.65 });
        this.rainParticles = new THREE.Points(geo, mat);
        this.rainParticles.visible = false;
        this.scene.add(this.rainParticles);
    }

    setWeather(condition) {
        const isRain = condition && /rain|shower|storm/i.test(condition);
        this.isRaining = isRain;
        this.rainParticles.visible = isRain;
        if (isRain) {
            this.skyUniforms.topColor.value.setHex(0x010308);
            this.skyUniforms.bottomColor.value.setHex(0x060c14);
        }
    }

    syncWorldTime(timeFraction, circadianCategory) {
        if (typeof timeFraction === 'number' && !isNaN(timeFraction)) {
            this.targetTimeOfDay = timeFraction;
            this.circadianCategory = circadianCategory;
        }
    }

    updateDayNightCycle(delta) {
        if (this.targetTimeOfDay !== undefined) {
            let diff = this.targetTimeOfDay - this.timeOfDay;
            if (diff > 0.5) diff -= 1.0;
            if (diff < -0.5) diff += 1.0;
            this.timeOfDay = (this.timeOfDay + diff * Math.min(1.0, delta * 4.0) + 1.0) % 1.0;
        } else {
            this.timeOfDay = (this.timeOfDay + delta * 0.002) % 1.0;
        }
        const t = this.timeOfDay;

        const sunAngle = (t - 0.25) * Math.PI * 2;
        const sunR = 1600;
        this.sunMesh.position.set(Math.cos(sunAngle) * sunR, Math.sin(sunAngle) * sunR, -250);
        this.moonMesh.position.set(-Math.cos(sunAngle) * sunR, -Math.sin(sunAngle) * sunR, -250);

        let topCol, botCol, sunIntensity, ambIntensity, hemiIntensity, sunHex, nightFactor;

        // Categorize circadian phase with high fidelity
        if (t >= 0.0 && t < 0.17) {
            // MIDNIGHT (00:00 - 04:00)
            topCol = new THREE.Color(0x010308);
            botCol = new THREE.Color(0x060c18);
            sunIntensity = 0.0;
            ambIntensity = 0.5;
            hemiIntensity = 0.4;
            sunHex = 0x88aacc;
            nightFactor = 1.0;
        } else if (t >= 0.17 && t < 0.29) {
            // EARLY MORNING DAWN / BRAHMAMUHURTHA (04:00 - 07:00)
            const dawnProg = (t - 0.17) / (0.29 - 0.17);
            topCol = new THREE.Color(0x160826);
            botCol = new THREE.Color(0xd46838);
            sunIntensity = 0.4 + dawnProg * 2.5;
            ambIntensity = 0.8 + dawnProg * 1.2;
            hemiIntensity = 0.6 + dawnProg * 0.8;
            sunHex = 0xff7a38;
            nightFactor = Math.max(0.0, 1.0 - dawnProg * 1.5);
        } else if (t >= 0.29 && t < 0.50) {
            // MORNING (07:00 - 12:00)
            topCol = new THREE.Color(0x09224c);
            botCol = new THREE.Color(0x2d68a8);
            sunIntensity = 4.8;
            ambIntensity = 3.0;
            hemiIntensity = 2.2;
            sunHex = 0xfff8e7;
            nightFactor = 0.0;
        } else if (t >= 0.50 && t < 0.67) {
            // AFTERNOON (12:00 - 16:00)
            topCol = new THREE.Color(0x0c2f66);
            botCol = new THREE.Color(0x4286ce);
            sunIntensity = 5.5;
            ambIntensity = 3.4;
            hemiIntensity = 2.5;
            sunHex = 0xffffff;
            nightFactor = 0.0;
        } else if (t >= 0.67 && t < 0.75) {
            // LATE AFTERNOON (16:00 - 18:00)
            topCol = new THREE.Color(0x181224);
            botCol = new THREE.Color(0x8a4a2a);
            sunIntensity = 3.2;
            ambIntensity = 2.2;
            hemiIntensity = 1.6;
            sunHex = 0xffa044;
            nightFactor = 0.1;
        } else if (t >= 0.75 && t < 0.88) {
            // EVENING TWILIGHT (18:00 - 21:00)
            const duskProg = (t - 0.75) / (0.88 - 0.75);
            topCol = new THREE.Color(0x1e0a26);
            botCol = new THREE.Color(0xbd3a18);
            sunIntensity = Math.max(0.0, 2.0 - duskProg * 2.0);
            ambIntensity = 1.4 - duskProg * 0.6;
            hemiIntensity = 1.0 - duskProg * 0.4;
            sunHex = 0xff5518;
            nightFactor = Math.min(1.0, duskProg * 1.3);
        } else {
            // NIGHT (21:00 - 24:00)
            topCol = new THREE.Color(0x02050e);
            botCol = new THREE.Color(0x081324);
            sunIntensity = 0.0;
            ambIntensity = 0.7;
            hemiIntensity = 0.5;
            sunHex = 0x88aacc;
            nightFactor = 1.0;
        }

        if (!this.isRaining) {
            this.skyUniforms.topColor.value.copy(topCol);
            this.skyUniforms.bottomColor.value.copy(botCol);
        }

        this.sunLight.intensity = sunIntensity;
        this.ambientLight.intensity = ambIntensity;
        this.hemiLight.intensity = hemiIntensity;
        this.sunLight.position.copy(this.sunMesh.position);
        this.sunLight.color.setHex(sunHex);

        this.pointLights.forEach(pl => { pl.light.intensity = pl.baseIntensity * nightFactor; });
        this.streetLights.forEach(sl => { sl.intensity = 2.2 * nightFactor; });

        // Dynamic Circadian Window Modulation: Windows glow brightly at night (up to 1.95x emissive)
        const winIntensity = 0.35 + nightFactor * 1.55;
        if (this.buildingWindowMaterials && this.buildingWindowMaterials.length > 0) {
            for (let i = 0; i < this.buildingWindowMaterials.length; i++) {
                this.buildingWindowMaterials[i].emissiveIntensity = winIntensity;
            }
        }

        if (this.starField) {
            this.starField.material.opacity = nightFactor;
            this.starField.material.transparent = true;
        }
    }

    onMouseMove(e) {
        const rect = this.renderer.domElement.getBoundingClientRect();
        this.mouse.x =  ((e.clientX - rect.left) / rect.width)  * 2 - 1;
        this.mouse.y = -((e.clientY - rect.top)  / rect.height) * 2 + 1;
        this.raycaster.setFromCamera(this.mouse, this.camera);

        const citizenGroups = [];
        this.citizens3D.forEach(c => { if (c.group) citizenGroups.push(c.group); });
        const hits = this.raycaster.intersectObjects(citizenGroups, true);
        let foundCit = null;

        for (const hit of hits) {
            let obj = hit.object;
            while (obj) {
                if (obj.userData && obj.userData.type === 'citizen') {
                    foundCit = this.citizens3D.get(obj.userData.id);
                    break;
                }
                obj = obj.parent;
            }
            if (foundCit) break;
        }

        if (foundCit) {
            this.renderer.domElement.style.cursor = 'pointer';
            this.hoverCitizen = foundCit;
            const p = foundCit.persona;

            const nw = p.net_worth ? `₹${Number(p.net_worth).toLocaleString()}` : `₹${(p.wallet_inr || 25000).toLocaleString()}`;
            const familyStatus = (p.marital_status === 'MARRIED') ? `💍 Married to ${p.partner_name || 'Partner'}` : ((p.marital_status === 'DATING') ? `❤️ Dating ${p.partner_name || 'Partner'}` : 'Single');
            const kidsStr = p.children_count > 0 ? ` • 🍼 ${p.children_count} Children` : '';
            const bizBadge = p.has_company ? `<div style="color:#f59e0b; font-size:10px; font-weight:bold; margin-top:2px;">👑 Startup Founder & CEO</div>` : '';

            this.tooltipEl.innerHTML = `
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #1e293b; padding-bottom:6px; margin-bottom:6px;">
                    <strong style="color:#38bdf8; font-size:13px;">${p.name || p.id}</strong>
                    <span style="background:#1e293b; color:#10b981; padding:2px 6px; border-radius:4px; font-size:10px;">Net Worth: ${nw}</span>
                </div>
                <div style="color:#94a3b8; font-size:11px; margin-bottom:2px;">💼 <strong>${p.role || 'Citizen'}</strong> (${p.department || 'Guild'})</div>
                <div style="color:#f43f5e; font-size:11px; margin-bottom:2px;">${familyStatus}${kidsStr}</div>
                <div style="color:#a78bfa; font-size:10px; margin-bottom:2px;">😊 Happiness: ${p.happiness || 80}% • Multiplier: ${p.doublings ? (2**p.doublings) + 'x' : '1x'}</div>
                ${bizBadge}
                <div style="color:#e2e8f0; font-size:11px; font-style:italic; margin-top:4px;">"${p.action || 'Active in Bengaluru'}"</div>
                <div style="margin-top:8px; font-size:10px; color:#38bdf8; text-align:center; border-top:1px dashed #334155; padding-top:4px;">📞 Click to Direct Call & View Life Profile</div>
            `;
            this.tooltipEl.style.display = 'block';
            this.tooltipEl.style.left = (e.clientX - rect.left + 14) + 'px';
            this.tooltipEl.style.top  = (e.clientY - rect.top  + 14) + 'px';
        } else {
            this.renderer.domElement.style.cursor = 'default';
            this.hoverCitizen = null;
            this.tooltipEl.style.display = 'none';
        }
    }

    onCanvasClick(e) {
        const rect = this.renderer.domElement.getBoundingClientRect();
        this.mouse.x =  ((e.clientX - rect.left) / rect.width)  * 2 - 1;
        this.mouse.y = -((e.clientY - rect.top)  / rect.height) * 2 + 1;
        this.raycaster.setFromCamera(this.mouse, this.camera);

        const citizenGroups = [];
        this.citizens3D.forEach(c => { if (c.group) citizenGroups.push(c.group); });
        const hits = this.raycaster.intersectObjects(citizenGroups, true);
        for (const hit of hits) {
            let obj = hit.object;
            while (obj) {
                if (obj.userData && obj.userData.type === 'citizen') {
                    const citId = obj.userData.id;
                    if (window.inspectCitizen) window.inspectCitizen(citId);
                    return;
                }
                obj = obj.parent;
            }
        }
    }

    onCanvasDblClick(e) {
        if (this.hoverCitizen) {
            const targetPos = this.hoverCitizen.group.position;
            this.controls.target.copy(targetPos);
            this.camera.position.set(targetPos.x, targetPos.y + 35, targetPos.z + 55);
        }
    }

    cinematicWindowFlyThrough(venueKey = 'Manyata_Tech_Park') {
        const sPos = this._sectorWorldPos ? this._sectorWorldPos[venueKey] : { x: 0, z: 0 };
        this.cameraMode = 'flythrough';
        this.controls.enabled = false;
        
        let startPos = this.camera.position.clone();
        if (startPos.length() < 50) startPos = new THREE.Vector3(sPos.x + 80, 260, sPos.z + 340);

        let finalPos, finalLook, breachDesc, cueText;
        if (venueKey === 'IISc_Research_Campus') {
            finalPos = new THREE.Vector3(sPos.x, 8.8, sPos.z + 22.0);
            finalLook = new THREE.Vector3(sPos.x, 6.8, sPos.z - 8.0);
            breachDesc = '// WINDOW BREACH: THE ACADEMY AUDITORIUM // PROF. RAMANATHAN // 94.2% PASS RATE';
            cueText = "You're about to walk into The Academy.";
        } else if (venueKey === 'UB_City_Luxury_Towers') {
            finalPos = new THREE.Vector3(sPos.x, 68.0, sPos.z + 28.0);
            finalLook = new THREE.Vector3(sPos.x, 72.0, sPos.z - 4.0);
            breachDesc = '// WINDOW BREACH: UB CITY SKY SUITE // HIGH-RISE OBSERVATION DECK // LUXURY WINDOW ATLAS';
            cueText = "High above Bengaluru in the UB City Towers.";
        } else if (venueKey === 'Electronic_City_Phase_1') {
            finalPos = new THREE.Vector3(sPos.x, 42.0, sPos.z + 28.0);
            finalLook = new THREE.Vector3(sPos.x, 40.0, sPos.z - 10.0);
            breachDesc = '// WINDOW BREACH: ELECTRONIC CITY SILICON CORE // TWIN TOWERS // CYBER REPEAT ATLAS';
            cueText = "Swooping into Electronic City Hub.";
        } else {
            finalPos = new THREE.Vector3(sPos.x - 12, 7.0, sPos.z + 13.8);
            finalLook = new THREE.Vector3(sPos.x - 12, 5.6, sPos.z + 6.2);
            breachDesc = '// WINDOW BREACH: MANYATA CLOUD BAY // AARAV SHARMA WORKSTATION // 0ms INPUT LATENCY';
            cueText = "You're about to walk into their rooms.";
        }

        this.flyThroughState = {
            venueKey,
            sPos,
            startTime: performance.now(),
            duration: 5200,
            startPos,
            finalPos,
            finalLook,
            breachDesc,
            breachTriggered: false
        };

        const cue = document.getElementById('autopolis-cue-card');
        if (cue) {
            cue.innerText = cueText;
            cue.style.opacity = '1';
            cue.style.borderColor = '#00f5ff';
            cue.style.boxShadow = '0 0 30px rgba(0, 245, 255, 0.6)';
        }
    }

    toggleDayNight() {
        if (this.timeOfDay >= 0.22 && this.timeOfDay <= 0.72) {
            this.targetTimeOfDay = 0.94; // Switch to deep night
            const cue = document.getElementById('autopolis-cue-card');
            if (cue) {
                cue.innerText = "🌙 Circadian Night Active: 100,000+ Glowing Windows";
                cue.style.opacity = '1';
                setTimeout(() => { if (cue) cue.style.opacity = '0'; }, 3000);
            }
        } else {
            this.targetTimeOfDay = 0.38; // Switch to crisp midday
            const cue = document.getElementById('autopolis-cue-card');
            if (cue) {
                cue.innerText = "☀️ Circadian Midday Active: Clear Blue Sky & Sunlight";
                cue.style.opacity = '1';
                setTimeout(() => { if (cue) cue.style.opacity = '0'; }, 3000);
            }
        }
    }

    flyToVenue(venueKey) {
        this.cameraMode = 'orbit';
        this.controls.enabled = true;
        if (venueKey === 'overview' || venueKey === 'orbit') {
            this.targetCameraPos = new THREE.Vector3(0, 490, 580);
            this.targetLookAt = new THREE.Vector3(0, 20, 0);
            return;
        }
        const sPos = this._sectorWorldPos ? this._sectorWorldPos[venueKey] : null;
        if (sPos) {
            this.targetLookAt = new THREE.Vector3(sPos.x, 6.0, sPos.z);
            this.targetCameraPos = new THREE.Vector3(sPos.x, 24.0, sPos.z + 36.0);
        }
    }

    onKeyDown(e) {
        this.keys[e.key.toLowerCase()] = true;
        if (e.key === 'c' || e.key === 'C' || e.key === 'v' || e.key === 'V') {
            this.toggleCameraMode();
        }
        if (e.key === 'r' || e.key === 'R') {
            this.controls.target.set(0, 20, 0);
            this.camera.position.set(0, 490, 580);
            this.cameraMode = 'orbit';
            this.controls.enabled = true;
            this.updateCameraBadge();
        }
    }

    toggleCameraMode() {
        if (this.cameraMode === 'orbit') {
            this.cameraMode = 'follow';
            this.controls.enabled = false;
        } else if (this.cameraMode === 'follow') {
            this.cameraMode = 'firstperson';
            this.controls.enabled = false;
        } else {
            this.cameraMode = 'orbit';
            this.controls.enabled = true;
        }
        this.updateCameraBadge();
        return this.cameraMode;
    }

    updateCameraBadge() {
        const badge = document.getElementById('camera-mode-badge');
        if (badge) {
            const labels = {
                'orbit': '🌐 ORBIT (God View)',
                'follow': '🎥 3RD PERSON (Follow)',
                'firstperson': '🚶 1ST PERSON (WASD Eye)'
            };
            badge.innerText = labels[this.cameraMode] || this.cameraMode.toUpperCase();
        }
    }

    checkProximityHud() {
        if (!this.governorAvatar) return;
        const p = this.governorAvatar.position;
        const hud = document.getElementById('avatar-proximity-hud');
        if (!hud) return;

        const landmarks = [
            { name: "🛕 Bull Temple (Dodda Basavana Gudi)", x: -115, z: 230, desc: "Stepped Gopuram tower • Incense aroma & sacred bells audible" },
            { name: "⛪ St. Mark's Cathedral (MG Road)", x: 0, z: 0, desc: "Gothic spire • Stained glass rose window glow" },
            { name: "🏘️ Dev Co-Living PG (Indiranagar)", x: 115, z: 0, desc: "Terracotta balconies • Tech founders hacking on terrace" },
            { name: "🏥 Narayana Health Care Clinic (HSR Layout)", x: 115, z: 115, desc: "Emergency medical clinic • Ambulance ready" },
            { name: "☕ Church Street Cafe", x: 0, z: -40, desc: "Baristas brewing filter coffee • MacBooks buzzing" },
            { name: "🏢 Manyata Tech Park", x: -230, z: -230, desc: "Cloud architecture desks • Dual-monitor developers" }
        ];

        let activeMsg = null;
        for (const lm of landmarks) {
            const dx = p.x - lm.x;
            const dz = p.z - lm.z;
            const dist = Math.sqrt(dx * dx + dz * dz);
            if (dist < 48) {
                activeMsg = `📍 NEAR: ${lm.name} — ${lm.desc}`;
                break;
            }
        }
        if (activeMsg) {
            hud.innerText = activeMsg;
            hud.style.color = '#38bdf8';
        } else {
            hud.innerText = `🚶 Governor Avatar at (${p.x.toFixed(0)}, ${p.z.toFixed(0)}) • Walk near Temples, Churches & Cafes`;
            hud.style.color = '#94a3b8';
        }
    }

    onKeyUp(e) { this.keys[e.key.toLowerCase()] = false; }

    onWindowResize() {
        const w = this.container.clientWidth  || 900;
        const h = this.container.clientHeight || 680;
        this.camera.aspect = w / h;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(w, h);
    }

    animate() {
        requestAnimationFrame(this.animate);
        if (window.activeViewMode && window.activeViewMode !== '3d') return;
        const delta = Math.min(this.clock.getDelta(), 0.1);
        this.animTime += delta;
        const t = this.animTime;

        this.updateDayNightCycle(delta);

        // Blinking Red Aviation Warning Beacons (FAA/ICAO Strobe Pulse)
        if (this.rooftopBeacons && this.rooftopBeacons.length > 0) {
            const beaconTime = this.animTime * 3.6;
            for (let i = 0; i < this.rooftopBeacons.length; i++) {
                const b = this.rooftopBeacons[i];
                const pulse = Math.sin(beaconTime + b.phase);
                if (pulse > 0.42) {
                    b.mesh.material.color.setHex(0xff1133);
                    b.mesh.scale.set(1.4, 1.4, 1.4);
                } else {
                    b.mesh.material.color.setHex(0x330008);
                    b.mesh.scale.set(0.85, 0.85, 0.85);
                }
            }
        }

        this.cloudMeshes.forEach(c => {
            c.group.position.x += c.speed * delta;
            if (c.group.position.x > 1200) c.group.position.x = -1200;
        });

        this.trains3D.forEach(tr => {
            const seg = tr.segments[tr.curSeg];
            if (!seg) return;

            tr.t += (tr.speed * 60 * delta) / seg.len;
            if (tr.t >= 1.0) {
                tr.t = 0;
                if (tr.forward) {
                    tr.curSeg++;
                    if (tr.curSeg >= tr.segments.length) {
                        tr.curSeg = tr.segments.length - 1;
                        tr.forward = false;
                    }
                } else {
                    tr.curSeg--;
                    if (tr.curSeg < 0) {
                        tr.curSeg = 0;
                        tr.forward = true;
                    }
                }
            }

            const curSeg = tr.segments[tr.curSeg];
            const pStart = tr.forward ? curSeg.p1 : curSeg.p2;
            const pEnd   = tr.forward ? curSeg.p2 : curSeg.p1;

            this._scratchV1.lerpVectors(pStart, pEnd, tr.t);
            tr.group.position.copy(this._scratchV1);
            tr.group.lookAt(pEnd);
        });

        this.vehicles3D.forEach(v => {
            v.pos += v.speed * v.dir * delta * 25;
            if (v.pos > 450) v.pos = -450;
            if (v.pos < -450) v.pos = 450;

            if (v.isEW) {
                v.group.position.set(v.pos, 0.4, v.lanePos + (v.dir > 0 ? 3.5 : -3.5));
                v.group.rotation.y = v.dir > 0 ? Math.PI/2 : -Math.PI/2;
            } else {
                v.group.position.set(v.lanePos + (v.dir > 0 ? 3.5 : -3.5), 0.4, v.pos);
                v.group.rotation.y = v.dir > 0 ? 0 : Math.PI;
            }
        });

        // BMTC Vajra & Electric Bus Fleet Animation
        if (this.bmtcBuses) {
            this.bmtcBuses.forEach(bus => {
                bus.pos += bus.speed * bus.dir * delta * 24;
                if (bus.pos > 520) bus.pos = -520;
                if (bus.pos < -520) bus.pos = 520;

                if (bus.isEW) {
                    bus.group.position.set(bus.pos, 0, bus.lanePos);
                    bus.group.rotation.y = bus.dir > 0 ? Math.PI / 2 : -Math.PI / 2;
                } else {
                    bus.group.position.set(bus.lanePos, 0, bus.pos);
                    bus.group.rotation.y = bus.dir > 0 ? 0 : Math.PI;
                }

                // Spin all 6 bus wheels dynamically
                const wheelSpin = bus.dir * bus.speed * delta * 18;
                bus.wheels.forEach(wh => wh.rotation.x += wheelSpin);
            });
        }

        // Living Animals: Dogs, Cats, and Birds Animation
        if (this.animals) {
            // 1. Dogs trotting and wagging tails
            this.animals.dogs.forEach(d => {
                const dx = d.target.x - d.group.position.x;
                const dz = d.target.z - d.group.position.z;
                const dist = Math.sqrt(dx * dx + dz * dz);

                if (dist > 1.0) {
                    d.group.position.x += dx * d.speed;
                    d.group.position.z += dz * d.speed;
                    d.group.rotation.y = Math.atan2(dx, dz);

                    d.walkCycle += delta * 14;
                    d.legs[0].rotation.x =  Math.sin(d.walkCycle) * 0.7;
                    d.legs[1].rotation.x = -Math.sin(d.walkCycle) * 0.7;
                    d.legs[2].rotation.x = -Math.sin(d.walkCycle) * 0.7;
                    d.legs[3].rotation.x =  Math.sin(d.walkCycle) * 0.7;
                    d.group.position.y = Math.abs(Math.sin(d.walkCycle * 0.5)) * 0.2;
                } else {
                    d.legs.forEach(l => l.rotation.x *= 0.8);
                    d.group.position.y = 0;
                    if (Math.random() < 0.02) {
                        d.target.set(
                            d.basePos.x + (Math.random() - 0.5) * 36,
                            0,
                            d.basePos.z + (Math.random() - 0.5) * 36
                        );
                    }
                }
                d.tail.rotation.y = Math.sin(t * 16 + d.walkCycle) * 0.6;
            });

            // 2. Cats lounging and prowling
            this.animals.cats.forEach(c => {
                c.tail.rotation.z = Math.sin(t * 3.5) * 0.4;
                c.legs.forEach(l => l.rotation.x *= 0.9);
            });

            // 3. Birds flapping wings and flocking in 3D sky formations
            this.animals.birds.forEach(b => {
                b.angle += b.speed * delta * 50;
                const x = Math.cos(b.angle) * b.radius;
                const z = Math.sin(b.angle) * b.radius;
                const y = b.altBase + Math.sin(b.angle * 2.5 + b.seed) * 12;

                const tx = -Math.sin(b.angle);
                const tz =  Math.cos(b.angle);

                b.group.position.set(x, y, z);
                b.group.rotation.y = Math.atan2(tx, tz);
                b.group.rotation.x = Math.sin(b.angle * 2.5 + b.seed) * 0.15;

                const flap = Math.sin(t * 18 + b.seed) * 0.75;
                b.rWing.rotation.z = -flap;
                b.lWing.rotation.z =  flap;
            });
        }

        this.citizens3D.forEach(cit => {
            const dx = cit.targetX - cit.group.position.x;
            const dz = cit.targetZ - cit.group.position.z;
            const dist = Math.sqrt(dx * dx + dz * dz);

            if (dist > 1.2) {
                const spd = 0.07;
                cit.group.position.x += dx * spd;
                cit.group.position.z += dz * spd;
                cit.group.rotation.y = Math.atan2(dx, dz);

                cit.walkCycle += delta * 12;
                cit.lLeg.rotation.x =  Math.sin(cit.walkCycle) * 0.85;
                cit.rLeg.rotation.x = -Math.sin(cit.walkCycle) * 0.85;
                cit.lArm.rotation.x = -Math.sin(cit.walkCycle) * 0.7;
                cit.rArm.rotation.x =  Math.sin(cit.walkCycle) * 0.7;
                cit.lArm.rotation.z = 0; cit.rArm.rotation.z = 0;
                cit.torso.rotation.x = 0;
                cit.head.rotation.x = 0; cit.head.rotation.y = 0;
                cit.group.position.y = 1.5 + Math.abs(Math.sin(cit.walkCycle * 0.5)) * 0.5;
            } else {
                if (cit.spotRot !== undefined) {
                    let diff = cit.spotRot - cit.group.rotation.y;
                    while (diff < -Math.PI) diff += Math.PI * 2;
                    while (diff > Math.PI) diff -= Math.PI * 2;
                    cit.group.rotation.y += diff * 0.12;
                }

                if (cit.pose === 'teacher') {
                    // Standing at lecture podium, gesturing toward digital chalkboard
                    cit.group.position.y = 1.8;
                    cit.lLeg.rotation.x = 0;
                    cit.rLeg.rotation.x = 0;
                    cit.torso.rotation.x = -0.04;
                    // Right arm pointing/gesturing toward the board
                    cit.rArm.rotation.x = -1.45 + Math.sin(t * 3.2 + cit.walkCycle) * 0.35;
                    cit.rArm.rotation.z = -0.45;
                    cit.lArm.rotation.x = -0.8 + Math.cos(t * 2.0) * 0.2;
                    cit.lArm.rotation.z = 0.2;
                    cit.head.rotation.y = Math.sin(t * 1.8) * 0.35;
                    cit.head.rotation.x = 0.05;
                } else if (cit.pose === 'student') {
                    // Seated at auditorium student desk, typing on laptop, taking notes, periodic hand raising
                    cit.group.position.y = -0.8;
                    cit.lLeg.rotation.x = -1.45;
                    cit.rLeg.rotation.x = -1.45;
                    cit.torso.rotation.x = 0.08;
                    const handRaise = Math.sin(t * 0.4 + cit.walkCycle);
                    if (handRaise > 0.7) {
                        cit.rArm.rotation.x = -2.8; // arm straight up
                        cit.rArm.rotation.z = -0.2;
                        cit.head.rotation.x = -0.25; // looking up at professor
                    } else {
                        cit.rArm.rotation.x = -1.1 + Math.sin(t * 12.0) * 0.15;
                        cit.rArm.rotation.z = -0.25;
                        cit.head.rotation.x = 0.2;
                    }
                    cit.lArm.rotation.x = -1.1 - Math.sin(t * 12.0) * 0.15;
                    cit.lArm.rotation.z = 0.25;
                    cit.head.rotation.y = Math.sin(t * 1.2) * 0.1;
                } else if (cit.pose === 'desk') {
                    // Physical desk posture: seated at swivel chair, typing on dual glowing monitors
                    cit.group.position.y = -1.0;
                    cit.lLeg.rotation.x = -1.45;
                    cit.rLeg.rotation.x = -1.45;
                    cit.torso.rotation.x = 0.08;
                    cit.head.rotation.x = 0.16;
                    cit.head.rotation.y = Math.sin(t * 1.5 + cit.walkCycle) * 0.12;
                    // Dual-hand rapid code typing motions
                    cit.lArm.rotation.x = -1.15 + Math.sin(t * 14.0 + cit.walkCycle) * 0.18;
                    cit.rArm.rotation.x = -1.15 - Math.sin(t * 14.0 + cit.walkCycle) * 0.18;
                    cit.lArm.rotation.z = 0.28;
                    cit.rArm.rotation.z = -0.28;
                } else if (cit.pose === 'cafe') {
                    // Physical cafe posture: seated under umbrella, sipping filter coffee & chatting
                    cit.group.position.y = -1.0;
                    cit.lLeg.rotation.x = -1.45;
                    cit.rLeg.rotation.x = -1.45;
                    cit.torso.rotation.x = 0.04;
                    const sip = Math.sin(t * 0.8 + cit.walkCycle);
                    if (sip > 0.45) {
                        cit.rArm.rotation.x = -1.55;
                        cit.rArm.rotation.z = -0.32;
                        cit.head.rotation.x = -0.16;
                        cit.head.rotation.y = 0;
                    } else {
                        cit.rArm.rotation.x = -0.7;
                        cit.rArm.rotation.z = -0.15;
                        cit.head.rotation.x = 0.04;
                        cit.head.rotation.y = Math.sin(t * 1.2) * 0.22;
                    }
                    cit.lArm.rotation.x = -0.75 + Math.sin(t * 3.0) * 0.1;
                    cit.lArm.rotation.z = 0.2;
                } else if (cit.pose === 'meeting') {
                    // Physical conference room posture: seated in boardroom circle, debating or taking notes
                    cit.group.position.y = -1.0;
                    cit.lLeg.rotation.x = -1.45;
                    cit.rLeg.rotation.x = -1.45;
                    cit.torso.rotation.x = 0.06;
                    if (cit.speechTimer > 0) {
                        cit.lArm.rotation.x = -0.9 + Math.sin(t * 4.5 + cit.walkCycle) * 0.38;
                        cit.rArm.rotation.x = -1.1 - Math.cos(t * 4.0 + cit.walkCycle) * 0.32;
                        cit.lArm.rotation.z = 0.32;
                        cit.rArm.rotation.z = -0.32;
                        cit.head.rotation.y = Math.sin(t * 2.2) * 0.28;
                        cit.head.rotation.x = 0.0;
                    } else {
                        cit.lArm.rotation.x = -0.65;
                        cit.rArm.rotation.x = -0.65;
                        cit.lArm.rotation.z = 0.2;
                        cit.rArm.rotation.z = -0.2;
                        cit.head.rotation.x = Math.sin(t * 2.0 + cit.walkCycle) * 0.12;
                        cit.head.rotation.y = Math.sin(t * 0.5) * 0.15;
                    }
                } else if (cit.pose === 'darshini') {
                    // Standing at stainless counter sipping hot filter coffee
                    cit.group.position.y = 1.5;
                    cit.lLeg.rotation.x = 0;
                    cit.rLeg.rotation.x = 0;
                    cit.torso.rotation.x = 0;
                    const drink = Math.sin(t * 1.1 + cit.walkCycle);
                    if (drink > 0.4) {
                        cit.rArm.rotation.x = -1.6;
                        cit.rArm.rotation.z = -0.3;
                        cit.head.rotation.x = -0.15;
                    } else {
                        cit.rArm.rotation.x = -0.5;
                        cit.rArm.rotation.z = -0.1;
                        cit.head.rotation.x = 0.05;
                    }
                    cit.lArm.rotation.x = -0.2;
                    cit.lArm.rotation.z = 0.1;
                } else if (cit.pose === 'pub') {
                    // Seated on high stool at craft brewery bar counter sipping craft IPA & cheering
                    cit.group.position.y = -0.6;
                    cit.lLeg.rotation.x = -1.45;
                    cit.rLeg.rotation.x = -1.45;
                    cit.torso.rotation.x = 0.05;
                    cit.rArm.rotation.x = -1.5 + Math.sin(t * 2.5 + cit.walkCycle) * 0.2;
                    cit.rArm.rotation.z = -0.3;
                    cit.lArm.rotation.x = -0.8;
                    cit.lArm.rotation.z = 0.2;
                    cit.head.rotation.y = Math.sin(t * 1.6) * 0.25;
                } else if (cit.pose === 'gym_run') {
                    // High-cadence sprint on Cult.fit treadmill
                    cit.group.position.y = 1.6;
                    cit.torso.rotation.x = 0.16;
                    cit.lLeg.rotation.x =  Math.sin(t * 18.0 + cit.walkCycle) * 0.95;
                    cit.rLeg.rotation.x = -Math.sin(t * 18.0 + cit.walkCycle) * 0.95;
                    cit.lArm.rotation.x = -Math.sin(t * 18.0 + cit.walkCycle) * 0.9;
                    cit.rArm.rotation.x =  Math.sin(t * 18.0 + cit.walkCycle) * 0.9;
                    cit.lArm.rotation.z = 0.15;
                    cit.rArm.rotation.z = -0.15;
                    cit.head.rotation.x = 0.08;
                } else if (cit.pose === 'gym_lift') {
                    // Overhead Olympic barbell & dumbbell lifting
                    cit.group.position.y = 1.5;
                    cit.lLeg.rotation.x = 0;
                    cit.rLeg.rotation.x = 0;
                    cit.torso.rotation.x = -0.04;
                    const lift = Math.sin(t * 3.5 + cit.walkCycle);
                    cit.lArm.rotation.x = -1.8 + lift * 0.55;
                    cit.rArm.rotation.x = -1.8 + lift * 0.55;
                    cit.lArm.rotation.z = 0.25;
                    cit.rArm.rotation.z = -0.25;
                    cit.head.rotation.x = -0.15;
                } else if (cit.pose === 'park_sit') {
                    // Seated on Cubbon park bench enjoying the trees & watching birds
                    cit.group.position.y = -1.0;
                    cit.lLeg.rotation.x = -1.45;
                    cit.rLeg.rotation.x = -1.45;
                    cit.torso.rotation.x = 0.02;
                    cit.lArm.rotation.x = -0.6;
                    cit.rArm.rotation.x = -0.6;
                    cit.head.rotation.y = Math.sin(t * 0.8) * 0.25;
                } else if (cit.pose === 'jog') {
                    // Jogging along park perimeter
                    cit.group.position.y = 1.5 + Math.abs(Math.sin(t * 6.0)) * 0.3;
                    cit.lLeg.rotation.x =  Math.sin(t * 12.0) * 0.75;
                    cit.rLeg.rotation.x = -Math.sin(t * 12.0) * 0.75;
                    cit.lArm.rotation.x = -Math.sin(t * 12.0) * 0.7;
                    cit.rArm.rotation.x =  Math.sin(t * 12.0) * 0.7;
                } else if (cit.pose === 'bus_wait') {
                    // Waiting at BMTC bus bay
                    cit.group.position.y = -1.0;
                    cit.lLeg.rotation.x = -1.45;
                    cit.rLeg.rotation.x = -1.45;
                    cit.torso.rotation.x = 0.04;
                    cit.lArm.rotation.x = -0.5;
                    cit.rArm.rotation.x = -0.5;
                    cit.head.rotation.y = Math.sin(t * 1.2) * 0.3;
                } else {
                    // Transit / promenade walk & idle stance
                    ['lLeg','rLeg','lArm','rArm'].forEach(k => { if (cit[k]) cit[k].rotation.x *= 0.85; });
                    cit.lArm.rotation.z = 0; cit.rArm.rotation.z = 0;
                    cit.torso.rotation.x = 0;
                    cit.head.rotation.x = 0;
                    cit.head.rotation.y = Math.sin(t * 0.8 + cit.walkCycle) * 0.15;
                    cit.group.position.y = 1.5 + Math.sin(t * 1.5 + cit.walkCycle) * 0.12;

                    cit.idleTimer -= delta;
                    if (cit.idleTimer <= 0) {
                        cit.idleTimer = 5 + Math.random() * 7;
                        const sector = this.sectorObjects.get(cit.persona.zone);
                        if (sector) {
                            const r = sector.metadata.radius * 0.65;
                            cit.targetX = sector.worldX + (Math.random() - 0.5) * r * 1.4;
                            cit.targetZ = sector.worldZ + 12 + Math.random() * (r * 0.5);
                        }
                    }
                }
            }

            cit.beaconRing.rotation.z += delta * 2.0;
            const isHovered = (this.hoverCitizen === cit);
            const baseScale = isHovered ? 1.4 : 1.0;
            cit.beaconGroup.scale.setScalar(baseScale + Math.sin(t * 3.0 + cit.walkCycle) * 0.1);
            if (isHovered) {
                cit.beaconRing.material.color.setHex(0xfacc15);
            } else {
                cit.beaconRing.material.color.setHex(cit.color);
            }

            if (cit.speechTimer > 0) {
                cit.speechTimer -= delta;
                if (cit.speechSprite) {
                    cit.speechSprite.position.y = 29 + Math.sin(t * 2.0) * 0.4;
                }
                if (cit.speechTimer <= 0 && cit.speechSprite) {
                    cit.group.remove(cit.speechSprite);
                    if (cit.speechSprite.material) {
                        if (cit.speechSprite.material.map) cit.speechSprite.material.map.dispose();
                        cit.speechSprite.material.dispose();
                    }
                    cit.speechSprite = null;
                }
            }
        });

        this.voxelBlocks.forEach(vb => {
            if (vb.mesh.scale.x < vb.targetScale) {
                vb.mesh.scale.addScalar(0.08);
                if (vb.mesh.scale.x > vb.targetScale) vb.mesh.scale.setScalar(vb.targetScale);
                vb.mesh.rotation.y += 0.04;
            }
        });

        for (let i = this.particleSystems.length - 1; i >= 0; i--) {
            const ps = this.particleSystems[i];
            ps.life -= delta * 0.6;
            ps.pts.material.opacity = Math.max(0, ps.life);
            const pos = ps.posAttr.array;
            for (let j = 0; j < ps.vel.length; j++) {
                pos[j*3]   += ps.vel[j].x * delta * 3.5;
                pos[j*3+1] += ps.vel[j].y * delta * 3.5;
                pos[j*3+2] += ps.vel[j].z * delta * 3.5;
                ps.vel[j].y -= 6 * delta;
            }
            ps.posAttr.needsUpdate = true;
            if (ps.life <= 0) { this.scene.remove(ps.pts); this.particleSystems.splice(i, 1); }
        }

        if (this.isRaining && this.rainParticles) {
            const rp = this.rainParticles.geometry.attributes.position.array;
            for (let i = 0; i < rp.length; i += 3) {
                rp[i+1] -= 120 * delta;
                if (rp[i+1] < 0) rp[i+1] = 450;
            }
            this.rainParticles.geometry.attributes.position.needsUpdate = true;
        }

        if (this.governorAvatar) {
            const spd = 2.4;
            let moved = false;
            if (this.keys['w'] || this.keys['arrowup'])    { this.governorAvatar.position.z -= spd; this.governorAvatar.rotation.y = Math.PI;    moved = true; }
            if (this.keys['s'] || this.keys['arrowdown'])  { this.governorAvatar.position.z += spd; this.governorAvatar.rotation.y = 0;          moved = true; }
            if (this.keys['a'] || this.keys['arrowleft'])  { this.governorAvatar.position.x -= spd; this.governorAvatar.rotation.y = -Math.PI/2; moved = true; }
            if (this.keys['d'] || this.keys['arrowright']) { this.governorAvatar.position.x += spd; this.governorAvatar.rotation.y = Math.PI/2;  moved = true; }

            if (moved) {
                this.govWalkCycle += delta * 11;
                this.govLeftArm.rotation.x  = -Math.sin(this.govWalkCycle) * 0.85;
                this.govRightArm.rotation.x =  Math.sin(this.govWalkCycle) * 0.85;
                this.govLeftLeg.rotation.x  =  Math.sin(this.govWalkCycle) * 0.85;
                this.govRightLeg.rotation.x = -Math.sin(this.govWalkCycle) * 0.85;
                this.governorAvatar.position.y = 2.5 + Math.abs(Math.sin(this.govWalkCycle)) * 0.6;
            } else {
                [this.govLeftArm, this.govRightArm, this.govLeftLeg, this.govRightLeg].forEach(m => { if(m) m.rotation.x *= 0.88; });
                this.governorAvatar.position.y = 2.5 + Math.sin(t * 1.2) * 0.12;
            }

            if (this.cameraMode === 'follow') {
                this._scratchV1.copy(this.governorAvatar.position);
                this._scratchV1.y += 55;
                this._scratchV1.z += 95;
                this.camera.position.lerp(this._scratchV1, 0.08);
                this.camera.lookAt(this.governorAvatar.position);
            } else if (this.cameraMode === 'firstperson') {
                this._scratchV1.copy(this.governorAvatar.position);
                this._scratchV1.y += 16.5;
                this.camera.position.copy(this._scratchV1);
                const rotY = this.governorAvatar.rotation.y;
                this._scratchV2.set(Math.sin(rotY + Math.PI), 0, Math.cos(rotY + Math.PI)).multiplyScalar(40);
                this._scratchLook.copy(this._scratchV1).add(this._scratchV2);
                this.camera.lookAt(this._scratchLook);
            }
            this.checkProximityHud();
        }

        if (this.cameraMode === 'flythrough' && this.flyThroughState) {
            const elapsed = performance.now() - this.flyThroughState.startTime;
            const p = Math.min(elapsed / this.flyThroughState.duration, 1.0);
            // Smooth easeInOutCubic
            const ease = p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
            
            const sp = this.flyThroughState.startPos;
            const fp = this.flyThroughState.finalPos;
            const fl = this.flyThroughState.finalLook;
            const sPos = this.flyThroughState.sPos;

            // Curved 3D trajectory with rooftop swoop and window breach
            const midX = (sp.x + fp.x) * 0.5 + Math.sin(p * Math.PI) * 15;
            const midY = THREE.MathUtils.lerp(sp.y, fp.y, ease) + Math.sin(p * Math.PI) * 12;
            const midZ = THREE.MathUtils.lerp(sp.z, fp.z, ease);
            this.camera.position.set(midX, midY, midZ);

            this._scratchV1.set(sPos.x, 15, sPos.z);
            this._scratchLook.lerpVectors(this._scratchV1, fl, ease);
            this.camera.lookAt(this._scratchLook);

            if (p > 0.65 && !this.flyThroughState.breachTriggered) {
                this.flyThroughState.breachTriggered = true;
                const cue = document.getElementById('autopolis-cue-card');
                if (cue) cue.innerText = this.flyThroughState.breachDesc;
            }

            if (p >= 1.0) {
                this.cameraMode = 'orbit';
                this.controls.enabled = true;
                this.controls.target.copy(fl);
                this.camera.position.copy(fp);
                this.camera.lookAt(fl);
                this.controls.update();
                this.flyThroughState = null;
            }
        }

        if (this.targetCameraPos && this.targetLookAt) {
            this.camera.position.lerp(this.targetCameraPos, 0.06);
            this.controls.target.lerp(this.targetLookAt, 0.06);
            if (this.camera.position.distanceTo(this.targetCameraPos) < 1.0) {
                this.targetCameraPos = null;
                this.targetLookAt = null;
            }
        }

        if (this.cameraMode === 'orbit') this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }
}

window.VoxelMetropolis3D = VoxelMetropolis3D;

        
