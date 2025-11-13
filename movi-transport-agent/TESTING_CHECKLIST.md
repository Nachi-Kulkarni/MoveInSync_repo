# Movi Transport Agent - Testing Checklist

## Manual Testing Checklist for Ticket #11

This checklist helps you manually verify all critical functionality of the Movi Transport Agent system.

---

## Pre-Testing Setup

- [ ] Backend server running at `http://localhost:8000`
- [ ] Frontend server running at `http://localhost:7860`
- [ ] Database initialized with test data
- [ ] API keys configured (OpenRouter, OpenAI)
- [ ] Browser open to Gradio interface

---

## Test Scenario 1: Simple Read Query (Text Only)

### Steps:
1. Open Gradio interface at `http://localhost:7860`
2. Navigate to **🚌 Bus Dashboard** tab
3. In the Movi chat interface, type: **"How many unassigned vehicles?"**
4. Click **Send** or press Enter

### Expected Results:
- [ ] Response received within 3-5 seconds
- [ ] Agent responds with a count (e.g., "There are X unassigned vehicles")
- [ ] NO confirmation dialog appears
- [ ] TTS audio plays automatically (if enabled)
- [ ] Response is clear and accurate

### Notes:
```
Response time: ______ seconds
Agent response: _____________________
TTS working: YES / NO
```

---

## Test Scenario 2: Multimodal - Image Upload

### Steps:
1. Stay on **🚌 Bus Dashboard** tab
2. Click on **🎤 Multimodal Inputs** accordion to expand
3. Upload a screenshot of the dashboard (or any relevant image)
4. Type in text box: **"Remove vehicle from this trip"** (pointing to a trip in the image)
5. Click **Send**

### Expected Results:
- [ ] Image is uploaded successfully
- [ ] Gemini processes the image and extracts trip name
- [ ] Agent identifies the specific trip (e.g., "Bulk - 00:01")
- [ ] Consequence warning appears if trip has bookings
- [ ] Response time < 8 seconds

### Notes:
```
Image processed: YES / NO
Trip identified: _____________________
Warning shown: YES / NO
Response time: ______ seconds
```

---

## Test Scenario 3: High-Risk Action with Confirmation (FULL FLOW)

### Steps:
1. In Movi chat, type: **"Remove vehicle from Bulk - 00:01"**
2. Click **Send**
3. **Wait for warning message**
4. Observe the warning details
5. Click **✅ Yes, Proceed** button
6. Observe the execution result

### Expected Results:
- [ ] ⚠️ Warning message appears with:
  - [ ] Risk level indicator (🚨 or ⚠️)
  - [ ] Clear consequence explanation
  - [ ] Affected employee count (if applicable)
  - [ ] Bullet-pointed consequences
- [ ] Confirmation buttons visible:
  - [ ] ✅ Yes, Proceed (green/primary)
  - [ ] ❌ No, Cancel (red/secondary)
- [ ] After clicking "Yes":
  - [ ] Vehicle is removed from trip
  - [ ] Success/result message displayed
  - [ ] Buttons disappear
  - [ ] Trip data updated (check dashboard)

### Notes:
```
Warning appeared: YES / NO
Consequences listed: _____________________
Affected employees: ______ people
Action executed: YES / NO
Database updated: YES / NO
```

---

## Test Scenario 4: Cancellation Flow

### Steps:
1. In Movi chat, type: **"Remove vehicle from Path Path - 00:02"**
2. Click **Send**
3. **Wait for warning message** (if bookings exist)
4. Click **❌ No, Cancel** button
5. Observe the cancellation message

### Expected Results:
- [ ] Warning message appears (if high-risk)
- [ ] After clicking "No":
  - [ ] Action is NOT executed
  - [ ] Cancellation message displayed (e.g., "Action cancelled by user")
  - [ ] Vehicle remains assigned to trip
  - [ ] No database changes

### Notes:
```
Cancellation message: _____________________
Vehicle still assigned: YES / NO
```

---

## Test Scenario 5: Context Awareness (Page-Specific Behavior)

### Steps:
1. Navigate to **🛣️ Manage Routes** tab
2. In Movi chat, type: **"Create a new route for Path-1 at 09:00"**
3. Click **Send**
4. Observe the response
5. Now switch to **🚌 Bus Dashboard** tab
6. Type the same message again
7. Compare responses

### Expected Results:
- [ ] On Manage Routes tab:
  - [ ] Agent acknowledges correct page context
  - [ ] Processes route creation request appropriately
- [ ] On Bus Dashboard tab:
  - [ ] Agent may mention being on wrong page OR still processes request
  - [ ] Context is passed correctly in backend

### Notes:
```
Routes tab response: _____________________
Dashboard tab response: _____________________
Context awareness working: YES / NO
```

---

## Test Scenario 6: Error Handling (Invalid Input)

### Steps:
1. On any tab, type: **"Show me trip with ID 99999"**
2. Click **Send**
3. Observe the error handling

### Expected Results:
- [ ] NO system crash or error page
- [ ] Graceful error message from agent
- [ ] Agent suggests alternatives (e.g., "Available trips are...")
- [ ] Error message is user-friendly
- [ ] Chat interface remains functional

### Notes:
```
Error message: _____________________
Graceful handling: YES / NO
Suggestions provided: YES / NO
```

---

## Test Scenario 7: Voice Input (Audio Recording)

### Steps:
1. Click on **🎤 Multimodal Inputs** accordion
2. Click **Voice Input** microphone button
3. Allow microphone permissions (browser prompt)
4. Speak: **"List all stops for Path-2"**
5. Stop recording
6. Audio should be sent automatically
7. Observe the response

### Expected Results:
- [ ] Microphone permissions granted
- [ ] Audio recording successful
- [ ] Audio sent to backend for transcription (Gemini)
- [ ] Text extracted correctly from audio
- [ ] Agent processes query as normal text
- [ ] Response lists stops for Path-2
- [ ] TTS plays response aloud

### Notes:
```
Microphone working: YES / NO
Transcription accurate: YES / NO
Response correct: YES / NO
TTS playback: YES / NO
```

---

## Tool Verification Checklist

Test each of the 10 tools individually:

### Tool 1: `get_unassigned_vehicles_count`
- [ ] Query: **"How many unassigned vehicles?"**
- [ ] Response: Count returned
- [ ] Notes: _____________________

### Tool 2: `get_trip_status`
- [ ] Query: **"What's the status of Bulk - 00:01?"**
- [ ] Response: Status details returned
- [ ] Notes: _____________________

### Tool 3: `list_stops_for_path`
- [ ] Query: **"List stops for Path-1"**
- [ ] Response: Stop list returned
- [ ] Notes: _____________________

### Tool 4: `list_routes_by_path`
- [ ] Query: **"Show routes for Path-1"**
- [ ] Response: Route list returned
- [ ] Notes: _____________________

### Tool 5: `assign_vehicle_to_trip`
- [ ] Query: **"Assign vehicle MH-12-1234 to trip 1"**
- [ ] Response: Assignment confirmation
- [ ] Notes: _____________________

### Tool 6: `remove_vehicle_from_trip`
- [ ] Query: **"Remove vehicle from Bulk - 00:01"**
- [ ] Response: Warning → Confirmation → Removal
- [ ] Notes: _____________________

### Tool 7: `create_stop`
- [ ] Query: **"Create stop named 'Test Stop' at 12.9716, 77.5946"**
- [ ] Response: Stop created successfully
- [ ] Notes: _____________________

### Tool 8: `create_path`
- [ ] Query: **"Create path with stops 1, 3, 5"**
- [ ] Response: Path created
- [ ] Notes: _____________________

### Tool 9: `create_route`
- [ ] Query: **"Create route for Path-1 at 09:00, direction UP, capacity 40"**
- [ ] Response: Route created
- [ ] Notes: _____________________

### Tool 10: `get_consequences_for_action`
- [ ] Query: **"What happens if I delete vehicle from Bulk - 00:01?"**
- [ ] Response: Consequence details (without execution)
- [ ] Notes: _____________________

---

## Session Persistence Testing

### Multi-Turn Conversation:
1. **Turn 1**: Type: **"How many vehicles?"**
   - [ ] Response received
2. **Turn 2**: Type: **"What's the status of Bulk - 00:01?"**
   - [ ] Response received
3. **Turn 3**: Type: **"Remove vehicle from it"** (should remember "Bulk - 00:01")
   - [ ] Agent remembers context
   - [ ] Correct trip referenced
   - [ ] Session ID consistent

### Expected:
- [ ] Session ID remains consistent across turns
- [ ] Conversation history maintained
- [ ] Context preserved between messages

---

## Performance Benchmarks

| Test Type | Target | Actual | Pass/Fail |
|-----------|--------|--------|-----------|
| Simple read query | < 3s | ____s | [ ] |
| Complex query with consequence | < 5s | ____s | [ ] |
| Image processing | < 8s | ____s | [ ] |
| Video processing | < 15s | ____s | [ ] |
| TTS generation | < 2s | ____s | [ ] |

---

## UI/UX Verification

### Visual Elements:
- [ ] Warning messages have colored backgrounds (yellow/orange/red)
- [ ] Confirmation buttons styled correctly (green/red)
- [ ] Icons displayed (⚠️, 🚨, ✅, ❌)
- [ ] Chat messages formatted with proper spacing
- [ ] Tab navigation smooth
- [ ] Data tables display correctly
- [ ] Map renders with markers

### TTS Controls:
- [ ] 🔊 Enable Voice Output checkbox works
- [ ] Audio player appears for TTS
- [ ] Auto-play functionality works
- [ ] TTS can be disabled

### Multimodal Inputs:
- [ ] Audio input (microphone) accessible
- [ ] Image upload works
- [ ] Video upload works
- [ ] File size limits respected

---

## Bug Tracking

### Critical Bugs (Blocks Demo):
```
1. Bug: ____________________________
   Steps to reproduce: _____________
   Severity: CRITICAL
   Status: _________
```

### High Bugs:
```
1. Bug: ____________________________
   Steps to reproduce: _____________
   Severity: HIGH
   Status: _________
```

### Medium Bugs:
```
1. Bug: ____________________________
   Steps to reproduce: _____________
   Severity: MEDIUM
   Status: _________
```

### Low Bugs (Cosmetic):
```
1. Bug: ____________________________
   Steps to reproduce: _____________
   Severity: LOW
   Status: _________
```

---

## Final Checklist

### System Integration:
- [ ] Frontend ↔ Backend communication working
- [ ] Backend ↔ Database communication working
- [ ] LangGraph agent executing correctly
- [ ] All API endpoints responding
- [ ] Session management functional

### Feature Completeness:
- [ ] All 7 test scenarios pass
- [ ] All 10 tools verified
- [ ] Consequence checking works
- [ ] Confirmation flow works
- [ ] TTS works
- [ ] Multimodal input works

### Demo Readiness:
- [ ] No critical bugs
- [ ] UI looks professional
- [ ] Performance acceptable
- [ ] Error handling graceful
- [ ] System stable

---

## Sign-Off

**Tester Name**: _____________________
**Date**: _____________________
**Overall Status**: PASS / FAIL / PARTIAL

**Notes**:
```
________________________________________
________________________________________
________________________________________
```

---

**Next Steps:**
- [ ] Document bugs in BUGS.md
- [ ] Fix critical issues
- [ ] Proceed to TICKET #12 (Demo & Documentation)
