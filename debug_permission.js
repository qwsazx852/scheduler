
const { exec } = require('child_process');

const script = `
var app = Application('Calendar');
var cals = app.calendars();
var names = [];
for (var i=0; i<cals.length; i++) {
    names.push(cals[i].name());
}
names.join(', ');
`;

exec(`osascript -l JavaScript -e "${script.replace(/"/g, '\\"')}"`, (err, stdout, stderr) => {
    if (err) {
        console.error("Error:", err);
    }
    console.log("Stdout:", stdout);
    console.log("Stderr:", stderr);
});
