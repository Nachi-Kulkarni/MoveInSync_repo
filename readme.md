# Movi-Transport Agent

## Made by-Nachiket Kulkarni
### details- nachiram03@gmail.com, Phone.no- 9586797078

# Langgraph Architecture

Input (Text/Voice/Image)
    ↓
[Preprocessing Layer]
├─ Speech-to-Text (if voice)
├─ Image Quick Scan (if image)
└─ Context Injection (current page)
    ↓
[Intent Understanding] (Claude Sonnet 4.5)
├─ Extract: action, entities, page context
└─ Classify: read/create/delete/update
    ↓
[Consequence Checker] ← **THE STAR NODE**
├─ Query DB for implications
├─ Check: bookings? dependencies? conflicts?
└─ Risk Score: none/low/high
    ↓
    ├─[Conditional Edge]─────┐
    │                         │
[Low/No Risk]          [High Risk]
    │                         │
    ↓                         ↓
[Execute Action]      [Confirmation Dialog]
    │                   ├─ Explain consequences
    │                   ├─ Offer alternatives
    │                   └─ Wait for response
    │                         │
    │                    [User Response]
    │                    ├─ "Yes" → Execute
    │                    ├─ "No" → Cancel
    │                    └─ "Modify" → Replan
    │                         ↓
    └─────────────────>[Response Generator]
                              ↓
                     [TTS + UI Update]

