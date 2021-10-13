DROP TABLE IF EXISTS `DynRoomUserVCstamp`;
CREATE TABLE DynRoomUserVCstamp (user_id bigint, user_vc_ts bigint);

DROP TABLE IF EXISTS `DynamicRoom`;
CREATE TABLE DynamicRoom (guild_id BIGINT, room_id BIGINT, vc_id BIGINT, room_ts BIGINT, is_perma_room BOOLEAN);

DROP TABLE IF EXISTS `LanguageRoom`;
CREATE TABLE LanguageRoom (category VARCHAR(32), room_id SERIAL, english_name VARCHAR(32), room_name BLOB, room_quant INT, room_capacity INT);
INSERT INTO LanguageRoom (category, english_name, room_name, room_quant, room_capacity) VALUES 
/* 01 */('germanic', 'Swedish', 'Svenska 🪑🇸🇪', 2, 10),
/* 02 */('germanic', 'Norwegian', 'Norsk ⛷🇳🇴', 2, 10),
/* 03 */('germanic', 'Danish', 'Dansk 🥔🇩🇰', 2, 10),
/* 04 */('germanic', 'Dutch', 'Nederlands 🚴🇧🇪🇳🇱', 2, 10),
/* 05 */('sub-saharan', 'Afrikaans', 'Afrikaans 🦁🇿🇦', 2, 10),
/* 06 */('uralic', 'Finnish', 'Suomi ❄🇫🇮', 2, 10),
/* 07 */('uralic', 'Hungarian', 'Magyar 🌶🇭🇺', 2, 10),
/* 08 */('romance', 'Catalan', 'català', 2, 10),
/* 09 */('romance', 'Romanian', 'Română 🧛🇷🇴', 2, 10),
/* 10 */('baltic', 'Latvian', 'Latviešu 🥔🇱🇹', 2, 10),
/* 11 */('slavic', 'Polish', 'Polski 🧅🇵🇱', 2, 10),
/* 12 */('slavic', 'Czech', 'česko 🇨🇿🇸🇰', 2, 10),
/* 13 */('slavic', 'Ukrainian', 'Українська 🥣🇺🇦', 2, 10),
/* 14 */('balkan', 'Macedonian', 'Македонски 🇲🇰', 2, 10),
/* 15 */('slavic', 'Bulgarian', 'Български 🌹🇧🇬', 2, 10),
/* 16 */('semitic', 'Hebrew', 'עִברִית 🕎🇮🇱', 2, 10),
/* 17 */('turkic', 'Kazakh', 'Қазақ 🐎🇰🇿', 2, 10),
/* 18 */('turkic', 'Azerbaijani', 'Azərbaycan 🔥🇦🇿', 2, 10),
/* 19 */('iranian', 'Kurdish', 'كوردی🥪', 2, 10),
/* 20 */('iranian', 'Iran', 'فارسی🐈🇮🇷', 2, 10),
/* 21 */('asian', 'Vietnamese', 'Tiếng Việt🛵🇻🇳', 2, 10),
/* 22 */('asian', 'Khmer', 'ខ្មែរ🇰🇭', 2, 10),
/* 23 */('asian', 'Thai', 'ภาษาไทย 🥘🇹🇭', 2, 10),
/* 24 */('asian', 'Mongolian', 'Монгол хэл 🇲🇳', 2, 10),
/* 25 */('asian', 'Cantonese', '粤语 🍚🇭🇰', 2, 10),
/* 26 */('asian', 'South Asian Languages', 'South Asian languages🧘🇮🇳🇵🇰🇳🇵', 2, 10),
/* 27 */('asian', 'Hindi', 'हिन्दी 🏏🇮🇳', 2, 10),
/* 28 */('unafiliated', 'Greek', 'Ελληνικά 🏛️🇬🇷', 2, 10),
/* 29 */('germanic', 'Luxembourgish', 'lëtzebuergesch 🇱🇺', 2, 10),

/* 30 */('asian', 'Tamil', ' தமிழ் (Tamil)', 2, 10),
/* 31 */('asian', 'Punjabi', ' پنجاب (Punjabi) ', 2, 10),
/* 32 */('asian', 'Gujarati', 'ગુજરાતી (Gujarati)', 2, 10),
/* 33 */('asian', 'Marathi', 'मराठी (Marathi)', 2, 10),
/* 34 */('asian', 'Sanskrit', 'संस्कृत (Sanskrit)', 2, 10),
/* 35 */('asian', 'Malayalam', 'മലയാളം (Malayalam)', 2, 10),
/* 36 */('asian', 'Telugu', 'తెలుగు (Telugu)', 2, 10),
/* 37 */('asian', 'Kannada', 'ಕನ್ನಡ (Kannada)', 2, 10),
/* 38 */('asian', 'Bengali', 'বাংলা (Bengali)', 2, 10),
/* 39 */('asian', 'Nepali', 'ལྷོ་མཚམས་མའི་ཁ (Nepali)', 2, 10),

/* 40 */('asian', 'Urdu', 'اردو Urdu 🇵🇰', 2, 10),

/* 41 */('germanic', 'Swiss German', 'Schwyzerdütsch (Swiss German)', 2, 10),

/* 42 */('romance', 'Basque', 'Euskara', 2, 10),
/* 43 */('romance', 'Galician', 'Galego', 2, 10),

/* 44 */('sub-saharan', 'Yoruba', 'عِدعِ يوْرُبا', 2, 10),
/* 45 */('sub-saharan', 'Hausa', 'هَوْسَ', 2, 10),

/* 46 */('sub-saharan', 'Igbo', 'Ṇ́dị́ Ìgbò', 2, 10),
/* 47 */('sub-saharan', 'Somali', 'صومالي', 2, 10),
/* 48 */('sub-saharan', 'Swahili', 'Kiswahili', 2, 10),
/* 49 */('sub-saharan', 'Twi', 'Akan kasa', 2, 10),
/* 50 */('sub-saharan', 'Tigrinya', 'ትግርኛ', 2, 10),
/* 51 */('sub-saharan', 'Lingala', 'Lingála', 2, 10),
/* 52 */('sub-saharan', 'Zulu', 'isiZulu', 2, 10),
/* 53 */('sub-saharan', 'Wolof', 'ولوفل', 2, 10),
/* 54 */('sub-saharan', 'Xhosa', 'isiXhosa', 2, 10),
/* 55 */('sub-saharan', 'Ndebele', 'Ndebele', 2, 10),
/* 56 */('sub-saharan', 'Shona', 'chiShona', 2, 10),
/* 57 */('sub-saharan', 'Oromo', 'Afaan Oromoo', 2, 10),

/* 58 */('sub-saharan', 'Amharic', 'አማርኛ', 2, 10),

/* 59 */('romance', 'Lombard', 'Lumbard', 2, 10),
/* 60 */('romance', 'Sicilian', 'Sicilianu ', 2, 10),
/* 61 */('romance', 'Neapolitan', 'Napulitan', 2, 10),
/* 62 */('romance', 'Salentino', 'Salentinu', 2, 10),
/* 63 */('romance', 'Venetian', 'Vèneto ', 2, 10),
/* 64 */('romance', 'Ligurian', 'Lìgure ', 2, 10),
/* 65 */('romance', 'Sardinian', 'Sard', 2, 10),
/* 66 */('romance', 'Romanesco', 'Romanesco', 2, 10),

/* 67 */('germanic', 'Icelandic', 'íslenska', 2, 10),

/* 68 */('slavic', 'Albanian', 'shqip 🇦🇱', 2, 10),

/* 69 */('slavic', 'Slovak', 'slovenský', 2, 10),

/* 70 */('balkan', 'Croatian', 'Hrvatski 🇭🇷', 2, 10),
/* 71 */('balkan', 'Montenegrin', 'Crnogorski 🇧🇦', 2, 10),
/* 72 */('balkan', 'Serbian', 'Srpski 🇷🇸', 2, 10),

/* 73 */('baltic', 'Lithuanian', 'Lietuvių', 2, 10),

/* 74 */('asian', 'Wenzhounese', '溫州話 ', 2, 10),
/* 75 */('asian', 'Taishanese', '台山話 ', 2, 10),
/* 76 */('asian', 'Sichuanese', '四川話 ', 2, 10),
/* 77 */('asian', 'Hakka', '客家話 ', 2, 10),
/* 78 */('asian', 'Hainanese', '海南話 ', 2, 10),

/* 79 */('asian', 'Taiwanese', '閩南語 ', 2, 10),
/* 80 */('asian', 'Teochew', 'Teochew', 2, 10),
/* 81 */('asian', 'Hockchew', 'Hockchew', 2, 10),

/* 82 */('asian', 'Bisaya', 'Bisaya', 2, 10),
/* 83 */('asian', 'Waray-waray', 'Waray-waray', 2, 10),
/* 84 */('asian', 'Kapampangan', 'Kapampangan', 2, 10),
/* 85 */('asian', 'Cebuano', 'Cebuano', 2, 10),
/* 86 */('asian', 'Ilocano', 'Ilocano', 2, 10),

/* 87 */('asian', 'Javanese', 'Bahasa Jawa', 2, 10),
/* 88 */('asian', 'Lao', 'ພາສາລາວ ', 2, 10),

/* 89 */('romance', 'portunhol', 'Portunhol 🧉🌎', 2, 10),

/* ?? */('category', 'english_name', 'room_name', 2, 10)

;

/* Remember to set category permissions to:
* -> muted - can connect but not speak
* -> everyone - can connect but not view
* -> show me everything - can view

* speaker -> pretend permission the means view_channel, connect and speak
*/
DROP TABLE IF EXISTS `LanguageRoomPermissions`;
CREATE TABLE LanguageRoomPermissions (id SERIAL, room_id BIGINT, role_id BIGINT, permission_name VARCHAR(32), permission_value BOOLEAN);
INSERT INTO LanguageRoomPermissions (room_id, role_id, permission_name, permission_value) VALUES 
/* Swedish channel */
(1, /*Native Swedish*/ 471922035107430400, 'speaker', true),
(1, /*Fluent Swedish*/ 490121747824377856, 'speaker', true),
(1, /*Studying Swedish*/ 475484739655041034, 'speaker', true),
(1, /*Native Norwegian*/ 475484050493014036, 'speaker', true),
(1, /*Native Danish*/ 475989214186438656, 'speaker', true),

/* Norwegian channel */
(2, /*Native Norwegian*/ 475484050493014036, 'speaker', true),
(2, /*Fluent Norwegian*/ 490122353339006987, 'speaker', true),
(2, /*Studying Norwegian*/ 476480917628649473, 'speaker', true),
(2, /*Native Swedish*/ 471922035107430400, 'speaker', true),
(2, /*Native Danish*/ 475989214186438656, 'speaker', true),

/* Danish channel */
(3, /*Native Danish*/ 475989214186438656, 'speaker', true),
(3, /*Fluent Danish*/ 490129625096388655, 'speaker', true),
(3, /*Studying Danish*/ 476477915362754560, 'speaker', true),
(3, /*Native Swedish*/ 471922035107430400, 'speaker', true),
(3, /*Native Norwegian*/ 475484050493014036, 'speaker', true),

/* Dutch channel */
(4, /*Native Dutch*/ 486147198837587981, 'speaker', true),
(4, /*Fluent Dutch*/ 483863965747642368, 'speaker', true),
(4, /*Studying Dutch*/ 471932893027893248, 'speaker', true),

/* Afrikaans channel */
(5, /*Native Afrikaans*/ 531854806525018112, 'speaker', true),
(5, /*Fluent Afrikaans*/ 531855093817933834, 'speaker', true),
(5, /*Studying Afrikaans*/ 531855141352112139, 'speaker', true),
(5, /*Native Luxembourgish*/ 475240440501633034, 'speaker', true),
(5, /*Studying Luxembourgish*/ 490132397078347800, 'speaker', true),

/* Finnish channel */
(6, /*Native Finnish*/ 476018604240928779, 'speaker', true),
(6, /*Fluent Finnish*/ 476741198149713935, 'speaker', true),
(6, /*Studying Finnish*/ 476741389112180737, 'speaker', true),

/* Hungarian channel */
(7, /*Native Hungarian*/ 476019880798453762, 'speaker', true),
(7, /*Studying Hungarian*/ 476764441707282456, 'speaker', true),

/* Catalan channel */
(8, /*Native Catalan*/ 484820153197002773, 'speaker', true),
(8, /*Fluent Catalan*/ 489345218852814848, 'speaker', true),
(8, /*Studying Catalan*/ 490144247559880729, 'speaker', true),
(8, /*Native Basque*/ 480754000275177483, 'speaker', true),
(8, /*Studying Basque*/ 563373255642185778, 'speaker', true),

/* Romanian channel */
(9, /*Native Romanian*/ 475240440891965471, 'speaker', true),
(9, /*Studying Romanian*/ 476506364831858690, 'speaker', true),

/* Latvian channel */
(10, /*Native Latvian*/ 476062242690039837, 'speaker', true),
(10, /*Studying Latvian*/ 476765630519836693, 'speaker', true),
(10, /*Native Lithuanian*/ 476032570979647508, 'speaker', true),
(10, /*Studying Lithuanian*/ 475290035470467072, 'speaker', true),

/* Polish channel */
(11, /*Native Polish*/ 475254841044631562, 'speaker', true),
(11, /*Fluent Polish*/ 476503475954647071, 'speaker', true),
(11, /*Studying Polish*/ 476630931252314153, 'speaker', true),

/* Czech channel */
(12, /*Native Czech-Slovak*/ 476019943003914251, 'speaker', true),
(12, /*Fluent Czech-Slovak*/ 471926693368692738, 'speaker', true),
(12, /*Studying Czech-Slovak*/ 471931483876229131, 'speaker', true),

/* Ukrainian channel */
(13, /*Native Ukrainian*/ 475240441277579274, 'speaker', true),
(13, /*Fluent Ukrainian*/ 476505951235735567, 'speaker', true),
(13, /*Studying Ukrainian*/ 475294137109708801, 'speaker', true),

/* Balkanski channel */
(14, /*Native Balkan Languages*/ 476020149846278154, 'speaker', true),
(14, /*Native Macedonian*/ 476505421457391626, 'speaker', true),
(14, /*Fluent Balkan Languages*/ 476645488574070785, 'speaker', true),
(14, /*Fluent Macedonian*/ 476506585867223040, 'speaker', true),
(14, /*Studying Balkan Languages*/ 476630854706397186, 'speaker', true),
(14, /*Studying Macedonian*/ 476631603872006144, 'speaker', true),

/* Bulgarian channel */
(15, /*Native Bulgarian*/ 475240441084903445, 'speaker', true),
(15, /*Native Albanian*/ 475240441084903445, 'speaker', true),
(15, /*Fluent Bulgarian*/ 476506070039134259, 'speaker', true),
(15, /*Studying Bulgarian*/ 476763017204203560, 'speaker', true),
(15, /*Studying Albanian*/ 489739368471199745, 'speaker', true),

/* Hebrew channel */
(16, /*Native Hebrew*/ 474894084704698370, 'speaker', true),
(16, /*Fluent Hebrew*/ 476639355146993664, 'speaker', true),
(16, /*Studying Hebrew*/ 562053868356370434, 'speaker', true),

/* Kazakh channel */
(17, /*Native Kazakh*/ 480431310007959572, 'speaker', true),
(17, /*Native Turkic Languages*/ 810441635418079233, 'speaker', true),
(17, /*Studying Kazakh*/ 823204473908363324, 'speaker', true),

/* Azerbaijani channel */
(18, /*Native Azerbaijani*/ 479441520257138698, 'speaker', true),
(18, /*Native Turkic Languages*/ 810441635418079233, 'speaker', true),
(18, /*Studying Azerbaijani*/ 764665103701639179, 'speaker', true),

/* Kurdish channel */
(19, /*Native Kurdish*/ 478181311971065867, 'speaker', true),

/* Iran channel */
(20, /*Native Iran*/ 478178098437685248, 'speaker', true),
(20, /*Fluent Iran*/ 478178529368866826, 'speaker', true),
(20, /*Studying Iran*/ 563369533440655360, 'speaker', true),

/* Vietnamese channel */
(21, /*Native Vietnamese*/ 475240442779140116, 'speaker', true),
(21, /*Fluent Vietnamese*/ 476746087856603166, 'speaker', true),
(21, /*Studying Vietnamese*/ 563361451222237194, 'speaker', true),

/* Khmer channel */
(22, /*Native Khmer*/ 823204525891911690, 'speaker', true),
(22, /*Studying Khmer*/ 823203829876654131, 'speaker', true),

/* Thai channel */
(23, /*Native Thai*/ 478973636389109784, 'speaker', true),
(23, /*Fluent Thai*/ 476745694770626560, 'speaker', true),
(23, /*Studying Thai*/ 563359993005473808, 'speaker', true),

/* Mongolian channel */
(24, /*Native Mongolian*/ 471925922791030785, 'speaker', true),
(24, /*Studying Mongolian*/ 563366459217149957, 'speaker', true),

/* Cantonese channel */
(25, /*Native Cantonese*/ 491571804566192129, 'speaker', true),
(25, /*Fluent Cantonese*/ 562546146304720897, 'speaker', true),
(25, /*Studying Cantonese*/ 562053222961774612, 'speaker', true),

/* South Asian Languages channel */
(26, /*Native South Asian Languages*/ 531855188873445387, 'speaker', true),
(26, /*Fluent South Asian Languages*/ 531855277012549642, 'speaker', true),
(26, /*Studying South Asian Languages*/ 563064564518879279, 'speaker', true),

/* Hindi channel */
(27, /*Native Hindi-Urdu*/ 823204505242959882, 'speaker', true),
(27, /*Fluent Hindi-Urdu*/ 823470151059505172, 'speaker', true),
(27, /*Studying Hindi-Urdu*/ 823469852924575794, 'speaker', true),

/* Greek channel */
(28, /*Native Greek*/ 478235006121017355, 'speaker', true),
(28, /*Fluent Greek*/ 490174425363251210, 'speaker', true),
(28, /*Studying Greek*/ 562034165789491231, 'speaker', true),

/* Luxembourgish channel */
(29, /*Native Luxembourgish*/ 475240440501633034, 'speaker', true),
(29, /*Studying Luxembourgish*/ 490132397078347800, 'speaker', true),

(30, /*Native South Asian Languages*/ 531855188873445387, 'speaker', true),
(30, /*Fluent South Asian Languages*/ 531855277012549642, 'speaker', true),
(30, /*Studying South Asian Languages*/ 563064564518879279, 'speaker', true),

(31, /*Native South Asian Languages*/ 531855188873445387, 'speaker', true),
(31, /*Fluent South Asian Languages*/ 531855277012549642, 'speaker', true),
(31, /*Studying South Asian Languages*/ 563064564518879279, 'speaker', true),

(32, /*Native South Asian Languages*/ 531855188873445387, 'speaker', true),
(32, /*Fluent South Asian Languages*/ 531855277012549642, 'speaker', true),
(32, /*Studying South Asian Languages*/ 563064564518879279, 'speaker', true),

(33, /*Native South Asian Languages*/ 531855188873445387, 'speaker', true),
(33, /*Fluent South Asian Languages*/ 531855277012549642, 'speaker', true),
(33, /*Studying South Asian Languages*/ 563064564518879279, 'speaker', true),

(34, /*Native South Asian Languages*/ 531855188873445387, 'speaker', true),
(34, /*Fluent South Asian Languages*/ 531855277012549642, 'speaker', true),
(34, /*Studying South Asian Languages*/ 563064564518879279, 'speaker', true),

(35, /*Native South Asian Languages*/ 531855188873445387, 'speaker', true),
(35, /*Fluent South Asian Languages*/ 531855277012549642, 'speaker', true),
(35, /*Studying South Asian Languages*/ 563064564518879279, 'speaker', true),

(36, /*Native South Asian Languages*/ 531855188873445387, 'speaker', true),
(36, /*Fluent South Asian Languages*/ 531855277012549642, 'speaker', true),
(36, /*Studying South Asian Languages*/ 563064564518879279, 'speaker', true),

(37, /*Native South Asian Languages*/ 531855188873445387, 'speaker', true),
(37, /*Fluent South Asian Languages*/ 531855277012549642, 'speaker', true),
(37, /*Studying South Asian Languages*/ 563064564518879279, 'speaker', true),

(38, /*Native South Asian Languages*/ 531855188873445387, 'speaker', true),
(38, /*Fluent South Asian Languages*/ 531855277012549642, 'speaker', true),
(38, /*Studying South Asian Languages*/ 563064564518879279, 'speaker', true),

(39, /*Native South Asian Languages*/ 531855188873445387, 'speaker', true),
(39, /*Fluent South Asian Languages*/ 531855277012549642, 'speaker', true),
(39, /*Studying South Asian Languages*/ 563064564518879279, 'speaker', true),

/* Urdu Channel */
(40, /*Native Hindi-Urdu*/ 823204505242959882, 'speaker', true),
(40, /*Fluent Hindi-Urdu*/ 823470151059505172, 'speaker', true),
(40, /*Studying Hindi-Urdu*/ 823469852924575794, 'speaker', true),

/* Swiss German Channel */
(41, /*Native German*/ 471921967499444225, 'speaker', true),
(41, /*Fluent Language*/ 490131150879195138, 'speaker', true),
(41, /*Studying Language*/ 475241077578924053, 'speaker', true),

/* Basque Channel */
(42, /*Native Basque*/ 480754000275177483, 'speaker', true),
(42, /*Studying Basque*/ 563373255642185778, 'speaker', true),

/* Galician Channel */
(43, /*Native Spanish*/ 474726084638670848, 'speaker', true),
(43, /*Fluent Spanish*/ 474720724125351937, 'speaker', true),
(43, /*Studying Spanish*/ 474745895796342784, 'speaker', true),

/* Yoruba Channel */
(44, /*Native Sub-Saharan*/ 777305645636124675, 'speaker', true),
(44, /*Studying Sub-Saharan*/ 590491309278494720, 'speaker', true),

/* Hausa Channel */
(45, /*Native Sub-Saharan*/ 777305645636124675, 'speaker', true),
(45, /*Studying Sub-Saharan*/ 590491309278494720, 'speaker', true),

/* Igbo Channel */
(46, /*Native Sub-Saharan*/ 777305645636124675, 'speaker', true),
(46, /*Studying Sub-Saharan*/ 590491309278494720, 'speaker', true),

/* Somali Channel */
(47, /*Native Sub-Saharan*/ 777305645636124675, 'speaker', true),
(47, /*Studying Sub-Saharan*/ 590491309278494720, 'speaker', true),

/* Swahili Channel */
(48, /*Native Sub-Saharan*/ 777305645636124675, 'speaker', true),
(48, /*Studying Sub-Saharan*/ 590491309278494720, 'speaker', true),

/* Twi Channel */
(49, /*Native Sub-Saharan*/ 777305645636124675, 'speaker', true),
(49, /*Studying Sub-Saharan*/ 590491309278494720, 'speaker', true),

/* Tigrinya Channel */
(50, /*Native Sub-Saharan*/ 777305645636124675, 'speaker', true),
(50, /*Studying Sub-Saharan*/ 590491309278494720, 'speaker', true),

/* Lingala Channel */
(51, /*Native Sub-Saharan*/ 777305645636124675, 'speaker', true),
(51, /*Studying Sub-Saharan*/ 590491309278494720, 'speaker', true),

/* Zulu Channel */
(52, /*Native Sub-Saharan*/ 777305645636124675, 'speaker', true),
(52, /*Studying Sub-Saharan*/ 590491309278494720, 'speaker', true),

/* Wolof Channel */
(53, /*Native Sub-Saharan*/ 777305645636124675, 'speaker', true),
(53, /*Studying Sub-Saharan*/ 590491309278494720, 'speaker', true),

/* Xhosa Channel */
(54, /*Native Sub-Saharan*/ 777305645636124675, 'speaker', true),
(54, /*Studying Sub-Saharan*/ 590491309278494720, 'speaker', true),

/* Ndebele Channel */
(55, /*Native Sub-Saharan*/ 777305645636124675, 'speaker', true),
(55, /*Studying Sub-Saharan*/ 590491309278494720, 'speaker', true),

/* Shona Channel */
(56, /*Native Sub-Saharan*/ 777305645636124675, 'speaker', true),
(56, /*Studying Sub-Saharan*/ 590491309278494720, 'speaker', true),

/* Oromo Channel */
(57, /*Native Sub-Saharan*/ 777305645636124675, 'speaker', true),
(57, /*Studying Sub-Saharan*/ 590491309278494720, 'speaker', true),

/* Amharic Channel */
(58, /*Native Sub-Saharan*/ 777305645636124675, 'speaker', true),
(58, /*Studying Sub-Saharan*/ 590491309278494720, 'speaker', true),

/* Lombard Channel */
(59, /*Native Italian*/ 474876492585893908, 'speaker', true),
(59, /*Fluent Italian*/ 474720800071614489, 'speaker', true),
(59, /*Studying Italian*/ 475236110315028490, 'speaker', true),

/* Sicilian Channel */
(60, /*Native Italian*/ 474876492585893908, 'speaker', true),
(60, /*Fluent Italian*/ 474720800071614489, 'speaker', true),
(60, /*Studying Italian*/ 475236110315028490, 'speaker', true),

/* Neapolitan Channel */
(61, /*Native Italian*/ 474876492585893908, 'speaker', true),
(61, /*Fluent Italian*/ 474720800071614489, 'speaker', true),
(61, /*Studying Italian*/ 475236110315028490, 'speaker', true),

/* Salentino Channel */
(62, /*Native Italian*/ 474876492585893908, 'speaker', true),
(62, /*Fluent Italian*/ 474720800071614489, 'speaker', true),
(62, /*Studying Italian*/ 475236110315028490, 'speaker', true),

/* Venetian Channel */
(63, /*Native Italian*/ 474876492585893908, 'speaker', true),
(63, /*Fluent Italian*/ 474720800071614489, 'speaker', true),
(63, /*Studying Italian*/ 475236110315028490, 'speaker', true),

/* Ligurian Channel */
(64, /*Native Italian*/ 474876492585893908, 'speaker', true),
(64, /*Fluent Italian*/ 474720800071614489, 'speaker', true),
(64, /*Studying Italian*/ 475236110315028490, 'speaker', true),

/* Sardinian Channel */
(65, /*Native Italian*/ 474876492585893908, 'speaker', true),
(65, /*Fluent Italian*/ 474720800071614489, 'speaker', true),
(65, /*Studying Italian*/ 475236110315028490, 'speaker', true),

/* Romanesco Channel */
(66, /*Native Italian*/ 474876492585893908, 'speaker', true),
(66, /*Fluent Italian*/ 474720800071614489, 'speaker', true),
(66, /*Studying Italian*/ 475236110315028490, 'speaker', true),

/* Icelandic Channel */
(67, /*Native Icelandic*/ 477438984432386048, 'speaker', true),
(67, /*Fluent Icelandic*/ 490123385376997376, 'speaker', true),
(67, /*Studying Icelandic*/ 477439167257772045, 'speaker', true),

/* Albanian Channel */
(68, /*Native Albanian*/ 475240441084903445, 'speaker', true),
(68, /*Studying Albanian*/ 489739368471199745, 'speaker', true),
(68, /*Native Bulgarian*/ 475240441084903445, 'speaker', true),
(68, /*Fluent Bulgarian*/ 476506070039134259, 'speaker', true),
(68, /*Studying Bulgarian*/ 476763017204203560, 'speaker', true),

/* Slovak Channel */
(69, /*Native Czech-Slovak*/ 476019943003914251, 'speaker', true),
(69, /*Fluent Czech-Slovak*/ 471926693368692738, 'speaker', true),
(69, /*Studying Czech-Slovak*/ 471931483876229131, 'speaker', true),

/* Croatian Channel */
(70, /*Native Balkan Languages*/ 476020149846278154, 'speaker', true),
(70, /*Native Macedonian*/ 476505421457391626, 'speaker', true),
(70, /*Fluent Balkan Languages*/ 476645488574070785, 'speaker', true),
(70, /*Fluent Macedonian*/ 476506585867223040, 'speaker', true),
(70, /*Studying Balkan Languages*/ 476630854706397186, 'speaker', true),
(70, /*Studying Macedonian*/ 476631603872006144, 'speaker', true),

/* Montenegrin Channel */
(71, /*Native Balkan Languages*/ 476020149846278154, 'speaker', true),
(71, /*Native Macedonian*/ 476505421457391626, 'speaker', true),
(71, /*Fluent Balkan Languages*/ 476645488574070785, 'speaker', true),
(71, /*Fluent Macedonian*/ 476506585867223040, 'speaker', true),
(71, /*Studying Balkan Languages*/ 476630854706397186, 'speaker', true),
(71, /*Studying Macedonian*/ 476631603872006144, 'speaker', true),

/* Serbian Channel */
(72, /*Native Balkan Languages*/ 476020149846278154, 'speaker', true),
(72, /*Native Macedonian*/ 476505421457391626, 'speaker', true),
(72, /*Fluent Balkan Languages*/ 476645488574070785, 'speaker', true),
(72, /*Fluent Macedonian*/ 476506585867223040, 'speaker', true),
(72, /*Studying Balkan Languages*/ 476630854706397186, 'speaker', true),
(72, /*Studying Macedonian*/ 476631603872006144, 'speaker', true),

/* Lithuanian channel */
(73, /*Native Latvian*/ 476062242690039837, 'speaker', true),
(73, /*Studying Latvian*/ 476765630519836693, 'speaker', true),
(73, /*Native Lithuanian*/ 476032570979647508, 'speaker', true),
(73, /*Studying Lithuanian*/ 475290035470467072, 'speaker', true),

/* Wenzhounese Channel */
(74, /*Native Cantonese*/ 491571804566192129, 'speaker', true),
(74, /*Fluent Cantonese*/ 562546146304720897, 'speaker', true),
(74, /*Studying Cantonese*/ 562053222961774612, 'speaker', true),
(74, /*Native Mandarin*/ 475240442540326923, 'speaker', true),
(74, /*Fluent Mandarin*/ 476745894738264066, 'speaker', true),
(74, /*Studying Mandarin*/ 562053107027148820, 'speaker', true),

/* Taishanese Channel */
(75, /*Native Cantonese*/ 491571804566192129, 'speaker', true),
(75, /*Fluent Cantonese*/ 562546146304720897, 'speaker', true),
(75, /*Studying Cantonese*/ 562053222961774612, 'speaker', true),
(75, /*Native Mandarin*/ 475240442540326923, 'speaker', true),
(75, /*Fluent Mandarin*/ 476745894738264066, 'speaker', true),
(75, /*Studying Mandarin*/ 562053107027148820, 'speaker', true),

/* Sichuanese Channel */
(76, /*Native Cantonese*/ 491571804566192129, 'speaker', true),
(76, /*Fluent Cantonese*/ 562546146304720897, 'speaker', true),
(76, /*Studying Cantonese*/ 562053222961774612, 'speaker', true),
(76, /*Native Mandarin*/ 475240442540326923, 'speaker', true),
(76, /*Fluent Mandarin*/ 476745894738264066, 'speaker', true),
(76, /*Studying Mandarin*/ 562053107027148820, 'speaker', true),

/* Hakka Channel */
(77, /*Native Cantonese*/ 491571804566192129, 'speaker', true),
(77, /*Fluent Cantonese*/ 562546146304720897, 'speaker', true),
(77, /*Studying Cantonese*/ 562053222961774612, 'speaker', true),
(77, /*Native Mandarin*/ 475240442540326923, 'speaker', true),
(77, /*Fluent Mandarin*/ 476745894738264066, 'speaker', true),
(77, /*Studying Mandarin*/ 562053107027148820, 'speaker', true),

/* Hainanese Channel */
(78, /*Native Cantonese*/ 491571804566192129, 'speaker', true),
(78, /*Fluent Cantonese*/ 562546146304720897, 'speaker', true),
(78, /*Studying Cantonese*/ 562053222961774612, 'speaker', true),
(78, /*Native Mandarin*/ 475240442540326923, 'speaker', true),
(78, /*Fluent Mandarin*/ 476745894738264066, 'speaker', true),
(78, /*Studying Mandarin*/ 562053107027148820, 'speaker', true),

/* Taiwanese Channel */
(79, /*Native Cantonese*/ 491571804566192129, 'speaker', true),
(79, /*Fluent Cantonese*/ 562546146304720897, 'speaker', true),
(79, /*Studying Cantonese*/ 562053222961774612, 'speaker', true),
(79, /*Native Mandarin*/ 475240442540326923, 'speaker', true),
(79, /*Fluent Mandarin*/ 476745894738264066, 'speaker', true),
(79, /*Studying Mandarin*/ 562053107027148820, 'speaker', true),

/* Teochew Channel */
(80, /*Native Cantonese*/ 491571804566192129, 'speaker', true),
(80, /*Fluent Cantonese*/ 562546146304720897, 'speaker', true),
(80, /*Studying Cantonese*/ 562053222961774612, 'speaker', true),
(80, /*Native Mandarin*/ 475240442540326923, 'speaker', true),
(80, /*Fluent Mandarin*/ 476745894738264066, 'speaker', true),
(80, /*Studying Mandarin*/ 562053107027148820, 'speaker', true),

/* Hockchew Channel */
(81, /*Native Cantonese*/ 491571804566192129, 'speaker', true),
(81, /*Fluent Cantonese*/ 562546146304720897, 'speaker', true),
(81, /*Studying Cantonese*/ 562053222961774612, 'speaker', true),
(81, /*Native Mandarin*/ 475240442540326923, 'speaker', true),
(81, /*Fluent Mandarin*/ 476745894738264066, 'speaker', true),
(81, /*Studying Mandarin*/ 562053107027148820, 'speaker', true),

/* Bisaya Channel */
(82, /*Native Filipino*/ 477148625206640670, 'speaker', true),
(82, /*Fluent Filipino*/ 477148892773875722, 'speaker', true),
(82, /*Studying Filipino*/ 563360656032792587, 'speaker', true),

/* Waray-waray Channel */
(83, /*Native Filipino*/ 477148625206640670, 'speaker', true),
(83, /*Fluent Filipino*/ 477148892773875722, 'speaker', true),
(83, /*Studying Filipino*/ 563360656032792587, 'speaker', true),

/* Kapampangan Channel */
(84, /*Native Filipino*/ 477148625206640670, 'speaker', true),
(84, /*Fluent Filipino*/ 477148892773875722, 'speaker', true),
(84, /*Studying Filipino*/ 563360656032792587, 'speaker', true),

/* Cebuano Channel */
(85, /*Native Filipino*/ 477148625206640670, 'speaker', true),
(85, /*Fluent Filipino*/ 477148892773875722, 'speaker', true),
(85, /*Studying Filipino*/ 563360656032792587, 'speaker', true),

/* Ilocano Channel */
(86, /*Native Filipino*/ 477148625206640670, 'speaker', true),
(86, /*Fluent Filipino*/ 477148892773875722, 'speaker', true),
(86, /*Studying Filipino*/ 563360656032792587, 'speaker', true),

/* Javanese Channel */
(87, /*Native Indonesian*/ 476379670334406686, 'speaker', true),
(87, /*Fluent Indonesian*/ 562043546924744733, 'speaker', true),
(87, /*Studying Indonesian*/ 562043546924744733, 'speaker', true),

/* Lao Channel */
(88, /*Native Thai*/ 478973636389109784, 'speaker', true),
(88, /*Fluent Thai*/ 476745694770626560, 'speaker', true),
(88, /*Studying Thai*/ 563359993005473808, 'speaker', true),

/* Portunhol Channel */
(89, /*Native Portuguese*/ 471922090908581890, 'speaker', true),
(89, /*Fluent Portuguese*/ 474720855084105748, 'speaker', true),
(89, /*Studying Portuguese*/ 474722401436041216, 'speaker', true),
(89, /*Native Spanish*/ 474726084638670848, 'speaker', true),
(89, /*Fluent Spanish*/ 474720724125351937, 'speaker', true),
(89, /*Studying Spanish*/ 474745895796342784, 'speaker', true),

/* Language Channel */
(00, /*Native Language*/ 0000000000000000000, 'speaker', true),
(00, /*Fluent Language*/ 0000000000000000000, 'speaker', true),
(00, /*Studying Language*/ 0000000000000000000, 'speaker', true)

;
