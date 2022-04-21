DROP TABLE IF EXISTS `DynRoomUserVCstamp`;
CREATE TABLE Sloth.DynRoomUserVCstamp (user_id bigint, user_vc_ts bigint);

DROP TABLE IF EXISTS `DynamicRoom`;
CREATE TABLE Sloth.DynamicRoom (guild_id BIGINT, room_id BIGINT, vc_id BIGINT, room_ts BIGINT, is_perma_room BOOLEAN, empty_since_ts INT);

DROP TABLE IF EXISTS `LanguageRoom`;
CREATE TABLE Sloth.LanguageRoom (room_id SERIAL, category VARCHAR(32), english_name VARCHAR(32), room_name BLOB, room_quant INT, room_capacity INT, max_empty_time INT);
INSERT INTO Sloth.LanguageRoom (category, english_name, room_name, room_quant, room_capacity, max_empty_time) VALUES 
/* 001 */("germanic", "Swedish", "Svenska 🪑🇸🇪", 2, 10, 60 * 60 * 1),
/* 002 */("germanic", "Norwegian", "Norsk ⛷🇳🇴", 2, 10, 60 * 60 * 1),
/* 003 */("germanic", "Danish", "Dansk 🥔🇩🇰", 2, 10, 60 * 60 * 1),
/* 004 */("germanic", "Dutch", "Nederlands 🚴🇧🇪🇳🇱", 2, 10, 60 * 60 * 1),
/* 005 */("sub-saharan", "Afrikaans", "Afrikaans 🦁🇿🇦", 2, 10, 60 * 60 * 1),
/* 006 */("uralic", "Finnish", "Suomi ❄🇫🇮", 2, 10, 60 * 60 * 1),
/* 007 */("uralic", "Hungarian", "Magyar 🌶🇭🇺", 2, 10, 60),
/* 008 */("romance", "Catalan", "Català", 2, 10, 60 * 60 * 1),
/* 009 */("romance", "Romanian", "Română 🧛🇷🇴", 2, 10, 60 * 60 * 1),
/* 010 */("baltic", "Latvian", "Latviešu", 2, 10, 60),
/* 011 */("slavic", "Polish", "Polski 🧅🇵🇱", 2, 10, 60 * 60 * 1),
/* 012 */("slavic", "Czech", "česko 🇨🇿🇸🇰", 2, 10, 60),
/* 013 */("slavic", "Ukrainian", "Українська 🥣🇺🇦", 2, 10, 60),
/* 014 */("balkan", "Macedonian", "Македонски 🇲🇰", 2, 10, 60),
/* 015 */("slavic", "Bulgarian", "Български 🌹🇧🇬", 2, 10, 60),
/* 016 */("semitic", "Hebrew", "עִברִית 🕎🇮🇱", 2, 10, 60 * 60 * 1),
/* 017 */("turkic", "Kazakh", "Қазақ 🐎🇰🇿", 2, 10, 60),
/* 018 */("turkic", "Azerbaijani", "Azərbaycan 🔥🇦🇿", 2, 10, 60),
/* 019 */("iranian", "Kurdish", "كوردی🥪 (kurdish)", 2, 10, 60),
/* 020 */("iranian", "Farsi", "فارسی🐈🇮🇷", 2, 10, 60),
/* 021 */("south-east asian", "Vietnamese", "Tiếng Việt🛵🇻🇳", 2, 10, 60 * 60 * 1),
/* 022 */("south-east asian", "Khmer", "ខ្មែរ🇰🇭", 2, 10, 60),
/* 023 */("south-east asian", "Thai", "ภาษาไทย 🥘🇹🇭", 2, 10, 60),
/* 024 */("east asian", "Mongolian", "Монгол хэл 🇲🇳", 2, 10, 60),
/* 025 */("east asian", "Cantonese", "粤语 🍚🇭🇰", 2, 10, 60),
/* 026 */("south asian", "South Asian Languages", "South Asian languages🧘🇮🇳🇵🇰🇳🇵", 2, 10, 60),
/* 027 */("south asian", "Hindi", "हिन्दी 🏏🇮🇳", 2, 10, 60 * 60 * 1),
/* 028 */("unafiliated", "Greek", "Ελληνικά 🏛️🇬🇷", 2, 10, 60 * 60 * 1),
/* 029 */("germanic", "Luxembourgish", "lëtzebuergesch 🇱🇺", 2, 10, 60 * 60 * 1),

/* 030 */("south asian", "Tamil", "தமிழ் (Tamil)", 2, 10, 60),
/* 031 */("south asian", "Punjabi", "پنجاب (Punjabi) ", 2, 10, 60),
/* 032 */("south asian", "Gujarati", "ગુજરાતી (Gujarati)", 2, 10, 60),
/* 033 */("south asian", "Marathi", "मराठी (Marathi)", 2, 10, 60),
/* 034 */("south asian", "Sanskrit", "संस्कृत (Sanskrit)", 2, 10, 60),
/* 035 */("south asian", "Malayalam", "മലയാളം (Malayalam)", 2, 10, 60),
/* 036 */("south asian", "Telugu", "తెలుగు (Telugu)", 2, 10, 60),
/* 037 */("south asian", "Kannada", "ಕನ್ನಡ (Kannada)", 2, 10, 60),
/* 038 */("south asian", "Bengali", "বাংলা (Bengali)", 2, 10, 60),
/* 039 */("south asian", "Nepali", "नेपाली (Nepali)", 2, 10, 60),

/* 040 */("south asian", "Urdu", "اردو Urdu 🇵🇰", 2, 10, 60),

/* 041 */("germanic", "Swiss German", "Schwyzerdütsch (Swiss German)", 2, 10, 60),

/* 042 */("romance", "Basque", "Euskara", 2, 10, 60),
/* 043 */("romance", "Galician", "Galego", 2, 10, 60),

/* 044 */("sub-saharan", "Yoruba", "عِدعِ يوْرُبا (Yorúbà)", 2, 10, 60),
/* 045 */("sub-saharan", "Hausa", "هَرْشَن هَوْسَ (Hausa)", 2, 10, 60),

/* 046 */("sub-saharan", "Igbo", "Ṇ́dị́ Ìgbò (Igbo)", 2, 10, 60),
/* 047 */("sub-saharan", "Somali", "صومالي (Somali)", 2, 10, 60),
/* 048 */("sub-saharan", "Swahili", "Kiswahili", 2, 10, 60),
/* 049 */("sub-saharan", "Twi", "Akan kasa", 2, 10, 60),
/* 050 */("sub-saharan", "Tigrinya", "ትግርኛ (Tigrinya)", 2, 10, 60),
/* 051 */("sub-saharan", "Lingala", "Lingála", 2, 10, 60),
/* 052 */("sub-saharan", "Zulu", "isiZulu", 2, 10, 60),
/* 053 */("sub-saharan", "Wolof", "ولوفل (Wolof)", 2, 10, 60),
/* 054 */("sub-saharan", "Xhosa", "isiXhosa", 2, 10, 60),
/* 055 */("sub-saharan", "Ndebele", "Ndebele", 2, 10, 60),
/* 056 */("sub-saharan", "Shona", "chiShona", 2, 10, 60),
/* 057 */("sub-saharan", "Oromo", "Afaan Oromoo", 2, 10, 60),

/* 058 */("sub-saharan", "Amharic", "አማርኛ 🏴󠁥󠁴󠁡󠁭󠁿", 2, 10, 60),

/* 059 */("romance", "Lombard", "Lumbard 🇮🇹", 2, 10, 60),
/* 060 */("romance", "Sicilian", "Sicilianu 🇮🇹", 2, 10, 60),
/* 061 */("romance", "Neapolitan", "Napulitan 🇮🇹", 2, 10, 60),
/* 062 */("romance", "Salentino", "Salentinu 🇮🇹", 2, 10, 60),
/* 063 */("romance", "Venetian", "Vèneto 🇮🇹", 2, 10, 60),
/* 064 */("romance", "Ligurian", "Lìgure 🇮🇹", 2, 10, 60),
/* 065 */("romance", "Sardinian", "Sard 🇮🇹", 2, 10, 60),
/* 066 */("romance", "Romanesco", "Romanesco 🇮🇹", 2, 10, 60),

/* 067 */("germanic", "Icelandic", "íslenska 🇮🇸", 2, 10, 60 * 60 * 1),

/* 068 */("slavic", "Albanian", "shqip 🇦🇱", 2, 10, 60),

/* 069 */("slavic", "Slovak", "slovenský 🇸🇰", 2, 10, 60),

/* 070 */("balkan", "Croatian", "Hrvatski 🇭🇷", 2, 10, 60),
/* 071 */("balkan", "Montenegrin", "Crnogorski 🇲🇪", 2, 10, 60),
/* 072 */("balkan", "Serbian", "Srpski 🇷🇸", 2, 10, 60),
/* 122 */("balkan", "Bosnian", "Bosanci 🇧🇦", 2, 10, 60),

/* 073 */("baltic", "Lithuanian", "Lietuvių 🇱🇹🥔", 2, 10, 60),

/* 074 */("east asian", "Wenzhounese", "溫州話 🇨🇳", 2, 10, 60),
/* 075 */("east asian", "Taishanese", "台山話 🇨🇳", 2, 10, 60),
/* 076 */("east asian", "Sichuanese", "四川話 🇨🇳", 2, 10, 60),
/* 077 */("east asian", "Hakka", "客家話 🇨🇳", 2, 10, 60),
/* 078 */("east asian", "Hainanese", "海南話 🇨🇳", 2, 10, 60),

/* 079 */("east asian", "Taiwanese", "閩南語 ", 2, 10, 60),
/* 080 */("east asian", "Teochew", "Teochew", 2, 10, 60),
/* 081 */("east asian", "Hockchew", "Hockchew", 2, 10, 60),

/* 082 */("south-east asian", "Bisaya", "Bisaya", 2, 10, 60),
/* 083 */("south-east asian", "Waray-waray", "Waray-waray", 2, 10, 60),
/* 084 */("south-east asian", "Kapampangan", "Kapampangan", 2, 10, 60),
/* 085 */("south-east asian", "Cebuano", "Cebuano 🥥🇵🇭", 2, 10, 60),
/* 086 */("south-east asian", "Ilocano", "Ilocano", 2, 10, 60),

/* 087 */("south-east asian", "Javanese", "Bahasa Jawa 🇮🇩🦜", 2, 10, 60),
/* 088 */("south-east asian", "Lao", "ພາສາລາວ", 2, 10, 60),

/* 089 */("romance", "Portunhol", "Portuñol 🧉🌎", 2, 10, 60),

/* 090 */("semitic", "Amazigh", "ⵜⴰⵎⴰⵣⵉⵖⵜ (Tamazigh)", 2, 10, 60 * 60 * 1),

/* 091 */("conlang", "Esperanto", "Esperanto", 2, 10, 60),
/* 092 */("conlang", "Toki Pona", "Toki Pona", 2, 10, 60),

/* 093 */("sign languages", "American sign l.", "ASL (American sign l.)", 2, 10, 60),
/* 094 */("sign languages", "British sign l.", "BSL (British sign l.)", 2, 10, 60),
/* 095 */("sign languages", "Langue des signes française", "Libra (langue des signes)  ", 2, 10, 60),
/* 096 */("sign languages", "Deutsche Gebärdensprache", "DGS (Deutsche Gebärdensprache l.)", 2, 10, 60),
/* 097 */("sign languages", "Língua brasileira de sinais", "Libras (Língua brasileira de sinais)", 2, 10, 60),
/* 098 */("sign languages", "CSL (Chinese sign l.)", "CSL (中国手语)", 2, 10, 60),

/* 099 */("unafiliated", "Ancient Greek", "αρχαία ελληνικά (Ancient Greek)", 2, 10, 60),
/* 100 */("iranian", "Pashto", "پښتو (Pashto)", 2, 10, 60),
/* 101 */("germanic", "Faroese", "Føroyskt (Faroese)", 2, 10, 60),
/* 102 */("slavic", "Belarusian", "беларуская ", 2, 10, 60),
/* 103 */("turkic", "Turkmen", "Türkmençe (Turkmen)", 2, 10, 60),
/* 104 */("turkic", "Kyrgyz", "Кыргыз 🇰🇬", 2, 10, 60),
/* 105 */("turkic", "Uzbek", "Oʻzbek tili (Uzbek)", 2, 10, 60),

/* 106 */("indigenous", "Sami", "Sámi (Sami)", 2, 10, 60),
/* 107 */("indigenous", "Quechua", "Runasimi (Quechua)", 2, 10, 60),
/* 108 */("indigenous", "Guarani", "Avañeʼẽ (Guarani)", 2, 10, 60),
/* 109 */("indigenous", "Greenlandic", "Kalaallisut (Greenlandic)", 2, 10, 60),
/* 110 */("indigenous", "Nahuatl", "Aztec (Nahuatl)", 2, 10, 60),
/* 111 */("indigenous", "Yucatec", "Maya (Yucatec)", 2, 10, 60),

/* 112 */("unafiliated", "Armenian", "հայերեն (Armenian)", 2, 10, 60),
/* 113 */("unafiliated", "Georgian", "ქართული ენა (Georgian)", 2, 10, 60),

/* 114 */("south-east asian", "Kelantanese", "Kelantanese", 2, 10, 60),
/* 115 */("south-east asian", "Sarawak Malay", "Bahasa Sarawak", 2, 10, 60),
/* 116 */("south-east asian", "Kedahan", "Bahasa Melayu Kedah", 2, 10, 60),

/* 117 */("romance", "Latin", "Latin", 2, 10, 60 * 60 * 1),

/* 118 */("uralic", "Estonian", "Estonian", 2, 10, 60 * 60 * 1),

/* 119 */("south-east asian", "Bahasa Batak", "Bahasa Batak 🇮🇩🦏", 2, 10, 60),

/* 120 */("celtic", "Celtic", "Celtic", 2, 10, 60),

/* 121 */("iranian", "Gilaki", "گیلکی (Gilaki)", 2, 10, 60),

/* ??? */("category", "english_name", "room_name", 2, 10, 60)

;

/* Remember to set category permissions to:
* -> muted - can connect but not speak
* -> everyone - can connect but not view
* -> show me everything - can view

* speaker -> pretend permission the means view_channel, connect and speak
*/
DROP TABLE IF EXISTS `LanguageRoomPermissions`;
CREATE TABLE Sloth.LanguageRoomPermissions (id SERIAL, room_id BIGINT, role_id BIGINT, permission_name VARCHAR(32), permission_value BOOLEAN);
INSERT INTO Sloth.LanguageRoomPermissions (room_id, role_id, permission_name, permission_value) VALUES 
/* Swedish channel */
(1, /*Native Swedish*/ 471922035107430400, "speaker", true),
(1, /*Fluent Swedish*/ 490121747824377856, "speaker", true),
(1, /*Studying Swedish*/ 475484739655041034, "speaker", true),
(1, /*Native Norwegian*/ 475484050493014036, "speaker", true),
(1, /*Native Danish*/ 475989214186438656, "speaker", true),

/* Norwegian channel */
(2, /*Native Norwegian*/ 475484050493014036, "speaker", true),
(2, /*Fluent Norwegian*/ 490122353339006987, "speaker", true),
(2, /*Studying Norwegian*/ 476480917628649473, "speaker", true),
(2, /*Native Swedish*/ 471922035107430400, "speaker", true),
(2, /*Native Danish*/ 475989214186438656, "speaker", true),

/* Danish channel */
(3, /*Native Danish*/ 475989214186438656, "speaker", true),
(3, /*Fluent Danish*/ 490129625096388655, "speaker", true),
(3, /*Studying Danish*/ 476477915362754560, "speaker", true),
(3, /*Native Swedish*/ 471922035107430400, "speaker", true),
(3, /*Native Norwegian*/ 475484050493014036, "speaker", true),

/* Dutch channel */
(4, /*Native Dutch*/ 486147198837587981, "speaker", true),
(4, /*Fluent Dutch*/ 483863965747642368, "speaker", true),
(4, /*Studying Dutch*/ 471932893027893248, "speaker", true),

/* Afrikaans channel */
(5, /*Native Afrikaans*/ 531854806525018112, "speaker", true),
(5, /*Fluent Afrikaans*/ 531855093817933834, "speaker", true),
(5, /*Studying Afrikaans*/ 531855141352112139, "speaker", true),

/* Finnish channel */
(6, /*Native Finnish*/ 476018604240928779, "speaker", true),
(6, /*Fluent Finnish*/ 476741198149713935, "speaker", true),
(6, /*Studying Finnish*/ 476741389112180737, "speaker", true),

/* Hungarian channel */
(7, /*Native Hungarian*/ 476019880798453762, "speaker", true),
(7, /*Studying Hungarian*/ 476764441707282456, "speaker", true),

/* Catalan channel */
(8, /*Native Catalan*/ 484820153197002773, "speaker", true),
(8, /*Fluent Catalan*/ 489345218852814848, "speaker", true),
(8, /*Studying Catalan*/ 490144247559880729, "speaker", true),
(8, /*Native Basque*/ 480754000275177483, "speaker", true),
(8, /*Studying Basque*/ 563373255642185778, "speaker", true),

/* Romanian channel */
(9, /*Native Romanian*/ 475240440891965471, "speaker", true),
(9, /*Studying Romanian*/ 476506364831858690, "speaker", true),

/* Latvian channel */
(10, /*Native Latvian*/ 476062242690039837, "speaker", true),
(10, /*Studying Latvian*/ 476765630519836693, "speaker", true),
(10, /*Native Lithuanian*/ 476032570979647508, "speaker", true),
(10, /*Studying Lithuanian*/ 475290035470467072, "speaker", true),

/* Polish channel */
(11, /*Native Polish*/ 475254841044631562, "speaker", true),
(11, /*Fluent Polish*/ 476503475954647071, "speaker", true),
(11, /*Studying Polish*/ 476630931252314153, "speaker", true),

/* Czech channel */
(12, /*Native Czech-Slovak*/ 476019943003914251, "speaker", true),
(12, /*Fluent Czech-Slovak*/ 471926693368692738, "speaker", true),
(12, /*Studying Czech-Slovak*/ 471931483876229131, "speaker", true),

/* Ukrainian channel */
(13, /*Native Ukrainian*/ 475240441277579274, "speaker", true),
(13, /*Fluent Ukrainian*/ 476505951235735567, "speaker", true),
(13, /*Studying Ukrainian*/ 475294137109708801, "speaker", true),

/* Balkanski channel */
(14, /*Native Balkan Languages*/ 476020149846278154, "speaker", true),
(14, /*Native Macedonian*/ 476505421457391626, "speaker", true),
(14, /*Fluent Balkan Languages*/ 476645488574070785, "speaker", true),
(14, /*Fluent Macedonian*/ 476506585867223040, "speaker", true),
(14, /*Studying Balkan Languages*/ 476630854706397186, "speaker", true),
(14, /*Studying Macedonian*/ 476631603872006144, "speaker", true),

/* Bulgarian channel */
(15, /*Native Bulgarian*/ 475240441084903445, "speaker", true),
(15, /*Native Albanian*/ 475240441084903445, "speaker", true),
(15, /*Fluent Bulgarian*/ 476506070039134259, "speaker", true),
(15, /*Studying Bulgarian*/ 476763017204203560, "speaker", true),
(15, /*Studying Albanian*/ 489739368471199745, "speaker", true),

/* Hebrew channel */
(16, /*Native Hebrew*/ 474894084704698370, "speaker", true),
(16, /*Fluent Hebrew*/ 476639355146993664, "speaker", true),
(16, /*Studying Hebrew*/ 562053868356370434, "speaker", true),

/* Kazakh channel */
(17, /*Native Kazakh*/ 480431310007959572, "speaker", true),
(17, /*Native Turkic Languages*/ 810441635418079233, "speaker", true),
(17, /*Studying Kazakh*/ 823204473908363324, "speaker", true),

/* Azerbaijani channel */
(18, /*Native Azerbaijani*/ 479441520257138698, "speaker", true),
(18, /*Native Turkic Languages*/ 810441635418079233, "speaker", true),
(18, /*Studying Azerbaijani*/ 764665103701639179, "speaker", true),

/* Kurdish channel */
(19, /*Native Kurdish*/ 478181311971065867, "speaker", true),

/* Farsi channel */
(20, /*Native Farsi*/ 478178098437685248, "speaker", true),
(20, /*Fluent Farsi*/ 478178529368866826, "speaker", true),
(20, /*Studying Farsi*/ 563369533440655360, "speaker", true),

/* Vietnamese channel */
(21, /*Native Vietnamese*/ 475240442779140116, "speaker", true),
(21, /*Fluent Vietnamese*/ 476746087856603166, "speaker", true),
(21, /*Studying Vietnamese*/ 563361451222237194, "speaker", true),

/* Khmer channel */
(22, /*Native Khmer*/ 823204525891911690, "speaker", true),
(22, /*Studying Khmer*/ 823203829876654131, "speaker", true),

/* Thai channel */
(23, /*Native Thai*/ 478973636389109784, "speaker", true),
(23, /*Fluent Thai*/ 476745694770626560, "speaker", true),
(23, /*Studying Thai*/ 563359993005473808, "speaker", true),

/* Mongolian channel */
(24, /*Native Mongolian*/ 471925922791030785, "speaker", true),
(24, /*Studying Mongolian*/ 563366459217149957, "speaker", true),

/* Cantonese channel */
(25, /*Native Cantonese*/ 491571804566192129, "speaker", true),
(25, /*Fluent Cantonese*/ 562546146304720897, "speaker", true),
(25, /*Studying Cantonese*/ 562053222961774612, "speaker", true),

/* South Asian Languages channel */
(26, /*Native South Asian Languages*/ 531855188873445387, "speaker", true),
(26, /*Fluent South Asian Languages*/ 531855277012549642, "speaker", true),
(26, /*Studying South Asian Languages*/ 563064564518879279, "speaker", true),

/* Hindi channel */
(27, /*Native Hindi-Urdu*/ 823204505242959882, "speaker", true),
(27, /*Fluent Hindi-Urdu*/ 823470151059505172, "speaker", true),
(27, /*Studying Hindi-Urdu*/ 823469852924575794, "speaker", true),

/* Greek channel */
(28, /*Native Greek*/ 478235006121017355, "speaker", true),
(28, /*Fluent Greek*/ 490174425363251210, "speaker", true),
(28, /*Studying Greek*/ 562034165789491231, "speaker", true),

/* Luxembourgish channel */
(29, /*Native Luxembourgish*/ 475240440501633034, "speaker", true),
(29, /*Studying Luxembourgish*/ 490132397078347800, "speaker", true),

(30, /*Native South Asian Languages*/ 531855188873445387, "speaker", true),
(30, /*Fluent South Asian Languages*/ 531855277012549642, "speaker", true),
(30, /*Studying South Asian Languages*/ 563064564518879279, "speaker", true),

(31, /*Native South Asian Languages*/ 531855188873445387, "speaker", true),
(31, /*Fluent South Asian Languages*/ 531855277012549642, "speaker", true),
(31, /*Studying South Asian Languages*/ 563064564518879279, "speaker", true),

(32, /*Native South Asian Languages*/ 531855188873445387, "speaker", true),
(32, /*Fluent South Asian Languages*/ 531855277012549642, "speaker", true),
(32, /*Studying South Asian Languages*/ 563064564518879279, "speaker", true),

(33, /*Native South Asian Languages*/ 531855188873445387, "speaker", true),
(33, /*Fluent South Asian Languages*/ 531855277012549642, "speaker", true),
(33, /*Studying South Asian Languages*/ 563064564518879279, "speaker", true),

(34, /*Native South Asian Languages*/ 531855188873445387, "speaker", true),
(34, /*Fluent South Asian Languages*/ 531855277012549642, "speaker", true),
(34, /*Studying South Asian Languages*/ 563064564518879279, "speaker", true),

(35, /*Native South Asian Languages*/ 531855188873445387, "speaker", true),
(35, /*Fluent South Asian Languages*/ 531855277012549642, "speaker", true),
(35, /*Studying South Asian Languages*/ 563064564518879279, "speaker", true),

(36, /*Native South Asian Languages*/ 531855188873445387, "speaker", true),
(36, /*Fluent South Asian Languages*/ 531855277012549642, "speaker", true),
(36, /*Studying South Asian Languages*/ 563064564518879279, "speaker", true),

(37, /*Native South Asian Languages*/ 531855188873445387, "speaker", true),
(37, /*Fluent South Asian Languages*/ 531855277012549642, "speaker", true),
(37, /*Studying South Asian Languages*/ 563064564518879279, "speaker", true),

(38, /*Native South Asian Languages*/ 531855188873445387, "speaker", true),
(38, /*Fluent South Asian Languages*/ 531855277012549642, "speaker", true),
(38, /*Studying South Asian Languages*/ 563064564518879279, "speaker", true),

(39, /*Native South Asian Languages*/ 531855188873445387, "speaker", true),
(39, /*Fluent South Asian Languages*/ 531855277012549642, "speaker", true),
(39, /*Studying South Asian Languages*/ 563064564518879279, "speaker", true),

/* Urdu Channel */
(40, /*Native Hindi-Urdu*/ 823204505242959882, "speaker", true),
(40, /*Fluent Hindi-Urdu*/ 823470151059505172, "speaker", true),
(40, /*Studying Hindi-Urdu*/ 823469852924575794, "speaker", true),

/* Swiss German Channel */
(41, /*Native German*/ 471921967499444225, "speaker", true),
(41, /*Fluent German*/ 490131150879195138, "speaker", true),
(41, /*Studying German*/ 475241077578924053, "speaker", true),

/* Basque Channel */
(42, /*Native Basque*/ 480754000275177483, "speaker", true),
(42, /*Studying Basque*/ 563373255642185778, "speaker", true),

/* Galician Channel */
(43, /*Native Spanish*/ 474726084638670848, "speaker", true),
(43, /*Fluent Spanish*/ 474720724125351937, "speaker", true),
(43, /*Studying Spanish*/ 474745895796342784, "speaker", true),

/* Yoruba Channel */
(44, /*Native Sub-Saharan*/ 777305645636124675, "speaker", true),
(44, /*Studying Sub-Saharan*/ 590491309278494720, "speaker", true),

/* Hausa Channel */
(45, /*Native Sub-Saharan*/ 777305645636124675, "speaker", true),
(45, /*Studying Sub-Saharan*/ 590491309278494720, "speaker", true),

/* Igbo Channel */
(46, /*Native Sub-Saharan*/ 777305645636124675, "speaker", true),
(46, /*Studying Sub-Saharan*/ 590491309278494720, "speaker", true),

/* Somali Channel */
(47, /*Native Sub-Saharan*/ 777305645636124675, "speaker", true),
(47, /*Studying Sub-Saharan*/ 590491309278494720, "speaker", true),

/* Swahili Channel */
(48, /*Native Sub-Saharan*/ 777305645636124675, "speaker", true),
(48, /*Studying Sub-Saharan*/ 590491309278494720, "speaker", true),

/* Twi Channel */
(49, /*Native Sub-Saharan*/ 777305645636124675, "speaker", true),
(49, /*Studying Sub-Saharan*/ 590491309278494720, "speaker", true),

/* Tigrinya Channel */
(50, /*Native Sub-Saharan*/ 777305645636124675, "speaker", true),
(50, /*Studying Sub-Saharan*/ 590491309278494720, "speaker", true),

/* Lingala Channel */
(51, /*Native Sub-Saharan*/ 777305645636124675, "speaker", true),
(51, /*Studying Sub-Saharan*/ 590491309278494720, "speaker", true),

/* Zulu Channel */
(52, /*Native Sub-Saharan*/ 777305645636124675, "speaker", true),
(52, /*Studying Sub-Saharan*/ 590491309278494720, "speaker", true),

/* Wolof Channel */
(53, /*Native Sub-Saharan*/ 777305645636124675, "speaker", true),
(53, /*Studying Sub-Saharan*/ 590491309278494720, "speaker", true),

/* Xhosa Channel */
(54, /*Native Sub-Saharan*/ 777305645636124675, "speaker", true),
(54, /*Studying Sub-Saharan*/ 590491309278494720, "speaker", true),

/* Ndebele Channel */
(55, /*Native Sub-Saharan*/ 777305645636124675, "speaker", true),
(55, /*Studying Sub-Saharan*/ 590491309278494720, "speaker", true),

/* Shona Channel */
(56, /*Native Sub-Saharan*/ 777305645636124675, "speaker", true),
(56, /*Studying Sub-Saharan*/ 590491309278494720, "speaker", true),

/* Oromo Channel */
(57, /*Native Sub-Saharan*/ 777305645636124675, "speaker", true),
(57, /*Studying Sub-Saharan*/ 590491309278494720, "speaker", true),

/* Amharic Channel */
(58, /*Native Sub-Saharan*/ 777305645636124675, "speaker", true),
(58, /*Studying Sub-Saharan*/ 590491309278494720, "speaker", true),

/* Lombard Channel */
(59, /*Native Italian*/ 474876492585893908, "speaker", true),
(59, /*Fluent Italian*/ 474720800071614489, "speaker", true),
(59, /*Studying Italian*/ 475236110315028490, "speaker", true),

/* Sicilian Channel */
(60, /*Native Italian*/ 474876492585893908, "speaker", true),
(60, /*Fluent Italian*/ 474720800071614489, "speaker", true),
(60, /*Studying Italian*/ 475236110315028490, "speaker", true),

/* Neapolitan Channel */
(61, /*Native Italian*/ 474876492585893908, "speaker", true),
(61, /*Fluent Italian*/ 474720800071614489, "speaker", true),
(61, /*Studying Italian*/ 475236110315028490, "speaker", true),

/* Salentino Channel */
(62, /*Native Italian*/ 474876492585893908, "speaker", true),
(62, /*Fluent Italian*/ 474720800071614489, "speaker", true),
(62, /*Studying Italian*/ 475236110315028490, "speaker", true),

/* Venetian Channel */
(63, /*Native Italian*/ 474876492585893908, "speaker", true),
(63, /*Fluent Italian*/ 474720800071614489, "speaker", true),
(63, /*Studying Italian*/ 475236110315028490, "speaker", true),

/* Ligurian Channel */
(64, /*Native Italian*/ 474876492585893908, "speaker", true),
(64, /*Fluent Italian*/ 474720800071614489, "speaker", true),
(64, /*Studying Italian*/ 475236110315028490, "speaker", true),

/* Sardinian Channel */
(65, /*Native Italian*/ 474876492585893908, "speaker", true),
(65, /*Fluent Italian*/ 474720800071614489, "speaker", true),
(65, /*Studying Italian*/ 475236110315028490, "speaker", true),

/* Romanesco Channel */
(66, /*Native Italian*/ 474876492585893908, "speaker", true),
(66, /*Fluent Italian*/ 474720800071614489, "speaker", true),
(66, /*Studying Italian*/ 475236110315028490, "speaker", true),

/* Icelandic Channel */
(67, /*Native Icelandic*/ 477438984432386048, "speaker", true),
(67, /*Fluent Icelandic*/ 490123385376997376, "speaker", true),
(67, /*Studying Icelandic*/ 477439167257772045, "speaker", true),

/* Albanian Channel */
(68, /*Native Albanian*/ 475240441084903445, "speaker", true),
(68, /*Studying Albanian*/ 489739368471199745, "speaker", true),
(68, /*Native Bulgarian*/ 475240441084903445, "speaker", true),
(68, /*Fluent Bulgarian*/ 476506070039134259, "speaker", true),
(68, /*Studying Bulgarian*/ 476763017204203560, "speaker", true),

/* Slovak Channel */
(69, /*Native Czech-Slovak*/ 476019943003914251, "speaker", true),
(69, /*Fluent Czech-Slovak*/ 471926693368692738, "speaker", true),
(69, /*Studying Czech-Slovak*/ 471931483876229131, "speaker", true),

/* Croatian Channel */
(70, /*Native Balkan Languages*/ 476020149846278154, "speaker", true),
(70, /*Native Macedonian*/ 476505421457391626, "speaker", true),
(70, /*Fluent Balkan Languages*/ 476645488574070785, "speaker", true),
(70, /*Fluent Macedonian*/ 476506585867223040, "speaker", true),
(70, /*Studying Balkan Languages*/ 476630854706397186, "speaker", true),
(70, /*Studying Macedonian*/ 476631603872006144, "speaker", true),

/* Montenegrin Channel */
(71, /*Native Balkan Languages*/ 476020149846278154, "speaker", true),
(71, /*Native Macedonian*/ 476505421457391626, "speaker", true),
(71, /*Fluent Balkan Languages*/ 476645488574070785, "speaker", true),
(71, /*Fluent Macedonian*/ 476506585867223040, "speaker", true),
(71, /*Studying Balkan Languages*/ 476630854706397186, "speaker", true),
(71, /*Studying Macedonian*/ 476631603872006144, "speaker", true),

/* Serbian Channel */
(72, /*Native Balkan Languages*/ 476020149846278154, "speaker", true),
(72, /*Native Macedonian*/ 476505421457391626, "speaker", true),
(72, /*Fluent Balkan Languages*/ 476645488574070785, "speaker", true),
(72, /*Fluent Macedonian*/ 476506585867223040, "speaker", true),
(72, /*Studying Balkan Languages*/ 476630854706397186, "speaker", true),
(72, /*Studying Macedonian*/ 476631603872006144, "speaker", true),

-- /* Bosnian Channel */
(122, /*Native Balkan Languages*/ 476020149846278154, "speaker", true),
(122, /*Native Macedonian*/ 476505421457391626, "speaker", true),
(122, /*Fluent Balkan Languages*/ 476645488574070785, "speaker", true),
(122, /*Fluent Macedonian*/ 476506585867223040, "speaker", true),
(122, /*Studying Balkan Languages*/ 476630854706397186, "speaker", true),
(122, /*Studying Macedonian*/ 476631603872006144, "speaker", true),

/* Lithuanian channel */
(73, /*Native Latvian*/ 476062242690039837, "speaker", true),
(73, /*Studying Latvian*/ 476765630519836693, "speaker", true),
(73, /*Native Lithuanian*/ 476032570979647508, "speaker", true),
(73, /*Studying Lithuanian*/ 475290035470467072, "speaker", true),

/* Wenzhounese Channel */
(74, /*Native Cantonese*/ 491571804566192129, "speaker", true),
(74, /*Fluent Cantonese*/ 562546146304720897, "speaker", true),
(74, /*Studying Cantonese*/ 562053222961774612, "speaker", true),
(74, /*Native Mandarin*/ 475240442540326923, "speaker", true),
(74, /*Fluent Mandarin*/ 476745894738264066, "speaker", true),
(74, /*Studying Mandarin*/ 562053107027148820, "speaker", true),

/* Taishanese Channel */
(75, /*Native Cantonese*/ 491571804566192129, "speaker", true),
(75, /*Fluent Cantonese*/ 562546146304720897, "speaker", true),
(75, /*Studying Cantonese*/ 562053222961774612, "speaker", true),
(75, /*Native Mandarin*/ 475240442540326923, "speaker", true),
(75, /*Fluent Mandarin*/ 476745894738264066, "speaker", true),
(75, /*Studying Mandarin*/ 562053107027148820, "speaker", true),

/* Sichuanese Channel */
(76, /*Native Cantonese*/ 491571804566192129, "speaker", true),
(76, /*Fluent Cantonese*/ 562546146304720897, "speaker", true),
(76, /*Studying Cantonese*/ 562053222961774612, "speaker", true),
(76, /*Native Mandarin*/ 475240442540326923, "speaker", true),
(76, /*Fluent Mandarin*/ 476745894738264066, "speaker", true),
(76, /*Studying Mandarin*/ 562053107027148820, "speaker", true),

/* Hakka Channel */
(77, /*Native Cantonese*/ 491571804566192129, "speaker", true),
(77, /*Fluent Cantonese*/ 562546146304720897, "speaker", true),
(77, /*Studying Cantonese*/ 562053222961774612, "speaker", true),
(77, /*Native Mandarin*/ 475240442540326923, "speaker", true),
(77, /*Fluent Mandarin*/ 476745894738264066, "speaker", true),
(77, /*Studying Mandarin*/ 562053107027148820, "speaker", true),

/* Hainanese Channel */
(78, /*Native Cantonese*/ 491571804566192129, "speaker", true),
(78, /*Fluent Cantonese*/ 562546146304720897, "speaker", true),
(78, /*Studying Cantonese*/ 562053222961774612, "speaker", true),
(78, /*Native Mandarin*/ 475240442540326923, "speaker", true),
(78, /*Fluent Mandarin*/ 476745894738264066, "speaker", true),
(78, /*Studying Mandarin*/ 562053107027148820, "speaker", true),

/* Taiwanese Channel */
(79, /*Native Cantonese*/ 491571804566192129, "speaker", true),
(79, /*Fluent Cantonese*/ 562546146304720897, "speaker", true),
(79, /*Studying Cantonese*/ 562053222961774612, "speaker", true),
(79, /*Native Mandarin*/ 475240442540326923, "speaker", true),
(79, /*Fluent Mandarin*/ 476745894738264066, "speaker", true),
(79, /*Studying Mandarin*/ 562053107027148820, "speaker", true),

/* Teochew Channel */
(80, /*Native Cantonese*/ 491571804566192129, "speaker", true),
(80, /*Fluent Cantonese*/ 562546146304720897, "speaker", true),
(80, /*Studying Cantonese*/ 562053222961774612, "speaker", true),
(80, /*Native Mandarin*/ 475240442540326923, "speaker", true),
(80, /*Fluent Mandarin*/ 476745894738264066, "speaker", true),
(80, /*Studying Mandarin*/ 562053107027148820, "speaker", true),

/* Hockchew Channel */
(81, /*Native Cantonese*/ 491571804566192129, "speaker", true),
(81, /*Fluent Cantonese*/ 562546146304720897, "speaker", true),
(81, /*Studying Cantonese*/ 562053222961774612, "speaker", true),
(81, /*Native Mandarin*/ 475240442540326923, "speaker", true),
(81, /*Fluent Mandarin*/ 476745894738264066, "speaker", true),
(81, /*Studying Mandarin*/ 562053107027148820, "speaker", true),

/* Bisaya Channel */
(82, /*Native Filipino*/ 477148625206640670, "speaker", true),
(82, /*Fluent Filipino*/ 477148892773875722, "speaker", true),
(82, /*Studying Filipino*/ 563360656032792587, "speaker", true),

/* Waray-waray Channel */
(83, /*Native Filipino*/ 477148625206640670, "speaker", true),
(83, /*Fluent Filipino*/ 477148892773875722, "speaker", true),
(83, /*Studying Filipino*/ 563360656032792587, "speaker", true),

/* Kapampangan Channel */
(84, /*Native Filipino*/ 477148625206640670, "speaker", true),
(84, /*Fluent Filipino*/ 477148892773875722, "speaker", true),
(84, /*Studying Filipino*/ 563360656032792587, "speaker", true),

/* Cebuano Channel */
(85, /*Native Filipino*/ 477148625206640670, "speaker", true),
(85, /*Fluent Filipino*/ 477148892773875722, "speaker", true),
(85, /*Studying Filipino*/ 563360656032792587, "speaker", true),

/* Ilocano Channel */
(86, /*Native Filipino*/ 477148625206640670, "speaker", true),
(86, /*Fluent Filipino*/ 477148892773875722, "speaker", true),
(86, /*Studying Filipino*/ 563360656032792587, "speaker", true),

/* Javanese Channel */
(87, /*Native Indonesian*/ 476379670334406686, "speaker", true),
(87, /*Fluent Indonesian*/ 562043546924744733, "speaker", true),
(87, /*Studying Indonesian*/ 562043546924744733, "speaker", true),

/* Lao Channel */
(88, /*Native Thai*/ 478973636389109784, "speaker", true),
(88, /*Fluent Thai*/ 476745694770626560, "speaker", true),
(88, /*Studying Thai*/ 563359993005473808, "speaker", true),

/* Portunhol Channel */
(89, /*Native Portuguese*/ 471922090908581890, "speaker", true),
(89, /*Fluent Portuguese*/ 474720855084105748, "speaker", true),
(89, /*Studying Portuguese*/ 474722401436041216, "speaker", true),
(89, /*Native Spanish*/ 474726084638670848, "speaker", true),
(89, /*Fluent Spanish*/ 474720724125351937, "speaker", true),
(89, /*Studying Spanish*/ 474745895796342784, "speaker", true),

/* Amazigh Channel */
(90, /*Native Amazigh*/ 658059163041267722, "speaker", true),
(90, /*Studying Amazigh*/ 948986544138616862, "speaker", true),

/* Esperanto Channel */
(91, /*Studying Conlang*/ 591576844042502193, "speaker", true),

/* Toki Pona Channel */
(92, /*Studying Conlang*/ 591576844042502193, "speaker", true),

/* American sign l. Channel */
(93, /*Native Sign Languages*/ 822155795475070977, "speaker", true),

/* British sign l. Channel */
(94, /*Native Sign Languages*/ 822155795475070977, "speaker", true),

/* Langue des signes française Channel */
(95, /*Native Sign Languages*/ 822155795475070977, "speaker", true),

/* Deutsche Gebärdensprache Channel */
(96, /*Native Sign Languages*/ 822155795475070977, "speaker", true),

/* Língua brasileira de sinais Channel */
(97, /*Native Sign Languages*/ 822155795475070977, "speaker", true),

/* CSL (Chinese sign l.) Channel */
(98, /*Native Sign Languages*/ 822155795475070977, "speaker", true),

/* Ancient Greek Channel */
(99, /*Studying Language*/ 885823354152570880, "speaker", true),

/* Pashto Channel */
(100, /*Native Farsi*/ 478178098437685248, "speaker", true),
(100, /*Fluent Farsi*/ 478178529368866826, "speaker", true),
(100, /*Studying Farsi*/ 563369533440655360, "speaker", true),

/* Faroese Channel */
(101, /*Native German*/ 471921967499444225, "speaker", true),
(101, /*Fluent Language*/ 490131150879195138, "speaker", true),
(101, /*Studying Language*/ 475241077578924053, "speaker", true),

/* Belarusian Channel */
(102, /*Native Belarusian*/ 476505043315458049, "speaker", true),
(102, /*Studying Belarusian*/ 476631439241117698, "speaker", true),

/* Turkmen Channel */
(103, /*Native Turkic Languages*/ 810441635418079233, "speaker", true),

/* Kyrgyz Channel */
(104, /*Native Turkic Languages*/ 810441635418079233, "speaker", true),

/* Uzbek Channel */
(105, /*Native Turkic Languages*/ 810441635418079233, "speaker", true),

/* Sami Channel */
(106, /*Native Indigenous Languages*/ 490171186198741012, "speaker", true),
(106, /*Studying Indigenous Languages*/ 821440812671041626, "speaker", true),

/* Quechua Channel */
(107, /*Native Indigenous Languages*/ 490171186198741012, "speaker", true),
(107, /*Studying Indigenous Languages*/ 821440812671041626, "speaker", true),

/* Guarani Channel */
(108, /*Native Indigenous Languages*/ 490171186198741012, "speaker", true),
(108, /*Studying Indigenous Languages*/ 821440812671041626, "speaker", true),

/* Greenlandic Channel */
(109, /*Native Indigenous Languages*/ 490171186198741012, "speaker", true),
(109, /*Studying Indigenous Languages*/ 821440812671041626, "speaker", true),

/* Nahuatl Channel */
(110, /*Native Indigenous Languages*/ 490171186198741012, "speaker", true),
(110, /*Studying Indigenous Languages*/ 821440812671041626, "speaker", true),

/* Yucatec Channel */
(111, /*Native Indigenous Languages*/ 490171186198741012, "speaker", true),
(111, /*Studying Indigenous Languages*/ 821440812671041626, "speaker", true),

/* Armenian Channel */
(112, /*Native Armenian*/ 481141297659248651, "speaker", true),
(112, /*Studying Armenian*/ 563373263355379723, "speaker", true),

/* Georgian Channel */
(113, /*Native Georgian*/ 486664331719737363, "speaker", true),
(113, /*Studying Georgian*/ 483848214122987541, "speaker", true),

/* Kelantanese Channel */
(114, /*Native Malay*/ 481139094001549338, "speaker", true),
(114, /*Studying Malay*/ 562043669440364555, "speaker", true),

/* Kelantanese Channel */
(115, /*Native Malay*/ 481139094001549338, "speaker", true),
(115, /*Studying Malay*/ 562043669440364555, "speaker", true),

/* Kedahan Malay Channel */
(116, /*Native Malay*/ 481139094001549338, "speaker", true),
(116, /*Studying Malay*/ 562043669440364555, "speaker", true),

/* Latin Channel */
(117, /*Studying Latin*/ 562043075229122563, "speaker", true),

/* Estonian Channel */
(118, /*Native Estonian*/ 898439786602299452, "speaker", true),
(118, /*Studying Estonian*/ 476764995460530188, "speaker", true),

/* Bahasa Batak Channel */
(119, /*Native Indonesian*/ 476379670334406686, "speaker", true),
(119, /*Fluent Indonesian*/ 562043546924744733, "speaker", true),
(119, /*Studying Indonesian*/ 562043546924744733, "speaker", true),

/* Celtic Channel */
(120, /*Native Celtic*/ 490155744184762378, "speaker", true),
(120, /*Studying Celtic*/ 650661949478273044, "speaker", true),

/* Gilaki Channel */
(121, /*Native Farsi*/ 478178098437685248, "speaker", true),
(121, /*Fluent Farsi*/ 478178529368866826, "speaker", true),
(121, /*Studying Farsi*/ 563369533440655360, "speaker", true),

/* Language Channel */
(00, /*Native Language*/ 0000000000000000000, "speaker", true),
(00, /*Fluent Language*/ 0000000000000000000, "speaker", true),
(00, /*Studying Language*/ 0000000000000000000, "speaker", true)

;
