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

-> Druckzeit halbieren, damit ich es heute abholen kann noch