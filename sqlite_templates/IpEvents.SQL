SELECT 
	written_time AS "Time",
	source_name AS "SourceName",
	event_identifier AS "EventId",
	identifier AS "Identifier",
	hit.value AS "IpAddress",
	json_extract(GetIpInfo(hit.value),'$.country') AS "IpCountry",
	RemoveNewLines(xml_string) AS "Event"
FROM 
	winevent,
	json_each(
		GetRegMatchArray(
			xml_string,
			1,
			'\b((?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))\b'
		)
	) AS hit
WHERE xml_string REGEXP '\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
ORDER BY written_time DESC