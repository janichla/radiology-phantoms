19/06/2026

Fehlermeldung: "First layer defects were detected. If the defects are acceptable, tab "Resume" to resume the printing job. [0300 8002 101124]"

Ist es ein Druckerproblem oder ein Codeproblem?

- könnte Haftung, Z-Offset oder Kalibrierung sein
- könnte Mesh-Qualität (Marching_cubes, Zero-Setzen einer Hälfte in split_mold, Pin-/Socket-Voxel-Manipulation) sein
- könnte eine gekrümmte Auflagefläche sein
- Features könnten zu dünn sein

-> Claude meint, wenn die STLs gut aussehen, dann ist es eher ein Druckerproblem

-> Problem, dass die Kontaktfläche zur ersten Schicht nur die Pins sind?
vermutlich ist die Form der Leber schwierig zu drucken, daher das Problem

-> Leberhälfte mit den Pins umgedreht, um die Auflagefläche zu erhöhen

-> Randtyp: "nur äußeren Rand" (flacher Kragen neben dem Objekt); Floßschichten: 3 (Hilfsplatte auf der das Objekt gedruckt wird, also die anhebt praktisch)

-> neuer Druckversuch

03/07/26

Tips for Claude Code:
- \init to create CLAUDE.md file, so that Claude doesn't need to start from scratch when a new chat is opened
- use plan mode
- \clear after each task
- build slash commands for your repeat workflows
- wire up a validation loop
- use parallel sessions and sub-agents for isolated work
- encode workflows as skills
- follow plan-execute-review

Tasks:
1. Work on the locking mechanism
2. Remove two small parts inside
3. Print new liver

LOCKING MECHANISM
Pin & Socket Mechanismus

find_pin_voxel_positions in create_mold: Code schaut sich die Schnittebene an und berechnet die Mitte des Rings der Wandvoxel. Dann versteilt er 4 Stifte gleichmäßig im Kreis drumherum. 
Jeder Stift ist 5mm dick und 5mm hoch. Die Löcher sollen aktuell 0.3mm höher sein.

Probleme: - kein echter Einrast-Mechanismus -> nur durch Drucken sichtbar, ob das das Problem ist
- der Stift ist doppelt so breit wie die Wand und daher hängt die Hälfte in der Luft

17/08/2026

TO DO: 
- load stl file in repo
- remove small parts inside
- finish repo
- print new liver