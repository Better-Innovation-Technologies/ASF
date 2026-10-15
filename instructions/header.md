# instructions.md — {{project_name}}

> **ASF v{{asf_version}}** · composed {{composed_at}} from the ASF instructions catalog {{catalog_ref}}

> **Layer L1 · Owner: Dev Lead**
> Development rules, code conventions and quality standards for this project.
> Where this file contradicts a task.md, this file wins — unless the task says otherwise explicitly.
> **Agents may not modify this file. It requires a Dev Lead gate.**

> **How this file is made.** Every section between `asf:module` markers comes from one module of the
> catalog, at the version written in the marker, and is recomposed from `.asf/instructions.json`. To
> change a section, change the choice of module (or propose a change to the module in the standard);
> rules that belong to this project only go in **Project rules** at the end, which is never recomposed.
