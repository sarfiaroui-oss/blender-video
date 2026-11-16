# Blender Video — Taj Mahal (2-minute animation)

A Blender project for a **two-character animated conversation about the Taj Mahal**.

## Creative brief
- **Duration:** 2 minutes (120 seconds)
- **Setting:** The Taj Mahal environment matching the reference image shared in the original project chat
- **Characters:** Two separate Tripo-generated 3D characters; prioritize attractive, expressive, high-quality faces
- **Animation:** Natural dialogue, facial expressions, mouth movement/lip sync, body gestures, cinematic camera shots, and smooth transitions
- **Audio:** Spoken conversation using an ONNX-based speech synthesis pipeline (e.g. Piper-compatible voice models), with synchronized animation
- **Output goal:** A polished, rendered 1080p video, ideally at 24 fps

## Current asset availability

The original conversation named three Tripo ZIP archives and contained an environment reference image, but **the actual ZIP data and image are not included in this repository** and were not accessible to the assistant when this repository was initialized.

See [ASSETS.md](ASSETS.md) for exact names and the import checklist. No completed video or prior Blender render has been recovered. This repository is a project handoff, **not a claim that the final video has been rendered**.

## Intended layout

```text
blender-video/
├── README.md
├── PROJECT_BRIEF.md
├── ASSETS.md
├── dialogue/
│   └── conversation.md
├── assets/
│   ├── source/       # Original Tripo ZIPs (upload when available)
│   ├── characters/   # Extracted GLB/FBX/OBJ files
│   └── reference/    # Original Taj Mahal environment image
├── audio/            # ONNX-generated dialogue WAV files
├── blender/          # Blender scenes and build scripts
└── renders/          # Render output (not stored in ordinary Git)
```

## Next steps
1. Upload the three **original Tripo ZIPs** and the **Taj Mahal reference image** to this project.
2. Inspect meshes, textures, facial topology, blendshapes, and skeletons; rig or rebuild facial controls where needed.
3. Build the referenced scene in Blender, block camera shots and character acting, and add synchronized ONNX voice.
4. Render a complete 2-minute MP4, review the results, then publish the scene and deliverables. Use Git LFS or release assets for files too large for normal Git.

> This repository captures the requirements visible from the earlier project chat. Unavailable binary assets are deliberately not represented as uploaded.
