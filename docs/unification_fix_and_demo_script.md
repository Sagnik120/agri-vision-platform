# The Unification Fix & Demo Script

## 4.1 One login / one farmer identity
- The system correctly uses a single SQLite table `farm` with a primary key `farm_id` representing the user.
- Both crop and livestock data strictly reference this one `farm_id`.

## 4.2 One history timeline, not two
- `farm_memory.get_all_history_records(farm_id)` correctly fetches an interleaved timeline, ordered by timestamp, merging `observation` and `diagnosis` tables for both domains.

## 4.3 One advisory flow, not two code paths
- The flow is properly unified in `pipeline.py:run_zone1_pipeline(domain: str)`. It takes the domain as a parameter and runs identical downstream logic (fusion -> gate -> advisory) regardless of whether the initial expert was crop or livestock.

## 4.4 The 60-second demo script

**0:00–0:15 (The Hook)**
- *Presenter states:* "Farmers today are forced to run one app for crops, and a completely different app or vet visit for livestock. This fragmentation is why adoption is so low. We solved that. Agri-Vision is one farmer, one login, one history, and one advisory engine for both."
- *Action:* Screen shows the unified login page, and logs in.

**0:15–0:35 (Crop Demo)**
- *Presenter states:* "Let's upload an image of a diseased tomato leaf. The local Edge AI instantly recognizes it and provides a local advisory. But watch this—it writes to the exact same farm record as everything else."
- *Action:* Upload crop image. Wait for local result. Click to Farm History tab. 

**0:35–0:55 (Livestock Cloud Escalation)**
- *Presenter states:* "Now, if a cow is sick, the same camera auto-detects the animal. But for safety-critical conditions like Foot and Mouth Disease, our safety gate triggers a cloud escalation to Gemini for expert veterinary validation. Different domain, same login, same history."
- *Action:* Upload livestock image. Wait for cloud result. Switch to Farm History tab to show them interleaved.

**0:55–1:00 (The Closer)**
- *Presenter states:* "As you can see on the timeline, total farm management is finally unified in one place."
- *Action:* Leave the screen on the Unified Farm History tab.
