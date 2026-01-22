tell application "Calendar"
	set output to {}
	set curDate to current date
	-- Look back 1 day and forward 7 days to be sure
	set startDate to curDate - 1 * days
	set endDate to curDate + 7 * days
	
	set allCalendars to calendars
	
	repeat with aCal in allCalendars
		try
			set evtList to (every event of aCal whose start date > startDate and start date < endDate)
			repeat with evt in evtList
				set evtInfo to {summary:summary of evt, startDate:(start date of evt) as text, location:location of evt, description:description of evt, allDay:allday event of evt}
				copy evtInfo to end of output
			end repeat
		on error errMsg
			-- Ignore errors (e.g. reminders calendar often errors on event queries)
		end try
	end repeat
	
	return output
end tell
