/**
 * Hindi for text that comes from the backend rather than from en.ts/hi.ts:
 * model labels (disease names), the offline advisory knowledge base
 * (src/zone1_edge/knowledge/*.json), gate reasons and Indian state names.
 * Anything not listed here (e.g. free-form cloud LLM text) is shown as sent.
 */

/** Whole-label names, keyed by normalised label (lowercase letters/digits only). */
export const CONDITION_HI: Record<string, string> = {
  tomatoearlyblight: "टमाटर का अगेती झुलसा",
  tomatolateblight: "टमाटर का पछेती झुलसा",
  potatoearlyblight: "आलू का अगेती झुलसा",
  potatolateblight: "आलू का पछेती झुलसा",
  maizecommonrust: "मक्के का सामान्य रतुआ",
  corncommonrust: "मक्के का सामान्य रतुआ",
  cornmaizecommonrust: "मक्के का सामान्य रतुआ",
  maizehealthy: "स्वस्थ मक्का",
  cornhealthy: "स्वस्थ मक्का",
  cornmaizehealthy: "स्वस्थ मक्का",
  tomatohealthy: "स्वस्थ टमाटर",
  potatohealthy: "स्वस्थ आलू",
  pepperbacterialspot: "शिमला मिर्च का जीवाणु धब्बा",
  pepperbellbacterialspot: "शिमला मिर्च का जीवाणु धब्बा",
  pepperbellhealthy: "स्वस्थ शिमला मिर्च",
  lumpyskindisease: "लम्पी त्वचा रोग",
  footandmouthdisease: "खुरपका-मुंहपका रोग",
  mastitissuspected: "थनैला रोग (संभावित)",
  mastitis: "थनैला रोग",
  abnormaltemperature: "असामान्य तापमान",
  healthy: "स्वस्थ",
  healthycrop: "स्वस्थ फ़सल",
  crophealthy: "स्वस्थ फ़सल",
  wheatrust: "गेहूँ का रतुआ",
  wheatbrownrust: "गेहूँ का भूरा रतुआ",
  wheatyellowrust: "गेहूँ का पीला रतुआ",
  wheathealthy: "स्वस्थ गेहूँ",
  riceblast: "धान का झोंका रोग",
  riceleafblast: "धान का पत्ती झोंका रोग",
  ricebrownspot: "धान का भूरा धब्बा",
  ricehealthy: "स्वस्थ धान",
  cottonbollworm: "कपास की सुंडी",
  poultryavianinfluenza: "मुर्गियों में बर्ड फ़्लू",
  poultrynewcastledisease: "मुर्गियों में रानीखेत रोग",
  goatpestedespetitsruminants: "बकरियों में पीपीआर रोग",
  soybeanrust: "सोयाबीन का रतुआ",
  soybeanhealthy: "स्वस्थ सोयाबीन",
  citruscanker: "नींबू वर्गीय कैंकर",
  mangoanthracnose: "आम का एन्थ्रेक्नोज़",
  cropnitrogendeficiency: "फ़सल में नाइट्रोजन की कमी",
  cropphosphorusdeficiency: "फ़सल में फ़ॉस्फ़ोरस की कमी",
  livestockheatstress: "पशुओं में गर्मी का तनाव",
  livestockketosis: "पशुओं में कीटोसिस",
  bananabunchytop: "केले का गुच्छा शीर्ष रोग",
  corngrayleafspot: "मक्के का धूसर पत्ती धब्बा",
  cornmaizecercosporaleafspotgrayleafspot: "मक्के का धूसर पत्ती धब्बा",
  cornmaizenorthernleafblight: "मक्के का उत्तरी पत्ती झुलसा",
  squashpowderymildew: "कद्दू का चूर्णी फफूंद",
  tomatobacterialspot: "टमाटर का जीवाणु धब्बा",
  tomatoleafmold: "टमाटर की पत्ती फफूंद",
  tomatoseptorialeafspot: "टमाटर का सेप्टोरिया पत्ती धब्बा",
  tomatospidermitestwospottedspidermite: "टमाटर पर मकड़ी घुन",
  tomatotargetspot: "टमाटर का लक्ष्य धब्बा",
  tomatotomatoyellowleafcurlvirus: "टमाटर का पीला पत्ती मोड़क वायरस",
  tomatotomatomosaicvirus: "टमाटर का मोज़ेक वायरस",
  appleapplescab: "सेब की पपड़ी",
  appleblackrot: "सेब का काला सड़न",
  applecedarapplerust: "सेब का रतुआ",
  applehealthy: "स्वस्थ सेब",
  blueberryhealthy: "स्वस्थ ब्लूबेरी",
  cherryincludingsourpowderymildew: "चेरी का चूर्णी फफूंद",
  cherryincludingsourhealthy: "स्वस्थ चेरी",
  grapeblackrot: "अंगूर का काला सड़न",
  grapeescablackmeasles: "अंगूर का एस्का रोग",
  grapeleafblightisariopsisleafspot: "अंगूर का पत्ती झुलसा",
  grapehealthy: "स्वस्थ अंगूर",
  orangehaunglongbingcitrusgreening: "संतरे का ग्रीनिंग रोग",
  peachbacterialspot: "आड़ू का जीवाणु धब्बा",
  peachhealthy: "स्वस्थ आड़ू",
  raspberryhealthy: "स्वस्थ रास्पबेरी",
  strawberryleafscorch: "स्ट्रॉबेरी की पत्ती झुलसन",
  strawberryhealthy: "स्वस्थ स्ट्रॉबेरी",
  invalid: "अमान्य फ़ोटो",
  mockdisease: "डेमो रोग (नमूना)",
  unknown: "अज्ञात",
};

/** Word-level fallback for labels not in CONDITION_HI (e.g. new model classes). */
const WORD_HI: Record<string, string> = {
  tomato: "टमाटर", potato: "आलू", maize: "मक्का", corn: "मक्का", wheat: "गेहूँ", rice: "धान", cotton: "कपास",
  pepper: "मिर्च", soybean: "सोयाबीन", mango: "आम", banana: "केला", citrus: "नींबू", apple: "सेब", grape: "अंगूर",
  cattle: "मवेशी", goat: "बकरी", poultry: "मुर्गी", livestock: "पशुधन", crop: "फ़सल",
  early: "अगेती", late: "पछेती", blight: "झुलसा", rust: "रतुआ", spot: "धब्बा", leaf: "पत्ती", mold: "फफूंद",
  mildew: "फफूंद", rot: "सड़न", virus: "वायरस", bacterial: "जीवाणु", healthy: "स्वस्थ", disease: "रोग",
  deficiency: "कमी", blast: "झोंका", brown: "भूरा", yellow: "पीला", black: "काला",
};

export const norm = (s: string) => s.toLowerCase().replace(/[^a-z0-9]+/g, "");

export function conditionHi(label: string): string | null {
  const exact = CONDITION_HI[norm(label)];
  if (exact) return exact;
  const words = label.toLowerCase().split(/[^a-z]+/).filter(Boolean);
  if (!words.length || !words.every((w) => WORD_HI[w])) return null;
  return words.map((w) => WORD_HI[w]).join(" ");
}

/** Exact English sentences from the offline knowledge base, gate and quality checks. */
export const SENTENCE_HI: Record<string, string> = {
  // --- local_advisories.json: descriptions
  "Fungal disease causing concentric brown spots on lower leaves, spreading upward.": "फफूंद रोग जिसमें निचली पत्तियों पर गोल छल्लेदार भूरे धब्बे बनते हैं, जो ऊपर की ओर फैलते हैं।",
  "Aggressive fungal-like disease (Phytophthora) causing dark, water-soaked lesions that spread rapidly in humid weather.": "तेज़ी से फैलने वाला फफूंद जैसा रोग (फाइटोफ्थोरा), जिसमें गहरे, पानी से भीगे जैसे धब्बे बनते हैं और नम मौसम में तेज़ी से फैलते हैं।",
  "Fungal disease showing target-like brown spots on older potato leaves.": "फफूंद रोग जिसमें आलू की पुरानी पत्तियों पर निशाने जैसे भूरे धब्बे दिखते हैं।",
  "Fast-spreading disease causing dark lesions on leaves and stems, especially in cool, wet weather.": "तेज़ी से फैलने वाला रोग जिसमें पत्तियों और तनों पर गहरे धब्बे बनते हैं, खासकर ठंडे और गीले मौसम में।",
  "Fungal disease producing reddish-brown pustules on maize leaves.": "फफूंद रोग जिसमें मक्के की पत्तियों पर लाल-भूरे फफोले बनते हैं।",
  "No disease symptoms detected on this maize sample.": "इस मक्के के नमूने पर रोग का कोई लक्षण नहीं मिला।",
  "No disease symptoms detected on this tomato sample.": "इस टमाटर के नमूने पर रोग का कोई लक्षण नहीं मिला।",
  "Bacterial disease causing small, dark, raised spots on pepper leaves and fruit.": "जीवाणु रोग जिसमें मिर्च की पत्तियों और फलों पर छोटे, गहरे, उभरे धब्बे बनते हैं।",
  "Viral disease in cattle causing firm skin nodules, fever, and reduced milk yield, spread by biting insects.": "मवेशियों का वायरल रोग जिसमें त्वचा पर सख़्त गांठें, बुखार और दूध में कमी होती है; काटने वाले कीड़ों से फैलता है।",
  "Highly contagious viral disease causing fever, blisters on mouth/feet, and limping in cattle.": "अत्यधिक संक्रामक वायरल रोग जिसमें मवेशियों को बुखार, मुँह/खुरों पर छाले और लंगड़ापन होता है।",
  "Suspected udder inflammation, often from bacterial infection, reducing milk quality/yield.": "थन में सूजन की आशंका, अक्सर जीवाणु संक्रमण से, जिससे दूध की गुणवत्ता/मात्रा घटती है।",
  "Sensor detected temperature outside the normal range for cattle, combined with behavioural signs.": "सेंसर ने मवेशी का तापमान सामान्य सीमा से बाहर पाया, साथ में व्यवहार में बदलाव के संकेत भी हैं।",
  "No disease symptoms detected on this livestock sample.": "इस पशु के नमूने पर रोग का कोई लक्षण नहीं मिला।",
  "Fungal disease causing orange/brown pustules on wheat leaves.": "फफूंद रोग जिसमें गेहूँ की पत्तियों पर नारंगी/भूरे फफोले बनते हैं।",
  "Devastating fungal disease causing diamond-shaped lesions on rice leaves.": "विनाशकारी फफूंद रोग जिसमें धान की पत्तियों पर हीरे के आकार के धब्बे बनते हैं।",
  "Pest larvae that feed on cotton bolls, destroying the fiber.": "कीट की सुंडियाँ जो कपास के टिंडे खाकर रेशा नष्ट करती हैं।",
  "Highly contagious viral disease in poultry causing sudden death and respiratory distress.": "मुर्गियों का अत्यधिक संक्रामक वायरल रोग जिससे अचानक मौत और साँस की तकलीफ़ होती है।",
  "Viral disease in birds causing twisting of the neck, paralysis, and drop in egg production.": "पक्षियों का वायरल रोग जिसमें गर्दन मुड़ना, लकवा और अंडा उत्पादन में गिरावट होती है।",
  "Severe viral disease (PPR) of sheep and goats causing fever, sores in the mouth, and diarrhea.": "भेड़-बकरियों का गंभीर वायरल रोग (पीपीआर) जिसमें बुखार, मुँह में घाव और दस्त होते हैं।",
  "Aggressive fungal disease causing premature defoliation in soybean.": "तेज़ फफूंद रोग जिससे सोयाबीन की पत्तियाँ समय से पहले झड़ जाती हैं।",
  "Bacterial disease causing raised corky lesions on citrus leaves, stems, and fruit.": "जीवाणु रोग जिसमें नींबू वर्गीय पौधों की पत्तियों, तनों और फलों पर उभरे खुरदरे धब्बे बनते हैं।",
  "Fungal disease causing dark irregular spots on leaves, blossoms, and fruits of mango.": "फफूंद रोग जिसमें आम की पत्तियों, बौर और फलों पर गहरे अनियमित धब्बे बनते हैं।",
  "Nutrient deficiency causing overall yellowing of older leaves and stunted growth.": "पोषक तत्व की कमी जिसमें पुरानी पत्तियाँ पूरी तरह पीली पड़ती हैं और बढ़वार रुक जाती है।",
  "Nutrient deficiency causing dark green leaves with purplish discoloration, especially on leaf edges.": "पोषक तत्व की कमी जिसमें पत्तियाँ गहरी हरी होकर बैंगनी रंग लेती हैं, खासकर किनारों पर।",
  "Animal showing excessive panting, lethargy, and reduced feed intake due to high environmental temperatures.": "अधिक गर्मी के कारण पशु तेज़ हाँफ रहा है, सुस्त है और कम चारा खा रहा है।",
  "Metabolic disorder usually occurring in high-yielding dairy cows shortly after calving, causing sweet-smelling breath and weight loss.": "चयापचय विकार जो आमतौर पर अधिक दूध देने वाली गायों में ब्याने के कुछ समय बाद होता है; साँस में मीठी गंध और वज़न घटता है।",
  "Devastating viral disease causing stunted growth and bunching of leaves at the top of the banana plant.": "विनाशकारी वायरल रोग जिसमें केले के पौधे की बढ़वार रुकती है और ऊपर पत्तियाँ गुच्छे में बन जाती हैं।",
  "No disease symptoms detected on the photographed leaf.": "फ़ोटो वाली पत्ती पर रोग का कोई लक्षण नहीं मिला।",
  "No local advisory entry found for this condition.": "इस स्थिति के लिए स्थानीय सलाह उपलब्ध नहीं है।",
  "No description available.": "विवरण उपलब्ध नहीं है।",

  // --- immediate / preventive actions
  "Remove and destroy infected lower leaves immediately.": "संक्रमित निचली पत्तियाँ तुरंत हटाकर नष्ट करें।",
  "Rotate crops — avoid planting tomato/potato in the same spot next season.": "फ़सल चक्र अपनाएँ — अगले मौसम में उसी जगह टमाटर/आलू न लगाएँ।",
  "Remove and burn/bury infected plants — do not compost.": "संक्रमित पौधे हटाकर जलाएँ या गाड़ दें — खाद में न डालें।",
  "Avoid working in the field when leaves are wet to prevent spread.": "फैलाव रोकने के लिए पत्तियाँ गीली हों तब खेत में काम न करें।",
  "Remove severely infected foliage.": "बहुत ज़्यादा संक्रमित पत्तियाँ हटा दें।",
  "Practice 2-3 year crop rotation with non-solanaceous crops.": "गैर-सोलनेसी फ़सलों के साथ 2-3 साल का फ़सल चक्र अपनाएँ।",
  "Destroy infected plant material away from the field.": "संक्रमित पौध सामग्री को खेत से दूर नष्ट करें।",
  "Harvest early if the disease is spreading fast to save remaining tubers.": "रोग तेज़ी से फैल रहा हो तो बचे कंद बचाने के लिए जल्दी खुदाई करें।",
  "Apply fungicide (e.g. propiconazole) if infection is detected early in the season.": "मौसम की शुरुआत में संक्रमण दिखे तो फफूंदनाशक (जैसे प्रोपिकोनाज़ोल) डालें।",
  "Monitor weekly during humid growing periods.": "नम मौसम में हर हफ़्ते निगरानी करें।",
  "Continue regular monitoring, especially after rain.": "नियमित निगरानी जारी रखें, खासकर बारिश के बाद।",
  "Maintain balanced irrigation and fertilization schedule.": "सिंचाई और खाद का संतुलित समय बनाए रखें।",
  "Continue regular monitoring for early signs of blight.": "झुलसा के शुरुआती लक्षणों के लिए नियमित निगरानी जारी रखें।",
  "Maintain consistent watering and mulching.": "नियमित सिंचाई और मल्चिंग बनाए रखें।",
  "Remove infected plant debris and avoid working with wet plants.": "संक्रमित पौध अवशेष हटाएँ और गीले पौधों के साथ काम न करें।",
  "Avoid overhead irrigation.": "ऊपर से (फव्वारा) सिंचाई न करें।",
  "Isolate the affected animal immediately from the herd.": "प्रभावित पशु को तुरंत झुंड से अलग करें।",
  "Disinfect shared equipment and water troughs.": "साझा उपकरण और पानी की नांद कीटाणुरहित करें।",
  "Isolate the animal and restrict herd movement immediately.": "पशु को अलग करें और झुंड की आवाजाही तुरंत रोकें।",
  "Do not sell or move animals until cleared by an official.": "अधिकारी की अनुमति तक पशुओं को न बेचें और न कहीं ले जाएँ।",
  "Milk the affected quarter separately and discard the milk.": "प्रभावित थन को अलग से दुहें और वह दूध फेंक दें।",
  "Check milking equipment hygiene to prevent spread to other animals.": "दूसरे पशुओं में फैलाव रोकने के लिए दुहने के उपकरणों की सफ़ाई जांचें।",
  "Recheck temperature with a manual thermometer to confirm sensor reading.": "सेंसर रीडिंग की पुष्टि के लिए थर्मामीटर से दोबारा तापमान जांचें।",
  "Contact a veterinarian if fever persists beyond 24 hours.": "बुखार 24 घंटे से ज़्यादा रहे तो पशु चिकित्सक से संपर्क करें।",
  "Continue routine health monitoring.": "नियमित स्वास्थ्य निगरानी जारी रखें।",
  "Maintain vaccination and deworming schedule.": "टीकाकरण और कृमिनाशक दवा का समय बनाए रखें।",
  "Apply systemic fungicides (e.g. tebuconazole) at first sign.": "पहला लक्षण दिखते ही सर्वांगी फफूंदनाशक (जैसे टेबुकोनाज़ोल) डालें।",
  "Use resistant wheat varieties in future.": "आगे से रोगरोधी गेहूँ की किस्में लगाएँ।",
  "Maintain proper flooding in paddies.": "धान के खेत में पानी का सही स्तर बनाए रखें।",
  "Apply tricyclazole or similar fungicide.": "ट्राइसाइक्लाज़ोल या इसी तरह का फफूंदनाशक डालें।",
  "Monitor with pheromone traps.": "फेरोमोन ट्रैप से निगरानी करें।",
  "Destroy crop residues after harvest.": "कटाई के बाद फ़सल अवशेष नष्ट करें।",
  "Isolate the flock immediately.": "झुंड को तुरंत अलग करें।",
  "Implement strict biosecurity and cull infected birds.": "सख़्त जैव-सुरक्षा अपनाएँ और संक्रमित पक्षियों को हटाएँ।",
  "Vaccinate healthy birds immediately.": "स्वस्थ पक्षियों का तुरंत टीकाकरण करें।",
  "Disinfect premises thoroughly.": "पूरे परिसर को अच्छी तरह कीटाणुरहित करें।",
  "Quarantine new animals.": "नए पशुओं को अलग (क्वारंटीन) रखें।",
  "Provide supportive care and antibiotics for secondary infections.": "सहायक देखभाल दें और द्वितीयक संक्रमण के लिए एंटीबायोटिक दें।",
  "Apply fungicide immediately upon detection.": "पता चलते ही फफूंदनाशक डालें।",
  "Ensure good canopy penetration of spray.": "ध्यान दें कि छिड़काव पौधे के अंदर तक पहुँचे।",
  "Use copper-based sprays preventatively.": "बचाव के लिए कॉपर आधारित छिड़काव करें।",
  "Decontaminate tools between trees.": "हर पेड़ के बाद औज़ार साफ़ करें।",
  "Apply fungicides during flowering and early fruit set.": "फूल आने और शुरुआती फल बनने के समय फफूंदनाशक डालें।",
  "Prune canopy for better aeration.": "बेहतर हवा के लिए पेड़ की छंटाई करें।",
  "Apply a nitrogen-rich fertilizer (e.g., urea) immediately.": "तुरंत नाइट्रोजन वाली खाद (जैसे यूरिया) डालें।",
  "Ensure soil moisture is adequate to allow nutrient uptake.": "पोषक तत्व लेने के लिए मिट्टी में पर्याप्त नमी रखें।",
  "Apply phosphorus-based fertilizer (e.g., DAP or superphosphate) near the root zone.": "जड़ों के पास फ़ॉस्फ़ोरस वाली खाद (जैसे डीएपी या सुपरफ़ॉस्फ़ेट) डालें।",
  "Check soil pH; high acidity or alkalinity can lock up phosphorus.": "मिट्टी का pH जांचें; ज़्यादा अम्लीय या क्षारीय मिट्टी फ़ॉस्फ़ोरस रोक लेती है।",
  "Move the animal to a shaded, well-ventilated area immediately.": "पशु को तुरंत छायादार, हवादार जगह पर ले जाएँ।",
  "Spray the animal with cool water or use fans.": "पशु पर ठंडा पानी छिड़कें या पंखे चलाएँ।",
  "Provide high-energy feed supplements (e.g., propylene glycol or molasses).": "ऊर्जा वाला पूरक आहार दें (जैसे प्रोपिलीन ग्लाइकॉल या गुड़/शीरा)।",
  "Consult a veterinarian if the animal refuses to eat.": "पशु खाना न खाए तो पशु चिकित्सक से सलाह लें।",
  "Uproot and completely destroy the infected plant to prevent spread.": "फैलाव रोकने के लिए संक्रमित पौधा उखाड़कर पूरी तरह नष्ट करें।",
  "Use certified virus-free planting material in the future.": "आगे से प्रमाणित वायरस-मुक्त पौध सामग्री लगाएँ।",
  "No treatment needed.": "किसी उपचार की ज़रूरत नहीं।",
  "Continue routine weekly scouting, crop rotation and balanced fertilisation.": "हर हफ़्ते खेत की जांच, फ़सल चक्र और संतुलित खाद जारी रखें।",
  "Escalate to cloud advisory (Person B) for a knowledge-base-grounded answer.": "ज्ञानकोष आधारित उत्तर के लिए क्लाउड सलाह लें।",
  "Consult a local agriculture/veterinary officer if symptoms worsen.": "लक्षण बढ़ें तो स्थानीय कृषि/पशु चिकित्सा अधिकारी से सलाह लें।",

  // --- escalation triggers (shown as warnings)
  "If more than 50% of the plant is affected, consult a local agriculture officer before further chemical use.": "अगर पौधे का 50% से ज़्यादा हिस्सा प्रभावित है, तो और रसायन डालने से पहले स्थानीय कृषि अधिकारी से सलाह लें।",
  "Late blight can destroy a field within days. Escalate to an expert if spread is rapid across multiple plants.": "पछेती झुलसा कुछ ही दिनों में खेत नष्ट कर सकता है। कई पौधों में तेज़ी से फैले तो विशेषज्ञ से संपर्क करें।",
  "Monitor tubers at harvest for secondary infection.": "खुदाई के समय कंदों में द्वितीयक संक्रमण की जांच करें।",
  "This is the disease responsible for historic famine-level crop loss — treat as high priority.": "इसी रोग ने इतिहास में अकाल जैसा फ़सल नुकसान किया है — इसे उच्च प्राथमिकता दें।",
  "Usually manageable; escalate only if yield-bearing leaves are heavily damaged before tasseling.": "आमतौर पर नियंत्रित हो जाता है; नर मंजरी से पहले उपज वाली पत्तियाँ बहुत ख़राब हों तभी विशेषज्ञ से मिलें।",
  "None — recheck if new symptoms appear.": "कोई नहीं — नए लक्षण दिखें तो दोबारा जांचें।",
  "Bacterial spot does not respond to fungicides — use copper-based bactericides only.": "जीवाणु धब्बे पर फफूंदनाशक असर नहीं करते — केवल कॉपर आधारित जीवाणुनाशक इस्तेमाल करें।",
  "Notifiable disease in many regions — report to local veterinary authority.": "कई क्षेत्रों में सूचना योग्य रोग — स्थानीय पशु चिकित्सा अधिकारी को बताएँ।",
  "Reportable disease — contact veterinary authorities immediately, do not self-treat.": "सूचना योग्य रोग — तुरंत पशु चिकित्सा अधिकारियों से संपर्क करें, ख़ुद इलाज न करें।",
  "Untreated mastitis can become chronic — seek veterinary care promptly.": "बिना इलाज थनैला पुराना हो सकता है — जल्दी पशु चिकित्सक को दिखाएँ।",
  "Persistent high fever combined with low feed intake needs urgent veterinary attention.": "लगातार तेज़ बुखार और कम चारा खाने पर तुरंत पशु चिकित्सक की ज़रूरत है।",
  "Can cause severe yield loss if not treated before heading.": "बाली निकलने से पहले इलाज न हो तो उपज में भारी नुकसान हो सकता है।",
  "Highly destructive; treat early.": "बहुत विनाशकारी; जल्दी इलाज करें।",
  "Pests can develop resistance; rotate chemicals.": "कीटों में प्रतिरोध बन सकता है; रसायन बदल-बदलकर डालें।",
  "Zoonotic potential! Notify authorities immediately.": "इंसानों में फैलने का ख़तरा! तुरंत अधिकारियों को सूचित करें।",
  "Highly contagious; strict quarantine required.": "अत्यधिक संक्रामक; सख़्त क्वारंटीन ज़रूरी है।",
  "High mortality rate; notify vet services.": "मृत्यु दर ऊँची है; पशु चिकित्सा सेवा को सूचित करें।",
  "Can spread rapidly by wind.": "हवा से तेज़ी से फैल सकता है।",
  "Highly contagious in wet conditions.": "गीले मौसम में अत्यधिक संक्रामक।",
  "Can cause severe post-harvest rot.": "तुड़ाई के बाद गंभीर सड़न हो सकती है।",
  "Prolonged deficiency will severely reduce yield.": "लंबे समय तक कमी रहने से उपज बहुत घटेगी।",
  "Can delay crop maturity and reduce root development.": "फ़सल पकने में देरी और जड़ों का विकास कम हो सकता है।",
  "Severe heat stress can lead to fatal heat stroke. Monitor closely.": "गंभीर गर्मी का तनाव जानलेवा लू का कारण बन सकता है। ध्यान से निगरानी करें।",
  "Can lead to severe milk drop and liver damage if untreated.": "इलाज न हो तो दूध में भारी गिरावट और लीवर को नुकसान हो सकता है।",
  "Highly infectious and cannot be cured. Eradicate infected plants immediately.": "अत्यधिक संक्रामक और लाइलाज। संक्रमित पौधे तुरंत नष्ट करें।",
  "This condition is not yet in the offline knowledge base.": "यह स्थिति अभी ऑफ़लाइन ज्ञानकोष में नहीं है।",

  // --- safety notes
  "Standard agricultural safety applies.": "सामान्य कृषि सुरक्षा नियम लागू होते हैं।",
  "High priority disease.": "उच्च प्राथमिकता वाला रोग।",
  "Unknown.": "अज्ञात।",

  // --- seasonal_guidance.json
  "Monsoon humidity and leaf wetness favour rapid fungal spread: scout fields within 1-2 days after rain, keep drainage clear and avoid overhead irrigation.": "मानसून की नमी और गीली पत्तियाँ फफूंद को तेज़ी से फैलाती हैं: बारिश के 1-2 दिन में खेत जांचें, जल निकासी साफ़ रखें और ऊपर से सिंचाई न करें।",
  "Cool nights with dew or fog can still trigger infection: inspect lower leaves on foggy mornings and irrigate in the morning so foliage dries by evening.": "ओस या कोहरे वाली ठंडी रातों में भी संक्रमण हो सकता है: कोहरे वाली सुबह निचली पत्तियाँ जांचें और सुबह सिंचाई करें ताकि शाम तक पत्तियाँ सूख जाएँ।",
  "Hot dry weather usually slows spread, but irrigated plots stay at risk: keep foliage dry and remove infected leaves promptly.": "गर्म सूखा मौसम फैलाव धीमा करता है, पर सिंचित खेतों में ख़तरा रहता है: पत्तियाँ सूखी रखें और संक्रमित पत्तियाँ जल्दी हटाएँ।",
  "Rain splash spreads bacteria: avoid working in wet fields and disinfect tools between plots.": "बारिश की छींटों से जीवाणु फैलते हैं: गीले खेत में काम न करें और हर खेत के बाद औज़ार कीटाणुरहित करें।",
  "Spread slows in cooler, drier weather; still avoid handling wet plants and use clean seed/transplants.": "ठंडे, सूखे मौसम में फैलाव धीमा होता है; फिर भी गीले पौधे न छुएँ और साफ़ बीज/पौध लगाएँ।",
  "Limit sprinkler irrigation, which splashes bacteria between plants.": "फव्वारा सिंचाई कम करें, इससे जीवाणु पौधों के बीच फैलते हैं।",
  "Insect vector populations rise with warmth and humidity: monitor whiteflies/aphids closely and remove infected plants early.": "गर्मी और नमी में रोग फैलाने वाले कीट बढ़ते हैं: सफ़ेद मक्खी/माहू पर ध्यान रखें और संक्रमित पौधे जल्दी हटाएँ।",
  "Vector activity is usually lower; remove infected plants before the next warm season to cut the source of spread.": "कीटों की सक्रियता आमतौर पर कम होती है; फैलाव का स्रोत ख़त्म करने के लिए अगले गर्म मौसम से पहले संक्रमित पौधे हटाएँ।",
  "Warm dry spells favour whiteflies and aphids: use yellow sticky traps and remove weed hosts around the field.": "गर्म सूखे दिनों में सफ़ेद मक्खी और माहू बढ़ते हैं: पीले चिपचिपे ट्रैप लगाएँ और खेत के आसपास के खरपतवार हटाएँ।",
  "Biting flies and mosquitoes peak in the monsoon: remove standing water, control vectors around sheds and isolate affected animals.": "मानसून में काटने वाली मक्खियाँ और मच्छर सबसे ज़्यादा होते हैं: जमा पानी हटाएँ, बाड़े के आसपास कीट नियंत्रण करें और प्रभावित पशुओं को अलग रखें।",
  "Vector pressure is lower, but keep affected animals isolated and report cases to the veterinary officer.": "कीटों का दबाव कम है, पर प्रभावित पशुओं को अलग रखें और मामलों की सूचना पशु चिकित्सा अधिकारी को दें।",
  "Keep sheds clean and dry to reduce flies; isolate affected animals.": "मक्खियाँ कम करने के लिए बाड़ा साफ़ और सूखा रखें; प्रभावित पशुओं को अलग रखें।",
  "Wet, crowded conditions aid spread: restrict animal movement, disinfect sheds and report to the local veterinary officer.": "गीली और भीड़ वाली जगहों पर रोग तेज़ी से फैलता है: पशुओं की आवाजाही रोकें, बाड़ा कीटाणुरहित करें और स्थानीय पशु चिकित्सा अधिकारी को बताएँ।",
  "Cold stress can lower immunity: keep animals sheltered, restrict movement and report suspected cases.": "ठंड से रोग प्रतिरोधक क्षमता घट सकती है: पशुओं को आश्रय में रखें, आवाजाही रोकें और संदिग्ध मामलों की सूचना दें।",
  "Avoid shared water points and markets during outbreaks; report suspected cases.": "प्रकोप के समय साझा पानी के स्थान और पशु बाज़ार से बचें; संदिग्ध मामलों की सूचना दें।",
  "Humid heat reduces cooling: ensure shade, ventilation and constant clean drinking water.": "उमस भरी गर्मी में शरीर ठंडा नहीं हो पाता: छाया, हवा और लगातार साफ़ पीने का पानी दें।",
  "Heat stress is uncommon now; re-check the temperature and look for fever or infection instead.": "अभी गर्मी का तनाव कम होता है; तापमान दोबारा जांचें और बुखार या संक्रमण की जांच करें।",
  "Peak heat season: provide shade, cool water several times a day and avoid work in midday heat.": "सबसे गर्म मौसम: छाया दें, दिन में कई बार ठंडा पानी दें और दोपहर की गर्मी में काम न कराएँ।",
  "Heavy rain can leach nutrients: apply fertiliser in split doses after a soil test.": "तेज़ बारिश से पोषक तत्व बह सकते हैं: मिट्टी जांच के बाद खाद किस्तों में डालें।",
  "Plan fertiliser at sowing based on a soil test; cold soils can slow nutrient uptake.": "बुवाई के समय मिट्टी जांच के आधार पर खाद तय करें; ठंडी मिट्टी में पोषक तत्व धीरे लिए जाते हैं।",
  "Irrigate before top-dressing so nutrients reach the roots.": "ऊपर से खाद डालने से पहले सिंचाई करें ताकि पोषक तत्व जड़ों तक पहुँचें।",
  "Pest populations build quickly in warm humid weather: scout weekly and use pheromone/sticky traps.": "गर्म नम मौसम में कीट तेज़ी से बढ़ते हैं: हर हफ़्ते जांच करें और फेरोमोन/चिपचिपे ट्रैप लगाएँ।",
  "Pest pressure is often lower; keep scouting and destroy crop residues.": "कीटों का दबाव अक्सर कम रहता है; जांच जारी रखें और फ़सल अवशेष नष्ट करें।",
  "Hot dry weather favours mites: scout leaf undersides and maintain adequate irrigation.": "गर्म सूखे मौसम में घुन बढ़ते हैं: पत्तियों के नीचे जांचें और पर्याप्त सिंचाई रखें।",
  "Keep bedding and udders clean and dry during the wet season.": "बरसात में बिछावन और थन साफ़ और सूखे रखें।",
  "Maintain balanced feeding through the cold season and monitor intake.": "ठंड के मौसम में संतुलित आहार दें और खाने पर नज़र रखें।",
  "Ensure enough water and shade; heat can reduce feed intake.": "पर्याप्त पानी और छाया दें; गर्मी से चारा खाना कम हो सकता है।",
  "No disease detected. The monsoon is high-risk for most diseases, so keep checking every few days.": "कोई रोग नहीं मिला। मानसून में ज़्यादातर रोगों का ख़तरा ज़्यादा होता है, इसलिए हर कुछ दिनों में जांच करते रहें।",
  "No disease detected. Continue routine weekly checks.": "कोई रोग नहीं मिला। हर हफ़्ते की नियमित जांच जारी रखें।",
  "No disease detected. Watch for heat and water stress.": "कोई रोग नहीं मिला। गर्मी और पानी की कमी पर नज़र रखें।",

  // --- quality check / rejection reasons
  "Image is too blurry.": "फ़ोटो बहुत धुंधली है।",
  "Image is poorly exposed (too dark or too bright).": "फ़ोटो में रोशनी ठीक नहीं है (बहुत अंधेरी या बहुत चमकीली)।",
  "Image resolution is too low (< 50px).": "फ़ोटो का रिज़ॉल्यूशन बहुत कम है (< 50px)।",
  "Image contrast is too low.": "फ़ोटो का कंट्रास्ट बहुत कम है।",
  "Overall quality is very low.": "फ़ोटो की कुल गुणवत्ता बहुत कम है।",
  "Image too blurry or dark. Please retake the photo.": "फ़ोटो बहुत धुंधली या अंधेरी है। कृपया दोबारा फ़ोटो लें।",
  "Please retake the photo.": "कृपया दोबारा फ़ोटो लें।",
  "This image doesn't appear to be a crop or livestock photo — please retake or upload a relevant photo.": "यह फ़ोटो फ़सल या पशु की नहीं लगती — कृपया दोबारा लें या सही फ़ोटो अपलोड करें।",

  // --- API / network errors
  "Cannot reach the Agri-Vision server. Is it running?": "एग्री-विज़न सर्वर से संपर्क नहीं हो पा रहा। क्या सर्वर चालू है?",
  "Account not found.": "खाता नहीं मिला।",
  "Enter a valid 10-digit mobile number.": "सही 10 अंकों का मोबाइल नंबर डालें।",
  "Incorrect or expired code.": "कोड गलत है या उसकी समय-सीमा ख़त्म हो गई।",
  "No photo for this record.": "इस रिकॉर्ड की फ़ोटो नहीं है।",
  "Not found.": "नहीं मिला।",
  "PIN must be 4 digits.": "पिन 4 अंकों का होना चाहिए।",
  "Phone number or PIN is incorrect.": "फ़ोन नंबर या पिन गलत है।",
  "Phone verification expired. Please request a new code.": "फ़ोन सत्यापन की समय-सीमा ख़त्म। कृपया नया कोड मंगाएँ।",
  "Photo is larger than 10 MB.": "फ़ोटो 10 MB से बड़ी है।",
  "Please enter your name.": "कृपया अपना नाम डालें।",
  "Please upload a JPG, PNG or WebP photo.": "कृपया JPG, PNG या WebP फ़ोटो अपलोड करें।",
  "Record not found.": "रिकॉर्ड नहीं मिला।",
  "Session expired. Please log in again.": "सत्र समाप्त। कृपया फिर से लॉग इन करें।",
  "Unauthorized.": "अनुमति नहीं है।",
  "Unknown region.": "अज्ञात क्षेत्र।",
  "Streaming not supported": "यह ब्राउज़र स्ट्रीमिंग सपोर्ट नहीं करता",

  // --- confidence gate reasons
  "Safety critical prediction": "सुरक्षा के लिहाज़ से गंभीर पहचान",
  "Farmer symptoms conflict": "किसान के बताए लक्षण मेल नहीं खाते",
  "Poor input quality (e.g., blurry/dark)": "फ़ोटो की गुणवत्ता कम (जैसे धुंधली/अंधेरी)",
  "Low evidence agreement": "सबूतों में कम सहमति",
};

const TIER_HI: Record<string, string> = {
  confident: "पक्की", possible: "संभावित", refer_expert: "विशेषज्ञ को भेजें", local: "स्थानीय", cloud: "क्लाउड",
};

export const REGION_HI: Record<string, string> = {
  "Andhra Pradesh": "आंध्र प्रदेश", "Arunachal Pradesh": "अरुणाचल प्रदेश", Assam: "असम", Bihar: "बिहार",
  Chhattisgarh: "छत्तीसगढ़", Goa: "गोवा", Gujarat: "गुजरात", Haryana: "हरियाणा", "Himachal Pradesh": "हिमाचल प्रदेश",
  Jharkhand: "झारखंड", Karnataka: "कर्नाटक", Kerala: "केरल", "Madhya Pradesh": "मध्य प्रदेश", Maharashtra: "महाराष्ट्र",
  Manipur: "मणिपुर", Meghalaya: "मेघालय", Mizoram: "मिज़ोरम", Nagaland: "नागालैंड", Odisha: "ओडिशा", Punjab: "पंजाब",
  Rajasthan: "राजस्थान", Sikkim: "सिक्किम", "Tamil Nadu": "तमिलनाडु", Telangana: "तेलंगाना", Tripura: "त्रिपुरा",
  "Uttar Pradesh": "उत्तर प्रदेश", Uttarakhand: "उत्तराखंड", "West Bengal": "पश्चिम बंगाल", Delhi: "दिल्ली",
  "Jammu and Kashmir": "जम्मू और कश्मीर", Ladakh: "लद्दाख", Puducherry: "पुडुचेरी",
};

/** Translate one known backend sentence, including the few templated ones. */
export function sentenceHi(s: string): string | null {
  const text = s.trim();
  if (SENTENCE_HI[text]) return SENTENCE_HI[text];

  // seasonal note + " For locally approved products, check with your <Region> KVK / ..."
  const kvk = text.match(/^(.*?)\s*For locally approved products, check with your (.+?) KVK \/ agriculture or veterinary department\.$/);
  if (kvk) {
    const base = sentenceHi(kvk[1]) ?? kvk[1];
    const region = REGION_HI[kvk[2]] ?? kvk[2];
    return `${base} स्थानीय रूप से स्वीकृत दवाओं के लिए अपने ${region} के केवीके / कृषि या पशु चिकित्सा विभाग से पूछें।`;
  }

  // explainability.format_reason: "Routed to <tier> tier[ because: a, b]."
  const routed = text.match(/^Routed to (\w+) tier(?: because: (.+))?\.$/);
  if (routed) {
    const tier = TIER_HI[routed[1]] ?? routed[1];
    if (!routed[2]) return `${tier} श्रेणी में भेजा गया।`;
    return `${tier} श्रेणी में भेजा गया, क्योंकि: ${splitReasons(routed[2]).map(reasonHi).join(", ")}।`;
  }

  // Several quality reasons joined with spaces.
  const parts = text.split(/(?<=\.)\s+/);
  if (parts.length > 1 && parts.every((p) => SENTENCE_HI[p])) return parts.map((p) => SENTENCE_HI[p]).join(" ");
  return null;
}

function splitReasons(s: string) {
  // Reasons are joined with ", " but one reason itself contains "(e.g., blurry/dark)".
  return s.split(/, (?=[A-Z])/);
}

function reasonHi(r: string): string {
  if (SENTENCE_HI[r]) return SENTENCE_HI[r];
  const conf = r.match(/^Confidence ([\d.]+) below threshold ([\d.]+)$/);
  if (conf) return `विश्वास ${conf[1]}, सीमा ${conf[2]} से कम`;
  const missing = r.match(/^Prediction '(.+)' not found in local offline database$/);
  if (missing) return `'${conditionHi(missing[1]) ?? missing[1]}' ऑफ़लाइन ज्ञानकोष में नहीं मिला`;
  return r;
}
