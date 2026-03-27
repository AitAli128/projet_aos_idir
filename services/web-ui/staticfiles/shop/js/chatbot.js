(function () {
    /*
      Pharm-AI Smarter Chatbot v3 (High Performance NLP)
      Implements: Normalization, Intent Discovery, State Management, Multilingual Support
    */

    const CONFIG = {
        primaryColor: '#10b981',
        secondaryColor: '#3b82f6',
        botName: 'Pharm-AI',
        typingDelay: 1200,
    };

    // Chatbot Internal State
    const STATE = {
        lastIntent: null,
        language: 'fr', // fr, dz, en
        awaitingInput: null, // e.g., 'duration'
        isOpen: false
    };

    // Intent Mapping
    const INTENTS = {
        "greeting": {
            keywords: ["saha", "bonjour", "hello", "hi", "marhba", "aslama", "salut"],
            responses: {
                "dz": "Saha ! Marhba bik f' MarketPharm 🇩🇿. Kifech neqder n'awnek?",
                "fr": "Bonjour ! Je suis Pharm-AI 🤖. Comment puis-je vous aider aujourd'hui ?",
                "en": "Hello! I am Pharm-AI 🤖, your assistant. How can I help you today?"
            }
        },
        "headache": {
            keywords: ["rassi", "tete", "headache", "doua rassi", "mal a la tete", "migraine"],
            responses: {
                "dz": "Rassek yawja3 ? Tqedder takhed Doliprane. Mel-weqat bda lawja3 ?",
                "fr": "Douleur à la tête ? Le Paracétamol est indiqué. Depuis quand avez-vous mal ?",
                "en": "Headache? Paracetamol is usually recommended. Since when do you have this pain?"
            },
            nextState: "ask_duration"
        },
        "fever": {
            keywords: ["skhana", "fievre", "fever", "fiya skhana", "chaud"],
            responses: {
                "dz": "Fiya skhana? Paracétamol hia l'hall. Qis t-température ta'ek mlih.",
                "fr": "De la fièvre ? Prenez du Paracétamol et hydratez-vous. Quelle est votre température ?",
                "en": "Fever? Take Paracetamol and stay hydrated. What is your temperature?"
            },
            nextState: "ask_temp"
        },
        "stomach": {
            keywords: ["kerchi", "ventre", "stomach", "mal au ventre", "douleur estomac"],
            responses: {
                "dz": "Kerchek toujak'? Spasfon neqder ysa3dek. Klit haja mn barra?",
                "fr": "Mal au ventre ? Le Spasfon peut soulager. Avez-vous mangé quelque chose d'inhabituel ?",
                "en": "Stomach pain? Spasfon or an antacid can help. Did you eat something heavy?"
            }
        },
        "help": {
            keywords: ["aide", "help", "m'awna", "kifech"],
            responses: {
                "dz": "Neqder n'awnek f' el catalogue wala n'n'ensahék b' dwa simple.",
                "fr": "Je peux vous aider à naviguer ou vous conseiller pour des symptômes légers.",
                "en": "I can help you browse the catalog or advice on minor symptoms."
            }
        },
        "thanks": {
            keywords: ["merci", "thanks", "chokran", "sahit", "shoukran", "barak allah"],
            responses: {
                "dz": "Bla mziya ! Rabi yjib el chifa 🤲.",
                "fr": "Je vous en prie ! N'hésitez pas si vous avez d'autres questions.",
                "en": "You're welcome! Get well soon! 🌟"
            }
        }
    };

    // NLP Utilities
    function normalize(text) {
        if (!text) return "";
        return text.toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "") // Remove accents
            .replace(/[^\w\s]/g, "") // Remove punctuation
            .trim();
    }

    function detectLanguage(text) {
        const norm = normalize(text);
        if (/saha|rassi|skhana|kerchi|sahit|marhba|doua/i.test(norm)) return 'dz';
        if (/hello|hi|fever|headache|thanks|stomach|help/i.test(norm)) return 'en';
        return 'fr';
    }

    function getResponse(text) {
        const norm = normalize(text);
        const lang = detectLanguage(text);
        STATE.language = lang;

        // Contextual matching if we were waiting for info
        if (STATE.awaitingInput === 'duration') {
            STATE.awaitingInput = null;
            return {
                "dz": "ila lwja3 fog 3 iyam , lazém tchouf tbib.",
                "fr": "Si la douleur persiste plus de 3 jours, veuillez consulter un médecin.",
                "en": "If the pain persists for more than 3 days, please see a doctor."
            }[lang];
        }

        // Search for Intent
        for (const [key, data] of Object.entries(INTENTS)) {
            if (data.keywords.some(k => norm.includes(normalize(k)))) {
                STATE.lastIntent = key;
                if (data.nextState) {
                    STATE.awaitingInput = data.nextState === 'ask_duration' ? 'duration' : 'temp';
                }
                return data.responses[lang];
            }
        }

        // Fuzzy/Fallback
        return {
            "dz": "Ma f'hemtech mlih... tqedder t'qol fia skhana wala rassi yawja3 ?",
            "fr": "Désolé, je n'ai pas bien compris. Pouvez-vous décrire vos symptômes (ex: fièvre, mal de tête) ?",
            "en": "Sorry, I didn't catch that. Could you describe your symptoms? (e.g., headache, fever)"
        }[lang];
    }

    // UI Construction
    function initUI() {
        const chatRoot = document.createElement('div');
        chatRoot.id = 'pharm-ai-chat-root';
        chatRoot.style.cssText = 'position:fixed; bottom:25px; right:25px; z-index:10000; font-family:"Plus Jakarta Sans", "Outfit", sans-serif;';

        const launcher = document.createElement('button');
        launcher.innerHTML = '<i class="fas fa-robot"></i>';
        launcher.style.cssText = `
            width:68px; height:68px; border-radius:34px; 
            background: linear-gradient(135deg, ${CONFIG.primaryColor}, ${CONFIG.secondaryColor});
            color:white; border:none; cursor:pointer; font-size:1.8rem;
            box-shadow: 0 10px 30px rgba(16, 185, 129, 0.4);
            transition: all 0.4s cubic-bezier(0.19, 1, 0.22, 1);
        `;

        launcher.onmouseover = () => launcher.style.transform = 'scale(1.1) translateY(-5px)';
        launcher.onmouseout = () => launcher.style.transform = 'scale(1) translateY(0)';

        const win = document.createElement('div');
        win.style.cssText = `
            display:none; width:400px; height:600px; max-height:80vh;
            background: rgba(255, 255, 255, 0.98); 
            backdrop-filter: blur(15px);
            border-radius:28px; box-shadow: 0 25px 80px rgba(0,0,0,0.25);
            border: 1px solid rgba(255,255,255,0.4);
            position:absolute; bottom:85px; right:0;
            flex-direction:column; overflow:hidden;
        `;

        win.innerHTML = `
            <div style="background: linear-gradient(135deg, ${CONFIG.primaryColor}, ${CONFIG.secondaryColor}); color:white; padding:1.4rem; display:flex; justify-content:space-between; align-items:center;">
                <div style="display:flex; align-items:center; gap:0.8rem;">
                    <div style="background:white; width:45px; height:45px; border-radius:50%; display:flex; align-items:center; justify-content:center; color:${CONFIG.primaryColor}; font-size:1.4rem;">
                        <i class="fas fa-microchip"></i>
                    </div>
                    <div>
                        <div style="font-weight:700; font-size:1.1rem;">Pharm-AI 3.0</div>
                        <div style="font-size:0.75rem; opacity:0.9;"><i class="fas fa-circle" style="font-size:0.5rem; color:#4ade80;"></i> Intelligent & Multilingual</div>
                    </div>
                </div>
                <i class="fas fa-chevron-down" style="cursor:pointer; opacity:0.8;" id="chat-close"></i>
            </div>
            <div id="chat-body" style="flex:1; padding:1.5rem; overflow-y:auto; display:flex; flex-direction:column; gap:1.2rem; background: #fafafa;">
                <div class="bot-msg" style="background:white; border:1px solid #eee; padding:1.1rem; border-radius:20px 20px 20px 4px; align-self:flex-start; max-width:85%; font-size:0.95rem; line-height:1.5; color:#334155; box-shadow:0 4px 6px rgba(0,0,0,0.02);">
                    Marhba bik! Bonjour! Hello! Je suis votre assistant Pharm-AI boosté à l'IA. Comment puis-je vous aider ? 🌿
                </div>
            </div>
            <div id="chat-typing" style="display:none; padding:0.4rem 1.5rem; font-size:0.8rem; color:#94a3b8; font-style:italic;">Pharm-AI analyse votre message...</div>
            <div style="padding:1.4rem; border-top:1px solid #eee; display:flex; gap:0.8rem; background:white;">
                <input type="text" id="chat-input" placeholder="Parlez-moi de vos symptômes..." style="flex:1; border:2px solid #f1f5f9; border-radius:30px; padding:0.8rem 1.4rem; outline:none; font-size:1rem; transition:all 0.3s; background:#f8fafc;">
                <button id="chat-send" style="background:${CONFIG.primaryColor}; border:none; color:white; width:50px; height:50px; border-radius:50%; cursor:pointer; display:flex; align-items:center; justify-content:center; box-shadow:0 4px 12px rgba(16, 185, 129, 0.2);"><i class="fas fa-paper-plane"></i></button>
            </div>
        `;

        chatRoot.appendChild(win);
        chatRoot.appendChild(launcher);
        document.body.appendChild(chatRoot);

        const input = win.querySelector('#chat-input');
        const send = win.querySelector('#chat-send');
        const body = win.querySelector('#chat-body');
        const typing = win.querySelector('#chat-typing');
        const close = win.querySelector('#chat-close');

        launcher.onclick = () => { win.style.display = (win.style.display === 'flex') ? 'none' : 'flex'; if (win.style.display === 'flex') input.focus(); };
        close.onclick = () => win.style.display = 'none';

        function addMsg(text, isUser = false) {
            const m = document.createElement('div');
            m.style.cssText = `
                padding:1.1rem; border-radius:${isUser ? '20px 20px 4px 20px' : '20px 20px 20px 4px'}; 
                max-width:85%; align-self:${isUser ? 'flex-end' : 'flex-start'};
                font-size:0.95rem; line-height:1.5; box-shadow:0 8px 20px rgba(0,0,0,0.05);
                animation: slideUp 0.4s ease-out;
                ${isUser ? `background:linear-gradient(135deg, ${CONFIG.primaryColor}, ${CONFIG.secondaryColor}); color:white;` : 'background:white; border:1px solid #eee; color:#334155;'}
            `;
            m.textContent = text;
            body.appendChild(m);
            body.scrollTop = body.scrollHeight;
        }

        async function handle() {
            const val = input.value.trim();
            if (!val) return;
            addMsg(val, true);
            input.value = '';

            typing.style.display = 'block';
            body.scrollTop = body.scrollHeight;

            setTimeout(() => {
                typing.style.display = 'none';
                addMsg(getResponse(val));
            }, CONFIG.typingDelay);
        }

        send.onclick = handle;
        input.onkeypress = (e) => { if (e.key === 'Enter') handle(); };

        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideUp { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }
            #chat-input:focus { border-color: ${CONFIG.primaryColor} !important; background:white !important; box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.1); }
        `;
        document.head.appendChild(style);
    }

    if (document.readyState === 'complete') initUI();
    else window.addEventListener('load', initUI);
})();
