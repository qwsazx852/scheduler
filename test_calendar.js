function run() {
    var app = Application('Calendar');
    var now = new Date();
    // Start of today
    var startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    // End of today (start of tomorrow)
    var endDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1);

    var data = [];
    
    // Iterate over all calendars
    var calendars = app.calendars();
    for (var i = 0; i < calendars.length; i++) {
        var cal = calendars[i];
        // Skip some standard read-only or irrelevant calendars if needed, but for now grab all
        
        // Get events in range
        // Note: 'whose' filters can be slow or tricky in JXA. 
        // A common pattern is to get all events in a range if the API supports it, 
        // but Calendar JXA support is limited.
        // Let's try to just get events and filter manually if the count is low, 
        // OR use the correct whose clause.
        
        try {
            var events = cal.events.whose({
                startDate: { _greaterThanEquals: startDate },
                endDate: { _lessThan: endDate }
            })();
            
            for (var j = 0; j < events.length; j++) {
                var evt = events[j];
                data.push({
                    title: evt.summary(),
                    startDate: evt.startDate().toISOString(),
                    endDate: evt.endDate().toISOString(),
                    location: evt.location(),
                    description: evt.description(),
                    isAllDay: evt.alldayEvent()
                });
            }
        } catch (e) {
            // Ignore errors for specific calendars
        }
    }
    
    return JSON.stringify(data);
}
