"""
Re-export / mirror of idiom_detector for role2 module independence.
"""
import sys
from pathlib import Path

# Add project root to sys.path if not present
ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from src.relevance.idiom_detector import (
        is_slang_or_figurative,
        IDIOM_PATTERNS,
        COMPILED_IDIOM_PATTERNS,
        AUTHENTIC_EMERGENCY_SIGNALS,
        COMPILED_AUTHENTIC_SIGNALS,
    )
except ImportError:
    # Inline fallback if imported in isolated role2 environment
    import re
    from typing import Tuple

    IDIOM_PATTERNS = [
        r"\b(?:is|was|are|were|be|been|being)\s+(?:straight|pure|absolute|totally|so|too|hella|super)?\s*fire\b",
        r"\b(?:straight|pure|absolute|hella|mad)\s+fire\b",
        r"\bthat(?:'s|\s+is|\s+was)?\s+fire\b",
        r"\bfire\s+(?:beat|track|song|album|mixtape|flow|bars|verse|rhymes|lyrics)\b",
        r"\bfire\s+(?:movie|film|show|trailer|scene|episode|series|cinema)\b",
        r"\bfire\s+(?:fit|outfit|kicks|shoes|sneakers|drip|jacket|clothes|dress)\b",
        r"\bfire\s+(?:food|tacos|pizza|burger|ramen|wings|bbq|sauce|meal|taste|dish)\b",
        r"\bfire\s+(?:deal|deals|sale|sales|discount|price|prices)\b",
        r"\b(?:dumpster\s+fire)\b",
        r"\b(?:on\s+fire)\b(?!\s+(?:and\s+burning|burning\s+down|in\s+the\s+building))",
        r"\b(?:spit|spitting|spits)\s+fire\b",
        r"\b(?:putting\s+out\s+fires|put\s+out\s+fires)\s+(?:at\s+work|in\s+the\s+office|at\s+my\s+job)\b",
        r"\b(?:burning\s+desire|burning\s+curiosity|burning\s+passion|burning\s+question|burning\s+ambition)\b",
        r"\b(?:burn\s+rubber|slow\s+burn)\b",
        r"\b(?:smoking\s+hot)\b",
        r"\b(?:smoke\s+the\s+competition)\b",
        r"\b(?:go\s+up\s+in\s+smoke|went\s+up\s+in\s+smoke)\b",
        r"\b(?:blow|blowing)\s+smoke\b",
        r"\b(?:where\s+there\s+is\s+smoke\s+there\s+is\s+fire|where\s+there(?:'s)?\s+smoke)\b",
        r"\b(?:roast\s+battle|got\s+roasted|getting\s+roasted|roasted\s+him|roasted\s+her|roasted\s+them)\b",
        r"\b(?:roasted\s+so\s+badly|roasted\s+in\s+the\s+comments?)\b",
        r"\b(?:is|was|are|were)\s+(?:the\s+bomb|da\s+bomb)\b",
        r"\b(?:this|that)\s+\w+\s+is\s+the\s+bomb\b",
        r"\b(?:had|having|have)\s+a\s+blast\b",
        r"\b(?:it|that|party|concert|trip|event|vacation|night)\s+(?:was|is)\s+(?:an?\s+)?(?:absolute\s+|total\s+)?blast\b",
        r"\b(?:what\s+a\s+blast)\b",
        r"\b(?:full\s+blast)\b",
        r"\b(?:blast\s+from\s+the\s+past)\b",
        r"\b(?:bombed\s+(?:the|his|her|my|their|our)(?:\s+\w+)?\s+(?:test|exam|interview|audition|presentation|quiz|performance))\b",
        r"\b(?:bombed\s+on\s+stage)\b",
        r"\b(?:dropped\s+a\s+bombshell|bombshell\s+announcement|bombshell\s+news|bombshell\s+trailer|bombshell\s+revelation|bombshell\s+report)\b",
        r"\b(?:dropped\s+a\s+bomb\s+on\s+us)\b",
        r"\b(?:blew\s+up\s+on\s+(?:tiktok|twitter|instagram|youtube|social\s+media|the\s+internet))\b",
        r"\b(?:blew\s+up\s+overnight)\b",
        r"\b(?:phone\s+blew\s+up|notifications?\s+blew\s+up)\b",
        r"\b(?:blew\s+my\s+mind|mind\s*blowing|blown\s+away)\b",
        r"\b(?:head|brain)\s+(?:is\s+about\s+to|feels\s+like\s+it(?:'s)?\s+about\s+to|is\s+gonna)\s+explode\b",
        r"\b(?:exploded\s+with\s+(?:laughter|cheers|applause|excitement|joy|anger|rage))\b",
        r"\b(?:exploded\s+in\s+popularity|exploded\s+onto\s+the\s+scene)\b",
        r"\b(?:explosive\s+(?:guitar\s+solo|performance|growth|pace|speed|talent|energy|gameplay))\b",
        r"\b(?:code|server|servers|app|application|browser|chrome|firefox|safari|pc|computer|laptop|macbook|game|program|software|script|process|docker|service|database|postgres|redis|node|api|ui|pipeline|build|system)\s+(?:has\s+)?(?:crashed|crashing|crashes)\b",
        r"\b(?:crashed\s+(?:on|in)\s+(?:production|prod|staging|dev|runtime|startup|background))\b",
        r"\b(?:crashed\s+and\s+i\s+lost\s+(?:my\s+tabs|all\s+my\s+tabs|my\s+work|my\s+data))\b",
        r"\b(?:stock\s+market|stocks?|bitcoin|crypto|shares?|nasdaq|dow\s+jones|sp500|economy)\s+(?:took\s+a\s+dive\s+and\s+)?(?:crashed|crash|crashing)\b",
        r"\b(?:crashed\s+(?:twenty|thirty|forty|fifty|ten|[0-9]+)\s*(?:%|percent))\b",
        r"\b(?:crash\s+course\s+(?:in|on))\b",
        r"\b(?:crash\s+(?:on|at)\s+(?:your|my|his|her|their|the)\s+(?:couch|place|sofa|bed))\b",
        r"\b(?:crash\s+(?:the\s+)?(?:wedding|party|reception|gate))\b",
        r"\b(?:train\s+wreck|emotional\s+wreck|nervous\s+wreck)\b",
        r"\b(?:happy\s+accident)\b",
        r"\b(?:accidentally\s+(?:deleted|pressed|clicked|liked|sent))\b",
        r"\b(?:dying\s+of\s+laughter|dying\s+laughing|dead\s+from\s+laughing|laughed\s+so\s+hard|had\s+me\s+dying|has\s+me\s+dying)\b",
        r"\b(?:i(?:'m|\s+am)?\s+literally\s+dying\s+laughing)\b",
        r"\b(?:dying\s+to\s+(?:know|see|try|hear|eat|visit|meet|go))\b",
        r"\b(?:dying\s+for\s+(?:a\s+coffee|a\s+drink|some\s+food|a\s+vacation|a\s+break))\b",
        r"\b(?:had|having|have)\s+a\s+heart\s+attack\s+when\s+i\s+saw\s+(?:the\s+)?(?:bill|price|check|receipt|cost|grade|score)\b",
        r"\b(?:almost\s+gave\s+me\s+a\s+heart\s+attack)\b",
        r"\b(?:traffic|commute|workout|exam|test|schedule)(?:\s+(?:on|in|at)\s+[^,\.]+)?\s+is\s+(?:absolute\s+|total\s+)?murder\b",
        r"\b(?:my\s+)?(?:feet|legs|arms|back|head|eyes|shoes)\s+are\s+killing\s+me\b",
        r"\b(?:killer(?:\s+\w+)?\s+(?:bassline|riff|solo|beat|drop|track|song|playlist|performance|outfit|look|dress|shoes|heels|smile|body))\b",
        r"\b(?:killed\s+it|killing\s+it)\s+(?:on\s+stage|tonight|during\s+the|at\s+the|in\s+the)\b",
        r"\b(?:they|she|he|we|you)\s+(?:completely\s+|totally\s+|absolutely\s+)?(?:killed\s+it|killed\s+their(?:\s+\w+)?\s+performance)\b",
        r"\b(?:choked\s+(?:during|in)\s+(?:my|the|his|her)\s+(?:presentation|speech|interview|audition|exam|finals?|match|game|fourth\s+quarter|final\s+set))\b",
        r"\b(?:choked\s+under\s+pressure|choking\s+under\s+pressure)\b",
        r"\b(?:choked\s+up\s+with\s+emotion|choking\s+back\s+tears)\b",
        r"\b(?:died\s+of\s+embarrassment|died\s+inside)\b",
        r"\b(?:drop\s+dead\s+gorgeous)\b",
        r"\b(?:phone|laptop|airpods|battery)\s+(?:is|are)\s+(?:completely\s+|totally\s+)?dead\b",
        r"\b(?:screen\s+is\s+bleeding\s+light|light\s+bleed|bleeding\s+money|bleeding\s+cash|bleeding\s+heart)\b",
        r"\b(?:stroke\s+of\s+luck|stroke\s+of\s+genius|different\s+strokes\s+for\s+different\s+folks)\b",
        r"\b(?:shooting\s+hoops|shoot\s+some\s+hoops|shoot\s+some\s+pool|shoot\s+pool)\b",
        r"\b(?:shoot\s+(?:you|me|us|them)\s+(?:a|an)\s+(?:quick\s+)?(?:email|dm|text|message))\b",
        r"\b(?:photoshoot|photo\s+shoot|shooting\s+(?:a\s+scene|a\s+video|a\s+commercial|photos|film))\b",
        r"\b(?:taking\s+shots|take\s+shots|shots\s+of\s+tequila|shots\s+of\s+vodka|jello\s+shots|shots\s+at\s+the\s+bar)\b",
        r"\b(?:call\s+the\s+shots|shot\s+in\s+the\s+dark|give\s+it\s+your\s+best\s+shot|long\s+shot|cheap\s+shot)\b",
        r"\b(?:shotgun\s+wedding|riding\s+shotgun|ride\s+shotgun)\b",
        r"\b(?:stole\s+my\s+heart|stole\s+the\s+show|stole\s+the\s+spotlight|steal\s+the\s+show)\b",
        r"\b(?:highway\s+robbery|daylight\s+robbery)\b",
        r"\b(?:robbed\s+of\s+(?:victory|the\s+win|the\s+title|the\s+award|the\s+championship))\b",
        r"\b(?:flooded\s+with(?:\s+\w+)?\s+(?:emails|messages|notifications|dms|work|homework|assignments|calls|complaints|requests|orders|applications))\b",
        r"\b(?:flood\s+of\s+(?:childhood\s+memories|memories|emotions|complaints|calls|tears|nostalgia))\b",
        r"\b(?:drowning\s+in(?:\s+\w+)?\s+(?:paperwork|work|debt|homework|assignments|tasks|emails|chores))\b",
        r"\b(?:team|defense|offense|player|squad)\s+collapsed\s+(?:under\s+pressure|in\s+the\s+(?:fourth|4th|last)\s+quarter|in\s+the\s+second\s+half|in\s+the\s+final\s+minutes?)\b",
        r"\b(?:company(?:\s+stock|\'s\s+stock)?\s+price\s+collapsed)\b",
        r"\b(?:caved\s+in\s+to\s+(?:public\s+pressure|demands|criticism))\b",
        r"\b(?:caved\s+under\s+pressure)\b",
        r"\b(?:movie\s+i\s+watched|watched\s+a\s+movie|watching\s+a\s+movie|movie\s+last\s+night)\b",
        r"\b(?:listening\s+to\s+(?:a\s+song|music|the\s+album|the\s+track|the\s+podcast))\b",
        r"\b(?:standup\s+comedian|comedy\s+show|funny\s+meme|hilarious\s+video)\b",
        r"\b(?:best\s+buy|mall|store\s+sale|taco\s+truck|restaurant\s+bill)\b",
        r"\b(?:playing\s+(?:video\s+games?|call\s+of\s+duty|counter\s*strike|fortnite|gta|minecraft))\b",
    ]
    COMPILED_IDIOM_PATTERNS = [re.compile(p, re.IGNORECASE) for p in IDIOM_PATTERNS]

    AUTHENTIC_EMERGENCY_SIGNALS = [
        r"\bcall\s+(?:911|108|999|112|the\s+police|the\s+fire\s+department|an\s+ambulance)\b",
        r"\b(?:send|need|dispatch)\s+(?:help|ambulance|firefighters?|first\s+responders?|paramedics?|police|rescue\s+team)\b",
        r"\b(?:flames\s+coming\s+out|black\s+smoke\s+pouring|thick\s+smoke|visible\s+flames|fire\s+spreading|building\s+on\s+fire)\b",
        r"\b(?:fire\s+broke\s+out|fire\s+has\s+broken\s+out|caught\s+fire|structure\s+fire)\b",
        r"\b(?:people|victims?|passengers?|residents?|occupants?)\s+(?:trapped|pinned|screaming|injured|unconscious|bleeding|evacuating)\b",
        r"\b(?:several|multiple|\d+)\s+(?:vehicles?|cars?|trucks?)\s+(?:crashed|collided|involved\s+in\s+crash|overturned)\b",
        r"\b(?:car|truck|bus|vehicle)\s+(?:accident|crash|collision)\s+(?:on|at|near|blocking)\b",
        r"\b(?:overturned\s+vehicle|head-on\s+collision|pileup\s+on)\b",
        r"\b(?:gas\s+pipeline|transformer|gas\s+tank|boiler)\s+(?:exploded|leaking|blast)\b",
        r"\b(?:active\s+shooter|shots\s+fired|gunshots?\s+heard|armed\s+robbery|stabbing|person\s+assaulted)\b",
        r"\b(?:unconscious|not\s+breathing|in\s+cardiac\s+arrest|stopped\s+breathing|severe\s+chest\s+pain)\b",
        r"\b(?:bleeding\s+heavily|profuse\s+bleeding|severe\s+injur(?:y|ies))\b",
        r"\b(?:choking\s+on\s+food|cannot\s+breathe|turning\s+blue)\b",
        r"\b(?:flash\s+flood|water\s+rising\s+rapidly|streets?\s+submerged|homes?\s+flooding)\b",
        r"\b(?:ceiling|roof|wall|building|balcony|structure)\s+collapsed\b",
        r"\b(?:trapped\s+under\s+rubble|under\s+debris)\b",
        r"\b(?:child|person|toddler)\s+(?:missing|abducted|kidnapped)\b",
    ]
    COMPILED_AUTHENTIC_SIGNALS = [re.compile(s, re.IGNORECASE) for s in AUTHENTIC_EMERGENCY_SIGNALS]

    def is_slang_or_figurative(text: str) -> Tuple[bool, str]:
        if not text:
            return False, "empty_text"
        lower_text = text.lower().strip()
        for signal_pattern in COMPILED_AUTHENTIC_SIGNALS:
            if signal_pattern.search(lower_text):
                return False, "authentic_emergency_signal_present"
        for pattern in COMPILED_IDIOM_PATTERNS:
            match = pattern.search(lower_text)
            if match:
                return True, f"matched_slang_idiom: '{match.group(0)}'"
        return False, "no_slang_detected"
