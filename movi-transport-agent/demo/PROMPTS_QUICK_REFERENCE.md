`# Demo Video - Quick Reference Card

## 🎬 DEMO SEQUENCE (4.5 minutes)

### SETUP
```bash
# Terminal 1
cd backend && ../venv/bin/python -m uvicorn main:app --reload

# Terminal 2
cd frontend && ../venv/bin/python gradio_app.py

# Browser
http://localhost:7860
```

---

## 📝 PROMPTS IN ORDER

### 1️⃣ Bus Dashboard - List Unassigned (30s)
**Tab:** 🚌 Bus Dashboard
```
Show me all trips that don't have vehicles assigned
```

---

### 2️⃣ Tribal Knowledge - Consequence Flow (60s) ⭐
**Tab:** 🚌 Bus Dashboard
```
Remove vehicle from Evening Rush 17:00
```
**Expected:** ⚠️ High risk warning with booking percentage

**Then type:**
```
no
```
**Expected:** ✅ Action cancelled

---

### 3️⃣ Vehicle Assignment - Fuzzy Matching (30s)
**Tab:** 🚌 Bus Dashboard
```
Assign vehicle KA-01-AB-1234 and driver Amit to the trip that has no vehicle at 6:30
```
**Expected:** ✅ Success (matches "06:30" and "Amit Kumar")
**Action:** Click 🔄 Refresh to show updated data

---

### 4️⃣ Image Input - Screenshot Analysis (45s) ⭐
**Tab:** 🚌 Bus Dashboard
**Action:** Take screenshot of dashboard first, save as `dashboard_screenshot.png`
```
[Upload dashboard_screenshot.png]

Which trip in this screenshot has the highest booking percentage?
```
**Expected:** Agent identifies trip with highest booking from image

---

### 5️⃣ Manage Routes - Create Stop (45s)
**Tab:** 🛣️ Manage Routes
```
Create a new stop called Tech Park at coordinates 12.9716, 77.5946
```
**Expected:** ✅ Stop created with ID 39
**Action:** Click 🔄 Refresh to see stop in Stops table

---

### 6️⃣ UI Context Awareness - Wrong Page (30s) ⭐
**Tab:** 🛣️ Manage Routes (stay here intentionally)
```
Assign vehicle TN-09-BC-5678 to Airport Express 06:00
```
**Expected:** 📍 "Please switch to Bus Dashboard tab" message

**Then:** Switch to 🚌 Bus Dashboard and repeat:
```
Assign vehicle TN-09-BC-5678 to Airport Express 06:00
```
**Expected:** ✅ Success on correct page

---

### 7️⃣ Create Path (30s)
**Tab:** 🛣️ Manage Routes
```
Create a new path called 'Cubbon-Loop' using stops Gavipuram, Peenya, and Koramangala
```
**Expected:** ✅ Path created with stop sequence

---

### 8️⃣ Fuzzy Matching Demo (20s)
**Tab:** Either (READ operation)
```
Show me details about the airport express trip at 6:00
```
**Expected:** Finds "Airport Express 06:00" (6:00 → 06:00 normalization)

---

## ⭐ CRITICAL FEATURES TO SHOW

✅ **Both UI Pages**
- Bus Dashboard with trip management
- Manage Routes with routes/stops tables

✅ **Tribal Knowledge** (Prompt #2)
- High-risk warning
- Consequence explanation
- Text confirmation ("no")

✅ **Image Input** (Prompt #4)
- Upload screenshot
- Gemini analyzes visually

✅ **UI Context Awareness** (Prompt #6)
- Wrong page detection
- Redirect guidance
- Action succeeds on correct page

---

## 🎯 WHAT TO HIGHLIGHT

| Moment | Highlight |
|--------|-----------|
| Consequence warning | Zoom in, add red box |
| Booking percentage | Circle in red |
| Image upload | Show file dialog |
| Wrong page message | Highlight "📍" message |
| Success messages | Show ✅ clearly |
| Refresh actions | Show data updating |

---

## ⚠️ BACKUP PROMPTS

**If Evening Rush 17:00 doesn't exist:**
```
Remove vehicle from Bulk - 00:01
```
(25% booking, should trigger consequence)

**If image upload fails:**
```
How many unassigned vehicles are available?
```

**If fuzzy matching fails:**
```
Assign vehicle to morning commute
```

---

## ⏱️ TIMING

- Introduction: 15s
- Dashboard basics: 30s
- **Consequence flow: 60s** ⭐
- Vehicle assignment: 30s
- **Image input: 45s** ⭐
- Create stop: 45s
- **Context awareness: 30s** ⭐
- Create path: 30s
- Fuzzy matching: 20s
- Conclusion: 15s

**Total: 4:30 minutes**

---

## 🎥 RECORDING TIPS

1. **Before recording:**
   - Close unnecessary tabs
   - Disable notifications
   - Test microphone
   - Take screenshot for Prompt #4

2. **During recording:**
   - Speak clearly
   - Pause 2s after each response
   - Show full responses (don't cut off)
   - Use cursor to highlight important text

3. **After recording:**
   - Add text overlays for features
   - Speed up refresh/loading (1.5x)
   - Add arrows to highlight warnings
   - Low-volume background music

---

## ✅ PRE-FLIGHT CHECKLIST

- [ ] Backend running (port 8000)
- [ ] Frontend running (port 7860)
- [ ] Database has trips with high booking (85%+)
- [ ] Database has trips without vehicles
- [ ] Screenshot file ready
- [ ] Screen recorder ready
- [ ] Microphone tested
- [ ] Browser zoom 80-100%
- [ ] Notifications disabled

---

## 🎬 ACTION!

**Start recording when all checkboxes above are complete.**

**Remember:**
- Show the 3 critical features: Consequence Flow, Image Input, Context Awareness
- Speak confidently about what the agent is doing
- Highlight the fuzzy matching capabilities
- Demonstrate both UI pages clearly

**Good luck! 🚀**
