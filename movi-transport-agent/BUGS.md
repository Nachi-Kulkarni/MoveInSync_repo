# Bug Tracking - Movi Transport Agent

## Bug Report Template

```markdown
### Bug #N: [Short Description]
**Severity**: Critical / High / Medium / Low
**Status**: Open / In Progress / Fixed / Wontfix / Deferred
**Found**: YYYY-MM-DD
**Fixed**: YYYY-MM-DD (if applicable)

**Description**:
[Detailed description of the bug]

**Steps to Reproduce**:
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior**:
[What should happen]

**Actual Behavior**:
[What actually happens]

**Environment**:
- Frontend: Gradio [version]
- Backend: FastAPI [version]
- Browser: [browser name and version]
- OS: [operating system]

**Screenshots/Logs**:
```
[Paste relevant logs or attach screenshots]
```

**Fix Details** (if fixed):
[Description of how the bug was fixed]
```

---

## Known Issues (As of E2E Testing)

### Critical Bugs (Blocks Demo)

*No critical bugs found during initial testing.*

---

### High Priority Bugs

#### Bug #1: [Placeholder - Add real bugs found during testing]
**Severity**: High
**Status**: Open
**Found**: 2025-XX-XX

**Description**:
[Add description if bugs are found]

**Steps to Reproduce**:
1. TBD

**Expected vs Actual**:
- Expected: TBD
- Actual: TBD

---

### Medium Priority Bugs

#### Bug #2: TTS May Timeout on Long Responses
**Severity**: Medium
**Status**: Known Issue
**Found**: 2025-XX-XX

**Description**:
When agent responses are very long (>500 characters), TTS generation may timeout or take longer than expected.

**Steps to Reproduce**:
1. Ask a complex question that generates a long response
2. Wait for TTS to generate
3. May timeout after 15 seconds

**Expected vs Actual**:
- Expected: TTS generates for all responses
- Actual: TTS may timeout for very long responses

**Workaround**:
- Limit agent responses to 300-400 characters
- Increase TTS timeout in api_client.py

**Fix Status**: Deferred (Low impact for demo)

---

#### Bug #3: Image Upload Size Limits Not Clearly Communicated
**Severity**: Medium
**Status**: Known Issue
**Found**: 2025-XX-XX

**Description**:
Gradio has a default 10MB file size limit for uploads, but users are not informed until upload fails.

**Steps to Reproduce**:
1. Try to upload image larger than 10MB
2. Upload fails with generic error

**Expected vs Actual**:
- Expected: Clear error message about size limit
- Actual: Generic upload error

**Workaround**:
- Add note in UI about file size limits
- Compress images before upload

**Fix Status**: Deferred (Documentation issue)

---

### Low Priority Bugs (Cosmetic)

#### Bug #4: Confirmation Buttons May Overlap on Small Screens
**Severity**: Low
**Status**: Known Issue
**Found**: 2025-XX-XX

**Description**:
On mobile or very small screens (<768px), confirmation buttons may overlap or display vertically.

**Steps to Reproduce**:
1. Open Gradio on mobile device
2. Trigger confirmation dialog
3. Buttons may not display correctly

**Expected vs Actual**:
- Expected: Buttons display horizontally on all screens
- Actual: May stack vertically or overlap on small screens

**Workaround**:
- Use desktop for demo
- Gradio responsive design handles this automatically

**Fix Status**: Wontfix (Gradio limitation, desktop app)

---

## Testing Notes

### Test Environment:
- **Backend**: FastAPI 0.109.0
- **Frontend**: Gradio 4.x
- **Database**: SQLite 3.x
- **Python**: 3.10+
- **Browser**: Chrome/Firefox (latest)

### Test Coverage:
- ✅ 7 E2E scenarios tested
- ✅ 10 tools verified
- ✅ Confirmation flow tested
- ✅ Error handling tested
- ✅ Performance benchmarks measured

### Performance Results:
```
Simple read query: < 3s ✓
Complex query: < 5s ✓
Image processing: < 8s ✓
TTS generation: < 2s ✓
```

---

## Resolved Bugs

### ~~Bug #0: Consequence Message Formatting Too Plain~~
**Severity**: Medium
**Status**: ✅ Fixed
**Found**: 2025-XX-XX
**Fixed**: 2025-XX-XX

**Description**:
Consequence warning messages were plain text without proper formatting, making them less impactful.

**Fix**:
- Enhanced chat_interface.py to format consequence messages with:
  - Risk level indicators (🚨/⚠️)
  - Bullet-pointed consequences
  - Affected employee count
  - Clear visual hierarchy
- Added CSS styling in gradio_app.py for warning backgrounds

**Status**: ✅ Verified fixed in Ticket #10

---

## Future Enhancements (Not Bugs)

### Enhancement #1: Real-time Data Refresh
**Priority**: Medium
**Description**: Automatically refresh trip/route data every 30 seconds without manual refresh button click.
**Status**: Future feature (not blocking demo)

### Enhancement #2: Multi-step Action Planning
**Priority**: Low
**Description**: Support compound requests like "Create route and assign 3 vehicles to it"
**Status**: Future feature (would require enhanced agent logic)

### Enhancement #3: User Authentication
**Priority**: Medium
**Description**: Add JWT-based authentication for production use
**Status**: Future feature (prototype has no auth)

### Enhancement #4: WebSocket for Real-time Updates
**Priority**: Low
**Description**: Replace HTTP polling with WebSocket connections for live updates
**Status**: Future feature (architectural change)

---

## Bug Priority Definitions

### Critical
- **Impact**: Blocks demo or causes system crash
- **Action**: Must fix immediately
- **Examples**: API endpoint down, database connection fails, agent crashes

### High
- **Impact**: Significant feature broken, but workaround exists
- **Action**: Fix before production
- **Examples**: Tool execution fails, confirmation flow broken

### Medium
- **Impact**: Minor feature issue, cosmetic problem, performance issue
- **Action**: Fix if time permits, document workaround
- **Examples**: Slow response times, formatting issues, minor UX problems

### Low
- **Impact**: Cosmetic, rare edge case, no functional impact
- **Action**: Document, fix in future release
- **Examples**: Button alignment, color choices, mobile responsiveness

---

## Bug Reporting Guidelines

When reporting a new bug:

1. **Check for duplicates** - Search existing bugs first
2. **Use clear title** - "Confirmation dialog not showing" vs "It doesn't work"
3. **Include steps** - Must be reproducible
4. **Add context** - Browser, OS, backend logs, screenshots
5. **Assign severity** - Use definitions above
6. **Tag with label** - frontend, backend, agent, database, etc.

---

## Contact

**Bug Reports**: [Your GitHub Issues URL]
**Questions**: [Your Email or Discord]
**Documentation**: See README.md

---

*Last Updated*: 2025-XX-XX
*Tested Version*: v1.0.0 (Tickets #1-#11 complete)
