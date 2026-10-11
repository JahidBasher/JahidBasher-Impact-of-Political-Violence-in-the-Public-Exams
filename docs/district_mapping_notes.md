# District mapping notes: `data/bangladesh_ged_selected_data_2011_2025.xlsx`

## Summary

A `district` column was added to the GED event sheet, between `where_description` and `country`. Every one of the 227 events was assigned one of Bangladesh's 64 districts, or `Unknown` when the source data gives no location below country level.

| Outcome | Events |
|---|---|
| Assigned directly from the place name or description | 202 |
| Ambiguous place name or vague location, checked individually (table below) | 12 |
| `Unknown` (country-level only) | 13 |
| **Total** | **227** |

## Naming convention

District names use the exact spelling in the `District Name` column of `data/bangladesh_ssc_hsc_district_year_education_with_exam_dates.xlsx`, so the two files can be joined on district. These are the older English spellings:

- Bogra, not Bogura
- Chittagong, not Chattogram
- Comilla, not Cumilla
- Jessore, not Jashore
- Barisal, not Barishal
- Chapai Nawabganj, Cox's Bazar, Moulvibazar, Lakshmipur

Every value in the column, apart from `Unknown`, appears in that list.

## Method

Each event was mapped by reading its `where_coordinates` and `where_description` fields, in this order:

1. **District named directly.** Examples: "Rangpur district", "Satkhira District". The named district was used.
2. **City or town that is a district headquarters.** Examples: "Sylhet town", "Natore town", "Dhaka city". The district of the same name was used.
3. **Upazila, town, village, camp or neighbourhood.** The place was mapped to the district that contains it. When the description named the district, as in "Kutupalong camp in Ukhiya sub-district of Cox's Bazar district", that name was used. Otherwise standard administrative geography was applied. Examples:
   - Savar, Mirpur, Gulshan, Jatrabari → Dhaka
   - Ukhiya, Teknaf, all numbered Rohingya camps → Cox's Bazar
   - Ghumdum, Naikhongchhari, "Bangladesh–Myanmar border (Bandarban district)" → Bandarban
   - Madhabdi, Palash, Raipura → Narsingdi
   - Kanchpur, Rupganj → Narayanganj
   - Kaunia → Rangpur; Patgram, Hatibandha → Lalmonirhat
   - Bhujpur ("Bhozpur town"), Patiya → Chittagong
4. **Ambiguous names or vague locations.** These were checked against the `source_article` citation and contemporaneous news reports (see below).
5. **No recoverable location.** These were set to `Unknown`.

## Events resolved with outside sources

| Row | relid | Location in data | District | Basis | Confidence |
|---|---|---|---|---|---|
| 10 | BNG-2013-2-X3374-6 | Shibganj sub-district | Chapai Nawabganj | Fatal Jamaat-Shibir clashes in Shibganj town (Chapai Nawabganj) after the Sayeedi verdict, 28 Feb–1 Mar 2013 | Medium |
| 19 | BNG-2013-2-X3374-11 | Shibganj sub-district (Umarpur village) | Chapai Nawabganj | Inferred from the location and the April 2013 Jamaat attacks there; no report of this exact event was found | Medium–low |
| 38 | BNG-2013-2-29-12 | Shibganj sub-district | Chapai Nawabganj | An AL activist was burnt to death when his shop at Shibganj Bazar (Chapai Nawabganj) was set on fire | Medium |
| 90 | BNG-2017-1-14718-12 | Shibganj sub-district | Chapai Nawabganj | Operation "Eagle Hunt": police raid on a Neo-JMB hideout at Shibnagar, Shibganj (Chapai Nawabganj), 26–27 Apr 2017, four dead | High |
| 51 | BNG-2015-3-1076-4 | Shibganj town | Bogra | The description says "Shibganj area of Bogra district" | High |
| 80 | BNG-2017-1-14718-6 | Jamnagar village | Bogra | Neo-JMB commander killed in a police "gunfight", Jamnagar, Sherpur upazila, Bogra, 2 Mar 2017 | High |
| 91 | BNG-2017-1-14718-13 | Bazrapur village | Jhenaidah | Suicide blasts during a raid at Bazrapur, Moheshpur upazila, Jhenaidah, 7 May 2017 | High |
| 28 | BNG-2013-2-29-9 | Chupair village | Gazipur | Chupair is a locality in Kaliganj upazila, Gazipur (Chupair Girls' High School). Date matches the 27 Nov 2013 AL–BNP clash killing there; no report naming Chupair was found | Medium |
| 37 | BNG-2013-2-X3374-20 | Kaliganj sub-district (Choumohoni) | Satkhira | Matches the December 2013 Jamaat killing of an AL leader in Kaliganj, Satkhira; Kaliganj upazilas also exist in Gazipur, Jhenaidah and Lalmonirhat | Medium |
| 16 | BNG-2013-2-29-0 | Gopalpur town | Tangail | Gopalpur upazila town in Tangail is the most likely match; no report of this event was found, and a Gopalpur also exists in Lalpur, Natore | Low |
| 186 | BNG-2024-2-17997-17 | Bangladesh ("Dhaka–Chittagong highway") | Narayanganj | Fish trader shot at Shimrail on the highway, Siddhirganj, 21 Jul 2024 | High |
| 193 | BNG-2024-2-17997-25 | Bangladesh ("Joypurhat") | Joypurhat | The description names Joypurhat | Medium |

## Events set to `Unknown`

These 13 events are coded only at country level. Their sources are nationwide summaries: election-violence round-ups, nationwide death tolls from the 2024 protests, monthly human-rights reports, and terrorism timelines. No single district can be recovered from them.

Rows 4, 106, 108, 167, 181, 185, 205, 216, 221, 225, 226, 227, 228.

Row 185 (BNG-2024-2-17997-19) says "Place of killing unknown; case filed in Joypurhat". Where a case was filed does not show where the killing happened, so this row was left `Unknown` rather than set to Joypurhat.

## Verification (9 October 2026)

**Data checks.** The GED sheet's original seven columns are unchanged; only `district` was added. The derived JSON (`output/bangladesh_conflict_education.json`) and the web view were compared field by field against both Excel files. All 227 events have the same district, year, deaths, source and place in every file, and the 960 education rows match exactly. All counts in this document were recomputed from the files.

**Placements that depend on geography rather than text.** 47 events were placed in a district that is not written in the row. Most are upazilas, camps or towns whose name belongs to only one district (Patiya, Savar, Kaunia, Palash, Ukhiya, and so on). The less obvious ones were checked against news reports:

| Row | relid | Location in data | District | Evidence |
|---|---|---|---|---|
| 3 | BNG-2012-2-29-2 | Enayetpur town | Sirajganj | Enayetpur is a police station area in Sirajganj. The December 2012 event itself was not found in news searches |
| 18 | BNG-2013-2-X3374-10 | Bhozpur town ("Buzpur") | Chittagong | Clash at Kazirhat, Bhujpur, Fatikchhari upazila, 11 Apr 2013 |
| 110 | BNG-2018-2-5201-10 | Mohanpur sub-district | Rajshahi | AL supporter killed at Pakuria Government High School centre, Jahanabad union, Mohanpur, Rajshahi-3, 30 Dec 2018 |
| 201 | BNG-2024-2-17997-35 | Munshiganj village ("Mushiganj") | Munshiganj | Murder case over a protester shot in Munshiganj on 4 Aug 2024, filed at Munshiganj Sadar police station. This rules out the Munshiganj in Shyamnagar, Satkhira |

**Still unconfirmed.** Rows 16 (Gopalpur), 19 (Umarpur) and 37 (Kaliganj, date) could not be matched to a specific news report. Their confidence levels above reflect that.

## Event ID prefixes

Most `relid` values start with `BNG`, but 51 start with another country code. The prefix is the country UCDP files the conflict or actor under, not where the event happened. All 51 events took place in Bangladesh.

| Prefix | Events | What they are |
|---|---|---|
| `MYA-…-3-15167` | 28 | Killings of Rohingya in the Cox's Bazar camps (one-sided violence). Sources attribute them mainly to ARSA |
| `MYA-…-1-11387` | 5 | Deaths in Bandarban from fighting in Myanmar's Rakhine (Arakan) State across the border, such as mortar fire and landmines |
| `AFG-…-3-1076`, `AFG-…-3-973` | 15 | Islamic State attacks in Bangladesh, including the July 2016 Holey Artisan café attack and the 2016 killings of Hindu priests and Christian converts |
| `IND-…-3-954` | 3 | Bangladeshis shot by India's Border Security Force (BSF) on the Panchagarh and Lalmonirhat borders |

The digit after the year is UCDP's type of violence: 1 = state-based, 2 = non-state, 3 = one-sided.

## Caveats

- Rows marked Medium or Low confidence above should be reviewed if district-level results depend on them.
- Some events span areas or boundaries, such as border incidents or several neighbourhoods. Each was assigned to the single district named or implied by its location.
- Row numbers refer to the sheet as of this mapping. Use `relid` as the stable identifier if the data is re-sorted.

## Sources consulted

- Dhaka Tribune, "Two killed in 'gunfights' in two districts" (3 Mar 2017): https://archive.dhakatribune.com/bangladesh/crime/2017/03/03/two-killed-gunfight-two-districts
- South Asia Terrorism Portal, Bangladesh Timeline 2017: https://www.satp.org/satporgtp/countries/bangladesh/timeline/2017.htm
- BenarNews, "2 Suspected Militants Killed in Police Raid in Southwestern Bangladesh" (7 May 2017): https://www.benarnews.org/english/news/bengali/militants-killed-05072017135855.html
- The Daily Star, "Chapainawabganj AL activist burnt to death": https://thedailystar.net/node/10020
- The Daily Star, "Another AL man killed by 'Jamaat'": https://archive.thedailystar.net/beta2/news/another-al-man-killed-by-jamaat/
- Jago News, "Hasina, Quader, Shamim sued for killing fish trader": https://www.jagonews24.com/en/politics/news/76278
- The Daily Star, "Four killed in militant den" (Shibganj, Apr 2017): https://www.thedailystar.net/frontpage/four-killed-militant-den-1397650
- The Daily Star, "Violence at Fatikchhari" (Bhujpur, Apr 2013): https://online-d11.thedailystar.net/news/violence-at-fatikchhari
- The Daily Star, "17 killed in polls violence" (Pakuria, Mohanpur, Dec 2018): https://www.thedailystar.net/bangladesh-national-election-2018/election-clash-with-bnp-men-rangamati-jubo-league-leader-killed-1680721
- The Business Standard, "Hasina, Quader among 313 sued for murder in Munshiganj": https://www.tbsnews.net/node/929366
- teachers.gov.bd, training report naming Chupair Girls' High School, Kaliganj, Gazipur: https://www.teachers.gov.bd/index.php/content/details/729985
- Wikipedia, "Attack on Enayetpur police station" (locates Enayetpur in Sirajganj): https://en.wikipedia.org/wiki/Attack_on_Enayetpur_police_station
- UCDP GED codebook (relid structure, type of violence codes): https://ucdp.uu.se/downloads/ged/ged171.pdf
