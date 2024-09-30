track availability of tickets for events from ticketmaster.co.uk

# How it works
1. open new tab for ticketmaster.co.uk in running Mozilla Firefox instance
2. retrieve ticketmaster.co.uk cookies from running instance
3. call Ticketmaster API
4. write response to /logs/<event_id>.csv
5. when cookies expire after about 15 Minutes, start from beginning

# Requirements

- Running Mozilla Firefox Instance
- Python 3
- [Tab Wrangler Addon](https://github.com/tabwrangler/tabwrangler/) (optional)

# Ticketmaster API

API to retrieve  list of available tickets of an event

## Endpoint

/api/quickpicks/<EVENT_ID>/list

## URL Parameters

|Name|Value|Description|
|----|-----|-----------|
|EVENT_ID|23006130DAB40C0B|ID of  Event|

## GET Parameters

|Name|Value|Description|
|----|-----|-----------|
|resale|true|if true, only resale tickets will be returned|
|qty|1|number of tickets you're looking for|
|offset|0|position from where to start returning results|
|limit|100|number of maxium returned results|
|sort|price|attribute to sort results|
|primary|true|n/a|
|defaultToOne|true|n/a|
|tids|000000000004|n/a|

## Request Headers

see [sample.config.json](sample.config.json)

## Cookies

### Required

|Name|Domain|
|----|------|
|BID|.ticketmaster.co.uk|
|eps_sid|.ticketmaster.co.uk|
|language|.ticketmaster.co.uk|
|reese84|.ticketmaster.co.uk|

### Others

|Name|Domain|
|----|------|
|Queue-it|queue.ticketmaster.co.uk|
|cf_clearance|.help.ticketmaster.co.uk|
|ma.did|.identity.ticketmaster.co.uk|

## Response

### HTTP Status Codes

|Status|Descripton|How Tracker handles it|
|------|----------|----------------------|
|200|Request successful|write response to logs\\<EVENT_ID>.csv|
|401|Cookie expired|write status to logs\\<EVENT_ID>.csv, retrieve new cookie|
|403|Headers invalid|write error to logs\\<EVENT_ID>.html, cancel execution|
|404|Event not found|write error to logs\\<EVENT_ID>.html, cancel execution|
|503|Event temporarily not available|replace failing event id with new event id|
|504|Timeout|replace failing event id with new event id|

### Body when no Ticket is available

```
{
	"quantity": 0,
	"total": 0,
	"picks": [],
	"descriptions": []
}
```

### Body when 1 Ticket is available

```
{
	"quantity": 1,
	"eventId": "23006113B5E30BFD",
	"total": 1,
	"picks": [
		{
			"id": "lg899kjn6",
			"type": "general-seating",
			"section": "PITCH",
			"originalPrice": 396.93,
			"description": "",
			"areaName": "",
			"placeDescriptionId": "IE5DCNJMHE",
			"hasSpecialDescription": false,
			"offerIds": [
				"HF6GYZZYHE4WW2TOGY"
			],
			"snapshotImageUrl": "image?systemId=HOST_UK&segmentIds=s_168",
			"quality": 0.97235,
			"sellerBusinessType": "private",
			"resaleListingId": "lg899kjn6",
			"sellerAffiliationType": "unaffiliated",
			"attributes": []
		}
	],
	"descriptions": [
		{
			"id": "IE5DCNJMHE",
			"descriptions": [
				"No U14s. Under 18s with adult 18+",
				"Incl. 2.75 Facility Fee"
			]
		}
	]
}
```

## Subdomains

- www.ticketmaster.co.uk
- queue.ticketmaster.co.uk
- identity.ticketmaster.co.uk
- help.ticketmaster.co.uk

# CSV Schema

|quantity|total|picks|descriptions|status|time|date|
|--------|-----|-----|------------|------|----|----|
|0|0|[]|[]|200|23:59:59|01.01.2024|

# Configuration

create config.json with following attributes:

|Name|Description|Available Values|
|----|-----------|----------------|
|firefox_executable|absolute path to Mozialla Firefox executable|n/a|
|selenium|NOT IMPLEMENTED YET!|chrome, firefox|
|cookies|Cookie String or cookies.txt File, if empty Cookie from running Firefox instance will be used||
|headers|Array of required Request Headers|see sample.config.json|
|domain|Ticketmaster domain|.ticketmaster.co.uk|
|api_path|API path|/api/quickpicks/|
|primary_events|Array of Event IDs which will be tracked|see sample.config.json|
|secondary_events|Array of Event IDs which will be used if primary Event fails|see sample.config.json|
|method|API method incl. query parameters|list?resale=true&qty=1&offset=0&limit=100&sort=price|
|request_delay|delay between requests (in seconds)|30|
|refresh_delay|delay until new loaded cookies will be used (in seconds)|15|
|picks_list|JSON Array with all found tickets|picks.json|
|response_sample|load API response sample for testing|list.json|

for sample values see [sample.config.json](sample.config.json)

# To-Dos

- implement headless browser
- write results to to SQLite