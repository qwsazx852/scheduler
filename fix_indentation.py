
import os

filepath = "app_scheduler.py"
with open(filepath, 'r') as f:
    lines = f.readlines()

# Identify blocks
# 0-67: Header + try:
header = lines[:68] # Lines 0..67 (68 lines). Line 67 is 'try:\n'

# Content to indent
# Line 70 (index 70, 1-based 71) is 'st.title...'
# We need to grab everything from index 70 to end, EXCLUDING the except block.
# Let's locate the except block dynamically to be safe.
except_start_idx = -1
except_end_idx = -1

for i, line in enumerate(lines):
    if line.strip().startswith("except Exception as e:"):
        except_start_idx = i
    if except_start_idx != -1 and "st.code(traceback.format_exc())" in line:
        except_end_idx = i
        break

print(f"Except block detected at: {except_start_idx} to {except_end_idx}")

# Body 1: From 'st.title' (index 70) to except_start_idx
body1 = lines[70:except_start_idx]

# Body 2: From except_end_idx + 1 to end
body2 = lines[except_end_idx+2:] # +1 to skip the line with st.code, +2 for margin?
# wait, line 481 was empty. 483 was else.
# Let's look at the file content again.
# 480: st.code...
# 481: <newline>
# 482: <newline>
# 483: else:

# So if except_end is 480. We want to resume at 483 (index 483).
# Let's just find the "else:" line.
else_idx = -1
for i in range(except_end_idx, len(lines)):
    if line.strip().startswith("else:") and "if" not in line: # simplistic
         # actually "else:"
         pass

# Safer: manually specifying ranges based on the view_file logic
# Header: 0 to 67 (inclusive) -> lines[:68]
# Body1: 70 to 475 (inclusive) -> lines[70:476]
# Except: 476 to 480 (inclusive) -> lines[476:481]
# Body2: 483 to end -> lines[483:]

# Note: Python slice [70:476] includes index 70 up to 475.
# This matches lines 71 to 476 (1-based).
# Line 476 1-based is "except Exception...". So index 475.
# So lines[70:476]?
# Line 71 (1-based) is index 70.
# Line 475 (1-based) is index 474.
# So lines[70:475] gives lines 71..475.

header = lines[:68] # 0..67. Line 67 is try.

# Gap lines 68, 69?
# 68 (line 69): empty
# 69 (line 70): # --- UI Layout ---
# All these should be indented too probably, or at least 69.
# Let's basically take everything from 68 onwards, exclude "except", then indent.

body_lines = []
except_block = []

# Scan from 68
i = 68
while i < len(lines):
    line = lines[i]
    if line.strip().startswith("except Exception as e:"):
        # Capture except block
        except_block.append(line)
        i += 1
        while i < len(lines):
             # Heuristic: capture until indentation drops or specific end
             # The except block is 476-480.
             # 477-480 are indented.
             sub = lines[i]
             except_block.append(sub)
             if "traceback.format_exc" in sub:
                 # Last line of except block
                 i += 1
                 break
             i += 1
    else:
        # Check if this is the "else" line that was unindented?
        # No, body2 is lines 483+ which matches "else:".
        body_lines.append(line)
        i += 1

# Now indent body_lines
indented_body = ["    " + line if line.strip() else line for line in body_lines]

# Reconstruct
new_content = "".join(header) + "".join(indented_body) + "\n" + "".join(except_block)

with open("app_scheduler.py", 'w') as f:
    f.write(new_content)

print("Fixed indentation.")
