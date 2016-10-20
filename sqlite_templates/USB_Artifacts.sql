SELECT
winevent.written_time AS "Time",
winevent.event_identifier AS "EventID",
winevent.computer_name AS "Computer",
CASE 
	WHEN (event_identifier IN (1003))
		THEN json_extract(we_jrec,'$.UserData.UMDFDriverManagerHostCreateStart.DeviceInstanceId.#text')
	WHEN (event_identifier IN (2003))
		THEN json_extract(we_jrec,'$.UserData.UMDFHostAddDeviceBegin.instance')
	WHEN (event_identifier IN (2003))
		THEN json_extract(we_jrec,'$.UserData.UMDFHostAddDeviceBegin.instance')
	WHEN (event_identifier IN (2005))
		THEN json_extract(we_jrec,'$.UserData.UMDFHostModuleLoad.instance')
	WHEN (event_identifier IN (2006))
		THEN json_extract(we_jrec,'$.UserData.UMDFHostAddDeviceEnd.instance')
	WHEN (event_identifier IN (2010))
		THEN json_extract(we_jrec,'$.UserData.UMDFHostDeviceArrivalEnd.instance')
	WHEN (event_identifier IN (2100,2101,2102,2105,2106))
		THEN json_extract(we_jrec,'$.UserData.UMDFHostDeviceRequest.instance')
	WHEN (event_identifier IN (10000))
		THEN json_extract(we_jrec,'$.UserData.UMDFDeviceInstallBegin.DeviceId.#text')
	WHEN (event_identifier IN (20001))
		THEN json_extract(we_jrec,'$.UserData.InstallDeviceID.DeviceInstanceID.#text')
	WHEN (event_identifier IN (20003))
		THEN json_extract(we_jrec,'$.UserData.AddServiceID.DeviceInstanceID.#text')
	ELSE '<Not Handled>'
	END AS "Device Info",
winevent.source_name AS "Channel",
winevent.we_source AS "Source"
FROM "winevent"
WHERE 
((source_name == 'Microsoft-Windows-DriverFrameworks-UserMode' AND (event_identifier IN (1003,2003,2004,2005,2006,2010,2100,2101,2102,2105,2106,10000)))
OR
(source_name == 'Microsoft-Windows-UserPnp' AND (event_identifier IN (20001,20003))))
AND ("Device Info" LIKE '%USBSTOR%')
ORDER BY written_time DESC