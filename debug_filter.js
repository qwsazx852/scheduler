
const fs = require('fs');
const path = require('path');

// Mock local_db
const DB_PATH = path.join(process.cwd(), 'personal_scheduler/local_events.json');

function getLocalEvents() {
    try {
        if (!fs.existsSync(DB_PATH)) {
            console.log("DB not found at", DB_PATH);
            return [];
        }
        const data = fs.readFileSync(DB_PATH, 'utf-8');
        return JSON.parse(data);
    } catch (e) {
        console.error("Error reading local DB:", e);
        return [];
    }
}

// Mock logic
const targetDateStr = process.argv[2] || new Date().toISOString();
const targetDate = new Date(targetDateStr);

console.log("Target Date Input:", targetDateStr);
console.log("Target Date Parsed:", targetDate.toString());

const start = new Date(targetDate);
start.setHours(0, 0, 0, 0);
const end = new Date(targetDate);
end.setHours(24, 0, 0, 0);

console.log("Start (Local):", start.toString());
console.log("End (Local):", end.toString());
console.log("Start (ISO):", start.toISOString());
console.log("End (ISO):", end.toISOString());

const localEvents = getLocalEvents();
console.log(`Found ${localEvents.length} events in DB`);

const localFiltered = localEvents.filter(e => {
    const eStart = new Date(e.startDate);
    console.log(`Checking '${e.title}': ${e.startDate} (${eStart.toISOString()})`);
    const match = eStart >= start && eStart < end;
    console.log(`   >= Start? ${eStart >= start}`);
    console.log(`   < End?   ${eStart < end}`);
    return match;
});

console.log("Filtered Events:", localFiltered.map(e => e.title));
