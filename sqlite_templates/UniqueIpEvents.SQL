SELECT DISTINCT
	source_name AS "SourceName",
	hit.value AS "IpAddress",
	json_extract(GetIpInfo(hit.value),'$.country') AS "IpCountry",
	count(*) AS "EventCount"
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
GROUP BY "SourceName","IpAddress"